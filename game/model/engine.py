"""Игровая логика — без Pygame."""

from __future__ import annotations

from game.config import (
    HINT_DURATION_MS,
    MESSAGE_DURATION_MS,
    PLAYBACK_START_DELAY_MS,
    TIMEOUT_MESSAGE_MS,
)
from game.model.settings import GameSettings
from game.model.entities import AppScreen, GamePhase
from game.model.rules import (
    apply_dynamic_difficulty,
    flash_duration_ms,
    gap_duration_ms,
    tempo_factor_for_level,
)
from game.model.sequence import append_color
from game.model.snapshot import GameSnapshot
from game.model.state import GameState


class GameEngine:
    def __init__(self, settings: GameSettings | None = None) -> None:
        self.settings = settings or GameSettings()
        self.state = GameState()

    def apply_settings(self, settings: GameSettings) -> None:
        self.settings = settings

    def reset(self, now_ms: int, *, grid_size: int = 2) -> None:
        self.state = GameState(lives=self.settings.lives_start, grid_size=grid_size)
        self.state.tempo_factor = tempo_factor_for_level(1)
        append_color(self.state.sequence, self._color_count())
        self._start_showing(now_ms)

    def _color_count(self) -> int:
        from game.model.field import color_count_for_grid

        return color_count_for_grid(self.state.grid_size)

    def load_state(self, state: GameState, now_ms: int) -> None:
        self.state = state
        if self.state.phase == GamePhase.SHOWING:
            self._start_showing(now_ms)
        elif self.state.phase == GamePhase.INPUT:
            self.state.answer_deadline_ms = now_ms + self._answer_time_ms()

    def export_state(self) -> GameState:
        return self.state

    def tick(self, now_ms: int) -> None:
        self._expire_hint(now_ms)
        self._update_playback(now_ms)

    def tick_input_timer(self, now_ms: int) -> bool:
        """True, если время ответа истекло."""
        if self.state.phase != GamePhase.INPUT:
            return False
        if now_ms >= self.state.answer_deadline_ms:
            self._on_wrong(now_ms, "Время вышло!", TIMEOUT_MESSAGE_MS)
            return True
        return False

    def press_color(self, color: int, now_ms: int) -> bool:
        if self.state.phase != GamePhase.INPUT:
            return False
        expected = self.state.sequence[self.state.player_index]
        if color != expected:
            self._on_wrong(now_ms)
            return False
        self.state.player_index += 1
        if self.state.player_index >= len(self.state.sequence):
            self.state.phase = GamePhase.LEVEL_DONE
            self.state.score += self.state.level * 10
            self._on_level_complete(now_ms)
        return True

    def is_game_over(self) -> bool:
        return self.state.phase == GamePhase.GAME_OVER

    def finalize_after_quit(self) -> tuple[int, int] | None:
        if self.state.phase == GamePhase.GAME_OVER and self.state.score > 0:
            return self.state.score, self.state.level
        return None

    def extend_answer_deadline(self, now_ms: int, remaining_ms: int) -> None:
        if self.state.phase == GamePhase.INPUT and remaining_ms > 0:
            self.state.answer_deadline_ms = now_ms + remaining_ms

    def get_answer_remaining_ms(self, now_ms: int) -> int:
        if self.state.phase != GamePhase.INPUT:
            return 0
        return max(0, self.state.answer_deadline_ms - now_ms)

    def build_snapshot(
        self,
        screen: AppScreen,
        *,
        has_saved_progress: bool,
        can_continue: bool,
        now_ms: int,
    ) -> GameSnapshot:
        s = self.state
        remaining: float | None = None
        if s.phase == GamePhase.INPUT:
            remaining = max(0.0, (s.answer_deadline_ms - now_ms) / 1000.0)

        phase_hints = {
            GamePhase.SHOWING: "Смотри и запоминай…",
            GamePhase.INPUT: "Твой ход!",
            GamePhase.LEVEL_DONE: "Верно!",
            GamePhase.GAME_OVER: "Игра окончена",
        }

        return GameSnapshot(
            screen=screen,
            phase=s.phase,
            level=s.level,
            score=s.score,
            lives=s.lives,
            sequence_length=len(s.sequence),
            tempo_factor=s.tempo_factor,
            active_flash=s.active_flash,
            hint_color=s.hint_color,
            show_hint=s.hint_color is not None and now_ms < s.hint_until_ms,
            answer_remaining_sec=remaining,
            status_message=s.status_message,
            show_status_message=bool(s.status_message) and now_ms < s.message_until_ms,
            phase_hint=phase_hints.get(s.phase, ""),
            has_saved_progress=has_saved_progress,
            can_continue=can_continue,
            settings=self.settings,
            grid_size=s.grid_size,
        )

    def _answer_time_ms(self) -> int:
        return int(self.settings.answer_time_sec * 1000)

    def _start_showing(self, now_ms: int) -> None:
        s = self.state
        s.phase = GamePhase.SHOWING
        s.playback_index = 0
        s.active_flash = None
        s.player_index = 0
        s.playback_next_ms = now_ms + PLAYBACK_START_DELAY_MS
        s.playback_flash_until_ms = 0

    def _update_playback(self, now_ms: int) -> None:
        s = self.state
        if s.phase != GamePhase.SHOWING:
            return

        if s.active_flash is not None:
            if now_ms >= s.playback_flash_until_ms:
                s.active_flash = None
                s.playback_next_ms = now_ms + gap_duration_ms(s)
            return

        if now_ms < s.playback_next_ms:
            return

        if s.playback_index >= len(s.sequence):
            s.phase = GamePhase.INPUT
            s.player_index = 0
            s.answer_deadline_ms = now_ms + self._answer_time_ms()
            return

        color = s.sequence[s.playback_index]
        s.active_flash = color
        s.playback_flash_until_ms = now_ms + flash_duration_ms(s)
        s.playback_index += 1

    def _on_wrong(
        self, now_ms: int, message: str = "", message_ms: int = 0
    ) -> None:
        s = self.state
        s.lives -= 1
        if self.settings.hints_enabled:
            expected = s.sequence[s.player_index]
            s.hint_color = expected
            s.hint_until_ms = now_ms + HINT_DURATION_MS
        msg = apply_dynamic_difficulty(s, level_passed=False, errored=True)
        if message:
            s.status_message = message
            s.message_until_ms = now_ms + message_ms
        elif msg:
            s.status_message = msg
            s.message_until_ms = now_ms + MESSAGE_DURATION_MS

        if s.lives <= 0:
            s.phase = GamePhase.GAME_OVER
        else:
            self._start_showing(now_ms)

    def _on_level_complete(self, now_ms: int) -> None:
        s = self.state
        msg = apply_dynamic_difficulty(s, level_passed=True, errored=False)
        if msg:
            s.status_message = msg
            s.message_until_ms = now_ms + MESSAGE_DURATION_MS
        s.level += 1
        s.tempo_factor = tempo_factor_for_level(s.level)
        append_color(s.sequence, self._color_count())
        self._start_showing(now_ms)

    def _expire_hint(self, now_ms: int) -> None:
        if self.state.hint_color is not None and now_ms >= self.state.hint_until_ms:
            self.state.hint_color = None

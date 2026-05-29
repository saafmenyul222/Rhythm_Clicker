"""Пользовательские настройки (без UI)."""

from __future__ import annotations

from dataclasses import dataclass

from game.config import ANSWER_TIME_SEC, LIVES_START, WINDOW_HEIGHT, WINDOW_WIDTH

ANSWER_TIME_OPTIONS = (8, 12, 16)
LIVES_OPTIONS = (3, 5)

# От меньшего к большему
RESOLUTION_OPTIONS: tuple[tuple[int, int], ...] = (
    (720, 560),
    (1024, 768),
    (1280, 720),
    (1600, 900),
    (1920, 1080),
    (1920, 1200),
)


@dataclass
class GameSettings:
    answer_time_sec: int = int(ANSWER_TIME_SEC)
    lives_start: int = LIVES_START
    hints_enabled: bool = True
    screen_width: int = WINDOW_WIDTH
    screen_height: int = WINDOW_HEIGHT
    fullscreen: bool = False

    def cycle_answer_time(self) -> None:
        opts = ANSWER_TIME_OPTIONS
        idx = opts.index(self.answer_time_sec) if self.answer_time_sec in opts else 1
        self.answer_time_sec = opts[(idx + 1) % len(opts)]

    def cycle_lives(self) -> None:
        opts = LIVES_OPTIONS
        idx = opts.index(self.lives_start) if self.lives_start in opts else 0
        self.lives_start = opts[(idx + 1) % len(opts)]

    def toggle_hints(self) -> None:
        self.hints_enabled = not self.hints_enabled

    def set_resolution(self, width: int, height: int) -> None:
        self.screen_width = width
        self.screen_height = height
        self.fullscreen = False

    def set_fullscreen(self, enabled: bool) -> None:
        self.fullscreen = enabled

    @property
    def resolution_label(self) -> str:
        if self.fullscreen:
            return "Полный экран"
        return f"{self.screen_width}×{self.screen_height}"

    def is_current_resolution(self, width: int, height: int) -> bool:
        return (
            not self.fullscreen
            and self.screen_width == width
            and self.screen_height == height
        )

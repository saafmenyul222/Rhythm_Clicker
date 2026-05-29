"""Правила темпа и динамической сложности."""

from game.config import (
    BASE_FLASH_MS,
    BASE_GAP_MS,
    ERROR_THRESHOLD,
    ERROR_WINDOW,
    STREAK_FOR_SKIP,
    TEMPO_MULTIPLIER,
    TEMPO_STEP_EVERY,
)
from game.model.sequence import append_color
from game.model.state import GameState


def tempo_factor_for_level(level: int) -> float:
    steps = (level - 1) // TEMPO_STEP_EVERY
    return TEMPO_MULTIPLIER**steps


def flash_duration_ms(state: GameState) -> int:
    return max(120, int(BASE_FLASH_MS / state.tempo_factor))


def gap_duration_ms(state: GameState) -> int:
    return max(60, int(BASE_GAP_MS / state.tempo_factor))


def apply_dynamic_difficulty(
    state: GameState, *, level_passed: bool, errored: bool
) -> str:
    if errored:
        state.recent_errors.append(True)
        state.streak_correct_levels = 0
        if len(state.recent_errors) > ERROR_WINDOW:
            state.recent_errors.pop(0)
        if sum(state.recent_errors) >= ERROR_THRESHOLD:
            state.tempo_factor = max(1.0, state.tempo_factor * 0.75)
            state.recent_errors.clear()
            return "Темп снижен — отдохни и сосредоточься"
    else:
        state.recent_errors.append(False)
        if len(state.recent_errors) > ERROR_WINDOW:
            state.recent_errors.pop(0)

    if level_passed:
        state.streak_correct_levels += 1
        if state.streak_correct_levels >= STREAK_FOR_SKIP:
            state.streak_correct_levels = 0
            state.level += 1
            append_color(state.sequence)
            return "Отлично! Пропуск +2 уровня"
    return ""

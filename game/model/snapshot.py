"""Снимок состояния для отрисовки (View читает только это)."""

from __future__ import annotations

from dataclasses import dataclass

from game.model.entities import AppScreen, GamePhase
from game.model.settings import GameSettings


@dataclass(frozen=True)
class GameSnapshot:
    screen: AppScreen
    phase: GamePhase
    level: int
    score: int
    lives: int
    sequence_length: int
    tempo_factor: float
    active_flash: int | None
    hint_color: int | None
    show_hint: bool
    answer_remaining_sec: float | None
    status_message: str
    show_status_message: bool
    phase_hint: str
    has_saved_progress: bool
    can_continue: bool
    settings: GameSettings
    grid_size: int = 2

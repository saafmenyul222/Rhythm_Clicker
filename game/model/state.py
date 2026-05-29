"""Состояние игровой сессии (чистые данные)."""

from __future__ import annotations

from dataclasses import dataclass, field

from game.config import LIVES_START
from game.model.entities import GamePhase


@dataclass
class GameState:
    grid_size: int = 2
    sequence: list[int] = field(default_factory=list)
    player_index: int = 0
    level: int = 1
    lives: int = LIVES_START
    phase: GamePhase = GamePhase.SHOWING
    score: int = 0
    streak_correct_levels: int = 0
    recent_errors: list[bool] = field(default_factory=list)
    tempo_factor: float = 1.0
    hint_color: int | None = None
    hint_until_ms: int = 0
    answer_deadline_ms: int = 0
    playback_index: int = 0
    playback_next_ms: int = 0
    playback_flash_until_ms: int = 0
    active_flash: int | None = None
    status_message: str = ""
    message_until_ms: int = 0

"""Сохранение и загрузка незавершённой игры."""

from __future__ import annotations

import json
from pathlib import Path

from game.config import DATA_DIR
from game.model.entities import GamePhase
from game.model.state import GameState

SAVE_PATH = DATA_DIR / "save.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def has_saved_game() -> bool:
    return SAVE_PATH.exists()


def save_progress(state: GameState) -> None:
    if state.phase == GamePhase.GAME_OVER:
        clear_progress()
        return
    _ensure_data_dir()
    payload = {
        "grid_size": state.grid_size,
        "sequence": state.sequence,
        "player_index": state.player_index,
        "level": state.level,
        "lives": state.lives,
        "phase": state.phase.value,
        "score": state.score,
        "streak_correct_levels": state.streak_correct_levels,
        "recent_errors": state.recent_errors,
        "tempo_factor": state.tempo_factor,
    }
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_progress() -> GameState | None:
    if not SAVE_PATH.exists():
        return None
    try:
        with open(SAVE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        phase = GamePhase(data["phase"])
        if phase == GamePhase.GAME_OVER:
            return None
        return GameState(
            grid_size=int(data.get("grid_size", 2)),
            sequence=list(data["sequence"]),
            player_index=int(data.get("player_index", 0)),
            level=int(data.get("level", 1)),
            lives=int(data.get("lives", 3)),
            phase=phase,
            score=int(data.get("score", 0)),
            streak_correct_levels=int(data.get("streak_correct_levels", 0)),
            recent_errors=list(data.get("recent_errors", [])),
            tempo_factor=float(data.get("tempo_factor", 1.0)),
        )
    except (json.JSONDecodeError, OSError, KeyError, ValueError):
        return None


def clear_progress() -> None:
    if SAVE_PATH.exists():
        SAVE_PATH.unlink()

"""Сохранение настроек в data/settings.json."""

from __future__ import annotations

import json

from game.config import DATA_DIR
from game.model.settings import GameSettings

SETTINGS_PATH = DATA_DIR / "settings.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> GameSettings:
    if not SETTINGS_PATH.exists():
        return GameSettings()
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return GameSettings(
            answer_time_sec=int(data.get("answer_time_sec", 12)),
            lives_start=int(data.get("lives_start", 3)),
            hints_enabled=bool(data.get("hints_enabled", True)),
            screen_width=int(data.get("screen_width", 720)),
            screen_height=int(data.get("screen_height", 560)),
            fullscreen=bool(data.get("fullscreen", False)),
        )
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return GameSettings()


def save_settings(settings: GameSettings) -> None:
    _ensure_data_dir()
    payload = {
        "answer_time_sec": settings.answer_time_sec,
        "lives_start": settings.lives_start,
        "hints_enabled": settings.hints_enabled,
        "screen_width": settings.screen_width,
        "screen_height": settings.screen_height,
        "fullscreen": settings.fullscreen,
    }
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

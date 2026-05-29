"""Топ рекордов (файл data/records.json)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from game.config import DATA_DIR, MAX_RECORDS

RECORDS_PATH = DATA_DIR / "records.json"


@dataclass
class RecordEntry:
    score: int
    level: int
    date: str

    @classmethod
    def from_dict(cls, data: dict) -> RecordEntry:
        return cls(
            score=int(data.get("score", 0)),
            level=int(data.get("level", 0)),
            date=str(data.get("date", "?")),
        )


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_records() -> list[RecordEntry]:
    if not RECORDS_PATH.exists():
        return []
    try:
        with open(RECORDS_PATH, encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            return []
        return [RecordEntry.from_dict(item) for item in raw]
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return []


def save_record(score: int, level: int) -> None:
    _ensure_data_dir()
    records = load_records()
    records.append(
        RecordEntry(
            score=score,
            level=level,
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
    )
    records.sort(key=lambda r: (r.score, r.level), reverse=True)
    records = records[:MAX_RECORDS]
    payload = [
        {"score": r.score, "level": r.level, "date": r.date} for r in records
    ]
    with open(RECORDS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

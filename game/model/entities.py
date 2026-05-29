"""Доменные сущности — без Pygame и без UI."""

from enum import Enum, IntEnum


class ColorId(IntEnum):
    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3


class GamePhase(str, Enum):
    SHOWING = "showing"
    INPUT = "input"
    LEVEL_DONE = "level_done"
    GAME_OVER = "game_over"


class AppScreen(str, Enum):
    MAIN_MENU = "main_menu"
    FIELD_SELECT = "field_select"
    PLAYING = "playing"
    PAUSED = "paused"
    SETTINGS = "settings"
    LEVELS = "levels"
    RECORDS = "records"
    GAME_OVER = "game_over"

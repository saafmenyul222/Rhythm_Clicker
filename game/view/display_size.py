"""Текущий размер окна (обновляется при смене разрешения)."""

from game.config import WINDOW_HEIGHT, WINDOW_WIDTH

REF_WIDTH = WINDOW_WIDTH
REF_HEIGHT = WINDOW_HEIGHT

WIDTH = WINDOW_WIDTH
HEIGHT = WINDOW_HEIGHT


def set_size(width: int, height: int) -> None:
    global WIDTH, HEIGHT
    WIDTH = width
    HEIGHT = height


def scale() -> float:
    return min(WIDTH / REF_WIDTH, HEIGHT / REF_HEIGHT)


def ui_scale() -> float:
    """Масштаб меню: слегка растёт на больших экранах, но без раздувания."""
    return min(1.12, scale())

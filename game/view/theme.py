"""Визуальная тема (только для View)."""

from game.model.entities import ColorId

BG_COLOR = (28, 30, 38)
TEXT_PRIMARY = (240, 240, 250)
TEXT_SECONDARY = (200, 200, 210)
TEXT_MUTED = (160, 160, 175)
TEXT_DIM = (180, 180, 195)
ACCENT = (255, 220, 120)
TIMER_WARN = (255, 100, 100)
TIMER_OK = (180, 220, 180)

# 2×2 — базовые четыре цвета
_BASE_PALETTE: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = [
    ((200, 50, 50), (255, 120, 120)),
    ((50, 80, 200), (120, 150, 255)),
    ((50, 160, 70), (120, 230, 140)),
    ((200, 180, 40), (255, 240, 100)),
]

# 3×3 — девять цветов
_EXTENDED_PALETTE: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = [
    *_BASE_PALETTE,
    ((200, 100, 50), (255, 160, 100)),
    ((140, 60, 180), (200, 130, 255)),
    ((50, 180, 180), (120, 240, 240)),
    ((220, 80, 140), (255, 150, 190)),
    ((160, 160, 170), (220, 220, 230)),
]

COLOR_PALETTE: dict[ColorId, tuple[str, tuple[int, int, int], tuple[int, int, int]]] = {
    ColorId.RED: ("Красный", *_BASE_PALETTE[0]),
    ColorId.BLUE: ("Синий", *_BASE_PALETTE[1]),
    ColorId.GREEN: ("Зелёный", *_BASE_PALETTE[2]),
    ColorId.YELLOW: ("Жёлтый", *_BASE_PALETTE[3]),
}

MENU_ITEMS = ("infinite", "continue", "levels", "settings", "records", "quit")


def color_pair(color_id: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if 0 <= color_id < len(_EXTENDED_PALETTE):
        return _EXTENDED_PALETTE[color_id]
    return (80, 80, 80), (120, 120, 120)

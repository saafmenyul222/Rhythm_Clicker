"""Геометрия UI (Pygame Rect — только во View)."""

from __future__ import annotations

import pygame

from game.model.field import color_count_for_grid
from game.view import display_size as ds


def color_button_rects(grid_size: int = 2) -> dict[int, pygame.Rect]:
    count = color_count_for_grid(grid_size)
    cx, cy = ds.WIDTH // 2, ds.HEIGHT // 2 + int(10 * ds.ui_scale())
    gap = int(12 * ds.ui_scale())

    if grid_size == 2:
        size = int(110 * ds.ui_scale())
        return {
            0: pygame.Rect(cx - size - gap // 2, cy - size - gap // 2, size, size),
            1: pygame.Rect(cx + gap // 2, cy - size - gap // 2, size, size),
            2: pygame.Rect(cx - size - gap // 2, cy + gap // 2, size, size),
            3: pygame.Rect(cx + gap // 2, cy + gap // 2, size, size),
        }

    size = int(88 * ds.ui_scale())
    grid_w = 3 * size + 2 * gap
    x0 = cx - grid_w // 2
    y0 = cy - grid_w // 2
    rects: dict[int, pygame.Rect] = {}
    for i in range(count):
        row, col = divmod(i, 3)
        x = x0 + col * (size + gap)
        y = y0 + row * (size + gap)
        rects[i] = pygame.Rect(x, y, size, size)
    return rects


def field_select_rects() -> dict[str, pygame.Rect]:
    s = ds.ui_scale()
    w, h = int(200 * s), int(80 * s)
    gap = int(20 * s)
    cx = ds.WIDTH // 2
    y = int(ds.HEIGHT * 0.38)
    total_w = w * 2 + gap
    x0 = cx - total_w // 2
    return {
        "grid_2": pygame.Rect(x0, y, w, h),
        "grid_3": pygame.Rect(x0 + w + gap, y, w, h),
    }


def field_select_back_rect() -> pygame.Rect:
    s = ds.ui_scale()
    w, h = int(200 * s), int(36 * s)
    return pygame.Rect(ds.WIDTH // 2 - w // 2, int(ds.HEIGHT * 0.78), w, h)


def _stacked_buttons(
    keys: tuple[str, ...],
    *,
    y0: int | None = None,
    w: int = 260,
    h: int = 34,
    gap: int = 6,
) -> dict[str, pygame.Rect]:
    s = ds.ui_scale()
    w = int(w * s)
    h = int(h * s)
    gap = int(gap * s)
    cx = ds.WIDTH // 2
    if y0 is None:
        total_h = len(keys) * h + max(0, len(keys) - 1) * gap
        y0 = max(int(ds.HEIGHT * 0.18), (ds.HEIGHT - total_h) // 2)
    rects: dict[str, pygame.Rect] = {}
    for i, key in enumerate(keys):
        rects[key] = pygame.Rect(cx - w // 2, y0 + i * (h + gap), w, h)
    return rects


def menu_button_rects() -> dict[str, pygame.Rect]:
    return _stacked_buttons(
        ("infinite", "continue", "levels", "settings", "records", "quit"),
        w=280,
        h=38,
        gap=6,
    )


def level_select_rects(count: int = 10, *, cols: int = 5) -> dict[int, pygame.Rect]:
    """Сетка кнопок уровней (1..count), компактная и по центру экрана."""
    s = ds.ui_scale()
    btn = int(56 * s)
    gap = int(10 * s)
    rows = (count + cols - 1) // cols
    grid_w = cols * btn + (cols - 1) * gap
    grid_h = rows * btn + (rows - 1) * gap
    x0 = (ds.WIDTH - grid_w) // 2
    top = int(ds.HEIGHT * 0.14)
    bottom = int(ds.HEIGHT * 0.82)
    y0 = top + max(0, (bottom - top - grid_h) // 2)
    rects: dict[int, pygame.Rect] = {}
    for i in range(count):
        row, col = divmod(i, cols)
        x = x0 + col * (btn + gap)
        y = y0 + row * (btn + gap)
        rects[i + 1] = pygame.Rect(x, y, btn, btn)
    return rects


def levels_back_button_rect() -> pygame.Rect:
    s = ds.ui_scale()
    w, h = int(200 * s), int(36 * s)
    y = int(ds.HEIGHT * 0.88) - h
    return pygame.Rect(ds.WIDTH // 2 - w // 2, y, w, h)


def pause_menu_rects() -> dict[str, pygame.Rect]:
    return _stacked_buttons(
        ("resume", "settings", "main_menu"),
        y0=ds.HEIGHT // 2 - int(50 * ds.ui_scale()),
        w=280,
        h=38,
        gap=6,
    )


def settings_option_rects(*, dropdown_open: bool = False) -> dict[str, pygame.Rect]:
    s = ds.ui_scale()
    h = int(40 * s)
    gap = int(6 * s)
    rects = _stacked_buttons(
        ("answer_time", "lives", "hints", "resolution", "fullscreen", "back"),
        y0=int(ds.HEIGHT * 0.10),
        w=380,
        h=h,
        gap=gap,
    )
    if dropdown_open:
        from game.model.settings import RESOLUTION_OPTIONS

        item_h = max(28, int(30 * s))
        offset = len(RESOLUTION_OPTIONS) * (item_h + 1) + 6
        for key in ("fullscreen", "back"):
            rects[key].y += offset
    return rects


def resolution_dropdown_rects(anchor: pygame.Rect) -> dict[str, pygame.Rect]:
    """Список разрешений под кнопкой «Разрешение»."""
    from game.model.settings import RESOLUTION_OPTIONS

    item_h = max(28, int(30 * ds.ui_scale()))
    gap = 2
    y = anchor.bottom + gap
    rects: dict[str, pygame.Rect] = {}
    for i, (w, h) in enumerate(RESOLUTION_OPTIONS):
        key = f"{w}x{h}"
        rects[key] = pygame.Rect(anchor.x, y + i * (item_h + 1), anchor.width, item_h)
    return rects


def pause_button_rect() -> pygame.Rect:
    margin = int(12 * ds.ui_scale())
    w, h = int(40 * ds.ui_scale()), int(32 * ds.ui_scale())
    return pygame.Rect(ds.WIDTH - w - margin, margin, w, h)


def hit_button(pos: tuple[int, int], rects: dict[str, pygame.Rect]) -> str | None:
    for key, rect in rects.items():
        if rect.collidepoint(pos):
            return key
    return None


def hit_color_button(pos: tuple[int, int], rects: dict[int, pygame.Rect]) -> int | None:
    for cid, rect in rects.items():
        if rect.collidepoint(pos):
            return int(cid)
    return None

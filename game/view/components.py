"""Переиспользуемые UI-компоненты."""

from __future__ import annotations

import pygame

from game.view.theme import TEXT_PRIMARY, color_pair


def draw_menu_button(
    surf: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    font: pygame.font.Font,
    *,
    enabled: bool = True,
    hovered: bool = False,
) -> None:
    if not enabled:
        fill = (55, 58, 68)
        text_col = (110, 112, 120)
    elif hovered:
        fill = (70, 120, 180)
        text_col = TEXT_PRIMARY
    else:
        fill = (50, 75, 110)
        text_col = TEXT_PRIMARY
    pygame.draw.rect(surf, fill, rect, border_radius=10)
    pygame.draw.rect(surf, (30, 30, 30), rect, 2, border_radius=10)
    pad = 14
    max_w = max(40, rect.width - pad * 2)
    draw_font = _font_fitting(label, font, max_w)
    text = draw_font.render(label, True, text_col)
    surf.blit(text, text.get_rect(center=rect.center))


def _font_fitting(label: str, font: pygame.font.Font, max_width: int) -> pygame.font.Font:
    if font.size(label)[0] <= max_width:
        return font
    base_size = font.get_height()
    for size in range(base_size - 1, 11, -1):
        candidate = pygame.font.SysFont("segoeui", size)
        if candidate.size(label)[0] <= max_width:
            return candidate
    return pygame.font.SysFont("segoeui", 12)


def draw_color_button(
    surf: pygame.Surface,
    color_id: int,
    rect: pygame.Rect,
    *,
    lit: bool = False,
    hint: bool = False,
) -> None:
    base, bright = color_pair(color_id)
    fill = bright if lit or hint else base
    if hint and not lit:
        pygame.draw.rect(surf, bright, rect.inflate(8, 8), border_radius=14)
    pygame.draw.rect(surf, fill, rect, border_radius=12)
    pygame.draw.rect(surf, (30, 30, 30), rect, 3, border_radius=12)

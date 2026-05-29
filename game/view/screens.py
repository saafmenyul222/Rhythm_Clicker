"""Отрисовка экранов по GameSnapshot."""

from __future__ import annotations

import pygame

from game.config import LEVEL_SELECT_COUNT
from game.model.entities import AppScreen
from game.model.snapshot import GameSnapshot
from game.persistence.records import RecordEntry
from game.view import components, display_size as ds, layout
from game.view.theme import (
    ACCENT,
    BG_COLOR,
    TEXT_DIM,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TIMER_OK,
    TIMER_WARN,
)

MAIN_MENU_LABELS = {
    "infinite": "Бесконечный режим",
    "continue": "Продолжить",
    "levels": "Уровни",
    "settings": "Настройки",
    "records": "Рекорды",
    "quit": "Выход",
}

PAUSE_MENU_LABELS = {
    "resume": "Продолжить",
    "main_menu": "В главное меню",
    "settings": "Настройки",
}

LEVELS_NOTICE_TEXT = "Пока ничего нет"
LEVELS_NOTICE_MS = 2500

class ScreenRenderer:
    def __init__(self) -> None:
        self.title_font = pygame.font.SysFont("segoeui", 36, bold=True)
        self.ui_font = pygame.font.SysFont("segoeui", 22)
        self.small_font = pygame.font.SysFont("segoeui", 18)
        self.menu_font = pygame.font.SysFont("segoeui", 24)
        self._hovered: str | None = None
        self._hover_group: str = ""
        self.resolution_dropdown_open = False
        self.resolution_dropdown_rects: dict[str, pygame.Rect] = {}
        self.levels_notice = ""
        self.levels_notice_until_ms = 0
        self.play_grid_size = 2
        self.rebuild_layout()

    def set_play_grid_size(self, grid_size: int) -> None:
        self.play_grid_size = grid_size
        self.color_rects = layout.color_button_rects(grid_size)

    def rebuild_layout(self) -> None:
        self.color_rects = layout.color_button_rects(self.play_grid_size)
        self.field_select_rects = layout.field_select_rects()
        self.field_select_back_rect = layout.field_select_back_rect()
        self.menu_rects = layout.menu_button_rects()
        self.pause_menu_rects = layout.pause_menu_rects()
        self.settings_rects = layout.settings_option_rects(
            dropdown_open=self.resolution_dropdown_open
        )
        self.pause_btn_rect = layout.pause_button_rect()
        self.level_rects = layout.level_select_rects(LEVEL_SELECT_COUNT)
        self.levels_back_rect = layout.levels_back_button_rect()
        self._rebuild_resolution_dropdown()

    def _rebuild_resolution_dropdown(self) -> None:
        if "resolution" in self.settings_rects:
            anchor = self.settings_rects["resolution"]
            self.resolution_dropdown_rects = layout.resolution_dropdown_rects(anchor)
        else:
            self.resolution_dropdown_rects = {}

    def toggle_resolution_dropdown(self) -> None:
        self.resolution_dropdown_open = not self.resolution_dropdown_open
        self.settings_rects = layout.settings_option_rects(
            dropdown_open=self.resolution_dropdown_open
        )
        self._rebuild_resolution_dropdown()

    def close_resolution_dropdown(self) -> None:
        if not self.resolution_dropdown_open:
            return
        self.resolution_dropdown_open = False
        self.settings_rects = layout.settings_option_rects(dropdown_open=False)

    def resolution_dropdown_hit(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        for key, rect in self.resolution_dropdown_rects.items():
            if rect.collidepoint(pos):
                w, h = key.split("x")
                return int(w), int(h)
        return None

    def point_in_resolution_dropdown(self, pos: tuple[int, int]) -> bool:
        if self.settings_rects.get("resolution", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
            return True
        return any(r.collidepoint(pos) for r in self.resolution_dropdown_rects.values())

    def set_hover(self, group: str, key: str | None) -> None:
        self._hover_group = group
        self._hovered = key

    def _is_hovered(self, group: str, key: str) -> bool:
        return self._hover_group == group and self._hovered == key

    def show_levels_notice(self, text: str, now_ms: int) -> None:
        self.levels_notice = text
        self.levels_notice_until_ms = now_ms + LEVELS_NOTICE_MS

    def menu_hit(self, pos: tuple[int, int]) -> str | None:
        return layout.hit_button(pos, self.menu_rects)

    def level_hit(self, pos: tuple[int, int]) -> int | None:
        for num, rect in self.level_rects.items():
            if rect.collidepoint(pos):
                return num
        return None

    def levels_back_hit(self, pos: tuple[int, int]) -> bool:
        return self.levels_back_rect.collidepoint(pos)

    def field_select_hit(self, pos: tuple[int, int]) -> int | None:
        if self.field_select_rects["grid_2"].collidepoint(pos):
            return 2
        if self.field_select_rects["grid_3"].collidepoint(pos):
            return 3
        return None

    def field_select_back_hit(self, pos: tuple[int, int]) -> bool:
        return self.field_select_back_rect.collidepoint(pos)

    def pause_menu_hit(self, pos: tuple[int, int]) -> str | None:
        return layout.hit_button(pos, self.pause_menu_rects)

    def settings_hit(self, pos: tuple[int, int]) -> str | None:
        return layout.hit_button(pos, self.settings_rects)

    def pause_btn_hit(self, pos: tuple[int, int]) -> bool:
        return self.pause_btn_rect.collidepoint(pos)

    def color_hit(self, pos: tuple[int, int]) -> int | None:
        return layout.hit_color_button(pos, self.color_rects)

    def active_hover_group(self, screen: AppScreen) -> str | None:
        if screen == AppScreen.MAIN_MENU:
            return "main"
        if screen == AppScreen.PAUSED:
            return "pause"
        if screen == AppScreen.SETTINGS:
            return "settings"
        if screen == AppScreen.LEVELS:
            return "levels"
        if screen == AppScreen.FIELD_SELECT:
            return "field_select"
        if screen == AppScreen.PLAYING:
            return "pause_btn"
        return None

    def hit_test_hover(self, screen: AppScreen, pos: tuple[int, int]) -> None:
        group = self.active_hover_group(screen)
        if group is None:
            self.set_hover("", None)
            return
        if group == "main":
            self.set_hover("main", self.menu_hit(pos))
        elif group == "pause":
            self.set_hover("pause", self.pause_menu_hit(pos))
        elif group == "settings":
            if self.resolution_dropdown_open:
                for key, rect in self.resolution_dropdown_rects.items():
                    if rect.collidepoint(pos):
                        self.set_hover("res_drop", key)
                        return
            self.set_hover("settings", self.settings_hit(pos))
        elif group == "levels":
            if self.levels_back_hit(pos):
                self.set_hover("levels", "back")
                return
            for num, rect in self.level_rects.items():
                if rect.collidepoint(pos):
                    self.set_hover("levels", str(num))
                    return
            self.set_hover("levels", None)
        elif group == "field_select":
            if self.field_select_back_hit(pos):
                self.set_hover("field_select", "back")
                return
            hit = layout.hit_button(pos, self.field_select_rects)
            self.set_hover("field_select", hit)
        elif group == "pause_btn":
            self.set_hover("pause_btn", "pause" if self.pause_btn_hit(pos) else None)

    def draw(
        self,
        surf: pygame.Surface,
        snapshot: GameSnapshot,
        records: list[RecordEntry],
        now_ms: int,
    ) -> None:
        surf.fill(BG_COLOR)
        title = self.title_font.render("Повтори сигнал", True, TEXT_PRIMARY)
        surf.blit(title, (ds.WIDTH // 2 - title.get_width() // 2, 16))

        if snapshot.screen == AppScreen.MAIN_MENU:
            self._draw_main_menu(surf, snapshot)
        elif snapshot.screen == AppScreen.RECORDS:
            self._draw_records(surf, records)
        elif snapshot.screen == AppScreen.LEVELS:
            self._draw_levels(surf, now_ms)
        elif snapshot.screen == AppScreen.FIELD_SELECT:
            self._draw_field_select(surf)
        elif snapshot.screen == AppScreen.SETTINGS:
            self._draw_settings(surf, snapshot)
        else:
            self._draw_playfield(surf, snapshot, now_ms)
            if snapshot.screen == AppScreen.PLAYING:
                self._draw_pause_button(surf)
            if snapshot.screen == AppScreen.PAUSED:
                self._draw_pause_overlay(surf)
            if snapshot.screen == AppScreen.GAME_OVER:
                self._draw_game_over_overlay(surf, snapshot)

    def _draw_pause_button(self, surf: pygame.Surface) -> None:
        hovered = self._is_hovered("pause_btn", "pause")
        fill = (90, 100, 120) if hovered else (60, 68, 85)
        pygame.draw.rect(surf, fill, self.pause_btn_rect, border_radius=8)
        pygame.draw.rect(surf, (30, 30, 30), self.pause_btn_rect, 2, border_radius=8)
        bars_x = self.pause_btn_rect.centerx - 10
        bars_y = self.pause_btn_rect.centery - 10
        for dx in (0, 14):
            pygame.draw.rect(surf, TEXT_PRIMARY, (bars_x + dx, bars_y, 6, 20), border_radius=2)

    def _draw_main_menu(self, surf: pygame.Surface, snapshot: GameSnapshot) -> None:
        subtitle = self.ui_font.render(
            "Запомни цвета и повтори сигнал", True, TEXT_SECONDARY
        )
        surf.blit(subtitle, (ds.WIDTH // 2 - subtitle.get_width() // 2, 58))

        for key, rect in self.menu_rects.items():
            enabled = key != "continue" or snapshot.can_continue
            components.draw_menu_button(
                surf,
                rect,
                MAIN_MENU_LABELS[key],
                self.menu_font,
                enabled=enabled,
                hovered=self._is_hovered("main", key) and enabled,
            )

        hint = self.small_font.render(
            "P — пауза  |  ESC — назад", True, TEXT_MUTED
        )
        surf.blit(hint, (ds.WIDTH // 2 - hint.get_width() // 2, ds.HEIGHT - 36))

    def _draw_playfield(
        self, surf: pygame.Surface, snapshot: GameSnapshot, now_ms: int
    ) -> None:
        info = (
            f"Уровень {snapshot.level}  |  "
            f"Очки {snapshot.score}  |  "
            f"Жизни {'♥' * snapshot.lives}"
        )
        surf.blit(self.ui_font.render(info, True, TEXT_PRIMARY), (20, 58))
        surf.blit(
            self.ui_font.render(
                f"Длина сигнала: {snapshot.sequence_length}", True, TEXT_DIM
            ),
            (20, 82),
        )
        surf.blit(
            self.ui_font.render(f"Темп: x{snapshot.tempo_factor:.2f}", True, TEXT_DIM),
            (20, 104),
        )
        surf.blit(
            self.ui_font.render(
                f"Поле: {snapshot.grid_size}×{snapshot.grid_size}", True, TEXT_DIM
            ),
            (20, 126),
        )

        if snapshot.answer_remaining_sec is not None:
            rem = snapshot.answer_remaining_sec
            col = TIMER_WARN if rem < 3 else TIMER_OK
            timer = self.ui_font.render(f"Время: {rem:.1f} с", True, col)
            surf.blit(timer, (ds.WIDTH - timer.get_width() - 70, 58))

        if snapshot.show_status_message:
            m = self.ui_font.render(snapshot.status_message, True, ACCENT)
            surf.blit(m, (ds.WIDTH // 2 - m.get_width() // 2, ds.HEIGHT - 48))

        if snapshot.phase_hint and snapshot.screen != AppScreen.PAUSED:
            t = self.ui_font.render(snapshot.phase_hint, True, TEXT_MUTED)
            surf.blit(t, (ds.WIDTH // 2 - t.get_width() // 2, ds.HEIGHT - 78))

        if snapshot.screen == AppScreen.PAUSED:
            return

        for cid, rect in self.color_rects.items():
            lit = snapshot.active_flash == cid
            hint = snapshot.show_hint and snapshot.hint_color == cid
            components.draw_color_button(surf, cid, rect, lit=lit, hint=hint)

    def _draw_pause_overlay(self, surf: pygame.Surface) -> None:
        overlay = pygame.Surface((ds.WIDTH, ds.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surf.blit(overlay, (0, 0))
        t = self.title_font.render("Пауза", True, TEXT_PRIMARY)
        surf.blit(t, (ds.WIDTH // 2 - t.get_width() // 2, ds.HEIGHT // 2 - 130))

        for key, rect in self.pause_menu_rects.items():
            components.draw_menu_button(
                surf,
                rect,
                PAUSE_MENU_LABELS[key],
                self.menu_font,
                hovered=self._is_hovered("pause", key),
            )

    def _draw_settings(self, surf: pygame.Surface, snapshot: GameSnapshot) -> None:
        overlay = pygame.Surface((ds.WIDTH, ds.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surf.blit(overlay, (0, 0))

        title = self.title_font.render("Настройки", True, TEXT_PRIMARY)
        surf.blit(title, (ds.WIDTH // 2 - title.get_width() // 2, 50))

        s = snapshot.settings
        arrow = "▲" if self.resolution_dropdown_open else "▼"
        labels = {
            "answer_time": f"Время на ответ: {s.answer_time_sec} с",
            "lives": f"Жизни: {s.lives_start}",
            "hints": f"Подсказки: {'Вкл' if s.hints_enabled else 'Выкл'}",
            "resolution": f"Разрешение: {s.resolution_label}  {arrow}",
            "fullscreen": f"Полный экран: {'Вкл' if s.fullscreen else 'Выкл'}",
            "back": "←  Назад",
        }
        for key, rect in self.settings_rects.items():
            components.draw_menu_button(
                surf,
                rect,
                labels[key],
                self.ui_font,
                hovered=self._is_hovered("settings", key),
            )

        if self.resolution_dropdown_open:
            self._draw_resolution_dropdown(surf, snapshot)

        hint = self.small_font.render(
            "Время и жизни — для новой игры; экран — сразу", True, TEXT_MUTED
        )
        surf.blit(hint, (ds.WIDTH // 2 - hint.get_width() // 2, ds.HEIGHT - 40))

    def _draw_resolution_dropdown(
        self, surf: pygame.Surface, snapshot: GameSnapshot
    ) -> None:
        if not self.resolution_dropdown_rects:
            return
        keys = list(self.resolution_dropdown_rects.keys())
        first = self.resolution_dropdown_rects[keys[0]]
        last = self.resolution_dropdown_rects[keys[-1]]
        panel = pygame.Rect(
            first.x - 2,
            first.y - 2,
            first.width + 4,
            last.bottom - first.y + 4,
        )
        pygame.draw.rect(surf, (35, 38, 48), panel, border_radius=8)
        pygame.draw.rect(surf, (80, 90, 110), panel, 2, border_radius=8)

        s = snapshot.settings
        for key, rect in self.resolution_dropdown_rects.items():
            w, h = (int(p) for p in key.split("x"))
            selected = s.is_current_resolution(w, h)
            hovered = self._is_hovered("res_drop", key)
            if selected:
                fill = (55, 95, 140)
            elif hovered:
                fill = (65, 75, 95)
            else:
                fill = (48, 52, 62)
            pygame.draw.rect(surf, fill, rect)
            mark = "● " if selected else "   "
            text = self.ui_font.render(f"{mark}{w}×{h}", True, TEXT_PRIMARY)
            surf.blit(text, (rect.x + 10, rect.centery - text.get_height() // 2))

    def _draw_game_over_overlay(self, surf: pygame.Surface, snapshot: GameSnapshot) -> None:
        overlay = pygame.Surface((ds.WIDTH, ds.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))
        t = self.title_font.render("Конец игры", True, TEXT_PRIMARY)
        surf.blit(t, (ds.WIDTH // 2 - t.get_width() // 2, ds.HEIGHT // 2 - 80))
        score_t = self.ui_font.render(
            f"Очки: {snapshot.score}  |  Уровень: {snapshot.level}", True, ACCENT
        )
        surf.blit(score_t, (ds.WIDTH // 2 - score_t.get_width() // 2, ds.HEIGHT // 2 - 30))
        sub = self.ui_font.render("ENTER — в меню", True, TEXT_SECONDARY)
        surf.blit(sub, (ds.WIDTH // 2 - sub.get_width() // 2, ds.HEIGHT // 2 + 20))

    def _draw_field_select(self, surf: pygame.Surface) -> None:
        overlay = pygame.Surface((ds.WIDTH, ds.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        title = self.title_font.render("Размер поля", True, TEXT_PRIMARY)
        surf.blit(title, (ds.WIDTH // 2 - title.get_width() // 2, int(ds.HEIGHT * 0.18)))

        labels = {"grid_2": "2 × 2", "grid_3": "3 × 3"}
        for key, rect in self.field_select_rects.items():
            components.draw_menu_button(
                surf,
                rect,
                labels[key],
                self.title_font,
                hovered=self._is_hovered("field_select", key),
            )

        components.draw_menu_button(
            surf,
            self.field_select_back_rect,
            "Назад",
            self.menu_font,
            hovered=self._is_hovered("field_select", "back"),
        )

    def _draw_levels(self, surf: pygame.Surface, now_ms: int) -> None:
        overlay = pygame.Surface((ds.WIDTH, ds.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        heading = self.title_font.render("Уровни", True, TEXT_PRIMARY)
        surf.blit(heading, (ds.WIDTH // 2 - heading.get_width() // 2, int(ds.HEIGHT * 0.06)))

        for num, rect in self.level_rects.items():
            hovered = self._is_hovered("levels", str(num))
            fill = (70, 120, 180) if hovered else (50, 75, 110)
            pygame.draw.rect(surf, fill, rect, border_radius=10)
            pygame.draw.rect(surf, (30, 30, 30), rect, 2, border_radius=10)
            label = self.ui_font.render(str(num), True, TEXT_PRIMARY)
            surf.blit(label, label.get_rect(center=rect.center))

        components.draw_menu_button(
            surf,
            self.levels_back_rect,
            "←  Назад в меню",
            self.menu_font,
            hovered=self._is_hovered("levels", "back"),
        )

        if self.levels_notice and now_ms < self.levels_notice_until_ms:
            box_w = int(340 * ds.scale())
            box_h = int(56 * ds.scale())
            box = pygame.Rect(ds.WIDTH // 2 - box_w // 2, ds.HEIGHT // 2 - box_h // 2, box_w, box_h)
            pygame.draw.rect(surf, (45, 50, 65), box, border_radius=12)
            pygame.draw.rect(surf, ACCENT, box, 2, border_radius=12)
            notice = self.ui_font.render(self.levels_notice, True, ACCENT)
            surf.blit(notice, notice.get_rect(center=box.center))
        elif now_ms >= self.levels_notice_until_ms:
            self.levels_notice = ""

    def _draw_records(self, surf: pygame.Surface, records: list[RecordEntry]) -> None:
        overlay = pygame.Surface((ds.WIDTH, ds.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surf.blit(overlay, (0, 0))
        title = self.title_font.render("Топ-10 рекордов", True, TEXT_PRIMARY)
        surf.blit(title, (ds.WIDTH // 2 - title.get_width() // 2, 40))

        if not records:
            empty = self.ui_font.render("Пока нет записей", True, TEXT_DIM)
            surf.blit(empty, (ds.WIDTH // 2 - empty.get_width() // 2, 120))
        else:
            for i, rec in enumerate(records):
                line = f"{i + 1}. {rec.score} очков (ур. {rec.level}) — {rec.date}"
                t = self.ui_font.render(line, True, TEXT_SECONDARY)
                surf.blit(t, (80, 100 + i * 32))

        back = self.ui_font.render("ESC — назад в меню", True, TEXT_MUTED)
        surf.blit(back, (ds.WIDTH // 2 - back.get_width() // 2, ds.HEIGHT - 50))

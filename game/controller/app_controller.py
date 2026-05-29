"""Связка Model ↔ View: события, экраны, сохранения."""

from __future__ import annotations

import pygame

from game.config import FPS
from game.view import display_size as display_size
from game.model.engine import GameEngine
from game.model.entities import AppScreen, GamePhase
from game.model.settings import GameSettings
from game.persistence.progress import (
    clear_progress,
    has_saved_game,
    load_progress,
    save_progress,
)
from game.persistence.records import load_records, save_record
from game.persistence.settings_store import load_settings, save_settings
from game.view.screens import ScreenRenderer


class AppController:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Повтори сигнал — Rhythm Clicker")
        self.clock = pygame.time.Clock()
        self.settings = load_settings()
        self.renderer = ScreenRenderer()
        self.screen = pygame.Surface((1, 1))
        self._apply_display_mode()
        self.engine = GameEngine(self.settings)
        self.screen_id = AppScreen.MAIN_MENU
        self._settings_return_to: AppScreen = AppScreen.MAIN_MENU
        self._frozen_answer_ms: int | None = None
        self.running = True
        self._autosave_counter = 0

    def run(self) -> None:
        while self.running:
            now_ms = pygame.time.get_ticks()
            self._handle_events(now_ms)
            self._update(now_ms)
            self._render(now_ms)
            self.clock.tick(FPS)
        self._on_shutdown()

    def _snapshot(self, now_ms: int):
        return self.engine.build_snapshot(
            self.screen_id,
            has_saved_progress=has_saved_game(),
            can_continue=has_saved_game(),
            now_ms=now_ms,
        )

    def _handle_events(self, now_ms: int) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
            elif event.type == pygame.KEYDOWN:
                self._on_key(event.key, now_ms)
            elif event.type == pygame.MOUSEMOTION:
                self.renderer.hit_test_hover(self.screen_id, event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_click(event.pos, now_ms)

    def _on_key(self, key: int, now_ms: int) -> None:
        if key == pygame.K_ESCAPE:
            self._on_escape()
        elif key == pygame.K_p and self.screen_id == AppScreen.PLAYING:
            self._pause(now_ms)
        elif key == pygame.K_RETURN:
            self._on_enter(now_ms)

    def _on_escape(self) -> None:
        if self.screen_id == AppScreen.SETTINGS:
            self._close_settings()
        elif self.screen_id in (
            AppScreen.RECORDS,
            AppScreen.LEVELS,
            AppScreen.FIELD_SELECT,
        ):
            self.screen_id = AppScreen.MAIN_MENU
        elif self.screen_id == AppScreen.PAUSED:
            self._go_main_menu(save=True)
        elif self.screen_id == AppScreen.PLAYING:
            self._pause(pygame.time.get_ticks())
        elif self.screen_id == AppScreen.GAME_OVER:
            self.screen_id = AppScreen.MAIN_MENU
        else:
            self._quit()

    def _on_enter(self, now_ms: int) -> None:
        if self.screen_id == AppScreen.PAUSED:
            self._resume(now_ms)
        elif self.screen_id == AppScreen.GAME_OVER:
            self.screen_id = AppScreen.MAIN_MENU

    def _on_click(self, pos: tuple[int, int], now_ms: int) -> None:
        if self.screen_id == AppScreen.MAIN_MENU:
            self._handle_main_menu_click(pos, now_ms)
            return

        if self.screen_id == AppScreen.PAUSED:
            self._handle_pause_menu_click(pos, now_ms)
            return

        if self.screen_id == AppScreen.SETTINGS:
            self._handle_settings_click(pos)
            return

        if self.screen_id == AppScreen.LEVELS:
            self._handle_levels_click(pos, now_ms)
            return

        if self.screen_id == AppScreen.FIELD_SELECT:
            self._handle_field_select_click(pos, now_ms)
            return

        if self.screen_id == AppScreen.PLAYING:
            if self.renderer.pause_btn_hit(pos):
                self._pause(now_ms)
                return
            color = self.renderer.color_hit(pos)
            if color is not None:
                self.engine.press_color(color, now_ms)
                if self.engine.is_game_over():
                    self._on_game_over()

    def _handle_main_menu_click(self, pos: tuple[int, int], now_ms: int) -> None:
        action = self.renderer.menu_hit(pos)
        if action == "infinite":
            self.screen_id = AppScreen.FIELD_SELECT
        elif action == "continue" and has_saved_game():
            self._continue_game(now_ms)
        elif action == "levels":
            self.screen_id = AppScreen.LEVELS
        elif action == "settings":
            self._open_settings(AppScreen.MAIN_MENU)
        elif action == "records":
            self.screen_id = AppScreen.RECORDS
        elif action == "quit":
            self._quit()

    def _handle_field_select_click(self, pos: tuple[int, int], now_ms: int) -> None:
        if self.renderer.field_select_back_hit(pos):
            self.screen_id = AppScreen.MAIN_MENU
            return
        grid_size = self.renderer.field_select_hit(pos)
        if grid_size is not None:
            self._start_new_game(now_ms, grid_size=grid_size)

    def _handle_levels_click(self, pos: tuple[int, int], now_ms: int) -> None:
        if self.renderer.levels_back_hit(pos):
            self.screen_id = AppScreen.MAIN_MENU
            return
        level = self.renderer.level_hit(pos)
        if level is not None:
            self.renderer.show_levels_notice("Пока ничего нет", now_ms)

    def _handle_pause_menu_click(self, pos: tuple[int, int], now_ms: int) -> None:
        action = self.renderer.pause_menu_hit(pos)
        if action == "resume":
            self._resume(now_ms)
        elif action == "main_menu":
            self._go_main_menu(save=True)
        elif action == "settings":
            self._open_settings(AppScreen.PAUSED)

    def _handle_settings_click(self, pos: tuple[int, int]) -> None:
        if self.renderer.resolution_dropdown_open:
            picked = self.renderer.resolution_dropdown_hit(pos)
            if picked is not None:
                w, h = picked
                self.settings.set_resolution(w, h)
                self.renderer.close_resolution_dropdown()
                save_settings(self.settings)
                self._apply_display_mode()
                return
            if not self.renderer.point_in_resolution_dropdown(pos):
                self.renderer.close_resolution_dropdown()

        action = self.renderer.settings_hit(pos)
        if action == "resolution":
            self.renderer.toggle_resolution_dropdown()
            return
        if action == "fullscreen":
            self.settings.set_fullscreen(not self.settings.fullscreen)
            save_settings(self.settings)
            self._apply_display_mode()
            return
        if action == "answer_time":
            self.settings.cycle_answer_time()
        elif action == "lives":
            self.settings.cycle_lives()
        elif action == "hints":
            self.settings.toggle_hints()
        elif action == "back":
            self.renderer.close_resolution_dropdown()
            self._close_settings()
            return
        else:
            return
        save_settings(self.settings)
        self.engine.apply_settings(self.settings)

    def _apply_display_mode(self) -> None:
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            w, h = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height)
            )
            w, h = self.settings.screen_width, self.settings.screen_height
        display_size.set_size(w, h)
        self.renderer.rebuild_layout()

    def _open_settings(self, return_to: AppScreen) -> None:
        self._settings_return_to = return_to
        self.screen_id = AppScreen.SETTINGS

    def _close_settings(self) -> None:
        self.renderer.close_resolution_dropdown()
        self.screen_id = self._settings_return_to

    def _start_new_game(self, now_ms: int, *, grid_size: int = 2) -> None:
        clear_progress()
        self.engine.apply_settings(self.settings)
        self.renderer.set_play_grid_size(grid_size)
        self.engine.reset(now_ms, grid_size=grid_size)
        self.screen_id = AppScreen.PLAYING
        self._frozen_answer_ms = None

    def _continue_game(self, now_ms: int) -> None:
        saved = load_progress()
        if saved is None:
            return
        self.engine.apply_settings(self.settings)
        self.renderer.set_play_grid_size(saved.grid_size)
        self.engine.load_state(saved, now_ms)
        self.screen_id = AppScreen.PLAYING
        self._frozen_answer_ms = None

    def _pause(self, now_ms: int) -> None:
        if self.screen_id != AppScreen.PLAYING:
            return
        self._frozen_answer_ms = self.engine.get_answer_remaining_ms(now_ms)
        save_progress(self.engine.export_state())
        self.screen_id = AppScreen.PAUSED

    def _resume(self, now_ms: int) -> None:
        if self.screen_id != AppScreen.PAUSED:
            return
        if self._frozen_answer_ms:
            self.engine.extend_answer_deadline(now_ms, self._frozen_answer_ms)
        self._frozen_answer_ms = None
        self.screen_id = AppScreen.PLAYING

    def _go_main_menu(self, *, save: bool) -> None:
        if save and self.screen_id in (AppScreen.PLAYING, AppScreen.PAUSED):
            if not self.engine.is_game_over():
                save_progress(self.engine.export_state())
        self._frozen_answer_ms = None
        self.screen_id = AppScreen.MAIN_MENU

    def _on_game_over(self) -> None:
        result = self.engine.finalize_after_quit()
        if result:
            save_record(result[0], result[1])
        clear_progress()
        self._frozen_answer_ms = None
        self.screen_id = AppScreen.GAME_OVER

    def _update(self, now_ms: int) -> None:
        if self.screen_id != AppScreen.PLAYING:
            return
        self.engine.tick(now_ms)
        if self.engine.tick_input_timer(now_ms) and self.engine.is_game_over():
            self._on_game_over()
        self._autosave_counter += 1
        if self._autosave_counter >= FPS * 5:
            self._autosave_counter = 0
            if not self.engine.is_game_over():
                save_progress(self.engine.export_state())

    def _render(self, now_ms: int) -> None:
        snapshot = self._snapshot(now_ms)
        records = load_records()
        self.renderer.draw(self.screen, snapshot, records, now_ms)
        pygame.display.flip()

    def _quit(self) -> None:
        if self.screen_id in (AppScreen.PLAYING, AppScreen.PAUSED):
            if not self.engine.is_game_over():
                save_progress(self.engine.export_state())
        save_settings(self.settings)
        self.running = False

    def _on_shutdown(self) -> None:
        if self.engine.is_game_over():
            result = self.engine.finalize_after_quit()
            if result:
                save_record(result[0], result[1])
        pygame.quit()

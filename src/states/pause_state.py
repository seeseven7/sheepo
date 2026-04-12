"""Pause state — freeze gameplay, option to resume or exit."""

import pygame

import settings as s
from src.states.base_state import BaseState


class PauseState(BaseState):
    """Overlay pause screen."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

    def enter(self) -> None:
        pygame.mouse.set_visible(True)

    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Resume — pop back to playing
                self.game.change_state("resume")
            elif event.key == pygame.K_q:
                self.game.change_state("title")

    def update(self, dt: float) -> None:
        pass  # Everything frozen

    def draw(self, surface: pygame.Surface) -> None:
        # The playing state is still drawn underneath (game handles this)
        # We draw the overlay on top
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        # PAUSED text
        text = self.font.render("PAUSED", True, s.WHITE)
        rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 - 20))
        surface.blit(text, rect)

        # Instructions
        resume_text = self.small_font.render("Press ESC to resume", True, s.UI_TEXT)
        quit_text = self.small_font.render("Press Q to exit to title", True, s.UI_TEXT)
        surface.blit(
            resume_text,
            resume_text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 + 30))
        )
        surface.blit(
            quit_text,
            quit_text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 + 60))
        )
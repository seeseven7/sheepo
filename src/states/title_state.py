"""Title screen state — spinning Sheepo, breakcore energy."""

import math
import os

import pygame

import settings as s
from src.states.base_state import BaseState


class TitleState(BaseState):
    """Title screen: game title, spinning sheep, press space to play."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.spin_angle: float = 0.0
        self.title_font: pygame.font.Font | None = None
        self.prompt_font: pygame.font.Font | None = None
        self.sheep_surface: pygame.Surface | None = None
        self.blink_timer: float = 0.0
        self.fade_alpha: float = 255.0
        self.fade_duration: float = 1.2
        self.fade_surface: pygame.Surface | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.Font(None, 56)
        self.prompt_font = pygame.font.Font(None, 28)
        self.spin_angle = 0.0
        self.blink_timer = 0.0
        self.fade_alpha = 255.0
        self.fade_surface = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        self.fade_surface.fill(s.BLACK)

        # Placeholder spinning sheep — a white circle with a face
        self.sheep_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(self.sheep_surface, s.SHEEPO_BODY, (32, 32), 28)
        pygame.draw.circle(self.sheep_surface, s.SHEEPO_FACE, (38, 26), 5)  # Eye
        pygame.draw.circle(self.sheep_surface, s.SHEEPO_FACE, (38, 38), 5)  # Eye 2
        pygame.draw.ellipse(self.sheep_surface, (200, 150, 150), (40, 28, 14, 10))  # Snout

        self._play_title_music()

    def exit(self) -> None:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.change_state("playing")

    def update(self, dt: float) -> None:
        self.spin_angle += 360 * dt  # One full rotation per second
        self.blink_timer += dt
        if self.fade_alpha > 0:
            fade_rate = 255.0 / self.fade_duration
            self.fade_alpha = max(0.0, self.fade_alpha - fade_rate * dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(s.SKY_BLUE)

        # Spinning sheep
        rotated = pygame.transform.rotate(self.sheep_surface, -self.spin_angle)
        rect = rotated.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2))
        surface.blit(rotated, rect)

        # Title text
        title_surf = self.title_font.render(s.GAME_TITLE, True, s.BLACK)
        title_rect = title_surf.get_rect(center=(s.SCREEN_WIDTH // 2, 120))
        surface.blit(title_surf, title_rect)

        # Blinking prompt
        if math.sin(self.blink_timer * 3) > 0:
            prompt_surf = self.prompt_font.render(
                "Press SPACEBAR to play", True, s.BLACK
            )
            prompt_rect = prompt_surf.get_rect(
                center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT - 100)
            )
            surface.blit(prompt_surf, prompt_rect)

        if self.fade_alpha > 0 and self.fade_surface:
            self.fade_surface.set_alpha(int(self.fade_alpha))
            surface.blit(self.fade_surface, (0, 0))

    def _play_title_music(self) -> None:
        """Play title music loop if configured and available."""
        if not s.MUSIC_TITLE or not pygame.mixer.get_init():
            return

        track_path = os.path.join(s.AUDIO_DIR, s.MUSIC_TITLE)
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(-1)
        except (FileNotFoundError, pygame.error):
            # Missing/invalid audio should not break the title screen.
            return
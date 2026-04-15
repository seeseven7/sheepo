"""Title screen state with crisp background and bobbing title."""

import math
import os

import pygame

import settings as s
from src.states.base_state import BaseState


class TitleState(BaseState):
    """Title screen: animated title over custom background."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.title_font: pygame.font.Font | None = None
        self.prompt_font: pygame.font.Font | None = None
        self.title_layers: list[tuple[pygame.Surface, tuple[int, int]]] = []
        self.title_sprite: pygame.Surface | None = None
        self.background_surface: pygame.Surface | None = None
        self.blink_timer: float = 0.0
        self.title_bob_timer: float = 0.0
        self.fade_alpha: float = 255.0
        self.fade_duration: float = 1.2
        self.fade_surface: pygame.Surface | None = None

    def enter(self) -> None:
        self.title_font = pygame.font.Font(None, 84)
        self.prompt_font = pygame.font.Font(None, 28)
        self.blink_timer = 0.0
        self.title_bob_timer = 0.0
        self.fade_alpha = 255.0
        self.title_layers = []
        self.fade_surface = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        self.fade_surface.fill(s.BLACK)
        self.background_surface = self._load_title_background()
        self.title_sprite = self._load_title_sprite()
        self._build_title_layers()

        self._play_title_music()

    def exit(self) -> None:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.change_state("playing")

    def update(self, dt: float) -> None:
        self.blink_timer += dt
        self.title_bob_timer += dt
        if self.fade_alpha > 0:
            fade_rate = 255.0 / self.fade_duration
            self.fade_alpha = max(0.0, self.fade_alpha - fade_rate * dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.background_surface:
            surface.blit(self.background_surface, (0, 0))
        else:
            surface.fill(s.SKY_BLUE)

        if self.title_sprite:
            tilt_degrees = math.sin(self.title_bob_timer * 2.4) * 6.5
            rotated = pygame.transform.rotate(self.title_sprite, tilt_degrees)
            pixelated_title = self._pixelate_surface(rotated, 0.4)
            title_rect = pixelated_title.get_rect(center=(s.SCREEN_WIDTH // 2, 105))
            surface.blit(pixelated_title, title_rect)
        else:
            title_center = (s.SCREEN_WIDTH // 2, 105)
            for title_layer, layer_offset in self.title_layers:
                title_rect = title_layer.get_rect(
                    center=(
                        title_center[0] + layer_offset[0],
                        title_center[1] + layer_offset[1],
                    )
                )
                surface.blit(title_layer, title_rect)

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

    def _load_title_background(self) -> pygame.Surface | None:
        """Load title background and fit to screen without forced pixelation."""
        image_path = os.path.join(s.SPRITE_DIR, "titlescreen.png")
        try:
            loaded = pygame.image.load(image_path).convert()
        except (FileNotFoundError, pygame.error):
            return None

        image_width, image_height = loaded.get_size()
        screen_size = (s.SCREEN_WIDTH, s.SCREEN_HEIGHT)
        if (image_width, image_height) == screen_size:
            return loaded

        # Cover/fill the screen with nearest-neighbor scaling, then center-crop.
        scale_factor = max(
            s.SCREEN_WIDTH / image_width,
            s.SCREEN_HEIGHT / image_height,
        )
        scaled_size = (
            max(1, int(round(image_width * scale_factor))),
            max(1, int(round(image_height * scale_factor))),
        )
        scaled = pygame.transform.scale(loaded, scaled_size)

        crop_x = max(0, (scaled_size[0] - s.SCREEN_WIDTH) // 2)
        crop_y = max(0, (scaled_size[1] - s.SCREEN_HEIGHT) // 2)
        crop_rect = pygame.Rect(crop_x, crop_y, s.SCREEN_WIDTH, s.SCREEN_HEIGHT)
        return scaled.subsurface(crop_rect).copy()

    def _load_title_sprite(self) -> pygame.Surface | None:
        """Load the custom title sprite if present."""
        image_path = os.path.join(s.SPRITE_DIR, "title.png")
        try:
            loaded = pygame.image.load(image_path).convert_alpha()
        except (FileNotFoundError, pygame.error):
            return None

        max_width = int(s.SCREEN_WIDTH * 0.86)
        max_height = int(s.SCREEN_HEIGHT * 0.32)
        width, height = loaded.get_size()
        if width <= max_width and height <= max_height:
            return loaded

        scale_factor = min(max_width / width, max_height / height)
        resized_size = (
            max(1, int(round(width * scale_factor))),
            max(1, int(round(height * scale_factor))),
        )
        return pygame.transform.scale(loaded, resized_size)

    def _pixelate_surface(
        self, source: pygame.Surface, scale_factor: float
    ) -> pygame.Surface:
        """Downscale and upscale a surface for crunchy retro pixels."""
        width, height = source.get_size()
        low_res_size = (
            max(1, int(round(width * scale_factor))),
            max(1, int(round(height * scale_factor))),
        )
        low_res = pygame.transform.scale(source, low_res_size)
        return pygame.transform.scale(low_res, (width, height))

    def _build_title_layers(self) -> None:
        """Create layered title text for a faux 3D pixel look."""
        title_text = s.GAME_TITLE.upper()
        max_width = int(s.SCREEN_WIDTH * 0.92)
        font_size = 96
        while font_size > 48:
            test_font = pygame.font.Font(None, font_size)
            if test_font.size(title_text)[0] <= max_width:
                break
            font_size -= 4

        self.title_font = pygame.font.Font(None, font_size)
        front_layer = self.title_font.render(title_text, False, (252, 246, 196))
        mid_layer = self.title_font.render(title_text, False, (229, 127, 58))
        shadow_layer = self.title_font.render(title_text, False, (82, 35, 48))
        outline_layer = self.title_font.render(title_text, False, s.BLACK)

        self.title_layers = [
            (outline_layer, (2, 2)),
            (outline_layer, (-2, 2)),
            (outline_layer, (2, -1)),
            (shadow_layer, (6, 6)),
            (mid_layer, (3, 3)),
            (front_layer, (0, 0)),
        ]

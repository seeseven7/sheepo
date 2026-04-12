"""Evil Bee — approaches Sheepo with a flamethrower."""

import math
import random

import pygame

import settings as s


class Bee:
    """A fast-moving bee that sets Sheepo on fire on contact."""

    def __init__(self) -> None:
        # Spawn from a random screen edge
        side = random.choice(["left", "right", "top"])
        if side == "left":
            self.x = -s.BEE_SIZE[0]
            self.y = random.uniform(50, s.SCREEN_HEIGHT * 0.6)
        elif side == "right":
            self.x = s.SCREEN_WIDTH + s.BEE_SIZE[0]
            self.y = random.uniform(50, s.SCREEN_HEIGHT * 0.6)
        else:
            self.x = random.uniform(100, s.SCREEN_WIDTH - 100)
            self.y = -s.BEE_SIZE[1]

        self.rect = pygame.Rect(0, 0, *s.BEE_SIZE)
        self.rect.center = (int(self.x), int(self.y))

        self.alive: bool = True
        self.wobble_offset: float = random.uniform(0, math.pi * 2)
        self.wobble_timer: float = 0.0

        # Placeholder surface
        self.surface = pygame.Surface(s.BEE_SIZE, pygame.SRCALPHA)
        # Body
        pygame.draw.ellipse(self.surface, s.BEE_YELLOW, (2, 4, 20, 16))
        # Stripes
        pygame.draw.line(self.surface, s.BEE_BLACK, (8, 4), (8, 20), 2)
        pygame.draw.line(self.surface, s.BEE_BLACK, (14, 4), (14, 20), 2)
        # Eye
        pygame.draw.circle(self.surface, (255, 0, 0), (19, 8), 3)  # Evil red eye
        # Wings
        pygame.draw.ellipse(self.surface, (200, 220, 255, 150), (4, 0, 10, 8))

    def update(self, dt: float, target_x: float, target_y: float) -> None:
        """Move toward the target (Sheepo) with wobble."""
        if not self.alive:
            return

        self.wobble_timer += dt

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 1:
            # Base direction toward sheepo
            dir_x = dx / dist
            dir_y = dy / dist

            # Add wobble for erratic movement
            wobble = math.sin(self.wobble_timer * 8 + self.wobble_offset) * 0.5
            perp_x = -dir_y * wobble
            perp_y = dir_x * wobble

            move = s.BEE_SPEED * dt
            self.x += (dir_x + perp_x) * move
            self.y += (dir_y + perp_y) * move

        self.rect.center = (int(self.x), int(self.y))

    def check_contact(self, sheepo_rect: pygame.Rect) -> bool:
        """Check if bee has reached Sheepo."""
        return self.alive and self.rect.colliderect(sheepo_rect)

    def swat(self) -> None:
        """Swat the bee — it dies."""
        self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bee."""
        if not self.alive:
            return
        surface.blit(self.surface, self.rect)
"""Pond — water source for filling the bucket."""

import math

import pygame

import settings as s


class Pond:
    """A small pond. Click with empty bucket to fill it."""

    def __init__(self) -> None:
        self.x, self.y = s.POND_POSITION
        self.rect = pygame.Rect(0, 0, *s.POND_SIZE)
        self.rect.center = (int(self.x), int(self.y))
        self.ripple_timer: float = 0.0

        # Placeholder surface
        self.surface = pygame.Surface(s.POND_SIZE, pygame.SRCALPHA)
        pygame.draw.ellipse(self.surface, s.POND_BLUE, (0, 0, *s.POND_SIZE))
        # Edge
        pygame.draw.ellipse(self.surface, (40, 120, 180), (0, 0, *s.POND_SIZE), 2)

    def update(self, dt: float) -> None:
        self.ripple_timer += dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.rect)
        # Animated ripple
        ripple_x = self.rect.centerx + int(math.sin(self.ripple_timer * 2) * 10)
        ripple_y = self.rect.centery + int(math.cos(self.ripple_timer * 1.5) * 4)
        pygame.draw.ellipse(
            surface, (100, 190, 255, 100),
            (ripple_x - 8, ripple_y - 3, 16, 6), 1
        )
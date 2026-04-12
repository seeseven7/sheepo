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
        w, h = s.BEE_SIZE
        body_rect = pygame.Rect(
            int(w * 0.08), int(h * 0.2), int(w * 0.84), int(h * 0.66)
        )
        # Body
        pygame.draw.ellipse(self.surface, s.BEE_YELLOW, body_rect)
        # Stripes
        stripe_width = max(1, int(w * 0.08))
        top = body_rect.top
        bottom = body_rect.bottom
        x1 = body_rect.left + int(body_rect.width * 0.35)
        x2 = body_rect.left + int(body_rect.width * 0.65)
        pygame.draw.line(self.surface, s.BEE_BLACK, (x1, top), (x1, bottom), stripe_width)
        pygame.draw.line(self.surface, s.BEE_BLACK, (x2, top), (x2, bottom), stripe_width)
        # Eye
        eye_radius = max(2, int(min(w, h) * 0.12))
        eye_x = body_rect.right - eye_radius - 1
        eye_y = body_rect.top + eye_radius + 1
        pygame.draw.circle(self.surface, (255, 0, 0), (eye_x, eye_y), eye_radius)  # Evil red eye
        # Wings
        wing_rect = pygame.Rect(
            int(w * 0.16), 0, int(w * 0.42), int(h * 0.33)
        )
        pygame.draw.ellipse(self.surface, (200, 220, 255, 150), wing_rect)

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
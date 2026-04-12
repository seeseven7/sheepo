"""German Nihilist — sneaks bush to bush, gives Sheepo existential dread."""

import random

import pygame

import settings as s


class Bush:
    """A bush that may contain a nihilist. Can be splashed with water."""

    def __init__(self, pos: tuple[float, float]) -> None:
        self.x, self.y = pos
        self.rect = pygame.Rect(0, 0, *s.BUSH_SIZE)
        self.rect.center = (int(self.x), int(self.y))
        self.has_nihilist: bool = False
        self.wet: bool = False
        self.wet_timer: float = 0.0

        # Placeholder surface
        self.surface = pygame.Surface(s.BUSH_SIZE, pygame.SRCALPHA)
        w, h = s.BUSH_SIZE
        pygame.draw.ellipse(
            self.surface, s.DARK_GREEN, (0, int(h * 0.15), w, int(h * 0.8))
        )
        pygame.draw.ellipse(
            self.surface, s.GREEN, (int(w * 0.12), 0, int(w * 0.76), int(h * 0.72))
        )

        # Wet overlay
        self.wet_surface = pygame.Surface(s.BUSH_SIZE, pygame.SRCALPHA)
        pygame.draw.ellipse(
            self.wet_surface, (100, 150, 255, 80), (0, int(h * 0.15), w, int(h * 0.8))
        )

    def splash(self) -> bool:
        """Splash water on this bush. Returns True if nihilist was flushed."""
        flushed = self.has_nihilist
        self.has_nihilist = False
        self.wet = True
        self.wet_timer = 2.0
        return flushed

    def update(self, dt: float) -> None:
        if self.wet:
            self.wet_timer -= dt
            if self.wet_timer <= 0:
                self.wet = False

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.rect)
        if self.wet:
            surface.blit(self.wet_surface, self.rect)
        # Eyes peeking if nihilist hiding
        if self.has_nihilist:
            eye_y = self.rect.centery - 4
            pygame.draw.circle(surface, s.WHITE, (self.rect.centerx - 6, eye_y), 4)
            pygame.draw.circle(surface, s.WHITE, (self.rect.centerx + 6, eye_y), 4)
            pygame.draw.circle(surface, s.BLACK, (self.rect.centerx - 5, eye_y), 2)
            pygame.draw.circle(surface, s.BLACK, (self.rect.centerx + 7, eye_y), 2)


class Nihilist:
    """A German nihilist sneaking from bush to bush toward Sheepo."""

    STATE_HIDING = "hiding"
    STATE_MOVING = "moving"
    STATE_REACHED = "reached"  # Got to Sheepo, applied DGAF
    STATE_DEAD = "dead"        # Flushed by water

    def __init__(self, bushes: list[Bush], from_left: bool = True) -> None:
        self.bushes = bushes
        self.state: str = self.STATE_HIDING
        self.alive: bool = True

        # Pick starting side
        if from_left:
            self.bush_sequence = [
                b for b in bushes
                if b.x < s.SCREEN_WIDTH // 2
            ]
            self.bush_sequence.sort(key=lambda b: b.x)  # Outer to inner
        else:
            self.bush_sequence = [
                b for b in bushes
                if b.x >= s.SCREEN_WIDTH // 2
            ]
            self.bush_sequence.sort(key=lambda b: b.x, reverse=True)

        self.current_bush_idx: int = 0
        self.hide_timer: float = random.uniform(
            s.NIHILIST_BUSH_WAIT_MIN, s.NIHILIST_BUSH_WAIT_MAX
        )

        # Position at first bush
        if self.bush_sequence:
            first_bush = self.bush_sequence[0]
            self.x = first_bush.x
            self.y = first_bush.y
            first_bush.has_nihilist = True
        else:
            self.state = self.STATE_DEAD
            self.alive = False
            self.x = 0
            self.y = 0
            return

        self.rect = pygame.Rect(0, 0, *s.NIHILIST_SIZE)
        self.rect.center = (int(self.x), int(self.y))

    def update(self, dt: float, sheepo_x: float, sheepo_y: float) -> bool:
        """Update nihilist. Returns True if just reached Sheepo (apply DGAF)."""
        if not self.alive:
            return False

        # Check if current bush was splashed
        if self.state == self.STATE_HIDING:
            current_bush = self.bush_sequence[self.current_bush_idx]
            if not current_bush.has_nihilist:
                # Bush was splashed — nihilist is dead
                self.state = self.STATE_DEAD
                self.alive = False
                return False

            self.hide_timer -= dt
            if self.hide_timer <= 0:
                # Move to next bush or to Sheepo
                current_bush.has_nihilist = False
                self.current_bush_idx += 1

                if self.current_bush_idx < len(self.bush_sequence):
                    self.state = self.STATE_MOVING
                else:
                    # No more bushes — rush to Sheepo
                    self.state = self.STATE_MOVING

        elif self.state == self.STATE_MOVING:
            # Determine target
            if self.current_bush_idx < len(self.bush_sequence):
                target = self.bush_sequence[self.current_bush_idx]
                tx, ty = target.x, target.y
            else:
                tx, ty = sheepo_x, sheepo_y

            dx = tx - self.x
            dy = ty - self.y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist > 3:
                move = s.NIHILIST_SNEAK_SPEED * dt
                self.x += (dx / dist) * move
                self.y += (dy / dist) * move
            else:
                # Arrived
                if self.current_bush_idx < len(self.bush_sequence):
                    # Arrived at next bush
                    next_bush = self.bush_sequence[self.current_bush_idx]
                    next_bush.has_nihilist = True
                    self.state = self.STATE_HIDING
                    self.hide_timer = random.uniform(
                        s.NIHILIST_BUSH_WAIT_MIN, s.NIHILIST_BUSH_WAIT_MAX
                    )
                else:
                    # Reached Sheepo!
                    self.state = self.STATE_REACHED
                    self.alive = False
                    return True  # Signal to apply DGAF

            self.rect.center = (int(self.x), int(self.y))

        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw nihilist only when moving (visible between bushes)."""
        if self.state == self.STATE_MOVING and self.alive:
            # Simple placeholder: dark figure
            pygame.draw.rect(surface, s.NIHILIST_COLOR, self.rect)
            # Beret
            beret_w = int(self.rect.width * 0.75)
            beret_h = max(10, int(self.rect.height * 0.22))
            pygame.draw.ellipse(
                surface, s.BLACK,
                (self.rect.x + 4, self.rect.y - 6, beret_w, beret_h)
            )
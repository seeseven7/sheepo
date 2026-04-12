"""The Sun — slowly approaches, sets Sheepo on fire, then flees."""

import pygame

import settings as s


class Sun:
    """Sunglasses-wearing sun. Approaches, triggers fire, escapes."""

    STATE_WAITING = "waiting"      # Off-screen, on cooldown
    STATE_APPROACHING = "approaching"
    STATE_ESCAPING = "escaping"

    def __init__(self) -> None:
        self.state: str = self.STATE_WAITING
        self.cooldown: float = s.SUN_INITIAL_COOLDOWN
        self.return_time: float = s.SUN_FIRST_RETURN
        self.times_appeared: int = 0

        # Start off-screen top-left
        self.x: float = -s.SUN_SIZE[0]
        self.y: float = -s.SUN_SIZE[1]

        self.rect = pygame.Rect(0, 0, *s.SUN_SIZE)
        self.rect.center = (int(self.x), int(self.y))

        self.has_fired: bool = False  # Fired this approach cycle?

        # Placeholder surface
        self.surface = pygame.Surface(s.SUN_SIZE, pygame.SRCALPHA)
        cx, cy = s.SUN_SIZE[0] // 2, s.SUN_SIZE[1] // 2
        # Sun body
        pygame.draw.circle(self.surface, s.SUN_YELLOW, (cx, cy), 24)
        # Rays
        for i in range(8):
            import math
            angle = i * (math.pi / 4)
            x1 = cx + int(math.cos(angle) * 24)
            y1 = cy + int(math.sin(angle) * 24)
            x2 = cx + int(math.cos(angle) * 30)
            y2 = cy + int(math.sin(angle) * 30)
            pygame.draw.line(self.surface, s.SUN_YELLOW, (x1, y1), (x2, y2), 3)
        # Sunglasses
        pygame.draw.rect(self.surface, s.BLACK, (cx - 14, cy - 6, 12, 8), border_radius=2)
        pygame.draw.rect(self.surface, s.BLACK, (cx + 2, cy - 6, 12, 8), border_radius=2)
        pygame.draw.line(self.surface, s.BLACK, (cx - 2, cy - 2), (cx + 2, cy - 2), 2)
        # Smirk
        pygame.draw.arc(self.surface, s.BLACK, (cx - 8, cy + 4, 16, 10), 3.14, 6.28, 2)

    def update(self, dt: float) -> bool:
        """Update sun state. Returns True if sun just triggered fire."""
        triggered_fire = False

        if self.state == self.STATE_WAITING:
            self.cooldown -= dt
            if self.cooldown <= 0:
                self._start_approach()

        elif self.state == self.STATE_APPROACHING:
            # Move toward fire threshold position (top-right area)
            target_x = s.SUN_FIRE_THRESHOLD_X
            target_y = s.SUN_FIRE_THRESHOLD_Y + 40
            dx = target_x - self.x
            dy = target_y - self.y

            dist = (dx * dx + dy * dy) ** 0.5
            if dist > 2:
                move = s.SUN_APPROACH_SPEED * dt
                self.x += (dx / dist) * move
                self.y += (dy / dist) * move
            else:
                # Reached position — trigger fire
                if not self.has_fired:
                    triggered_fire = True
                    self.has_fired = True
                self.state = self.STATE_ESCAPING

        elif self.state == self.STATE_ESCAPING:
            # Hastily exit off-screen to the right
            self.x += s.SUN_ESCAPE_SPEED * dt
            self.y -= s.SUN_ESCAPE_SPEED * dt * 0.3

            if self.x > s.SCREEN_WIDTH + 100 or self.y < -100:
                self._finish_escape()

        self.rect.center = (int(self.x), int(self.y))
        return triggered_fire

    def _start_approach(self) -> None:
        """Begin approaching from off-screen."""
        self.state = self.STATE_APPROACHING
        self.has_fired = False
        # Start from top-left off-screen
        self.x = -s.SUN_SIZE[0]
        self.y = -s.SUN_SIZE[1]

    def _finish_escape(self) -> None:
        """After escaping, go back to waiting with shorter cooldown."""
        self.state = self.STATE_WAITING
        self.times_appeared += 1
        # Halve the return time each cycle
        self.cooldown = max(
            s.SUN_MIN_RETURN,
            self.return_time * (s.SUN_RETURN_DECAY ** self.times_appeared),
        )

    @property
    def visible(self) -> bool:
        return self.state != self.STATE_WAITING

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the sun if visible."""
        if self.visible:
            surface.blit(self.surface, self.rect)
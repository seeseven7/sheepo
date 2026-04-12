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
        w, h = s.SUN_SIZE
        cx, cy = w // 2, h // 2
        sun_radius = int(min(w, h) * 0.38)
        ray_inner = sun_radius
        ray_outer = int(sun_radius * 1.25)
        # Sun body
        pygame.draw.circle(self.surface, s.SUN_YELLOW, (cx, cy), sun_radius)
        # Rays
        for i in range(8):
            import math
            angle = i * (math.pi / 4)
            x1 = cx + int(math.cos(angle) * ray_inner)
            y1 = cy + int(math.sin(angle) * ray_inner)
            x2 = cx + int(math.cos(angle) * ray_outer)
            y2 = cy + int(math.sin(angle) * ray_outer)
            pygame.draw.line(self.surface, s.SUN_YELLOW, (x1, y1), (x2, y2), max(2, w // 24))
        # Sunglasses
        lens_w = int(w * 0.2)
        lens_h = int(h * 0.12)
        lens_y = cy - lens_h // 2
        left_lens_x = cx - lens_w - 2
        right_lens_x = cx + 2
        pygame.draw.rect(
            self.surface, s.BLACK, (left_lens_x, lens_y, lens_w, lens_h), border_radius=2
        )
        pygame.draw.rect(
            self.surface, s.BLACK, (right_lens_x, lens_y, lens_w, lens_h), border_radius=2
        )
        pygame.draw.line(
            self.surface,
            s.BLACK,
            (left_lens_x + lens_w, lens_y + lens_h // 2),
            (right_lens_x, lens_y + lens_h // 2),
            2,
        )
        # Smirk
        smirk_rect = pygame.Rect(
            cx - int(w * 0.12), cy + int(h * 0.06), int(w * 0.24), int(h * 0.16)
        )
        pygame.draw.arc(self.surface, s.BLACK, smirk_rect, 3.14, 6.28, 2)

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
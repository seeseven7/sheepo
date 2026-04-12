"""Sheepo — the sheep you must protect at all costs"""

import math
import os
import random

import pygame

import settings as s


class Sheepo:
    """The main character. Wanders, grows wool, catches fire, gets nihilistic."""

    def __init__(self) -> None:
        # Position & movement
        bounds = s.SHEEPO_CENTER_BOUNDS
        self.x: float = bounds[0] + bounds[2] / 2
        self.y: float = bounds[1] + bounds[3] / 2
        self.rect = pygame.Rect(0, 0, *s.SHEEPO_SIZE)
        self.rect.center = (int(self.x), int(self.y))

        self.target_x: float = self.x
        self.target_y: float = self.y
        self.moving: bool = False
        self.facing_right: bool = False
        self.pause_timer: float = random.uniform(
            s.SHEEPO_WANDER_PAUSE_MIN, s.SHEEPO_WANDER_PAUSE_MAX
        )

        # Wool
        self.wool_stage: int = s.WOOL_STAGE_NORMAL
        self.wool_timer: float = 0.0

        # Fire
        self.on_fire: bool = False
        self.fire_timer: float = 0.0
        self.fire_flicker: float = 0.0

        # DGAF debuff
        self.dgaf_stacks: int = 0
        self.showing_bubble: bool = False
        self.bubble_timer: float = 0.0
        self.bubble_text: str = ""

        # Placeholder surfaces and optional sprite overrides
        self._build_placeholder()
        self._load_sprites()

    def _build_placeholder(self) -> None:
        """Create a simple colored placeholder sprite."""
        self.base_surfaces: dict[int, pygame.Surface] = {}
        for stage in range(3):
            surf = pygame.Surface(s.SHEEPO_SIZE, pygame.SRCALPHA)
            if stage == 0:
                color = s.SHEEPO_BODY
                size_bonus = 0
            elif stage == 1:
                color = s.WOOL_POOFY
                size_bonus = 4
            else:
                color = (255, 200, 200)
                size_bonus = 8

            w, h = s.SHEEPO_SIZE
            cx, cy = w // 2, h // 2
            # Wool poof
            r = min(w, h) // 2 - 2 + size_bonus
            pygame.draw.circle(surf, color, (cx, cy), r)
            # Face
            pygame.draw.circle(surf, s.SHEEPO_FACE, (cx + 8, cy - 6), 4)
            pygame.draw.circle(surf, s.SHEEPO_FACE, (cx + 8, cy + 4), 4)
            pygame.draw.ellipse(surf, (200, 150, 150), (cx + 10, cy - 3, 10, 8))
            # Legs
            pygame.draw.rect(surf, s.SHEEPO_FACE, (cx - 10, h - 8, 5, 8))
            pygame.draw.rect(surf, s.SHEEPO_FACE, (cx + 5, h - 8, 5, 8))
            self.base_surfaces[stage] = surf

        # DGAF overlay — bored eyes
        self.dgaf_overlay = pygame.Surface(s.SHEEPO_SIZE, pygame.SRCALPHA)
        cx, cy = s.SHEEPO_SIZE[0] // 2, s.SHEEPO_SIZE[1] // 2
        # Flat line eyes (bored)
        pygame.draw.line(self.dgaf_overlay, (200, 50, 50), (cx + 4, cy - 6), (cx + 12, cy - 6), 3)
        pygame.draw.line(self.dgaf_overlay, (200, 50, 50), (cx + 4, cy + 4), (cx + 12, cy + 4), 3)
        self.dgaf_surface: pygame.Surface | None = None

    def _load_sprite(self, filename: str) -> pygame.Surface | None:
        """Load and scale one sprite file, or return None if unavailable."""
        sprite_path = os.path.join(s.SPRITE_DIR, filename)
        try:
            loaded = pygame.image.load(sprite_path).convert_alpha()
        except (FileNotFoundError, pygame.error):
            return None
        return pygame.transform.scale(loaded, s.SHEEPO_SIZE)

    def _load_sprites(self) -> None:
        """Load Sheepo sprites and keep placeholders for missing files."""
        stage_files = {
            s.WOOL_STAGE_NORMAL: "sheepo_normal.png",
            s.WOOL_STAGE_WOOLY: "sheepo_wooly.png",
            s.WOOL_STAGE_TOO_WOOLY: "sheepo_very_wooly.png",
        }
        for stage, filename in stage_files.items():
            sprite = self._load_sprite(filename)
            if sprite is not None:
                self.base_surfaces[stage] = sprite

        self.dgaf_surface = self._load_sprite("sheepo_dgaf.png")

    def set_on_fire(self) -> None:
        """Ignite Sheepo. Starts the fire countdown."""
        if not self.on_fire:
            self.on_fire = True
            self.fire_timer = s.FIRE_TIMER

    def try_extinguish(self) -> bool:
        """Attempt to put out the fire. Returns True if successful.
        May be refused if DGAF stacks are active."""
        if self._dgaf_refuses():
            return False
        self.on_fire = False
        self.fire_timer = 0.0
        return True

    def try_clip(self) -> bool:
        """Attempt to clip wool. Returns True if successful.
        May be refused if DGAF stacks are active."""
        if self._dgaf_refuses():
            return False
        self.wool_stage = s.WOOL_STAGE_NORMAL
        self.wool_timer = 0.0
        return True

    def add_dgaf_stack(self) -> None:
        """Add one DGAF stack from a nihilist."""
        self.dgaf_stacks += 1

    def get_dgaf_refuse_chance(self) -> float:
        """Calculate refusal probability: 1 - (0.5 ^ stacks)."""
        if self.dgaf_stacks <= 0:
            return 0.0
        return 1.0 - (s.DGAF_BASE_REFUSE_CHANCE ** self.dgaf_stacks)

    def _dgaf_refuses(self) -> bool:
        """Roll for DGAF refusal. If refused, show bubble."""
        chance = self.get_dgaf_refuse_chance()
        if chance > 0 and random.random() < chance:
            self.showing_bubble = True
            self.bubble_timer = s.DGAF_BUBBLE_DURATION
            self.bubble_text = s.DGAF_TEXT
            return True
        return False

    def _pick_new_target(self) -> None:
        """Choose a new random wander target within bounds."""
        bounds = s.SHEEPO_CENTER_BOUNDS
        dist = random.uniform(s.SHEEPO_WANDER_DIST_MIN, s.SHEEPO_WANDER_DIST_MAX)
        angle = random.uniform(0, 2 * math.pi)
        new_x = self.x + math.cos(angle) * dist
        new_y = self.y + math.sin(angle) * dist

        # Clamp to bounds
        new_x = max(bounds[0], min(bounds[0] + bounds[2], new_x))
        new_y = max(bounds[1], min(bounds[1] + bounds[3], new_y))

        self.target_x = new_x
        self.target_y = new_y
        self.moving = True

    def update(self, dt: float) -> None:
        """Update Sheepo each frame."""
        # ── Movement ──
        if self.moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            if abs(dx) > 0.01:
                self.facing_right = dx > 0
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 2:
                self.moving = False
                self.pause_timer = random.uniform(
                    s.SHEEPO_WANDER_PAUSE_MIN, s.SHEEPO_WANDER_PAUSE_MAX
                )
            else:
                move = min(s.SHEEPO_SPEED * dt, dist)
                self.x += (dx / dist) * move
                self.y += (dy / dist) * move
        else:
            self.pause_timer -= dt
            if self.pause_timer <= 0:
                self._pick_new_target()

        self.rect.center = (int(self.x), int(self.y))

        # ── Wool growth ──
        if self.wool_stage < s.WOOL_STAGE_TOO_WOOLY:
            self.wool_timer += dt
            if self.wool_stage == s.WOOL_STAGE_NORMAL:
                if self.wool_timer >= s.WOOL_NORMAL_DURATION:
                    self.wool_stage = s.WOOL_STAGE_WOOLY
                    self.wool_timer = 0.0
            elif self.wool_stage == s.WOOL_STAGE_WOOLY:
                if self.wool_timer >= s.WOOL_WOOLY_DURATION:
                    self.wool_stage = s.WOOL_STAGE_TOO_WOOLY
                    # Game over will be detected by playing_state

        # ── Fire countdown ──
        if self.on_fire:
            self.fire_timer -= dt
            self.fire_flicker += dt * 10
            # Game over detected by playing_state when fire_timer <= 0

        # ── Bubble timer ──
        if self.showing_bubble:
            self.bubble_timer -= dt
            if self.bubble_timer <= 0:
                self.showing_bubble = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw Sheepo with current state."""
        # Base sprite for current wool stage
        stage = min(self.wool_stage, 2)
        if self.dgaf_stacks > 0 and self.dgaf_surface is not None:
            sprite = self.dgaf_surface.copy()
        else:
            sprite = self.base_surfaces[stage].copy()
            # Fallback DGAF marker when dedicated sprite is missing
            if self.dgaf_stacks > 0:
                sprite.blit(self.dgaf_overlay, (0, 0))
        if self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)

        surface.blit(sprite, self.rect)

        # Fire overlay
        if self.on_fire:
            self._draw_fire_overlay(surface)

        # Speech bubble
        if self.showing_bubble:
            self._draw_bubble(surface)

    def _draw_fire_overlay(self, surface: pygame.Surface) -> None:
        """Draw flickering fire effect over Sheepo."""
        fire_surf = pygame.Surface(
            (self.rect.width + 16, self.rect.height + 16), pygame.SRCALPHA
        )
        cx, cy = fire_surf.get_width() // 2, fire_surf.get_height() // 2
        # Flickering circles
        for i in range(5):
            offset_x = math.sin(self.fire_flicker + i * 1.3) * 8
            offset_y = math.cos(self.fire_flicker + i * 0.9) * 6 - i * 3
            r = random.randint(6, 14)
            color = s.FIRE_ORANGE if i % 2 == 0 else s.FIRE_RED
            alpha_color = (*color, 160)
            pygame.draw.circle(
                fire_surf,
                alpha_color,
                (int(cx + offset_x), int(cy + offset_y)),
                r,
            )
        pos = (self.rect.x - 8, self.rect.y - 8)
        surface.blit(fire_surf, pos)

    def _draw_bubble(self, surface: pygame.Surface) -> None:
        """Draw speech bubble above Sheepo."""
        font = pygame.font.Font(None, 20)
        text_surf = font.render(self.bubble_text, True, s.BLACK)
        padding = 8
        bw = text_surf.get_width() + padding * 2
        bh = text_surf.get_height() + padding * 2

        bubble_x = self.rect.centerx - bw // 2
        bubble_y = self.rect.top - bh - 10

        # Background
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bw, bh)
        pygame.draw.rect(surface, s.WHITE, bubble_rect, border_radius=6)
        pygame.draw.rect(surface, s.BLACK, bubble_rect, 2, border_radius=6)
        # Text
        surface.blit(text_surf, (bubble_x + padding, bubble_y + padding))
        # Little triangle pointer
        points = [
            (self.rect.centerx - 5, bubble_y + bh),
            (self.rect.centerx + 5, bubble_y + bh),
            (self.rect.centerx, bubble_y + bh + 6),
        ]
        pygame.draw.polygon(surface, s.WHITE, points)
        pygame.draw.lines(surface, s.BLACK, False, [points[0], points[2], points[1]], 2)

    def get_death_reason(self) -> str | None:
        """Returns a death reason string if Sheepo is dead, else None."""
        if self.wool_stage >= s.WOOL_STAGE_TOO_WOOLY:
            return "Sheepo got too poofy and died"
        if self.on_fire and self.fire_timer <= 0:
            return "Sheepo burned"
        return None
"""Tool Manager — handles equipping, bucket states, wet clippers."""

import pygame

import settings as s


class ToolManager:
    """Manages tool equipping, state transitions, and cursor changes."""

    def __init__(self) -> None:
        self.current_tool: str = s.TOOL_NONE
        self.bucket_full: bool = False

        # Wet clippers state
        self.clippers_wet: bool = False
        self.wet_timer: float = 0.0
        self.slipping: bool = False
        self.slip_timer: float = 0.0
        self.slip_cooldown: float = 0.0

        # Build cursor surfaces
        self._build_cursors()

    def _build_cursors(self) -> None:
        """Create placeholder cursor images for each tool."""
        size = (32, 32)

        # Hand cursor (default)
        self.cursor_hand = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.polygon(
            self.cursor_hand, (220, 190, 160),
            [(4, 0), (20, 12), (16, 28), (0, 20)]
        )
        pygame.draw.polygon(
            self.cursor_hand, s.BLACK,
            [(4, 0), (20, 12), (16, 28), (0, 20)], 2
        )

        # Clippers
        self.cursor_clippers = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.polygon(
            self.cursor_clippers, s.CLIPPER_SILVER,
            [(8, 0), (24, 0), (28, 20), (4, 20)]
        )
        pygame.draw.line(self.cursor_clippers, s.BLACK, (16, 20), (16, 32), 3)
        pygame.draw.polygon(
            self.cursor_clippers, s.BLACK,
            [(8, 0), (24, 0), (28, 20), (4, 20)], 2
        )

        # Bucket empty
        self.cursor_bucket_empty = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.polygon(
            self.cursor_bucket_empty, (160, 140, 120),
            [(6, 8), (26, 8), (28, 28), (4, 28)]
        )
        pygame.draw.arc(
            self.cursor_bucket_empty, s.BLACK,
            (8, 0, 16, 16), 0, 3.14, 2
        )
        pygame.draw.polygon(
            self.cursor_bucket_empty, s.BLACK,
            [(6, 8), (26, 8), (28, 28), (4, 28)], 2
        )

        # Bucket full
        self.cursor_bucket_full = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.polygon(
            self.cursor_bucket_full, (160, 140, 120),
            [(6, 8), (26, 8), (28, 28), (4, 28)]
        )
        pygame.draw.rect(
            self.cursor_bucket_full, s.BUCKET_BLUE,
            (7, 14, 18, 13)
        )
        pygame.draw.arc(
            self.cursor_bucket_full, s.BLACK,
            (8, 0, 16, 16), 0, 3.14, 2
        )
        pygame.draw.polygon(
            self.cursor_bucket_full, s.BLACK,
            [(6, 8), (26, 8), (28, 28), (4, 28)], 2
        )

    def equip(self, tool: str) -> None:
        """Equip a tool. Handles wet clippers interaction."""
        if tool == s.TOOL_CLIPPERS and self.current_tool in (
            s.TOOL_BUCKET_FULL,
        ):
            # Switching from full bucket to clippers — wet clippers!
            self.clippers_wet = True
            self.wet_timer = s.WET_CLIPPERS_ACTIVE_DURATION
            self.bucket_full = False  # Water spills everywhere
            self.slip_cooldown = s.WET_CLIPPERS_SLIP_INTERVAL

        if tool == s.TOOL_BUCKET_EMPTY or tool == s.TOOL_BUCKET_FULL:
            # Equip bucket, keep its state
            self.current_tool = s.TOOL_BUCKET_FULL if self.bucket_full else s.TOOL_BUCKET_EMPTY
        else:
            self.current_tool = tool

        self._update_cursor()

    def unequip(self) -> None:
        """Return to empty hand."""
        self.current_tool = s.TOOL_NONE
        self._update_cursor()

    def fill_bucket(self) -> None:
        """Fill the bucket from the pond."""
        self.bucket_full = True
        self.current_tool = s.TOOL_BUCKET_FULL
        self._update_cursor()

    def use_bucket(self) -> bool:
        """Use the full bucket. Returns True if had water."""
        if self.bucket_full:
            self.bucket_full = False
            self.current_tool = s.TOOL_BUCKET_EMPTY
            self._update_cursor()
            return True
        return False

    def update(self, dt: float) -> None:
        """Update wet clippers timer and slipping."""
        if self.clippers_wet:
            self.wet_timer -= dt
            if self.wet_timer <= 0:
                self.clippers_wet = False
                self.slipping = False
                return

            if self.slipping:
                self.slip_timer -= dt
                if self.slip_timer <= 0:
                    self.slipping = False
                    self.slip_cooldown = s.WET_CLIPPERS_SLIP_INTERVAL
            else:
                self.slip_cooldown -= dt
                if self.slip_cooldown <= 0 and self.current_tool == s.TOOL_CLIPPERS:
                    self.slipping = True
                    self.slip_timer = s.WET_CLIPPERS_SLIP_DURATION

    def can_use_tool(self) -> bool:
        """Check if current tool is usable (not slipping)."""
        if self.current_tool == s.TOOL_CLIPPERS and self.slipping:
            return False
        return True

    def _update_cursor(self) -> None:
        """Update the mouse cursor to match current tool."""
        # In a real build, we'd set the cursor image
        # For now, we draw the tool at cursor position in the game loop
        pass

    def get_cursor_surface(self) -> pygame.Surface:
        """Get the surface to draw at cursor position."""
        if self.current_tool == s.TOOL_CLIPPERS:
            if self.slipping:
                # Return None or offset version — handled in draw
                return self.cursor_clippers
            return self.cursor_clippers
        elif self.current_tool == s.TOOL_BUCKET_FULL:
            return self.cursor_bucket_full
        elif self.current_tool == s.TOOL_BUCKET_EMPTY:
            return self.cursor_bucket_empty
        return self.cursor_hand

    @property
    def is_hand(self) -> bool:
        return self.current_tool == s.TOOL_NONE

    @property
    def has_full_bucket(self) -> bool:
        return self.current_tool == s.TOOL_BUCKET_FULL

    @property
    def has_clippers(self) -> bool:
        return self.current_tool == s.TOOL_CLIPPERS
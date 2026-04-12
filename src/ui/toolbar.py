"""Toolbar — bottom-center tool selection bar."""

import pygame

import settings as s


class Toolbar:
    """Displays equippable tools at the bottom of the screen."""

    TOOLS = [
        (s.TOOL_NONE, "Hand"),
        (s.TOOL_CLIPPERS, "Clippers"),
        (s.TOOL_BUCKET_EMPTY, "Bucket"),
    ]

    def __init__(self) -> None:
        self.slot_size = 50
        self.padding = 8
        self.total_width = len(self.TOOLS) * (self.slot_size + self.padding) - self.padding
        self.x = (s.SCREEN_WIDTH - self.total_width) // 2
        self.y = s.SCREEN_HEIGHT - 65

        self.rects: list[pygame.Rect] = []
        for i in range(len(self.TOOLS)):
            r = pygame.Rect(
                self.x + i * (self.slot_size + self.padding),
                self.y,
                self.slot_size,
                self.slot_size,
            )
            self.rects.append(r)

        self.font = pygame.font.Font(None, 16)

        # Build slot icons
        self._build_icons()

    def _build_icons(self) -> None:
        """Create simple icons for each tool slot."""
        self.icons: list[pygame.Surface] = []

        # Hand
        hand = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(hand, (220, 190, 160), [(10, 4), (30, 16), (26, 34), (6, 28)])
        pygame.draw.polygon(hand, s.BLACK, [(10, 4), (30, 16), (26, 34), (6, 28)], 2)
        self.icons.append(hand)

        # Clippers
        clip = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(clip, s.CLIPPER_SILVER, [(12, 4), (28, 4), (32, 26), (8, 26)])
        pygame.draw.line(clip, s.BLACK, (20, 26), (20, 38), 3)
        pygame.draw.polygon(clip, s.BLACK, [(12, 4), (28, 4), (32, 26), (8, 26)], 2)
        self.icons.append(clip)

        # Bucket
        bucket = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(bucket, (160, 140, 120), [(10, 12), (30, 12), (33, 36), (7, 36)])
        pygame.draw.arc(bucket, s.BLACK, (12, 2, 16, 16), 0, 3.14, 2)
        pygame.draw.polygon(bucket, s.BLACK, [(10, 12), (30, 12), (33, 36), (7, 36)], 2)
        self.icons.append(bucket)

    def handle_click(self, pos: tuple[int, int]) -> str | None:
        """Check if a tool slot was clicked. Returns tool ID or None."""
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(pos):
                return self.TOOLS[i][0]
        return None

    def draw(self, surface: pygame.Surface, current_tool: str, bucket_full: bool) -> None:
        """Draw the toolbar with highlight on active tool."""
        # Background bar
        bg_rect = pygame.Rect(
            self.x - 10, self.y - 5,
            self.total_width + 20, self.slot_size + 10
        )
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((*s.TOOLBAR_BG, 200))
        surface.blit(bg_surf, bg_rect)
        pygame.draw.rect(surface, s.TOOLBAR_BORDER, bg_rect, 2, border_radius=6)

        for i, (tool_id, label) in enumerate(self.TOOLS):
            rect = self.rects[i]

            # Highlight active tool
            is_active = (
                current_tool == tool_id
                or (tool_id == s.TOOL_BUCKET_EMPTY and current_tool in (s.TOOL_BUCKET_EMPTY, s.TOOL_BUCKET_FULL))
            )

            if is_active:
                pygame.draw.rect(surface, (255, 220, 100), rect, border_radius=4)
            else:
                slot_bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                slot_bg.fill((80, 75, 70, 180))
                surface.blit(slot_bg, rect)

            pygame.draw.rect(surface, s.TOOLBAR_BORDER, rect, 2, border_radius=4)

            # Icon
            icon = self.icons[i]

            # If bucket slot and bucket is full, draw water overlay
            if tool_id == s.TOOL_BUCKET_EMPTY and bucket_full:
                icon = icon.copy()
                pygame.draw.rect(icon, s.BUCKET_BLUE, (11, 20, 18, 15))

            icon_rect = icon.get_rect(center=rect.center)
            surface.blit(icon, icon_rect)

            # Label
            label_surf = self.font.render(label, True, s.UI_TEXT)
            label_rect = label_surf.get_rect(midtop=(rect.centerx, rect.bottom + 2))
            surface.blit(label_surf, label_rect)
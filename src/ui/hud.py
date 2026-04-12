"""UI components: timer display, debuff bar, description box."""

import pygame

import settings as s


class TimerDisplay:
    """Top-center survival timer showing MM:SS.mmm."""

    def __init__(self) -> None:
        self.font = pygame.font.Font(None, s.TIMER_FONT_SIZE)

    def draw(self, surface: pygame.Surface, time_text: str) -> None:
        text_surf = self.font.render(time_text, True, s.BLACK)
        # Background pill
        padding = 10
        bg_rect = pygame.Rect(
            0, 0,
            text_surf.get_width() + padding * 2,
            text_surf.get_height() + padding
        )
        bg_rect.midtop = s.TIMER_POSITION
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((255, 255, 255, 180))
        surface.blit(bg_surf, bg_rect)
        pygame.draw.rect(surface, s.BLACK, bg_rect, 2, border_radius=8)
        text_rect = text_surf.get_rect(center=bg_rect.center)
        surface.blit(text_surf, text_rect)


class DebuffBar:
    """Shows active debuffs under Sheepo."""

    def __init__(self) -> None:
        self.font = pygame.font.Font(None, 18)
        self.hover_font = pygame.font.Font(None, 20)

    def draw(
        self,
        surface: pygame.Surface,
        sheepo_rect: pygame.Rect,
        dgaf_stacks: int,
        mouse_pos: tuple[int, int],
    ) -> str | None:
        """Draw debuffs under Sheepo. Returns description text if hovering, else None."""
        if dgaf_stacks <= 0:
            return None

        # DGAF icon position
        icon_x = sheepo_rect.centerx - s.DEBUFF_ICON_SIZE[0] // 2
        icon_y = sheepo_rect.bottom + s.DEBUFF_BAR_OFFSET_Y
        icon_rect = pygame.Rect(icon_x, icon_y, *s.DEBUFF_ICON_SIZE)

        # Draw icon (placeholder: gray circle with skull-ish face)
        pygame.draw.rect(surface, s.DGAF_GRAY, icon_rect, border_radius=4)
        pygame.draw.rect(surface, s.BLACK, icon_rect, 1, border_radius=4)
        # Tiny bored face
        cx, cy = icon_rect.centerx, icon_rect.centery
        pygame.draw.line(surface, s.BLACK, (cx - 4, cy - 2), (cx, cy - 2), 2)
        pygame.draw.line(surface, s.BLACK, (cx + 1, cy - 2), (cx + 5, cy - 2), 2)
        pygame.draw.line(surface, s.BLACK, (cx - 3, cy + 3), (cx + 4, cy + 3), 1)

        # Stack count
        if dgaf_stacks > 1:
            count_surf = self.font.render(f"x{dgaf_stacks}", True, s.WHITE)
            surface.blit(count_surf, (icon_rect.right + 2, icon_rect.centery - 6))

        # Check hover for description
        hover_rect = pygame.Rect(
            icon_x - 2, icon_y - 2,
            s.DEBUFF_ICON_SIZE[0] + (30 if dgaf_stacks > 1 else 4),
            s.DEBUFF_ICON_SIZE[1] + 4
        )
        if hover_rect.collidepoint(mouse_pos):
            chance = int((1.0 - (0.5 ** dgaf_stacks)) * 100)
            return f"DGAF Attitude (x{dgaf_stacks}): {chance}% chance Sheepo refuses your help. Thanks, nihilists."
        return None


class DescriptionBox:
    """Top-right text box that shows debuff descriptions on hover."""

    def __init__(self) -> None:
        self.font = pygame.font.Font(None, 18)

    def draw(self, surface: pygame.Surface, text: str | None) -> None:
        if not text:
            return

        pos = s.DESCRIPTION_BOX_POS
        size = s.DESCRIPTION_BOX_SIZE

        bg = pygame.Surface(size, pygame.SRCALPHA)
        bg.fill((30, 30, 30, 200))
        surface.blit(bg, pos)
        pygame.draw.rect(surface, s.TOOLBAR_BORDER, (*pos, *size), 2, border_radius=4)

        # Word wrap the text
        words = text.split()
        lines: list[str] = []
        current_line = ""
        for word in words:
            test = current_line + (" " if current_line else "") + word
            if self.font.size(test)[0] > size[0] - 16:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines[:4]):  # Max 4 lines
            line_surf = self.font.render(line, True, s.UI_TEXT)
            surface.blit(line_surf, (pos[0] + 8, pos[1] + 8 + i * 16))
"""Stim Board — a draggable window with fun noise buttons."""

import pygame

import settings as s


class StimBoard:
    """A draggable mini-window with 3 buttons that play sounds."""

    def __init__(self) -> None:
        self.visible: bool = False
        self.width, self.height = s.STIM_BOARD_SIZE
        self.x = s.SCREEN_WIDTH - self.width - 20
        self.y = s.SCREEN_HEIGHT - self.height - 80

        self.dragging: bool = False
        self.drag_offset: tuple[int, int] = (0, 0)

        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 22)

        # Button layout
        self.button_size = (140, 30)
        self.buttons: list[pygame.Rect] = []
        self.button_labels = ["BOING", "WHOOSH", "SPLAT"]
        self._update_buttons()

        # Toggle button (always visible)
        self.toggle_rect = pygame.Rect(
            s.STIM_BOARD_TOGGLE_POS[0] - 25,
            s.STIM_BOARD_TOGGLE_POS[1] - 15,
            50, 30
        )

        # Sound slots (None = no sound loaded yet)
        self.sounds: list[pygame.mixer.Sound | None] = [None, None, None]
        self._load_sounds()

    def _load_sounds(self) -> None:
        """Try to load stim sounds from audio slots."""
        sfx_slots = [s.SFX_STIM_1, s.SFX_STIM_2, s.SFX_STIM_3]
        for i, slot in enumerate(sfx_slots):
            if slot:
                try:
                    self.sounds[i] = pygame.mixer.Sound(s.AUDIO_DIR + slot)
                except pygame.error:
                    self.sounds[i] = None

    def _update_buttons(self) -> None:
        """Recalculate button positions based on window position."""
        self.buttons = []
        for i in range(s.STIM_BUTTON_COUNT):
            r = pygame.Rect(
                self.x + (self.width - self.button_size[0]) // 2,
                self.y + 30 + i * (self.button_size[1] + 8),
                *self.button_size,
            )
            self.buttons.append(r)

    def toggle(self) -> None:
        self.visible = not self.visible

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if event was consumed."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Toggle button
            if self.toggle_rect.collidepoint(event.pos):
                self.toggle()
                return True

            if not self.visible:
                return False

            # Check stim buttons
            for i, btn in enumerate(self.buttons):
                if btn.collidepoint(event.pos):
                    self._play_sound(i)
                    return True

            # Start dragging title bar area
            title_bar = pygame.Rect(self.x, self.y, self.width, 24)
            if title_bar.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = (event.pos[0] - self.x, event.pos[1] - self.y)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.x = event.pos[0] - self.drag_offset[0]
            self.y = event.pos[1] - self.drag_offset[1]
            # Clamp to screen
            self.x = max(0, min(s.SCREEN_WIDTH - self.width, self.x))
            self.y = max(0, min(s.SCREEN_HEIGHT - self.height, self.y))
            self._update_buttons()
            return True

        return False

    def _play_sound(self, index: int) -> None:
        """Play the sound at the given slot index."""
        if self.sounds[index]:
            self.sounds[index].play()
        # If no sound loaded, just do nothing (placeholder)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw toggle button and (if visible) the stim board window."""
        # Toggle button (always visible)
        pygame.draw.rect(surface, s.TOOLBAR_BG, self.toggle_rect, border_radius=4)
        pygame.draw.rect(surface, s.TOOLBAR_BORDER, self.toggle_rect, 2, border_radius=4)
        label = self.font.render("STIM", True, s.UI_TEXT)
        label_rect = label.get_rect(center=self.toggle_rect.center)
        surface.blit(label, label_rect)

        if not self.visible:
            return

        # Window background
        win_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        win_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        win_surf.fill((50, 45, 55, 230))
        surface.blit(win_surf, win_rect)
        pygame.draw.rect(surface, (180, 100, 220), win_rect, 2, border_radius=6)

        # Title bar
        title = self.title_font.render("~ STIM BOARD ~", True, (220, 180, 255))
        title_rect = title.get_rect(midtop=(self.x + self.width // 2, self.y + 4))
        surface.blit(title, title_rect)

        # Buttons
        for i, btn in enumerate(self.buttons):
            color = [(220, 80, 80), (80, 200, 80), (80, 130, 220)][i]
            pygame.draw.rect(surface, color, btn, border_radius=6)
            pygame.draw.rect(surface, s.WHITE, btn, 2, border_radius=6)
            lbl = self.font.render(self.button_labels[i], True, s.WHITE)
            lbl_rect = lbl.get_rect(center=btn.center)
            surface.blit(lbl, lbl_rect)
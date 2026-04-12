"""Playing state — main gameplay with all entities and systems."""

import pygame

import settings as s
from src.entities.bee import Bee
from src.entities.nihilist import Bush, Nihilist
from src.entities.pond import Pond
from src.entities.sheepo import Sheepo
from src.entities.sun import Sun
from src.states.base_state import BaseState
from src.systems.event_manager import EventManager
from src.systems.tool_manager import ToolManager
from src.ui.hud import DebuffBar, DescriptionBox, TimerDisplay
from src.ui.stim_board import StimBoard
from src.ui.toolbar import Toolbar


class PlayingState(BaseState):
    """The main gameplay state."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.sheepo: Sheepo | None = None
        self.sun: Sun | None = None
        self.pond: Pond | None = None
        self.tool_mgr: ToolManager | None = None
        self.event_mgr: EventManager | None = None

        self.bees: list[Bee] = []
        self.nihilists: list[Nihilist] = []
        self.bushes: list[Bush] = []

        # UI
        self.toolbar: Toolbar | None = None
        self.stim_board: StimBoard | None = None
        self.timer_display: TimerDisplay | None = None
        self.debuff_bar: DebuffBar | None = None
        self.desc_box: DescriptionBox | None = None

        # Grass color for background
        self.grass_color = (100, 180, 80)

    def enter(self) -> None:
        """Set up a new game."""
        self.sheepo = Sheepo()
        self.sun = Sun()
        self.pond = Pond()
        self.tool_mgr = ToolManager()

        # Create bushes
        self.bushes = [Bush(pos) for pos in s.ALL_BUSH_POSITIONS]

        self.event_mgr = EventManager(self.bushes)
        self.bees = []
        self.nihilists = []

        # UI
        self.toolbar = Toolbar()
        self.stim_board = StimBoard()
        self.timer_display = TimerDisplay()
        self.debuff_bar = DebuffBar()
        self.desc_box = DescriptionBox()

        # Reset score timer
        self.game.score_manager.reset_timer()

        # Hide system cursor — we draw our own
        pygame.mouse.set_visible(False)

        # TODO: play in-game music

    def exit(self) -> None:
        pygame.mouse.set_visible(True)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("paused")
                return

        # Let stim board consume events first
        if self.stim_board and self.stim_board.handle_event(event):
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

    def _handle_click(self, pos: tuple[int, int]) -> None:
        """Handle a left click based on current tool and target."""
        # Check toolbar first
        tool_clicked = self.toolbar.handle_click(pos)
        if tool_clicked is not None:
            if tool_clicked == s.TOOL_NONE:
                self.tool_mgr.unequip()
            else:
                self.tool_mgr.equip(tool_clicked)
            return

        # ── Tool actions on world ──
        if self.tool_mgr.is_hand:
            # Try to swat a bee
            for bee in self.bees:
                if bee.alive and bee.rect.collidepoint(pos):
                    bee.swat()
                    return

        elif self.tool_mgr.has_clippers:
            if not self.tool_mgr.can_use_tool():
                return  # Clippers are slipping!
            if self.sheepo.rect.collidepoint(pos):
                self.sheepo.try_clip()
                return

        elif self.tool_mgr.current_tool == s.TOOL_BUCKET_EMPTY:
            # Fill at pond
            if self.pond.rect.collidepoint(pos):
                self.tool_mgr.fill_bucket()
                return

        elif self.tool_mgr.has_full_bucket:
            # Throw water on Sheepo (extinguish)
            if self.sheepo.on_fire and self.sheepo.rect.collidepoint(pos):
                if self.tool_mgr.use_bucket():
                    self.sheepo.try_extinguish()
                return

            # Throw water on bush (flush nihilist)
            for bush in self.bushes:
                if bush.rect.collidepoint(pos) and bush.has_nihilist:
                    if self.tool_mgr.use_bucket():
                        bush.splash()
                    return

            # Throw water on pond (refill — already full, but click pond)
            if self.pond.rect.collidepoint(pos):
                return  # Already full, no-op

    def update(self, dt: float) -> None:
        # Score timer
        self.game.score_manager.update(dt)

        # Sheepo
        self.sheepo.update(dt)

        # Check death
        death = self.sheepo.get_death_reason()
        if death:
            self.game.death_reason = death
            self.game.change_state("gameover")
            return

        # Sun
        if self.sun.update(dt):
            self.sheepo.set_on_fire()

        # Pond
        self.pond.update(dt)

        # Bushes
        for bush in self.bushes:
            bush.update(dt)

        # Event manager — spawn new threats
        self.event_mgr.update(dt)
        self.bees.extend(self.event_mgr.collect_bees())
        self.nihilists.extend(self.event_mgr.collect_nihilists())

        # Bees
        for bee in self.bees:
            bee.update(dt, self.sheepo.x, self.sheepo.y)
            if bee.check_contact(self.sheepo.rect):
                self.sheepo.set_on_fire()
                bee.swat()  # Bee dies on contact

        # Clean up dead bees
        self.bees = [b for b in self.bees if b.alive]

        # Nihilists
        for nihilist in self.nihilists:
            if nihilist.update(dt, self.sheepo.x, self.sheepo.y):
                self.sheepo.add_dgaf_stack()

        # Clean up done nihilists
        self.nihilists = [n for n in self.nihilists if n.alive]

        # Tool manager
        self.tool_mgr.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        # Background — grass
        surface.fill(self.grass_color)

        # Draw some ground texture (simple)
        for gy in range(0, s.SCREEN_HEIGHT, 40):
            shade = 95 + (gy % 80 == 0) * 10
            pygame.draw.line(
                surface, (shade, 175, 75),
                (0, gy), (s.SCREEN_WIDTH, gy)
            )

        # Pond
        self.pond.draw(surface)

        # Bushes
        for bush in self.bushes:
            bush.draw(surface)

        # Nihilists (visible when moving)
        for nihilist in self.nihilists:
            nihilist.draw(surface)

        # Sheepo
        self.sheepo.draw(surface)

        # Sun
        self.sun.draw(surface)

        # Bees
        for bee in self.bees:
            bee.draw(surface)

        # ── UI ──
        # Timer
        time_text = self.game.score_manager.format_time()
        self.timer_display.draw(surface, time_text)

        # Debuff bar
        mouse_pos = pygame.mouse.get_pos()
        desc = self.debuff_bar.draw(
            surface, self.sheepo.rect, self.sheepo.dgaf_stacks, mouse_pos
        )

        # Description box
        self.desc_box.draw(surface, desc)

        # Toolbar
        self.toolbar.draw(surface, self.tool_mgr.current_tool, self.tool_mgr.bucket_full)

        # Stim board
        self.stim_board.draw(surface)

        # Fire timer warning
        if self.sheepo.on_fire:
            self._draw_fire_warning(surface)

        # Wet clippers indicator
        if self.tool_mgr.clippers_wet and self.tool_mgr.current_tool == s.TOOL_CLIPPERS:
            self._draw_wet_warning(surface)

        # Custom cursor (tool as pointer)
        self._draw_cursor(surface)

    def _draw_cursor(self, surface: pygame.Surface) -> None:
        """Draw the tool cursor at mouse position."""
        mx, my = pygame.mouse.get_pos()
        cursor_surf = self.tool_mgr.get_cursor_surface()

        if self.tool_mgr.slipping:
            # Clippers slipping — draw them falling below cursor
            import math
            offset = math.sin(pygame.time.get_ticks() / 100) * 5
            surface.blit(cursor_surf, (mx + offset, my + 20))
            # Draw a little "!" above
            font = pygame.font.Font(None, 24)
            warn = font.render("!", True, (255, 50, 50))
            surface.blit(warn, (mx + 8, my - 10))
        else:
            surface.blit(cursor_surf, (mx - 4, my - 4))

    def _draw_fire_warning(self, surface: pygame.Surface) -> None:
        """Draw fire timer countdown."""
        remaining = max(0, self.sheepo.fire_timer)
        font = pygame.font.Font(None, 32)
        color = (255, 50, 50) if remaining < 2 else (255, 150, 0)
        text = font.render(f"FIRE! {remaining:.1f}s", True, color)
        rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, 60))
        surface.blit(text, rect)

    def _draw_wet_warning(self, surface: pygame.Surface) -> None:
        """Draw wet clippers indicator."""
        font = pygame.font.Font(None, 18)
        text = font.render("CLIPPERS WET — SLIPPERY!", True, (100, 180, 255))
        rect = text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT - 90))
        surface.blit(text, rect)
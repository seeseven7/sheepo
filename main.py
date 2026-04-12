"""Fuck My Sheepo Life — main entry point and game loop."""

import sys

import pygame

import settings as s
from src.states.gameover_state import GameOverState
from src.states.pause_state import PauseState
from src.states.playing_state import PlayingState
from src.states.title_state import TitleState
from src.systems.score_manager import ScoreManager


class Game:
    """Main game class — owns the loop, clock, state machine."""

    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        pygame.display.set_caption(s.GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running: bool = True

        # Shared systems
        self.score_manager = ScoreManager()

        # Death reason passed from playing → gameover
        self.death_reason: str = ""

        # State machine
        self.states: dict[str, object] = {
            "title": TitleState(self),
            "playing": PlayingState(self),
            "paused": PauseState(self),
            "gameover": GameOverState(self),
        }
        self.current_state_name: str = "title"
        self.previous_state_name: str | None = None

        # For pause overlay — we need to keep drawing the playing state
        self._playing_snapshot: pygame.Surface | None = None

        self.current_state.enter()

    @property
    def current_state(self):
        return self.states[self.current_state_name]

    def change_state(self, new_state: str) -> None:
        """Transition to a new state."""
        if new_state == "resume":
            # Special case: unpause → go back to playing
            self.current_state.exit()
            self.current_state_name = "playing"
            # Don't call enter() — we're resuming, not restarting
            pygame.mouse.set_visible(False)
            return

        if new_state == "paused":
            # Take snapshot of current screen for pause overlay
            self._playing_snapshot = self.screen.copy()

        self.previous_state_name = self.current_state_name
        self.current_state.exit()
        self.current_state_name = new_state
        self.current_state.enter()

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(s.FPS) / 1000.0
            # Cap dt to prevent spiral of death
            dt = min(dt, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                self.current_state.handle_event(event)

            self.current_state.update(dt)

            # Draw
            if self.current_state_name == "paused" and self._playing_snapshot:
                # Draw the frozen game underneath the pause overlay
                self.screen.blit(self._playing_snapshot, (0, 0))
                self.current_state.draw(self.screen)
            else:
                self.current_state.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
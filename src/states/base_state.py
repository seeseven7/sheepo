"""Base state class — all game states inherit from this."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from main import Game


class BaseState(ABC):
    """Abstract base for all game states."""

    def __init__(self, game: "Game") -> None:
        self.game = game

    def enter(self) -> None:
        """Called when this state becomes active."""
        pass

    def exit(self) -> None:
        """Called when leaving this state."""
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Process a single pygame event."""
        ...

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update logic. dt is delta time in seconds."""
        ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw this state to the given surface."""
        ...
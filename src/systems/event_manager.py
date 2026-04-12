"""Event Manager — spawns threats based on time-scaled difficulty."""

import random

import settings as s
from src.entities.bee import Bee
from src.entities.nihilist import Bush, Nihilist


class EventManager:
    """Manages threat spawning with escalating frequency."""

    def __init__(self, bushes: list[Bush]) -> None:
        self.bushes = bushes
        self.elapsed: float = 0.0
        self.event_timer: float = 0.0
        self.next_event_in: float = s.GRACE_PERIOD

        # Active entities managed externally, we just spawn them
        self.pending_bees: list[Bee] = []
        self.pending_nihilists: list[Nihilist] = []

    def get_current_interval(self) -> float:
        """Get the current event spawn interval based on elapsed time."""
        for start, end, interval in s.EVENT_SCHEDULE:
            if start <= self.elapsed < end:
                return interval
        # Fallback
        return s.EVENT_SCHEDULE[-1][2]

    def update(self, dt: float) -> None:
        """Update timers and spawn events."""
        self.elapsed += dt

        if self.elapsed < s.GRACE_PERIOD:
            return

        self.event_timer += dt
        if self.event_timer >= self.next_event_in:
            self.event_timer = 0.0
            self.next_event_in = self.get_current_interval()
            self._spawn_random_event()

    def _spawn_random_event(self) -> None:
        """Randomly pick and spawn a threat."""
        # Available event types
        events = ["bee", "nihilist"]
        # Weighted — bees are more common
        weights = [3, 1]

        choice = random.choices(events, weights=weights, k=1)[0]

        if choice == "bee":
            self.pending_bees.append(Bee())
        elif choice == "nihilist":
            from_left = random.choice([True, False])
            n = Nihilist(self.bushes, from_left=from_left)
            if n.alive:
                self.pending_nihilists.append(n)

    def collect_bees(self) -> list[Bee]:
        """Collect and clear pending bee spawns."""
        bees = self.pending_bees
        self.pending_bees = []
        return bees

    def collect_nihilists(self) -> list[Nihilist]:
        """Collect and clear pending nihilist spawns."""
        nihilists = self.pending_nihilists
        self.pending_nihilists = []
        return nihilists
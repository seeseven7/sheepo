"""Score Manager — tracks survival time and persists high scores."""

import json
import os

import settings as s


class ScoreManager:
    """Tracks elapsed game time and manages the high score board."""

    def __init__(self) -> None:
        self.elapsed_ms: int = 0  # Current run time in milliseconds
        self.high_scores: list[int] = []  # Stored as milliseconds
        self._load_scores()

    def _load_scores(self) -> None:
        """Load high scores from JSON file."""
        if os.path.exists(s.HIGH_SCORE_FILE):
            try:
                with open(s.HIGH_SCORE_FILE, "r") as f:
                    data = json.load(f)
                    self.high_scores = data.get("scores", [])[:s.MAX_HIGH_SCORES]
            except (json.JSONDecodeError, KeyError):
                self.high_scores = []
        else:
            self.high_scores = []

    def _save_scores(self) -> None:
        """Save high scores to JSON file."""
        with open(s.HIGH_SCORE_FILE, "w") as f:
            json.dump({"scores": self.high_scores}, f)

    def reset_timer(self) -> None:
        """Reset for a new game."""
        self.elapsed_ms = 0

    def update(self, dt: float) -> None:
        """Accumulate time."""
        self.elapsed_ms += int(dt * 1000)

    def submit_score(self) -> int:
        """Submit current time as a score. Returns placement (0-indexed) or -1."""
        score = self.elapsed_ms
        self.high_scores.append(score)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:s.MAX_HIGH_SCORES]
        self._save_scores()

        try:
            return self.high_scores.index(score)
        except ValueError:
            return -1

    def format_time(self, ms: int | None = None) -> str:
        """Format milliseconds as MM:SS.mmm."""
        if ms is None:
            ms = self.elapsed_ms
        total_seconds = ms / 1000
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        millis = ms % 1000
        return f"{minutes:02d}:{seconds:02d}.{millis:03d}"

    def get_display_scores(self) -> list[str]:
        """Get formatted high score list with dashes for empty slots."""
        display = []
        for i in range(s.MAX_HIGH_SCORES):
            if i < len(self.high_scores):
                display.append(self.format_time(self.high_scores[i]))
            else:
                display.append("—")
        return display
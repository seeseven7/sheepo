"""Game Over state — show death reason, score, and high scores."""

import math

import pygame

import settings as s
from src.states.base_state import BaseState


class GameOverState(BaseState):
    """Game over screen with death message, time, and leaderboard."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.title_font: pygame.font.Font | None = None
        self.death_font: pygame.font.Font | None = None
        self.score_font: pygame.font.Font | None = None
        self.prompt_font: pygame.font.Font | None = None
        self.label_font: pygame.font.Font | None = None

        self.death_reason: str = ""
        self.final_time: str = ""
        self.placement: int = -1
        self.blink_timer: float = 0.0

    def enter(self) -> None:
        self.title_font = pygame.font.Font(None, 52)
        self.death_font = pygame.font.Font(None, 28)
        self.score_font = pygame.font.Font(None, 26)
        self.prompt_font = pygame.font.Font(None, 24)
        self.label_font = pygame.font.Font(None, 22)
        self.blink_timer = 0.0

        pygame.mouse.set_visible(True)

        # Grab death reason from game
        self.death_reason = getattr(self.game, "death_reason", "Sheepo died somehow")
        self.final_time = self.game.score_manager.format_time()

        # Submit score
        self.placement = self.game.score_manager.submit_score()

    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.change_state("playing")

    def update(self, dt: float) -> None:
        self.blink_timer += dt

    def draw(self, surface: pygame.Surface) -> None:
        # Dark background
        surface.fill((30, 25, 20))

        # Dim overlay pattern — subtle sadness
        for y in range(0, s.SCREEN_HEIGHT, 6):
            alpha = 15 + (y % 12 == 0) * 10
            pygame.draw.line(surface, (40, 35, 30), (0, y), (s.SCREEN_WIDTH, y))

        # ── GAME OVER ──
        go_text = self.title_font.render("GAME OVER", True, (220, 60, 60))
        go_rect = go_text.get_rect(center=(s.SCREEN_WIDTH // 2, 80))
        surface.blit(go_text, go_rect)

        # Death reason
        death_text = self.death_font.render(self.death_reason, True, (200, 180, 160))
        death_rect = death_text.get_rect(center=(s.SCREEN_WIDTH // 2, 130))
        surface.blit(death_text, death_rect)

        # Survival time
        time_label = self.score_font.render("You survived:", True, s.UI_TEXT)
        time_value = self.title_font.render(self.final_time, True, (255, 220, 100))
        surface.blit(
            time_label,
            time_label.get_rect(center=(s.SCREEN_WIDTH // 2, 180))
        )
        surface.blit(
            time_value,
            time_value.get_rect(center=(s.SCREEN_WIDTH // 2, 220))
        )

        # ── High Scores ──
        hs_x = s.SCREEN_WIDTH // 2
        hs_y_start = 280

        header = self.score_font.render("— HIGH SCORES —", True, (200, 180, 255))
        surface.blit(header, header.get_rect(center=(hs_x, hs_y_start)))

        scores = self.game.score_manager.get_display_scores()
        for i, score_text in enumerate(scores):
            y = hs_y_start + 35 + i * 28
            rank = f"#{i + 1}"

            # Highlight current placement
            if i == self.placement:
                color = (255, 220, 100)
                rank_color = (255, 220, 100)
                marker = " ← NEW"
            else:
                color = s.UI_TEXT
                rank_color = (160, 160, 160)
                marker = ""

            rank_surf = self.label_font.render(rank, True, rank_color)
            score_surf = self.score_font.render(score_text + marker, True, color)

            surface.blit(rank_surf, (hs_x - 100, y))
            surface.blit(score_surf, (hs_x - 60, y))

        # Blinking prompt
        if math.sin(self.blink_timer * 3) > 0:
            prompt = self.prompt_font.render(
                "Press SPACEBAR to play again", True, (180, 180, 180)
            )
            surface.blit(
                prompt,
                prompt.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT - 60))
            )
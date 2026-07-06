from __future__ import annotations

from dataclasses import dataclass

from .elo import expected_score


@dataclass(frozen=True)
class BaselineModel:
    player_count: int
    max_rating: float
    q: float
    learning_fraction: float

    @property
    def baseline(self) -> float:
        return self.max_rating / 2.0

    @property
    def gap(self) -> float:
        if self.player_count <= 1:
            return 0.0
        return self.max_rating / (self.player_count - 1)

    @property
    def k(self) -> float:
        return self.learning_fraction * self.gap

    @property
    def adjacent_win_probability(self) -> float:
        return expected_score(self.gap, 0.0, q=self.q) if self.gap else 0.5

    def hidden_skills(self) -> list[float]:
        midpoint = (self.player_count - 1) / 2.0
        return [
            self.baseline + self.gap * (midpoint - player)
            for player in range(self.player_count)
        ]

"""Immutable definition of the first forgetting toy world."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ToyWorld:
    """Fixed players, evenly spaced latent skills, and fixed-K Elo settings."""

    player_count: int = 10
    latent_gap: float = 40.0
    q: float = 400.0
    k: float = 5.0

    def __post_init__(self) -> None:
        if self.player_count < 2:
            raise ValueError("player_count must be at least 2")
        if not isfinite(self.latent_gap) or self.latent_gap <= 0:
            raise ValueError("latent_gap must be finite and positive")
        if not isfinite(self.q) or self.q <= 0:
            raise ValueError("q must be finite and positive")
        if not isfinite(self.k) or self.k <= 0:
            raise ValueError("k must be finite and positive")

    @property
    def latent_skills(self) -> tuple[float, ...]:
        midpoint = (self.player_count - 1) / 2.0
        return tuple(
            self.latent_gap * (midpoint - player)
            for player in range(self.player_count)
        )

    @property
    def flat_initial_ratings(self) -> tuple[float, ...]:
        return (0.0,) * self.player_count

    @property
    def inverted_initial_ratings(self) -> tuple[float, ...]:
        return tuple(-skill for skill in self.latent_skills)

    @property
    def pairs_per_event(self) -> int:
        return self.player_count * (self.player_count - 1) // 2


"""Result types for the canonical BKP1 prior producer."""

from __future__ import annotations

from dataclasses import dataclass, field

from ...sumo_core.BasicPrimitives import RikId
from ...sumo_core.Chii import Chii
from ...sumo_core.History import Date


@dataclass(frozen=True)
class ReplayResult:
    basho_start_ratings: dict[Date, dict[RikId, float]] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class IterationRow:
    iteration: int
    max_prior_change: float
    max_change_chii: str
    max_change_observation_count: int
    mean_recentering_adjustment: float
    minimum_recentering_adjustment: float
    maximum_recentering_adjustment: float


@dataclass(frozen=True)
class FixedPointResult:
    priors: dict[Chii, float]
    support: dict[Chii, int]
    converged: bool
    iterations: int
    final_delta: float
    iteration_rows: tuple[IterationRow, ...]

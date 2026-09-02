"""Result types for the P2 divisional-average experiment."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


DIVISIONS = (
    "Makuuchi",
    "Juryo",
    "Makushita",
    "Sandanme",
    "Jonidan",
    "Jonokuchi",
)


@dataclass(frozen=True, slots=True)
class DivisionAdjustment:
    iteration: int
    date: str
    phase: str
    division: str
    active_count: int
    target_mean: float
    raw_mean: float
    adjustment_per_rikishi: float
    adjusted_mean: float


@dataclass(frozen=True)
class ReplayResult:
    basho_start_ratings: dict[Date, dict[RikId, float]] = field(default_factory=dict)
    basho_end_ratings: dict[Date, dict[RikId, float]] = field(default_factory=dict)
    adjustments: tuple[DivisionAdjustment, ...] = ()
    rated_bout_count: int = 0
    mean_log_loss: float = 0.0
    mean_brier_loss: float = 0.0


@dataclass(frozen=True, slots=True)
class DivisionIterationRow:
    iteration: int
    division: str
    chii_count: int
    observation_count: int
    target_mean: float
    raw_map_mean: float
    centred_map_mean: float
    correction_mass: float
    mean_prior_difference_from_p1: float
    mean_absolute_prior_difference_from_p1: float
    minimum_prior: float
    maximum_prior: float


@dataclass(frozen=True, slots=True)
class IterationRow:
    iteration: int
    max_prior_change: float
    max_change_chii: str
    max_change_observation_count: int
    mean_log_loss: float
    mean_brier_loss: float


@dataclass(frozen=True)
class FixedPointResult:
    priors: dict[Chii, float]
    support: dict[Chii, int]
    initialization_support: dict[Chii, int]
    completion_sources: dict[Chii, Chii]
    supported_chii: frozenset[Chii]
    support_threshold: int
    targets: dict[str, float]
    converged: bool
    iterations: int
    final_delta: float
    iteration_rows: tuple[IterationRow, ...]
    division_iteration_rows: tuple[DivisionIterationRow, ...]
    prior_iteration_rows: tuple[dict[str, object], ...]
    replay: ReplayResult

"""Types for the Equelo population-policy experiment."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ...sumo_core.BasicPrimitives import RikId
from ...sumo_core.Chii import Chii
from ...sumo_core.History import Date


class PopulationPolicy(str, Enum):
    """Population and bout-mass treatments used by Tranche 1."""

    LEGACY_DEPARTURE = "legacy_departure"
    LEGACY_DEPARTURE_BOUT_MASS = "legacy_plus_dual_k"
    POST_BASHO_MEAN_START_ONLY = "whole_population_start_only"
    POST_BASHO_MEAN = "post_basho_mean"


@dataclass(frozen=True, slots=True)
class BashoAdjustment:
    policy: str
    date: str
    active_count: int
    entrant_count: int
    departure_count: int
    target_mean: float
    raw_start_mean: float
    start_adjustment_per_rikishi: float
    adjusted_start_mean: float
    bout_mass_change: float
    raw_end_mean: float
    end_adjustment_per_rikishi: float
    adjusted_end_mean: float


@dataclass(frozen=True)
class ReplayResult:
    variant: str
    policy: PopulationPolicy
    target_mean: float
    basho_start_ratings: dict[Date, dict[RikId, float]] = field(default_factory=dict)
    basho_end_ratings: dict[Date, dict[RikId, float]] = field(default_factory=dict)
    adjustments: tuple[BashoAdjustment, ...] = ()
    rated_bout_count: int = 0
    mean_log_loss: float = 0.0
    mean_brier_score: float = 0.0


@dataclass(frozen=True, slots=True)
class IterationRow:
    policy: str
    iteration: int
    max_prior_change: float
    map_recentering_shift: float
    max_change_chii: str
    max_change_chii_ordinal: int
    max_change_observation_count: int
    recentering_alpha: float
    minimum_recentering_adjustment: float
    maximum_recentering_adjustment: float
    maximum_pairwise_difference_change: float
    rms_pairwise_difference_change: float


@dataclass(frozen=True)
class FixedPointResult:
    variant: str
    policy: PopulationPolicy
    normalisation_alpha: float | None
    recentering_alpha: float
    priors: dict[Chii, float]
    converged: bool
    iterations: int
    final_delta: float
    iteration_rows: tuple[IterationRow, ...]
    replay: ReplayResult

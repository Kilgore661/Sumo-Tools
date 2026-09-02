"""Value objects for the Elo-58 full-history reconstruction."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


@dataclass(frozen=True, slots=True)
class SelectedBout:
    date: Date
    day: int
    rikishi_a: RikId
    rikishi_b: RikId
    chii_a: Chii
    chii_b: Chii
    a_won: bool


@dataclass(frozen=True, slots=True)
class ExcludedBout:
    date: Date
    day: int
    rikishi_1: RikId
    rikishi_2: RikId
    outcome_1: str
    outcome_2: str
    decision: str
    reason: str


@dataclass(frozen=True, slots=True)
class BashoSelection:
    bouts: tuple[SelectedBout, ...]
    excluded: tuple[ExcludedBout, ...]
    raw_result_count: int
    rated_bout_count: int
    excluded_fusen_count: int
    excluded_non_binary_count: int
    excluded_off_banzuke_count: int


@dataclass(frozen=True, slots=True)
class ForecastRow:
    run: str
    date: Date
    day: int
    rikishi_a: RikId
    rikishi_b: RikId
    chii_a: Chii
    chii_b: Chii
    rating_a_before: float
    rating_b_before: float
    rated_bouts_a_before: int
    rated_bouts_b_before: int
    probability_a_wins: float
    a_won: bool
    k_a: float
    k_b: float
    delta_a: float
    delta_b: float
    rating_a_after: float
    rating_b_after: float


@dataclass(frozen=True, slots=True)
class PopulationAdjustment:
    run: str
    date: Date
    active_count: int
    new_rikishi_count: int
    returning_rikishi_count: int
    departing_rikishi_count: int
    target_mean: float
    raw_start_mean: float
    start_adjustment: float
    adjusted_start_mean: float
    raw_end_mean: float
    end_adjustment: float
    adjusted_end_mean: float


@dataclass(frozen=True)
class BashoReplay:
    forecasts: tuple[ForecastRow, ...]
    adjustment: PopulationAdjustment
    start_ratings: dict[RikId, float]
    end_ratings: dict[RikId, float]
    rated_bouts_before: dict[RikId, int]
    rated_bouts_after: dict[RikId, int]
    initialisation_sources: dict[RikId, str]


@dataclass(slots=True)
class ReplayState:
    """All ever-observed ratings, including inactive archived rikishi."""

    ratings: dict[RikId, float] = field(default_factory=dict)
    rated_bouts: dict[RikId, int] = field(default_factory=dict)
    initialisation_sources: dict[RikId, str] = field(default_factory=dict)
    previous_active: set[RikId] = field(default_factory=set)

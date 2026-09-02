"""Production observation model for Elo-89."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


Ratings = dict[RikId, float]
RatingsByDate = dict[Date, Ratings]
DailyRatingsByDate = dict[Date, dict[Day, Ratings]]


@dataclass(frozen=True, slots=True)
class Forecast:
    date: Date
    day: Day
    rikishi_a: RikId
    rikishi_b: RikId
    chii_a: Chii | None
    chii_b: Chii | None
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
    initialisation_a: str
    initialisation_b: str


@dataclass(frozen=True, slots=True)
class BashoAdjustment:
    date: Date
    active_count: int
    new_rikishi_count: int
    departing_rikishi_count: int
    target_mean: float
    raw_start_mean: float
    start_adjustment: float
    raw_end_mean: float
    end_adjustment: float


@dataclass(frozen=True, slots=True)
class Elo89Run:
    target_mean: float
    basho_start_ratings: RatingsByDate = field(default_factory=dict)
    day_end_ratings: DailyRatingsByDate = field(default_factory=dict)
    basho_end_ratings: RatingsByDate = field(default_factory=dict)
    forecasts: tuple[Forecast, ...] = ()
    adjustments: tuple[BashoAdjustment, ...] = ()
    raw_result_count: int = 0
    rated_bout_count: int = 0
    excluded_fusen_count: int = 0
    excluded_draw_count: int = 0

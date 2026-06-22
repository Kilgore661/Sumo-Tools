"""Data model for exploratory Equelo rating-change rows."""

from __future__ import annotations

from dataclasses import dataclass

from src.sumo_core.BasicPrimitives import RikId


@dataclass(frozen=True)
class RatingChangeRow:
    """One rikishi row in an n-change table."""

    rikishi_id: int
    shikona: str
    chii_at_start: str
    chii_ordinal_at_start: int | str
    chii_at_end: str
    chii_ordinal_at_end: int | str
    rating_at_start: str
    rating_at_end: str
    delta: str
    length_of_streak: int
    expected_bouts: int
    actual_bouts: int
    bout_coverage: str
    normalised_delta: str
    normalised_delta_per_actual_bout: str
    normalised_delta_per_expected_bout: str


@dataclass(frozen=True)
class RatingSnapshot:
    """One rikishi rating at the end of one basho."""

    rikishi_id: RikId
    rating: float


@dataclass(frozen=True)
class BoutWindowMetrics:
    """Bout-level exposure and normalised movement over a date window."""

    actual_bouts: int
    normalised_delta: float

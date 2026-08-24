"""Pure fixed-K Elo replay over an already generated history."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from .history import ToyHistory


def expected_score(rating_a: float, rating_b: float, *, q: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / q))


@dataclass(frozen=True)
class EventSnapshot:
    event: int
    global_bouts: int
    ratings: tuple[float, ...]


@dataclass(frozen=True)
class BoutForecast:
    event: int
    bout_in_event: int
    global_bout: int
    player_a: int
    player_b: int
    rating_a_before: float
    rating_b_before: float
    probability_a_wins: float
    a_won: bool
    delta_a: float
    rating_a_after: float
    rating_b_after: float


@dataclass(frozen=True)
class ReplayResult:
    label: str
    initial_ratings: tuple[float, ...]
    snapshots: tuple[EventSnapshot, ...]
    forecasts: tuple[BoutForecast, ...]


def replay_history(
    history: ToyHistory,
    *,
    label: str,
    initial_ratings: Sequence[float],
    q: float,
    k: float,
    retain_forecasts: bool = True,
) -> ReplayResult:
    history.validate()
    if len(initial_ratings) != history.player_count:
        raise ValueError("initial rating count must match history player count")
    if not label:
        raise ValueError("replay label must not be empty")
    if not isfinite(q) or q <= 0:
        raise ValueError("q must be finite and positive")
    if not isfinite(k) or k <= 0:
        raise ValueError("k must be finite and positive")
    if any(not isfinite(float(rating)) for rating in initial_ratings):
        raise ValueError("initial ratings must be finite")

    ratings = [float(rating) for rating in initial_ratings]
    snapshots = [EventSnapshot(event=0, global_bouts=0, ratings=tuple(ratings))]
    forecasts: list[BoutForecast] = []

    for row in history.bouts:
        rating_a = ratings[row.player_a]
        rating_b = ratings[row.player_b]
        probability = expected_score(rating_a, rating_b, q=q)
        score_a = 1.0 if row.a_won else 0.0
        delta_a = k * (score_a - probability)
        ratings[row.player_a] = rating_a + delta_a
        ratings[row.player_b] = rating_b - delta_a
        if retain_forecasts:
            forecasts.append(
                BoutForecast(
                    event=row.event,
                    bout_in_event=row.bout_in_event,
                    global_bout=row.global_bout,
                    player_a=row.player_a,
                    player_b=row.player_b,
                    rating_a_before=rating_a,
                    rating_b_before=rating_b,
                    probability_a_wins=probability,
                    a_won=row.a_won,
                    delta_a=delta_a,
                    rating_a_after=ratings[row.player_a],
                    rating_b_after=ratings[row.player_b],
                )
            )
        if row.bout_in_event == history.player_count * (history.player_count - 1) // 2:
            snapshots.append(
                EventSnapshot(
                    event=row.event,
                    global_bouts=row.global_bout,
                    ratings=tuple(ratings),
                )
            )

    return ReplayResult(
        label=label,
        initial_ratings=tuple(float(rating) for rating in initial_ratings),
        snapshots=tuple(snapshots),
        forecasts=tuple(forecasts),
    )


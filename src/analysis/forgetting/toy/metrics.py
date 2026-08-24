"""Coupled forgetting and truth-relative metrics for event snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Sequence

from .elo import ReplayResult, expected_score


@dataclass(frozen=True)
class EventMetric:
    event: int
    global_bouts: int
    state_distance: float
    forecast_distance: float
    forecast_fraction_remaining: float
    true_state_error: float
    flat_state_error: float
    true_probability_error: float
    flat_probability_error: float


@dataclass(frozen=True)
class ForgettingLandmark:
    kind: str
    target: float
    tolerance: float
    first_event: int | None
    first_global_bout: int | None
    recrossed: bool | None
    later_fraction_below: float | None
    remaining_events: int | None
    right_censored: bool


def centred(values: Sequence[float]) -> tuple[float, ...]:
    mean = sum(values) / len(values)
    return tuple(float(value) - mean for value in values)


def vector_rmse(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("vectors must have the same positive length")
    return sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(left, right)) / len(left))


def centred_state_distance(left: Sequence[float], right: Sequence[float]) -> float:
    return vector_rmse(centred(left), centred(right))


def pair_probabilities(ratings: Sequence[float], *, q: float) -> tuple[float, ...]:
    return tuple(
        expected_score(ratings[player_a], ratings[player_b], q=q)
        for player_a in range(len(ratings))
        for player_b in range(player_a + 1, len(ratings))
    )


def forecast_distance(left: Sequence[float], right: Sequence[float], *, q: float) -> float:
    return vector_rmse(pair_probabilities(left, q=q), pair_probabilities(right, q=q))


def build_event_metrics(
    *,
    true_run: ReplayResult,
    flat_run: ReplayResult,
    latent_skills: Sequence[float],
    q: float,
) -> tuple[EventMetric, ...]:
    if len(true_run.snapshots) != len(flat_run.snapshots):
        raise ValueError("coupled runs must have the same snapshot count")
    true_probabilities = pair_probabilities(latent_skills, q=q)
    initial_forecast_distance = forecast_distance(
        true_run.snapshots[0].ratings,
        flat_run.snapshots[0].ratings,
        q=q,
    )
    rows: list[EventMetric] = []
    for true_snapshot, flat_snapshot in zip(true_run.snapshots, flat_run.snapshots):
        if (
            true_snapshot.event != flat_snapshot.event
            or true_snapshot.global_bouts != flat_snapshot.global_bouts
        ):
            raise ValueError("coupled snapshots do not share the same clock")
        current_forecast_distance = forecast_distance(
            true_snapshot.ratings,
            flat_snapshot.ratings,
            q=q,
        )
        rows.append(
            EventMetric(
                event=true_snapshot.event,
                global_bouts=true_snapshot.global_bouts,
                state_distance=centred_state_distance(
                    true_snapshot.ratings,
                    flat_snapshot.ratings,
                ),
                forecast_distance=current_forecast_distance,
                forecast_fraction_remaining=(
                    current_forecast_distance / initial_forecast_distance
                    if initial_forecast_distance
                    else 0.0
                ),
                true_state_error=centred_state_distance(
                    true_snapshot.ratings,
                    latent_skills,
                ),
                flat_state_error=centred_state_distance(
                    flat_snapshot.ratings,
                    latent_skills,
                ),
                true_probability_error=vector_rmse(
                    pair_probabilities(true_snapshot.ratings, q=q),
                    true_probabilities,
                ),
                flat_probability_error=vector_rmse(
                    pair_probabilities(flat_snapshot.ratings, q=q),
                    true_probabilities,
                ),
            )
        )
    return tuple(rows)


def _landmark(
    rows: Sequence[EventMetric],
    *,
    kind: str,
    target: float,
    tolerance: float,
    persistence_events: int,
) -> ForgettingLandmark:
    flags = [row.forecast_distance <= tolerance for row in rows]
    first_index: int | None = None
    for index in range(0, len(flags) - persistence_events + 1):
        if all(flags[index : index + persistence_events]):
            first_index = index
            break
    if first_index is None:
        return ForgettingLandmark(
            kind=kind,
            target=target,
            tolerance=tolerance,
            first_event=None,
            first_global_bout=None,
            recrossed=None,
            later_fraction_below=None,
            remaining_events=None,
            right_censored=True,
        )

    later_flags = flags[first_index:]
    return ForgettingLandmark(
        kind=kind,
        target=target,
        tolerance=tolerance,
        first_event=rows[first_index].event,
        first_global_bout=rows[first_index].global_bouts,
        recrossed=not all(later_flags),
        later_fraction_below=sum(later_flags) / len(later_flags),
        remaining_events=len(rows) - first_index - 1,
        right_censored=False,
    )


def build_forgetting_landmarks(
    rows: Sequence[EventMetric],
    *,
    persistence_events: int,
    fractional_reductions: Sequence[float] = (0.5, 0.9, 0.99),
    absolute_tolerances: Sequence[float] = (0.05, 0.02, 0.01, 0.005),
) -> tuple[ForgettingLandmark, ...]:
    if not rows:
        raise ValueError("at least one event metric is required")
    if persistence_events < 1:
        raise ValueError("persistence_events must be at least 1")
    initial = rows[0].forecast_distance
    landmarks = [
        _landmark(
            rows,
            kind="fractional_reduction",
            target=float(reduction),
            tolerance=initial * (1.0 - float(reduction)),
            persistence_events=persistence_events,
        )
        for reduction in fractional_reductions
    ]
    landmarks.extend(
        _landmark(
            rows,
            kind="absolute_tolerance",
            target=float(tolerance),
            tolerance=float(tolerance),
            persistence_events=persistence_events,
        )
        for tolerance in absolute_tolerances
    )
    return tuple(landmarks)


def integrated_forecast_disagreement(rows: Sequence[EventMetric]) -> float:
    if len(rows) < 2:
        return 0.0
    return sum(
        (left.forecast_distance + right.forecast_distance)
        * (right.event - left.event)
        / 2.0
        for left, right in zip(rows, rows[1:])
    )


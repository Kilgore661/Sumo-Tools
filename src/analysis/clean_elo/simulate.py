"""Persistent, mean-normalised Elo simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import TypeAlias

from src.sumo_core.BasicEnums import Division, MSD, Outcome
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult

from .config import DEFAULT_Q
from .policies import (
    ConstantInitialRatingPolicy,
    FideKPolicy,
    InitialRatingPolicy,
    KPolicy,
)


Ratings: TypeAlias = dict[RikId, float]


@dataclass(frozen=True)
class BashoRatings:
    """Ratings recorded at the boundaries of one basho."""

    initial_before_normalisation: Ratings = field(default_factory=dict)
    initial_after_normalisation: Ratings = field(default_factory=dict)
    final_ratings: Ratings = field(default_factory=dict)
    recorded_appearances: dict[RikId, int] = field(default_factory=dict)
    expected_appearances: dict[RikId, int] = field(default_factory=dict)
    inferred_absences: dict[RikId, int] = field(default_factory=dict)
    absence_rating_adjustments: Ratings = field(default_factory=dict)
    initial_normalisation_adjustment: float = 0.0
    final_normalisation_adjustment: float = 0.0


@dataclass(frozen=True)
class SimulationResult:
    target_mean: float
    basho_ratings: dict[Date, BashoRatings] = field(default_factory=dict)
    final_registry: Ratings = field(default_factory=dict)
    rated_bout_count: int = 0
    ignored_fusen_count: int = 0
    inferred_absence_count: int = 0


def expect(rating_a: float, rating_b: float, q: float = DEFAULT_Q) -> float:
    """Return A's expected score against B."""
    if not math.isfinite(q) or q <= 0.0:
        raise ValueError(f"q must be a positive finite number, got {q}")
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / q))


def simulate(
    history: History,
    start_date: Date,
    initial_rating_policy: InitialRatingPolicy | None = None,
    k_policy: KPolicy | None = None,
    *,
    q: float = DEFAULT_Q,
    count_absences: bool = False,
) -> SimulationResult:
    """Simulate observed results and optional kyujo from ``start_date`` onward.

    A blank decision only means that the kimarite is unavailable; its W/L
    result is rated normally. With ``count_absences=False``, paired FS/FP and
    opponentless kyujo are ignored. With it enabled, FS/FP is rated against the
    recorded opponent and inferred opponentless kyujo costs ``k / 2``.
    """
    if not math.isfinite(q) or q <= 0.0:
        raise ValueError(f"q must be a positive finite number, got {q}")
    if initial_rating_policy is None:
        initial_rating_policy = ConstantInitialRatingPolicy()
    if k_policy is None:
        k_policy = FideKPolicy.load()

    registry: Ratings = {}
    basho_ratings: dict[Date, BashoRatings] = {}
    target_mean: float | None = None
    rated_bout_count = 0
    ignored_fusen_count = 0
    inferred_absence_count = 0

    start_key = _date_key(start_date)
    dates = sorted(
        (date for date in history if _date_key(date) >= start_key),
        key=_date_key,
    )
    for date in dates:
        basho = history[date]
        recorded_appearances, daily_appearances = _appearance_counts(basho.summary)
        complete_divisions = _represented_divisions(
            basho.banzuke.rikchii,
            basho.summary,
        )
        can_infer_absences = count_absences and Day(15) in basho.summary
        participants = _bout_participants(basho.summary)
        if can_infer_absences:
            participants.update(
                rikid
                for rikid, chii in basho.banzuke.rikchii.items()
                if _division(chii) in complete_divisions
            )

        for rikid in sorted(participants):
            if rikid not in registry:
                chii = basho.banzuke.rikchii.get(rikid)
                registry[rikid] = float(initial_rating_policy.rating_for(chii))

        initial_before = {
            rikid: registry[rikid]
            for rikid in sorted(participants)
        }

        if target_mean is None and initial_before:
            target_mean = _mean(initial_before)

        initial_adjustment = 0.0
        if initial_before and target_mean is not None:
            initial_adjustment = _normalise_registry_subset(
                registry,
                participants,
                target_mean,
            )

        initial_after = {
            rikid: registry[rikid]
            for rikid in sorted(participants)
        }

        inferred_absences = {rikid: 0 for rikid in participants}
        absence_adjustments = {rikid: 0.0 for rikid in participants}
        for day in sorted(basho.summary.keys()):
            daily_results = basho.summary[day]
            for bout in daily_results.results_lookup.values():
                if bout.decision == "fusen" and not count_absences:
                    ignored_fusen_count += 1
                    continue

                _apply_bout(
                    registry=registry,
                    bout=bout,
                    date=date,
                    rikchii=basho.banzuke.rikchii,
                    k_policy=k_policy,
                    q=q,
                )
                rated_bout_count += 1

            if can_infer_absences:
                for rikid, chii in basho.banzuke.rikchii.items():
                    if not _is_sekitori(chii):
                        continue
                    if _division(chii) not in complete_divisions:
                        continue
                    if rikid in daily_appearances.get(day, set()):
                        continue
                    adjustment = _apply_inferred_absence(
                        registry=registry,
                        rikid=rikid,
                        chii=chii,
                        k_policy=k_policy,
                    )
                    inferred_absences[rikid] += 1
                    absence_adjustments[rikid] += adjustment
                    inferred_absence_count += 1

        if can_infer_absences:
            for rikid, chii in basho.banzuke.rikchii.items():
                if _is_sekitori(chii):
                    continue
                if _division(chii) not in complete_divisions:
                    continue
                missing = max(0, 7 - recorded_appearances.get(rikid, 0))
                if not missing:
                    continue
                adjustment = _apply_inferred_absence(
                    registry=registry,
                    rikid=rikid,
                    chii=chii,
                    k_policy=k_policy,
                    count=missing,
                )
                inferred_absences[rikid] += missing
                absence_adjustments[rikid] += adjustment
                inferred_absence_count += missing

        final_adjustment = 0.0
        if participants and target_mean is not None:
            final_adjustment = _normalise_registry_subset(
                registry,
                participants,
                target_mean,
            )

        final_ratings = {
            rikid: registry[rikid]
            for rikid in sorted(participants)
        }
        basho_ratings[date] = BashoRatings(
            initial_before_normalisation=initial_before,
            initial_after_normalisation=initial_after,
            final_ratings=final_ratings,
            recorded_appearances={
                rikid: recorded_appearances.get(rikid, 0)
                for rikid in sorted(participants)
            },
            expected_appearances={
                rikid: _expected_appearances(
                    basho.banzuke.rikchii.get(rikid),
                    complete_divisions,
                    can_infer_absences,
                )
                for rikid in sorted(participants)
            },
            inferred_absences={
                rikid: inferred_absences.get(rikid, 0)
                for rikid in sorted(participants)
            },
            absence_rating_adjustments={
                rikid: absence_adjustments.get(rikid, 0.0)
                for rikid in sorted(participants)
            },
            initial_normalisation_adjustment=initial_adjustment,
            final_normalisation_adjustment=final_adjustment,
        )

    if target_mean is None:
        raise ValueError(
            f"No bout participants found on or after {start_date}"
        )

    return SimulationResult(
        target_mean=target_mean,
        basho_ratings=basho_ratings,
        final_registry=registry.copy(),
        rated_bout_count=rated_bout_count,
        ignored_fusen_count=ignored_fusen_count,
        inferred_absence_count=inferred_absence_count,
    )


def _bout_participants(summary) -> set[RikId]:
    participants: set[RikId] = set()
    for daily_results in summary.values():
        for bout in daily_results.results_lookup.values():
            participants.add(bout.rikishi1)
            participants.add(bout.rikishi2)
    return participants


def _appearance_counts(summary) -> tuple[dict[RikId, int], dict[Day, set[RikId]]]:
    totals: dict[RikId, int] = {}
    by_day: dict[Day, set[RikId]] = {}
    for day, daily_results in summary.items():
        appeared: set[RikId] = set()
        for bout in daily_results.results_lookup.values():
            appeared.add(bout.rikishi1)
            appeared.add(bout.rikishi2)
        by_day[day] = appeared
        for rikid in appeared:
            totals[rikid] = totals.get(rikid, 0) + 1
    return totals, by_day


def _represented_divisions(rikchii, summary) -> set[Division]:
    """Return divisions with at least one recorded internal bout."""
    represented: set[Division] = set()
    for daily_results in summary.values():
        for bout in daily_results.results_lookup.values():
            chii1 = rikchii.get(bout.rikishi1)
            chii2 = rikchii.get(bout.rikishi2)
            if chii1 is None or chii2 is None:
                continue
            division1 = _division(chii1)
            if division1 == _division(chii2):
                represented.add(division1)
    return represented


def _apply_bout(
    *,
    registry: Ratings,
    bout: BoutResult,
    date: Date,
    rikchii,
    k_policy: KPolicy,
    q: float,
) -> None:
    rikishi1 = bout.rikishi1
    rikishi2 = bout.rikishi2
    if rikishi1 not in registry or rikishi2 not in registry:
        raise RuntimeError(
            f"Uninitialised participant in {date}: {rikishi1} vs {rikishi2}"
        )

    rating1 = registry[rikishi1]
    rating2 = registry[rikishi2]
    expected1 = expect(rating1, rating2, q)
    actual1 = _score(bout.outcome1)
    actual2 = _score(bout.outcome2)

    chii1 = rikchii.get(rikishi1)
    chii2 = rikchii.get(rikishi2)
    k1 = float(k_policy.k_for(chii1))
    k2 = float(k_policy.k_for(chii2))
    _validate_k(k1, chii1)
    _validate_k(k2, chii2)

    registry[rikishi1] = rating1 + k1 * (actual1 - expected1)
    registry[rikishi2] = rating2 + k2 * (actual2 - (1.0 - expected1))


def _score(outcome: Outcome) -> float:
    if outcome in (Outcome.W, Outcome.FS):
        return 1.0
    if outcome in (Outcome.L, Outcome.FP):
        return 0.0
    if outcome == Outcome.DRAW:
        return 0.5
    raise ValueError(f"Unsupported bout outcome: {outcome}")


def _apply_inferred_absence(
    *,
    registry: Ratings,
    rikid: RikId,
    chii: Chii,
    k_policy: KPolicy,
    count: int = 1,
) -> float:
    k = float(k_policy.k_for(chii))
    _validate_k(k, chii)
    adjustment = -count * k / 2.0
    registry[rikid] += adjustment
    return adjustment


def _normalise_registry_subset(
    registry: Ratings,
    participants: set[RikId],
    target_mean: float,
) -> float:
    current_mean = sum(registry[rikid] for rikid in participants) / len(participants)
    adjustment = target_mean - current_mean
    for rikid in participants:
        registry[rikid] += adjustment
    return adjustment


def _mean(ratings: Ratings) -> float:
    return sum(ratings.values()) / len(ratings)


def _date_key(date: Date) -> tuple[int, int]:
    """Compare semantically equal Date subclasses by their numeric value."""
    return int(date.year), int(date.month)


def _division(chii: Chii) -> Division:
    if isinstance(chii.level, MSD):
        return Division.MAKUUCHI
    return chii.level


def _is_sekitori(chii: Chii) -> bool:
    return isinstance(chii.level, MSD) or chii.level == Division.JURYO


def _expected_appearances(
    chii: Chii | None,
    complete_divisions: set[Division],
    can_infer_absences: bool,
) -> int:
    if (
        chii is None
        or not can_infer_absences
        or _division(chii) not in complete_divisions
    ):
        return 0
    return 15 if _is_sekitori(chii) else 7


def _validate_k(k: float, chii) -> None:
    if not math.isfinite(k) or k < 0.0:
        raise ValueError(f"k must be a finite non-negative number for {chii}: {k}")

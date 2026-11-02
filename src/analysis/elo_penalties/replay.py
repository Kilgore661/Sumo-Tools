"""Paired whole-population replay for the Elo89a viability experiment."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Mapping

from src.analysis.prediction.bouts import RatedBout, select_rated_bouts
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .ledger import build_nonappearance_ledger
from .model import BashoAdjustment, ExperimentArm, ReplayEvidence, ReplayResult


Q = 400.0
MISSING_CHII_K = 35.0


def prepare_replay_evidence(
    history: History,
    dates: tuple[Date, ...],
    final_records,
) -> ReplayEvidence:
    """Prepare shared bout selection and non-appearance evidence once."""

    if not dates:
        raise ValueError("Elo89a replay requires at least one basho")
    selection = select_rated_bouts(
        history,
        start_date=dates[0],
        end_date=dates[-1],
    )
    bouts_by_date: dict[Date, list[RatedBout]] = defaultdict(list)
    for bout in selection.bouts:
        bouts_by_date[bout.contest.id.date].append(bout)
    return ReplayEvidence(
        dates=dates,
        rated_bouts_by_date={date: tuple(bouts_by_date[date]) for date in dates},
        non_appearances=build_nonappearance_ledger(
            history,
            dates,
            final_records,
        ),
        raw_result_count=selection.raw_result_count,
        rated_bout_count=selection.rated_bout_count,
        excluded_fusen_count=selection.excluded_fusen_count,
        excluded_draw_count=selection.excluded_draw_count,
    )


def replay(
    history: History,
    evidence: ReplayEvidence,
    priors: Mapping[Chii, float],
    divisional_k: Callable[[int], float],
    arm: ExperimentArm,
    *,
    base: float,
    q: float = Q,
) -> ReplayResult:
    """Replay one arm, varying only the Elo89a basho-end deduction."""

    ratings: dict[RikId, float] = {}
    previous_active: set[RikId] = set()
    target_mean: float | None = None
    starts: dict[Date, dict[RikId, float]] = {}
    ends: dict[Date, dict[RikId, float]] = {}
    adjustments: list[BashoAdjustment] = []

    for date in evidence.dates:
        basho = history[date]
        bouts = evidence.rated_bouts_by_date[date]
        active = set(basho.banzuke.riks)
        for bout in bouts:
            active.add(bout.contest.rikishi_a)
            active.add(bout.contest.rikishi_b)

        departing = previous_active - active
        for rikishi in departing:
            del ratings[rikishi]

        new_rikishi = active - set(ratings)
        for rikishi in sorted(new_rikishi):
            chii = basho.banzuke.rikchii.get(rikishi)
            ratings[rikishi] = base if chii is None else float(priors[chii])

        raw_start_mean = _mean(ratings, active)
        if target_mean is None:
            target_mean = raw_start_mean
        start_adjustment = _shift_to_target(ratings, active, target_mean)
        normalised_start_mean = _mean(ratings, active)
        starts[date] = _snapshot(ratings, active)

        for bout in bouts:
            _apply_bout(
                ratings,
                bout,
                basho.banzuke.rikchii,
                divisional_k,
                q,
            )

        counts = evidence.non_appearances[date]
        fusen_pai_count = sum(count.fusen_pai for count in counts.values())
        absence_count = sum(count.absences for count in counts.values())
        total_deducted_mass = 0.0
        if arm is ExperimentArm.ELO89A:
            for rikishi, count in counts.items():
                chii = basho.banzuke.rikchii.get(rikishi)
                deduction = count.total * _k(chii, divisional_k) / 2.0
                ratings[rikishi] -= deduction
                total_deducted_mass += deduction

        raw_end_mean = _mean(ratings, active)
        end_adjustment = _shift_to_target(ratings, active, target_mean)
        normalised_end_mean = _mean(ratings, active)
        ends[date] = _snapshot(ratings, active)
        adjustments.append(
            BashoAdjustment(
                arm=arm.value,
                date=str(date),
                active_count=len(active),
                new_rikishi_count=len(new_rikishi),
                departing_rikishi_count=len(departing),
                fusen_pai_count=fusen_pai_count,
                absence_count=absence_count,
                penalised_rikishi_count=(
                    len(counts) if arm is ExperimentArm.ELO89A else 0
                ),
                total_deducted_mass=total_deducted_mass,
                target_mean=target_mean,
                raw_start_mean=raw_start_mean,
                start_adjustment=start_adjustment,
                normalised_start_mean=normalised_start_mean,
                raw_end_mean=raw_end_mean,
                end_adjustment=end_adjustment,
                normalised_end_mean=normalised_end_mean,
            )
        )
        previous_active = active

    assert target_mean is not None
    return ReplayResult(
        arm=arm,
        target_mean=target_mean,
        basho_start_ratings=starts,
        basho_end_ratings=ends,
        adjustments=tuple(adjustments),
    )


def _apply_bout(
    ratings: dict[RikId, float],
    bout: RatedBout,
    chii_by_rikishi,
    divisional_k: Callable[[int], float],
    q: float,
) -> None:
    """Apply one production-eligible contested result."""

    a = bout.contest.rikishi_a
    b = bout.contest.rikishi_b
    rating_a = ratings[a]
    rating_b = ratings[b]
    expected_a = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / q))
    residual = float(bout.a_won) - expected_a
    ratings[a] += _k(chii_by_rikishi.get(a), divisional_k) * residual
    ratings[b] -= _k(chii_by_rikishi.get(b), divisional_k) * residual


def _k(chii: Chii | None, divisional_k: Callable[[int], float]) -> float:
    return MISSING_CHII_K if chii is None else float(divisional_k(chii.ordinal()))


def _shift_to_target(
    ratings: dict[RikId, float],
    active: set[RikId],
    target_mean: float,
) -> float:
    adjustment = target_mean - _mean(ratings, active)
    for rikishi in active:
        ratings[rikishi] += adjustment
    return adjustment


def _mean(ratings: Mapping[RikId, float], active: set[RikId]) -> float:
    return sum(ratings[rikishi] for rikishi in active) / len(active)


def _snapshot(
    ratings: Mapping[RikId, float],
    active: set[RikId],
) -> dict[RikId, float]:
    return {rikishi: ratings[rikishi] for rikishi in sorted(active)}

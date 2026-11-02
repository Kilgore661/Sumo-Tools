"""Fixed-point solver for the paired Elo89a viability experiment."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from src.analysis.equelo_bkp1.recenter import recenter
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .model import (
    ExperimentArm,
    FixedPointResult,
    IterationPrior,
    IterationRow,
    ReplayEvidence,
    ReplayResult,
)
from .replay import replay


def solve(
    history: History,
    evidence: ReplayEvidence,
    divisional_k: Callable[[int], float],
    arm: ExperimentArm,
    *,
    base: float,
    epsilon: float,
    max_iterations: int,
    progress: Callable[[IterationRow], None] | None = None,
) -> FixedPointResult:
    """Solve one arm from a constant chii-prior map."""

    domain = {
        chii
        for date in evidence.dates
        for chii in history[date].banzuke.rikchii.values()
    }
    support = _chii_support(history, evidence.dates)
    priors = {chii: float(base) for chii in domain}
    rows: list[IterationRow] = []
    retained_priors: list[IterationPrior] = []
    final_delta = 0.0
    converged = False

    for iteration in range(1, max_iterations + 1):
        current_replay = replay(
            history,
            evidence,
            priors,
            divisional_k,
            arm,
            base=base,
        )
        raw = aggregate_by_chii(history, evidence, current_replay)
        centred = recenter(raw, base=base, support=support)
        next_priors = centred.ratings
        max_chii = max(
            domain,
            key=lambda chii: abs(next_priors[chii] - priors[chii]),
        )
        final_delta = abs(next_priors[max_chii] - priors[max_chii])
        row = IterationRow(
            arm=arm.value,
            iteration=iteration,
            max_prior_change=final_delta,
            max_change_chii=str(max_chii),
            max_change_chii_ordinal=max_chii.ordinal(),
            max_change_observation_count=support[max_chii],
            mean_recentering_adjustment=centred.mean_adjustment,
            minimum_recentering_adjustment=centred.minimum_adjustment,
            maximum_recentering_adjustment=centred.maximum_adjustment,
        )
        rows.append(row)
        retained_priors.extend(
            IterationPrior(
                arm=arm.value,
                iteration=iteration,
                chii=str(chii),
                ordinal=chii.ordinal(),
                observations=support[chii],
                rating=next_priors[chii],
            )
            for chii in sorted(domain, key=lambda item: item.ordinal())
        )
        if progress is not None:
            progress(row)
        priors = next_priors
        if final_delta < epsilon:
            converged = True
            break

    final_replay = replay(
        history,
        evidence,
        priors,
        divisional_k,
        arm,
        base=base,
    )
    return FixedPointResult(
        arm=arm,
        priors=priors,
        support=support,
        converged=converged,
        iterations=len(rows),
        final_delta=final_delta,
        iteration_rows=tuple(rows),
        iteration_priors=tuple(retained_priors),
        replay=final_replay,
    )


def aggregate_by_chii(
    history: History,
    evidence: ReplayEvidence,
    result: ReplayResult,
) -> dict[Chii, float]:
    """Average normalised basho-start ratings at each observed chii."""

    totals: dict[Chii, float] = defaultdict(float)
    counts: dict[Chii, int] = defaultdict(int)
    for date in evidence.dates:
        ratings = result.basho_start_ratings[date]
        for rikishi, chii in history[date].banzuke.rikchii.items():
            totals[chii] += ratings[rikishi]
            counts[chii] += 1
    return {chii: totals[chii] / counts[chii] for chii in counts}


def _chii_support(
    history: History,
    dates: tuple[Date, ...],
) -> dict[Chii, int]:
    counts: dict[Chii, int] = defaultdict(int)
    for date in dates:
        for chii in history[date].banzuke.rikchii.values():
            counts[chii] += 1
    return dict(counts)

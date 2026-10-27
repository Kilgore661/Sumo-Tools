"""Fixed-point solver for the canonical q=400, alpha=1 BKP1 prior."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from .model import FixedPointResult, IterationRow, ReplayResult
from .params import KFn, MODEL_BASE
from .recenter import recenter
from .simulate import BoutEligibility, replay


def solve(
    history: History,
    divisional_k: KFn,
    *,
    epsilon: float = 10.0,
    max_iterations: int = 200,
    progress: Callable[[IterationRow], None] | None = None,
    eligibility: BoutEligibility = BoutEligibility.P1,
) -> FixedPointResult:
    priors, support = initial_prior_state(history)
    rows: list[IterationRow] = []
    final_delta = 0.0

    for iteration in range(1, max_iterations + 1):
        priors, row = iterate_once(
            history,
            priors,
            support,
            divisional_k,
            iteration=iteration,
            eligibility=eligibility,
        )
        final_delta = row.max_prior_change
        rows.append(row)
        if progress is not None:
            progress(row)
        if final_delta < epsilon:
            return FixedPointResult(
                priors=priors,
                support=support,
                converged=True,
                iterations=iteration,
                final_delta=final_delta,
                iteration_rows=tuple(rows),
            )
    return FixedPointResult(
        priors=priors,
        support=support,
        converged=False,
        iterations=max_iterations,
        final_delta=final_delta,
        iteration_rows=tuple(rows),
    )


def initial_prior_state(
    history: History,
) -> tuple[dict[Chii, float], dict[Chii, int]]:
    """Return the canonical starting map and literal-chii support."""

    domain = {
        chii
        for basho in history.values()
        for chii in basho.banzuke.rikchii.values()
    }
    if not domain:
        raise ValueError("Cannot initialise a fixed-point solve from empty History")
    support = _chii_support(history)
    return {chii: MODEL_BASE for chii in domain}, support


def iterate_once(
    history: History,
    priors: dict[Chii, float],
    support: dict[Chii, int],
    divisional_k: KFn,
    *,
    iteration: int,
    eligibility: BoutEligibility = BoutEligibility.P1,
) -> tuple[dict[Chii, float], IterationRow]:
    """Apply one canonical BKP1 fixed-point iteration."""

    if iteration < 1:
        raise ValueError("iteration must be positive")
    if set(priors) != set(support):
        raise ValueError("Prior and support domains differ")
    current_replay = replay(
        history,
        priors,
        divisional_k,
        eligibility=eligibility,
    )
    raw = aggregate_by_chii(history, current_replay)
    centred = recenter(raw, base=MODEL_BASE, support=support)
    next_priors = centred.ratings
    max_chii = max(
        priors,
        key=lambda chii: abs(next_priors[chii] - priors[chii]),
    )
    final_delta = abs(next_priors[max_chii] - priors[max_chii])
    return next_priors, IterationRow(
        iteration=iteration,
        max_prior_change=final_delta,
        max_change_chii=str(max_chii),
        max_change_observation_count=support[max_chii],
        mean_recentering_adjustment=centred.mean_adjustment,
        minimum_recentering_adjustment=centred.minimum_adjustment,
        maximum_recentering_adjustment=centred.maximum_adjustment,
    )


def aggregate_by_chii(history: History, result: ReplayResult) -> dict[Chii, float]:
    totals: dict[Chii, float] = defaultdict(float)
    counts: dict[Chii, int] = defaultdict(int)
    for date in sorted(history):
        for rikid, chii in history[date].banzuke.rikchii.items():
            totals[chii] += result.basho_start_ratings[date][rikid]
            counts[chii] += 1
    return {chii: totals[chii] / counts[chii] for chii in counts}


def _chii_support(history: History) -> dict[Chii, int]:
    counts: dict[Chii, int] = defaultdict(int)
    for basho in history.values():
        for chii in basho.banzuke.rikchii.values():
            counts[chii] += 1
    return dict(counts)

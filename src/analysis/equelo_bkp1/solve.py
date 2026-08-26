"""Fixed-point solver for the canonical q=400, alpha=1 BKP1 prior."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from .model import FixedPointResult, IterationRow, ReplayResult
from .params import KFn, MODEL_BASE
from .recenter import recenter
from .simulate import replay


def solve(
    history: History,
    divisional_k: KFn,
    *,
    epsilon: float = 10.0,
    max_iterations: int = 200,
    progress: Callable[[IterationRow], None] | None = None,
) -> FixedPointResult:
    domain = {chii for basho in history.values() for chii in basho.banzuke.rikchii.values()}
    support = _chii_support(history)
    priors = {chii: MODEL_BASE for chii in domain}
    rows: list[IterationRow] = []
    final_delta = 0.0

    for iteration in range(1, max_iterations + 1):
        current_replay = replay(history, priors, divisional_k)
        raw = aggregate_by_chii(history, current_replay)
        centred = recenter(raw, base=MODEL_BASE, support=support)
        next_priors = centred.ratings
        max_chii = max(domain, key=lambda chii: abs(next_priors[chii] - priors[chii]))
        final_delta = abs(next_priors[max_chii] - priors[max_chii])
        row = IterationRow(
            iteration=iteration,
            max_prior_change=final_delta,
            max_change_chii=str(max_chii),
            max_change_observation_count=support[max_chii],
            mean_recentering_adjustment=centred.mean_adjustment,
            minimum_recentering_adjustment=centred.minimum_adjustment,
            maximum_recentering_adjustment=centred.maximum_adjustment,
        )
        rows.append(row)
        if progress is not None:
            progress(row)
        priors = next_priors
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

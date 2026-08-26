"""Fixed-point solver shared by the two population policies."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from ..equelo.expt1.params import EloParams
from .model import FixedPointResult, IterationRow, PopulationPolicy, ReplayResult
from .recenter import recenter
from .simulate import replay


def solve(
    history: History,
    params: EloParams,
    policy: PopulationPolicy,
    *,
    base: float,
    epsilon: float = 1.0,
    max_iterations: int = 500,
    progress: Callable[[IterationRow], None] | None = None,
    variant: str | None = None,
    normalisation_alpha: float | None = None,
    recentering_alpha: float = 0.0,
) -> FixedPointResult:
    """Solve the Expt2 chii prior with only population policy varied."""

    domain = {chii for basho in history.values() for chii in basho.banzuke.rikchii.values()}
    support = _chii_support(history)
    resolved_variant = variant or policy.value
    priors = {chii: float(base) for chii in domain}
    rows: list[IterationRow] = []
    final_replay: ReplayResult | None = None
    final_delta = 0.0

    for iteration in range(1, max_iterations + 1):
        current_replay = replay(
            history,
            params,
            priors,
            policy,
            variant=resolved_variant,
            normalisation_support=support,
            normalisation_alpha=normalisation_alpha or 0.0,
        )
        raw, counts = aggregate_by_chii_with_counts(history, current_replay)
        centred = recenter(
            raw,
            base=base,
            support=counts,
            alpha=recentering_alpha,
        )
        next_priors = centred.ratings
        max_chii = max(domain, key=lambda chii: abs(next_priors[chii] - priors[chii]))
        final_delta = abs(next_priors[max_chii] - priors[max_chii])
        row = IterationRow(
                policy=resolved_variant,
                iteration=iteration,
                max_prior_change=final_delta,
                map_recentering_shift=centred.mean_adjustment,
                max_change_chii=str(max_chii),
                max_change_chii_ordinal=max_chii.ordinal(),
                max_change_observation_count=counts[max_chii],
                recentering_alpha=recentering_alpha,
                minimum_recentering_adjustment=centred.minimum_adjustment,
                maximum_recentering_adjustment=centred.maximum_adjustment,
                maximum_pairwise_difference_change=centred.maximum_pairwise_difference_change,
                rms_pairwise_difference_change=centred.rms_pairwise_difference_change,
        )
        rows.append(row)
        if progress is not None:
            progress(row)
        priors = next_priors
        if final_delta < epsilon:
            final_replay = replay(
                history,
                params,
                priors,
                policy,
                variant=resolved_variant,
                normalisation_support=support,
                normalisation_alpha=normalisation_alpha or 0.0,
            )
            return FixedPointResult(
                variant=resolved_variant,
                policy=policy,
                normalisation_alpha=normalisation_alpha,
                recentering_alpha=recentering_alpha,
                priors=priors,
                converged=True,
                iterations=iteration,
                final_delta=final_delta,
                iteration_rows=tuple(rows),
                replay=final_replay,
            )

    final_replay = replay(
        history,
        params,
        priors,
        policy,
        variant=resolved_variant,
        normalisation_support=support,
        normalisation_alpha=normalisation_alpha or 0.0,
    )
    return FixedPointResult(
        variant=resolved_variant,
        policy=policy,
        normalisation_alpha=normalisation_alpha,
        recentering_alpha=recentering_alpha,
        priors=priors,
        converged=False,
        iterations=max_iterations,
        final_delta=final_delta,
        iteration_rows=tuple(rows),
        replay=final_replay,
    )


def aggregate_by_chii(history: History, result: ReplayResult) -> dict[Chii, float]:
    means, _ = aggregate_by_chii_with_counts(history, result)
    return means


def aggregate_by_chii_with_counts(
    history: History, result: ReplayResult
) -> tuple[dict[Chii, float], dict[Chii, int]]:
    totals: dict[Chii, float] = defaultdict(float)
    counts: dict[Chii, int] = defaultdict(int)
    for date in sorted(history):
        ratings = result.basho_start_ratings[date]
        for rikid, chii in history[date].banzuke.rikchii.items():
            totals[chii] += ratings[rikid]
            counts[chii] += 1
    return (
        {chii: totals[chii] / counts[chii] for chii in counts},
        dict(counts),
    )


def _chii_support(history: History) -> dict[Chii, int]:
    counts: dict[Chii, int] = defaultdict(int)
    for basho in history.values():
        for chii in basho.banzuke.rikchii.values():
            counts[chii] += 1
    return dict(counts)

"""Fixed-point solver for the P2 divisional-average experiment."""

from __future__ import annotations

from collections import defaultdict
from statistics import fmean
from typing import Callable

from src.analysis.equelo_bkp1.params import KFn
from src.analysis.equelo.fixed_supported.policy import complete_initial_ratings
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .division import division_name
from .model import (
    DivisionIterationRow,
    FixedPointResult,
    IterationRow,
    ReplayResult,
)
from .recenter import recenter_by_division
from .replay import replay


Progress = Callable[[IterationRow, tuple[DivisionIterationRow, ...]], None]


def solve(
    history: History,
    divisional_k: KFn,
    *,
    p1: dict[Chii, float],
    targets: dict[str, float],
    epsilon: float = 10.0,
    max_iterations: int = 200,
    support_threshold: int = 60,
    progress: Progress | None = None,
) -> FixedPointResult:
    domain = {
        chii for basho in history.values() for chii in basho.banzuke.rikchii.values()
    }
    missing = domain - set(p1)
    extra = set(p1) - domain
    if missing or extra:
        raise ValueError(
            f"P1/history mismatch: {len(missing)} missing and {len(extra)} extra chii"
        )
    if support_threshold < 1:
        raise ValueError("support_threshold must be at least 1")
    support, initialization_support = chii_support(history)
    supported_chii = frozenset(
        chii for chii, count in support.items() if count >= support_threshold
    )
    missing_divisions = {
        division_name(chii) for chii in domain
    } - {division_name(chii) for chii in supported_chii}
    if missing_divisions:
        raise ValueError(
            "Support threshold leaves no supported chii in divisions: "
            + ", ".join(sorted(missing_divisions))
        )
    supported_priors = {
        chii: targets[division_name(chii)] for chii in supported_chii
    }
    priors, completion_sources = complete_priors(domain, supported_priors)
    iteration_rows: list[IterationRow] = []
    division_rows: list[DivisionIterationRow] = []
    prior_rows: list[dict[str, object]] = []
    final_delta = 0.0

    for iteration in range(1, max_iterations + 1):
        current_replay = replay(
            history,
            priors,
            divisional_k,
            targets,
            iteration=iteration,
        )
        raw = aggregate_by_chii(history, current_replay)
        supported_raw = {chii: raw[chii] for chii in supported_chii}
        recentered = recenter_by_division(
            supported_raw, targets=targets, support=support
        )
        next_priors, completion_sources = complete_priors(
            domain, recentered.ratings
        )
        max_chii = max(
            supported_chii,
            key=lambda chii: abs(next_priors[chii] - priors[chii]),
        )
        final_delta = abs(next_priors[max_chii] - priors[max_chii])
        row = IterationRow(
            iteration=iteration,
            max_prior_change=final_delta,
            max_change_chii=str(max_chii),
            max_change_observation_count=support[max_chii],
            mean_log_loss=current_replay.mean_log_loss,
            mean_brier_loss=current_replay.mean_brier_loss,
        )
        current_division_rows = tuple(
            _division_iteration_row(
                iteration,
                summary.division,
                summary.chii_count,
                summary.observation_count,
                summary.target_mean,
                summary.raw_mean,
                summary.centred_mean,
                summary.correction_mass,
                next_priors,
                p1,
            )
            for summary in recentered.divisions
        )
        iteration_rows.append(row)
        division_rows.extend(current_division_rows)
        prior_rows.extend(
            {
                "iteration": iteration,
                "division": division_name(chii),
                "chii": str(chii),
                "chii_ordinal": chii.ordinal(),
                "observations": support[chii],
                "initialization_observations": initialization_support[chii],
                "carried_observations": (
                    support[chii] - initialization_support[chii]
                ),
                "supported": chii in supported_chii,
                "completion_source_chii": str(completion_sources[chii]),
                "p1_rating": p1[chii],
                "previous_rating": priors[chii],
                "rating": next_priors[chii],
                "iteration_change": next_priors[chii] - priors[chii],
                "difference_from_p1": next_priors[chii] - p1[chii],
            }
            for chii in sorted(domain, key=lambda item: item.ordinal())
        )
        if progress is not None:
            progress(row, current_division_rows)
        priors = next_priors
        if final_delta < epsilon:
            final_replay = replay(
                history,
                priors,
                divisional_k,
                targets,
                iteration=iteration,
            )
            return FixedPointResult(
                priors=priors,
                support=support,
                initialization_support=initialization_support,
                completion_sources=completion_sources,
                supported_chii=supported_chii,
                support_threshold=support_threshold,
                targets=targets,
                converged=True,
                iterations=iteration,
                final_delta=final_delta,
                iteration_rows=tuple(iteration_rows),
                division_iteration_rows=tuple(division_rows),
                prior_iteration_rows=tuple(prior_rows),
                replay=final_replay,
            )

    final_replay = replay(
        history,
        priors,
        divisional_k,
        targets,
        iteration=max_iterations,
    )
    return FixedPointResult(
        priors=priors,
        support=support,
        initialization_support=initialization_support,
        completion_sources=completion_sources,
        supported_chii=supported_chii,
        support_threshold=support_threshold,
        targets=targets,
        converged=False,
        iterations=max_iterations,
        final_delta=final_delta,
        iteration_rows=tuple(iteration_rows),
        division_iteration_rows=tuple(division_rows),
        prior_iteration_rows=tuple(prior_rows),
        replay=final_replay,
    )


def aggregate_by_chii(history: History, result: ReplayResult) -> dict[Chii, float]:
    totals: dict[Chii, float] = defaultdict(float)
    counts: dict[Chii, int] = defaultdict(int)
    for date in sorted(history):
        for rikishi, chii in history[date].banzuke.rikchii.items():
            totals[chii] += result.basho_start_ratings[date][rikishi]
            counts[chii] += 1
    return {chii: totals[chii] / counts[chii] for chii in counts}


def _division_iteration_row(
    iteration: int,
    division: str,
    chii_count: int,
    observation_count: int,
    target_mean: float,
    raw_mean: float,
    centred_mean: float,
    correction_mass: float,
    priors: dict[Chii, float],
    p1: dict[Chii, float],
) -> DivisionIterationRow:
    differences = [
        priors[chii] - p1[chii]
        for chii in priors
        if division_name(chii) == division
    ]
    ratings = [
        rating for chii, rating in priors.items() if division_name(chii) == division
    ]
    return DivisionIterationRow(
        iteration=iteration,
        division=division,
        chii_count=chii_count,
        observation_count=observation_count,
        target_mean=target_mean,
        raw_map_mean=raw_mean,
        centred_map_mean=centred_mean,
        correction_mass=correction_mass,
        mean_prior_difference_from_p1=fmean(differences),
        mean_absolute_prior_difference_from_p1=fmean(abs(value) for value in differences),
        minimum_prior=min(ratings),
        maximum_prior=max(ratings),
    )


def chii_support(history: History) -> tuple[dict[Chii, int], dict[Chii, int]]:
    """Count all observations and those freshly initialised by the replay."""

    counts: dict[Chii, int] = defaultdict(int)
    initializations: dict[Chii, int] = defaultdict(int)
    previous_active = set()
    for date in sorted(history):
        basho = history[date]
        active = set(basho.banzuke.riks)
        for rikishi, chii in basho.banzuke.rikchii.items():
            counts[chii] += 1
            if rikishi not in previous_active:
                initializations[chii] += 1
        previous_active = active
    return dict(counts), {
        chii: initializations.get(chii, 0) for chii in counts
    }


def complete_priors(
    domain: set[Chii], supported_ratings: dict[Chii, float]
) -> tuple[dict[Chii, float], dict[Chii, Chii]]:
    """Complete unsupported chii from the nearest supported literal chii."""

    rows = complete_initial_ratings(
        required_chii=domain,
        source_ratings=supported_ratings,
    )
    return (
        {row.chii: row.initial_rating for row in rows},
        {row.chii: row.source_chii for row in rows},
    )

"""Fixed-point solver for weighted dual-boundary prior assignments."""

from __future__ import annotations

from collections import defaultdict
import time

from src.analysis.equelo.expt1.initialisation import EntrantContext
from src.analysis.equelo.expt1.params import EloParams
from src.analysis.equelo.expt1.simulate import SimulationMode, simulate
from src.analysis.equelo.fixed_boundary.model import PriorKey
from src.analysis.equelo.fixed_boundary.solver import (
    CombinedSolveResult,
    ContextualSolveResult,
    IterationRow,
    PriorRatings,
    emit_iteration_progress,
    normalise,
)

from .model import DualBoundaryWorld, assignment_rating


def solve_scoped(
    *,
    history,
    world,
    params: EloParams,
    base: float,
    epsilon: float,
    max_iter: int,
    progress: bool = False,
) -> CombinedSolveResult:
    primary = solve(
        stage="primary",
        history=history,
        world=world,
        params=params,
        base=base,
        epsilon=epsilon,
        max_iter=max_iter,
        initial_ratings=None,
        progress=progress,
    )
    refinement = solve(
        stage="refinement",
        history=history,
        world=world,
        params=params,
        base=base,
        epsilon=epsilon,
        max_iter=max_iter,
        initial_ratings=primary.ratings,
        progress=progress,
    )
    return CombinedSolveResult(modern=primary, combined=refinement)


def solve_modern_then_combined(
    *,
    history,
    world,
    params: EloParams,
    base: float,
    epsilon: float,
    max_iter: int,
    modern_start_year: int,
    modern_end_year: int,
    progress: bool = False,
) -> CombinedSolveResult:
    """Solve the modern period, then refine over the complete supplied history."""

    modern_history = _slice_history(
        history,
        start_year=modern_start_year,
        end_year=modern_end_year,
    )
    modern = solve(
        stage="modern",
        history=modern_history,
        world=world,
        params=params,
        base=base,
        epsilon=epsilon,
        max_iter=max_iter,
        initial_ratings=None,
        progress=progress,
    )
    combined_domain = _domain(history, world)
    initial = {
        key: modern.ratings.get(key, float(base))
        for key in combined_domain
    }
    combined = solve(
        stage="combined",
        history=history,
        world=world,
        params=params,
        base=base,
        epsilon=epsilon,
        max_iter=max_iter,
        initial_ratings=initial,
        progress=progress,
    )
    return CombinedSolveResult(modern=modern, combined=combined)


def solve(
    *,
    stage,
    history,
    world,
    params,
    base,
    epsilon,
    max_iter,
    initial_ratings,
    progress=False,
) -> ContextualSolveResult:
    domain = _domain(history, world)
    mu = (
        {key: float(base) for key in domain}
        if initial_ratings is None
        else dict(initial_ratings)
    )
    rows = []
    final_delta = 0.0
    solve_started_at = time.perf_counter()
    if progress:
        print(
            f"[{stage}] starting fixed point: "
            f"{len(history)} basho, {len(domain)} prior keys, epsilon={epsilon:g}",
            flush=True,
        )
    for iteration in range(1, max_iter + 1):
        iter_started_at = time.perf_counter()
        result = simulate_with_prior(
            history=history, world=world, params=params, ratings=mu
        )
        raw, counts = aggregate(
            history=history, world=world, result=result
        )
        mu_next, shift = normalise(raw, base=base)
        max_key = max(domain, key=lambda key: abs(mu_next[key] - mu[key]))
        final_delta = abs(mu_next[max_key] - mu[max_key])
        iter_seconds = time.perf_counter() - iter_started_at
        rows.append(IterationRow(
            stage=stage,
            iteration=iteration,
            delta=final_delta,
            shift=shift,
            max_delta_key=max_key,
            max_delta_value=mu_next[max_key],
            max_delta_count=counts[max_key],
        ))
        if progress:
            emit_iteration_progress(
                stage=stage,
                iteration=iteration,
                delta=final_delta,
                shift=shift,
                max_key=max_key,
                max_label=world.labels.get(max_key, str(max_key.value)),
                max_count=counts[max_key],
                iter_seconds=iter_seconds,
                elapsed_seconds=time.perf_counter() - solve_started_at,
            )
        if final_delta < epsilon:
            if progress:
                print(
                    f"[{stage}] converged after {iteration} iterations "
                    f"({time.perf_counter() - solve_started_at:.1f}s)",
                    flush=True,
                )
            return ContextualSolveResult(
                ratings=mu_next,
                converged=True,
                iterations=iteration,
                final_delta=final_delta,
                rows=tuple(rows),
            )
        mu = mu_next
    if progress:
        print(
            f"[{stage}] stopped at max_iter={max_iter}; "
            f"delta={final_delta:.6f} "
            f"({time.perf_counter() - solve_started_at:.1f}s)",
            flush=True,
        )
    return ContextualSolveResult(
        ratings=mu,
        converged=False,
        iterations=max_iter,
        final_delta=final_delta,
        rows=tuple(rows),
    )


def simulate_with_prior(*, history, world, params, ratings):
    def initialise(context: EntrantContext) -> float:
        assignment = world.assignments_by_date_rikishi[context.date][context.rikid]
        return assignment_rating(assignment, ratings)

    return simulate(
        history=history,
        params=params,
        entrant_initialiser=initialise,
        mode=SimulationMode.CLOSED,
    )


def aggregate(*, history, world, result):
    totals: dict[PriorKey, float] = defaultdict(float)
    counts: dict[PriorKey, float] = defaultdict(float)
    for date in sorted(history):
        ratings = result.basho_start_ratings[date]
        assignments = world.assignments_by_date_rikishi[date]
        for rikid in history[date].banzuke.riks:
            for item in assignments[rikid]:
                totals[item.key] += item.weight * ratings[rikid]
                counts[item.key] += item.weight
    return (
        {key: totals[key] / counts[key] for key in counts},
        dict(counts),
    )


def _domain(history, world) -> frozenset[PriorKey]:
    return frozenset(
        item.key
        for date in history
        for rikid in history[date].banzuke.riks
        for item in world.assignments_by_date_rikishi[date][rikid]
    )


def _slice_history(history, *, start_year: int, end_year: int):
    return type(history)({
        date: history[date]
        for date in sorted(history)
        if start_year <= date.year <= end_year
    })

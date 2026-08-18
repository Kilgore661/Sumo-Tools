"""Fixed-point solver over contextual entrant-prior keys."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import time

from src.analysis.equelo.expt1.initialisation import EntrantContext
from src.analysis.equelo.expt1.params import EloParams
from src.analysis.equelo.expt1.simulate import SimulationMode, SimulationResult, simulate
from src.sumo_core.History import History

from .model import PriorKey, PriorWorld, key_sort_value


PriorRatings = dict[PriorKey, float]


@dataclass(frozen=True)
class IterationRow:
    stage: str
    iteration: int
    delta: float
    shift: float
    max_delta_key: PriorKey
    max_delta_value: float
    max_delta_count: int | float


@dataclass(frozen=True)
class ContextualSolveResult:
    ratings: PriorRatings
    converged: bool
    iterations: int
    final_delta: float
    rows: tuple[IterationRow, ...]


@dataclass(frozen=True)
class CombinedSolveResult:
    modern: ContextualSolveResult
    combined: ContextualSolveResult


@dataclass(frozen=True)
class CompletedPriorRating:
    key: PriorKey
    initial_rating: float
    source_key: PriorKey
    source_kind: str


def solve_modern_then_combined(
    *,
    history: History,
    world: PriorWorld,
    params: EloParams,
    base: float,
    epsilon: float,
    max_iter: int,
    modern_start_year: int,
    modern_end_year: int,
    progress: bool = False,
) -> CombinedSolveResult:
    """Run the production-shaped modern solve followed by full refinement."""

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
        key: modern.ratings[key] if key in modern.ratings else float(base)
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
    stage: str,
    history: History,
    world: PriorWorld,
    params: EloParams,
    base: float,
    epsilon: float,
    max_iter: int,
    initial_ratings: PriorRatings | None,
    progress: bool = False,
) -> ContextualSolveResult:
    """Find a self-consistent basho-start mean for every represented key."""

    domain = _domain(history, world)
    mu = (
        {key: float(base) for key in domain}
        if initial_ratings is None
        else dict(initial_ratings)
    )
    rows: list[IterationRow] = []
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
            history=history,
            world=world,
            params=params,
            ratings=mu,
        )
        raw, counts = aggregate_by_prior_key(
            history=history,
            world=world,
            result=result,
        )
        mu_next, shift = normalise(raw, base=base)
        max_key = max(
            domain,
            key=lambda key: abs(mu_next[key] - mu[key]),
        )
        final_delta = abs(mu_next[max_key] - mu[max_key])
        iter_seconds = time.perf_counter() - iter_started_at
        rows.append(
            IterationRow(
                stage=stage,
                iteration=iteration,
                delta=final_delta,
                shift=shift,
                max_delta_key=max_key,
                max_delta_value=mu_next[max_key],
                max_delta_count=counts[max_key],
            )
        )
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


def emit_iteration_progress(
    *,
    stage: str,
    iteration: int,
    delta: float,
    shift: float,
    max_key: PriorKey,
    max_label: str,
    max_count: int | float,
    iter_seconds: float,
    elapsed_seconds: float,
) -> None:
    """Echo one flush-safe fixed-point progress row in the Expt2 style."""

    print(
        f"[{stage}] iter={iteration:>3}  delta={delta:>10.6f}  "
        f"shift={shift:>+10.6f}  max={max_label} "
        f"({max_key.kind}, n={float(max_count):.1f})  "
        f"iter={iter_seconds:.2f}s  elapsed={elapsed_seconds:.1f}s",
        flush=True,
    )


def simulate_with_prior(
    *,
    history: History,
    world: PriorWorld,
    params: EloParams,
    ratings: PriorRatings,
) -> SimulationResult:
    """Run Equelo with entrant ratings resolved from contextual prior keys."""

    def initialise(context: EntrantContext) -> float:
        key = world.key_by_date_rikishi[context.date][context.rikid]
        return float(ratings[key])

    return simulate(
        history=history,
        params=params,
        entrant_initialiser=initialise,
        mode=SimulationMode.CLOSED,
    )


def aggregate_by_prior_key(
    *,
    history: History,
    world: PriorWorld,
    result: SimulationResult,
) -> tuple[PriorRatings, dict[PriorKey, int]]:
    """Aggregate basho-start ratings by their preassigned contextual keys."""

    totals: dict[PriorKey, float] = defaultdict(float)
    counts: dict[PriorKey, int] = defaultdict(int)
    for date in sorted(history):
        ratings = result.basho_start_ratings[date]
        keys = world.key_by_date_rikishi[date]
        for rikid in history[date].banzuke.riks:
            key = keys[rikid]
            totals[key] += ratings[rikid]
            counts[key] += 1
    means = {key: totals[key] / counts[key] for key in counts}
    return means, dict(counts)


def normalise(ratings: PriorRatings, *, base: float) -> tuple[PriorRatings, float]:
    """Apply the production-equivalent unweighted common map shift."""

    current_mean = sum(ratings.values()) / len(ratings)
    shift = float(base) - current_mean
    return ({key: rating + shift for key, rating in ratings.items()}, shift)


def complete_prior_ratings(
    *,
    required_keys: frozenset[PriorKey],
    source_ratings: PriorRatings,
) -> tuple[CompletedPriorRating, ...]:
    """Complete unsupported keys from the nearest supported key of the same kind."""

    supported_by_kind: dict[str, list[PriorKey]] = defaultdict(list)
    for key in source_ratings:
        supported_by_kind[key.kind].append(key)
    for keys in supported_by_kind.values():
        keys.sort(key=key_sort_value)

    completed = []
    for key in sorted(required_keys, key=key_sort_value):
        if key in source_ratings:
            source = key
            source_kind = "direct"
        else:
            candidates = supported_by_kind[key.kind]
            source = min(candidates, key=lambda item: (abs(item.value - key.value), item.value))
            source_kind = "nearest_supported"
        completed.append(
            CompletedPriorRating(
                key=key,
                initial_rating=float(source_ratings[source]),
                source_key=source,
                source_kind=source_kind,
            )
        )
    return tuple(completed)


def completed_rating_map(rows: tuple[CompletedPriorRating, ...]) -> PriorRatings:
    return {row.key: row.initial_rating for row in rows}


def _domain(history: History, world: PriorWorld) -> frozenset[PriorKey]:
    return frozenset(
        world.key_by_date_rikishi[date][rikid]
        for date in history
        for rikid in history[date].banzuke.riks
    )


def _slice_history(history: History, *, start_year: int, end_year: int) -> History:
    sliced = History()
    for date in sorted(history):
        if start_year <= date.year <= end_year:
            sliced[date] = history[date]
    return sliced

from pdb import set_trace

import time
from collections import defaultdict
from pathlib import Path

from ....sumo_core.Chii import Chii
from ....sumo_core.History import History

from ..config_main import EQUELO_RATINGS, INITIAL_ELO, OUTPUT_ROOT
from ..expt1.initialisation import EntrantInitialiser
from ..expt1.params import EloParams
from ..expt1.simulate import SimulationMode, SimulationResult, simulate
from .aggregate import aggregate
from .diagnostics import IterationDiagnosticsWriter, default_probe_set, probe_values
from .normalise import normalise
from .output import write_final_ratings_csv, write_final_ratings_stats_csv
from .types import (
    BashoStartRatingsByChii,
    ChiiRatings,
    IterationDiagnosticsRow,
    IterationDiagnosticsSink,
    ProbeSet,
    SolveResult,
)


def initialise(base: float, chiis: set[Chii]) -> ChiiRatings:
    """Return the initial flat prior with value ``base`` on every chii in the solved domain."""
    return {chii: float(base) for chii in chiis}



def make_entrant_initialiser(mu: ChiiRatings) -> EntrantInitialiser:
    """Return the entrant-initialiser induced by the current chii-rating map."""

    def entrant_initialiser(chii) -> float:
        return mu[chii]

    return entrant_initialiser



def simulate_with_prior(
    history: History,
    params: EloParams,
    mu: ChiiRatings,
    mode: SimulationMode,
) -> SimulationResult:
    return simulate(
        history=history,
        params=params,
        entrant_initialiser=make_entrant_initialiser(mu),
        mode=mode,
        observer=None,
    )



def max_abs_difference(a: ChiiRatings, b: ChiiRatings) -> float:
    """Return the sup-norm distance between two chii-rating maps.

    Domains are assumed equal by contract.
    """
    if not a and not b:
        return 0.0
    return max(abs(a[chii] - b[chii]) for chii in a)



def _chii_domain(history: History) -> set[Chii]:
    return {chii for basho in history.values() for chii in basho.banzuke.rikchii.values()}



def _slice_history_years(history: History, start_year: int, end_year: int) -> History:
    sliced = History()
    for date in sorted(history.keys()):
        if start_year <= date.year <= end_year:
            sliced[date] = history[date]
    return sliced



def _extend_mu_to_history_domain(
    mu: ChiiRatings,
    history: History,
    base: float,
) -> ChiiRatings:
    """Extend ``mu`` to the full ``Chii`` domain of ``history`` using ``base`` for missing keys."""
    domain = _chii_domain(history)
    extended = dict(mu)
    for chii in domain:
        if chii not in extended:
            extended[chii] = float(base)
    return extended



def _print_total_runtime(label: str, started_at: float) -> None:
    total_seconds = time.perf_counter() - started_at
    print(f"[{label}] total time: {total_seconds:.3f}s")



def _stats_output_csv_path(output_csv_path: Path) -> Path:
    return output_csv_path.with_name(f"{output_csv_path.stem}_with_stats{output_csv_path.suffix}")



def _collect_basho_start_ratings_by_chii(
    history: History,
    results: SimulationResult,
) -> BashoStartRatingsByChii:
    ratings_by_chii: BashoStartRatingsByChii = defaultdict(list)

    for date in sorted(history.keys()):
        if date not in results.basho_start_ratings:
            continue

        basho_state = history[date]
        start_ratings = results.basho_start_ratings[date]

        for rikid, chii in basho_state.banzuke.rikchii.items():
            ratings_by_chii[chii].append(start_ratings[rikid])

    return {chii: values for chii, values in ratings_by_chii.items()}



def _final_analysis_basho_start_ratings_by_chii(
    history: History,
    params: EloParams,
    mu: ChiiRatings,
    mode: SimulationMode,
) -> BashoStartRatingsByChii:
    final_results = simulate_with_prior(history=history, params=params, mu=mu, mode=mode)
    return _collect_basho_start_ratings_by_chii(history, final_results)



def _write_outputs(
    history: History,
    mu: ChiiRatings,
    output_csv_path: Path,
    basho_start_ratings_by_chii: BashoStartRatingsByChii | None = None,
) -> tuple[Path, Path, int]:
    csv_path = write_final_ratings_csv(mu, output_csv_path)
    stats_csv_path, violation_count = write_final_ratings_stats_csv(
        mu=mu,
        history=history,
        output_path=_stats_output_csv_path(output_csv_path),
        basho_start_ratings_by_chii=basho_start_ratings_by_chii,
    )
    print(f"[ratings] total violations: {violation_count}")
    return csv_path, stats_csv_path, violation_count



def _with_modern_aliases(result: SolveResult) -> SolveResult:
    return SolveResult(
        mu=result.mu,
        converged=result.converged,
        iterations=result.iterations,
        final_delta=result.final_delta,
        output_csv_path=result.output_csv_path,
        stats_csv_path=result.stats_csv_path,
        diagnostics_path=result.diagnostics_path,
        modern_output_csv_path=result.output_csv_path,
        modern_stats_csv_path=result.stats_csv_path,
        modern_diagnostics_path=result.diagnostics_path,
    )



def solve(
    history: History,
    params: EloParams,
    base: float,
    epsilon: float,
    max_iter: int,
    mode: SimulationMode,
    probes: ProbeSet,
    output_csv_path,
    diagnostics: IterationDiagnosticsSink | None = None,
    include_ci_stats: bool = False,
) -> SolveResult:
    """Estimate a self-consistent basho-start prior by fixed-point iteration."""
    loop_started_at = time.perf_counter()
    chiis = _chii_domain(history)
    mu = initialise(base, chiis)
    diagnostics_path = None
    final_delta = 0.0

    for iteration in range(1, max_iter + 1):
        iter_started_at = time.perf_counter()
        results = simulate_with_prior(history=history, params=params, mu=mu, mode=mode)
        raw = aggregate(history, results)
        norm = normalise(raw.mean_by_chii, base)
        mu_next = norm.mu
        final_delta = max_abs_difference(mu_next, mu)
        iter_seconds = time.perf_counter() - iter_started_at

        if diagnostics is not None:
            pv, pc = probe_values(mu_next, raw.count_by_chii, probes)
            diagnostics.record(
                IterationDiagnosticsRow(
                    iteration=iteration,
                    delta=final_delta,
                    shift=norm.shift,
                    iter_seconds=iter_seconds,
                    probe_values=pv,
                    probe_counts=pc,
                )
            )

        if final_delta < epsilon:
            basho_start_ratings_by_chii = None
            if include_ci_stats:
                basho_start_ratings_by_chii = _final_analysis_basho_start_ratings_by_chii(
                    history=history,
                    params=params,
                    mu=mu_next,
                    mode=mode,
                )
            csv_path, stats_csv_path, _ = _write_outputs(
                history,
                mu_next,
                output_csv_path,
                basho_start_ratings_by_chii=basho_start_ratings_by_chii,
            )
            if diagnostics is not None:
                diagnostics_path = diagnostics.finalise()
            _print_total_runtime("solve", loop_started_at)
            return SolveResult(
                mu=mu_next,
                converged=True,
                iterations=iteration,
                final_delta=final_delta,
                output_csv_path=csv_path,
                stats_csv_path=stats_csv_path,
                diagnostics_path=diagnostics_path,
            )

        mu = mu_next

    if diagnostics is not None:
        diagnostics_path = diagnostics.finalise()
    _print_total_runtime("solve", loop_started_at)
    return SolveResult(
        mu=mu,
        converged=False,
        iterations=max_iter,
        final_delta=final_delta,
        output_csv_path=None,
        stats_csv_path=None,
        diagnostics_path=diagnostics_path,
    )



def solve_variant_naive(
    history: History,
    params: EloParams,
    epsilon: float,
    max_iter: int,
    mode: SimulationMode = SimulationMode.CLOSED,
    probes: ProbeSet | None = None,
    output_csv_path=None,
    diagnostics: IterationDiagnosticsSink | None = None,
    base: float = INITIAL_ELO,
) -> SolveResult:
    if probes is None:
        probes = default_probe_set()
    if output_csv_path is None:
        output_csv_path = OUTPUT_ROOT / "expt2_variant_naive_final.csv"
    result = solve(
        history=history,
        params=params,
        base=base,
        epsilon=epsilon,
        max_iter=max_iter,
        mode=mode,
        probes=probes,
        output_csv_path=output_csv_path,
        diagnostics=diagnostics,
        include_ci_stats=True,
    )
    return _with_modern_aliases(result)



def solve_variant_modern(
    history: History,
    params: EloParams,
    epsilon: float,
    max_iter: int,
    modern_start_year: int = 1989,
    modern_end_year: int = 2026,
    mode: SimulationMode = SimulationMode.CLOSED,
    probes: ProbeSet | None = None,
    output_csv_path=None,
    diagnostics: IterationDiagnosticsSink | None = None,
    base: float = INITIAL_ELO,
) -> SolveResult:
    if probes is None:
        probes = default_probe_set()
    if output_csv_path is None:
        output_csv_path = OUTPUT_ROOT / "expt2_variant_modern_final.csv"

    modern_history = _slice_history_years(history, modern_start_year, modern_end_year)
    result = solve(
        history=modern_history,
        params=params,
        base=base,
        epsilon=epsilon,
        max_iter=max_iter,
        mode=mode,
        probes=probes,
        output_csv_path=output_csv_path,
        diagnostics=diagnostics,
        include_ci_stats=True,
    )
    return _with_modern_aliases(result)



def solve_variant_combined(
    history: History,
    params: EloParams,
    epsilon: float,
    max_iter: int,
    modern_start_year: int = 1989,
    modern_end_year: int = 2026,
    mode: SimulationMode = SimulationMode.CLOSED,
    probes: ProbeSet | None = None,
    output_csv_path=None,
    diagnostics: IterationDiagnosticsSink | None = None,
    base: float = INITIAL_ELO,
    modern_stem: str = "expt2_variant_modern",
    modern_metadata: dict[str, str] | None = None,
) -> SolveResult:
    if probes is None:
        probes = default_probe_set()
    if output_csv_path is None:
        output_csv_path = OUTPUT_ROOT / EQUELO_RATINGS

    modern_history = _slice_history_years(history, modern_start_year, modern_end_year)
    modern_diagnostics = IterationDiagnosticsWriter(
        probes=probes,
        stem=modern_stem,
        echo_to_console=True,
        metadata=modern_metadata,
    )
    modern_output_csv_path = output_csv_path.parent / f"{modern_stem}_final.csv"
    print(f"[combined] modern ({modern_start_year}–{modern_end_year})")
    modern_result = solve(
        history=modern_history,
        params=params,
        base=base,
        epsilon=epsilon,
        max_iter=max_iter,
        mode=mode,
        probes=probes,
        output_csv_path=modern_output_csv_path,
        diagnostics=modern_diagnostics,
        include_ci_stats=True,
    )

    if modern_result.stats_csv_path is not None:
        print(f"[combined] modern stats CSV: {modern_result.stats_csv_path}")

    refinement_mu = _extend_mu_to_history_domain(
        mu=modern_result.mu,
        history=history,
        base=base,
    )

    print("[combined] refinement (full history)")
    refinement_result = _solve_from_initial_mu(
        history=history,
        params=params,
        initial_mu=refinement_mu,
        base=base,
        epsilon=epsilon,
        max_iter=max_iter,
        mode=mode,
        probes=probes,
        output_csv_path=output_csv_path,
        diagnostics=diagnostics,
    )
    return SolveResult(
        mu=refinement_result.mu,
        converged=refinement_result.converged,
        iterations=refinement_result.iterations,
        final_delta=refinement_result.final_delta,
        output_csv_path=refinement_result.output_csv_path,
        stats_csv_path=refinement_result.stats_csv_path,
        diagnostics_path=refinement_result.diagnostics_path,
        modern_output_csv_path=modern_result.output_csv_path,
        modern_stats_csv_path=modern_result.stats_csv_path,
        modern_diagnostics_path=modern_result.diagnostics_path,
    )



def _solve_from_initial_mu(
    history: History,
    params: EloParams,
    initial_mu: ChiiRatings,
    base: float,
    epsilon: float,
    max_iter: int,
    mode: SimulationMode,
    probes: ProbeSet,
    output_csv_path,
    diagnostics: IterationDiagnosticsSink | None = None,
) -> SolveResult:
    loop_started_at = time.perf_counter()
    mu = dict(initial_mu)
    diagnostics_path = None
    final_delta = 0.0

    for iteration in range(1, max_iter + 1):
        iter_started_at = time.perf_counter()
        results = simulate_with_prior(history=history, params=params, mu=mu, mode=mode)
        raw = aggregate(history, results)
        norm = normalise(raw.mean_by_chii, base)
        mu_next = norm.mu
        final_delta = max_abs_difference(mu_next, mu)
        iter_seconds = time.perf_counter() - iter_started_at

        if diagnostics is not None:
            pv, pc = probe_values(mu_next, raw.count_by_chii, probes)
            diagnostics.record(
                IterationDiagnosticsRow(
                    iteration=iteration,
                    delta=final_delta,
                    shift=norm.shift,
                    iter_seconds=iter_seconds,
                    probe_values=pv,
                    probe_counts=pc,
                )
            )

        if final_delta < epsilon:
            write_final_ratings_csv(mu_next, output_csv_path)
            csv_path, stats_csv_path, _ = _write_outputs(history, mu_next, EQUELO_RATINGS)
            if diagnostics is not None:
                diagnostics_path = diagnostics.finalise()
                summary = diagnostics.summary_line() if hasattr(diagnostics, "summary_line") else None
                if summary is not None:
                    print(summary)
            _print_total_runtime("refine", loop_started_at)
            return SolveResult(
                mu=mu_next,
                converged=True,
                iterations=iteration,
                final_delta=final_delta,
                output_csv_path=csv_path,
                stats_csv_path=stats_csv_path,
                diagnostics_path=diagnostics_path,
            )

        mu = mu_next

    if diagnostics is not None:
        diagnostics_path = diagnostics.finalise()
        summary = diagnostics.summary_line() if hasattr(diagnostics, "summary_line") else None
        if summary is not None:
            print(summary)
    _print_total_runtime("refine", loop_started_at)
    return SolveResult(
        mu=mu,
        converged=False,
        iterations=max_iter,
        final_delta=final_delta,
        output_csv_path=None,
        stats_csv_path=None,
        diagnostics_path=diagnostics_path,
    )


# Backward-compatible aliases for any in-package callers not yet updated.
solve_variant_a = solve_variant_naive
solve_variant_b = solve_variant_combined

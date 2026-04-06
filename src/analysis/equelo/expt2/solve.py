import time

from ....sumo_core.History import History
from ....sumo_core.Chii import Chii

from ..config_main import INITIAL_ELO, OUTPUT_ROOT, EQUELO_RATINGS

from ..expt1.initialisation import EntrantInitialiser
from ..expt1.params import EloParams
from ..expt1.simulate import SimulationMode, SimulationResult, simulate

from .aggregate import aggregate
from .diagnostics import IterationDiagnosticsWriter, default_probe_set, probe_values
from .normalise import normalise
from .output import write_final_ratings_csv
from .types import (
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

    def entrant_initialiser(rikid, chii, date) -> float:
        del rikid, date
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
            csv_path = write_final_ratings_csv(mu_next, output_csv_path)
            if diagnostics is not None:
                diagnostics_path = diagnostics.finalise()
            _print_total_runtime("solve", loop_started_at)
            return SolveResult(
                mu=mu_next,
                converged=True,
                iterations=iteration,
                final_delta=final_delta,
                output_csv_path=csv_path,
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
        diagnostics_path=diagnostics_path,
    )



def solve_variant_a(
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
        output_csv_path = OUTPUT_ROOT / "expt2_variant_a_final.csv"
    return solve(
        history=history,
        params=params,
        base=base,
        epsilon=epsilon,
        max_iter=max_iter,
        mode=mode,
        probes=probes,
        output_csv_path=output_csv_path,
        diagnostics=diagnostics,
    )



def solve_variant_b(
    history: History,
    params: EloParams,
    epsilon: float,
    max_iter: int,
    calibration_start_year: int = 1989,
    calibration_end_year: int = 2026,
    mode: SimulationMode = SimulationMode.CLOSED,
    probes: ProbeSet | None = None,
    output_csv_path=None,
    diagnostics: IterationDiagnosticsSink | None = None,
    base: float = INITIAL_ELO,
) -> SolveResult:
    if probes is None:
        probes = default_probe_set()
    if output_csv_path is None:
        output_csv_path = OUTPUT_ROOT / EQUELO_RATINGS

    calibration_history = _slice_history_years(history, calibration_start_year, calibration_end_year)
    calibration_diagnostics = IterationDiagnosticsWriter(
        probes=probes,
        stem="expt2_variant_b_calibration",
        echo_to_console=True,
    )
    print(f"[variant B] calibration ({calibration_start_year}–{calibration_end_year})")
    calibration_mu_result = solve(
        history=calibration_history,
        params=params,
        base=base,
        epsilon=epsilon,
        max_iter=max_iter,
        mode=mode,
        probes=probes,
        output_csv_path=output_csv_path.parent / "_unused_variant_b_calibration.csv",
        diagnostics=calibration_diagnostics,
    )

    refinement_mu = _extend_mu_to_history_domain(
        mu=calibration_mu_result.mu,
        history=history,
        base=base,
    )

    print("[variant B] refinement (full history)")
    return _solve_from_initial_mu(
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
            csv_path = write_final_ratings_csv(mu_next, output_csv_path)
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
        diagnostics_path=diagnostics_path,
    )

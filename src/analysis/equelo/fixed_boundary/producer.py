"""Orchestrate the experimental M/J-boundary Equelo producer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.analysis.equelo.config_main import INITIAL_ELO
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import build_elo_params
from src.analysis.equelo.fixed_supported.build import oracle_collapse_mode
from src.analysis.equelo.fixed_supported.model import K_CONFIG, K_POLICY, Q
from src.analysis.equelo.fixed_supported.output import write_json
from src.infra.live_store.api import get_history
from src.sumo_core.History import History

from .history import build_supported_history
from .model import build_literal_prior_world, build_prior_world
from .output import (
    write_comparison_outputs,
    write_day_end_ratings,
    write_iteration_diagnostics,
    write_prior_map,
)
from .solver import (
    complete_prior_ratings,
    completed_rating_map,
    simulate_with_prior,
    solve_modern_then_combined,
)


OUTPUT_ROOT = Path("files/output/Equelo/fixed_boundary")


@dataclass(frozen=True)
class FixedBoundaryOutputs:
    run_directory: Path
    prior_map_csv: Path
    literal_control_prior_map_csv: Path
    iteration_diagnostics_csv: Path
    literal_control_diagnostics_csv: Path
    day_end_ratings_json: Path
    manifest_json: Path
    comparison_outputs: dict[str, Path]


def build_fixed_boundary(
    *,
    raw_history: History | None = None,
    output_root: Path = OUTPUT_ROOT,
    min_appearances: int = 60,
    epsilon: float = 1.0,
    max_iter: int = 10_000_000,
    start_year: int = 1989,
    end_year: int | None = None,
) -> FixedBoundaryOutputs:
    """Build post-1988 Equelo variants using contextual and literal priors."""

    source_history = get_history() if raw_history is None else raw_history
    scoped_history = _slice_history(
        source_history,
        start_year=start_year,
        end_year=end_year,
    )
    actual_end_year = max(date.year for date in scoped_history)
    run_directory = _create_run_directory(output_root)

    print(
        "[fixed-boundary] preparing Oracle history and prior keys "
        f"for {start_year}--{actual_end_year}"
    )
    oracle_history = make_oracle(
        scoped_history,
        collapse_mode=oracle_collapse_mode(),
    ).history
    world = build_prior_world(oracle_history)
    filtered = build_supported_history(
        oracle_history,
        world,
        min_appearances=min_appearances,
    )
    literal_world = build_literal_prior_world(oracle_history)
    literal_filtered = build_supported_history(
        oracle_history,
        literal_world,
        min_appearances=min_appearances,
    )
    params = build_elo_params(
        k_policy=K_POLICY,
        q=Q,
        config_path=K_CONFIG,
    )

    print("[fixed-boundary] solving boundary-index fixed point")
    solved = solve_modern_then_combined(
        history=filtered.history,
        world=world,
        params=params,
        base=INITIAL_ELO,
        epsilon=epsilon,
        max_iter=max_iter,
        modern_start_year=start_year,
        modern_end_year=actual_end_year,
    )
    if not solved.modern.converged or not solved.combined.converged:
        raise ValueError("Fixed-boundary solve did not converge")

    print("[fixed-boundary] solving like-for-like literal-chii control")
    literal_solved = solve_modern_then_combined(
        history=literal_filtered.history,
        world=literal_world,
        params=params,
        base=INITIAL_ELO,
        epsilon=epsilon,
        max_iter=max_iter,
        modern_start_year=start_year,
        modern_end_year=actual_end_year,
    )
    if not literal_solved.modern.converged or not literal_solved.combined.converged:
        raise ValueError("Literal-chii control solve did not converge")

    completed = complete_prior_ratings(
        required_keys=world.keys,
        source_ratings=solved.combined.ratings,
    )
    complete_map = completed_rating_map(completed)
    literal_completed = complete_prior_ratings(
        required_keys=literal_world.keys,
        source_ratings=literal_solved.combined.ratings,
    )
    literal_complete_map = completed_rating_map(literal_completed)

    print("[fixed-boundary] building process ratings")
    process_result = simulate_with_prior(
        history=oracle_history,
        world=world,
        params=params,
        ratings=complete_map,
    )

    prior_map_csv = write_prior_map(
        run_directory / "master_entrant_prior_map.csv",
        completed=completed,
        world=world,
    )
    literal_prior_map_csv = write_prior_map(
        run_directory / "literal_chii_control_prior_map.csv",
        completed=literal_completed,
        world=literal_world,
    )
    diagnostics_csv = write_iteration_diagnostics(
        run_directory / "fixed_point_iterations.csv",
        solved,
    )
    literal_diagnostics_csv = write_iteration_diagnostics(
        run_directory / "literal_chii_control_iterations.csv",
        literal_solved,
    )
    day_end_json = write_day_end_ratings(
        run_directory / "day_end_ratings.json",
        process_result.day_end_ratings,
    )
    comparison_outputs = write_comparison_outputs(
        output_root=run_directory,
        history=oracle_history,
        world=world,
        experimental=complete_map,
        literal_control=literal_complete_map,
        solve_result=solved,
        literal_solve_result=literal_solved,
    )
    manifest_path = run_directory / "manifest.json"
    write_json(
        manifest_path,
        {
            "kind": "fixed_boundary_equelo_experiment",
            "generated_at": datetime.now().astimezone().isoformat(),
            "history_scope": {
                "start_year": start_year,
                "end_year": actual_end_year,
                "scope_applied_before": [
                    "Oracle cleaning",
                    "prior-key assignment",
                    "support measurement",
                    "fixed-point solving",
                    "process ratings",
                    "chart aggregation",
                ],
            },
            "prior_contract": {
                "makuuchi": "negative position from bottom; bottommost is -1",
                "juryo": "position from top minus one; J1e is 0",
                "other_divisions": "annotation-free fixed-supported literal chii key",
                "coordinate_source": "Oracle banzuke before support filtering",
            },
            "policy": {
                "min_appearances": min_appearances,
                "completion": "nearest supported key of the same kind",
                "map_normalisation": "unweighted common shift to base",
                "base": INITIAL_ELO,
                "q": Q,
                "k_policy": K_POLICY,
                "k_config": str(K_CONFIG),
                "simulation_mode": "closed",
                "start_year": start_year,
                "end_year": actual_end_year,
                "epsilon": epsilon,
                "max_iter": max_iter,
            },
            "support": {
                "boundary": {
                    "required_key_count": len(world.keys),
                    "supported_key_count": len(filtered.supported_keys),
                    "retained_bouts": filtered.retained_bouts,
                    "ignored_bouts": filtered.ignored_bouts,
                },
                "literal_control": {
                    "required_key_count": len(literal_world.keys),
                    "supported_key_count": len(literal_filtered.supported_keys),
                    "retained_bouts": literal_filtered.retained_bouts,
                    "ignored_bouts": literal_filtered.ignored_bouts,
                },
            },
            "solve": {
                "boundary": {
                    "primary": {
                        "converged": solved.modern.converged,
                        "iterations": solved.modern.iterations,
                        "final_delta": solved.modern.final_delta,
                    },
                    "refinement": {
                        "converged": solved.combined.converged,
                        "iterations": solved.combined.iterations,
                        "final_delta": solved.combined.final_delta,
                    },
                },
                "literal_control": {
                    "primary": {
                        "converged": literal_solved.modern.converged,
                        "iterations": literal_solved.modern.iterations,
                        "final_delta": literal_solved.modern.final_delta,
                    },
                    "refinement": {
                        "converged": literal_solved.combined.converged,
                        "iterations": literal_solved.combined.iterations,
                        "final_delta": literal_solved.combined.final_delta,
                    },
                },
            },
            "outputs": {
                "prior_map_csv": str(prior_map_csv),
                "literal_control_prior_map_csv": str(literal_prior_map_csv),
                "iteration_diagnostics_csv": str(diagnostics_csv),
                "literal_control_diagnostics_csv": str(literal_diagnostics_csv),
                "day_end_ratings_json": str(day_end_json),
                **{name: str(path) for name, path in comparison_outputs.items()},
            },
        },
    )
    return FixedBoundaryOutputs(
        run_directory=run_directory,
        prior_map_csv=prior_map_csv,
        literal_control_prior_map_csv=literal_prior_map_csv,
        iteration_diagnostics_csv=diagnostics_csv,
        literal_control_diagnostics_csv=literal_diagnostics_csv,
        day_end_ratings_json=day_end_json,
        manifest_json=manifest_path,
        comparison_outputs=comparison_outputs,
    )


def _create_run_directory(root: Path) -> Path:
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    path = root / stamp
    path.mkdir(parents=True, exist_ok=False)
    return path


def _slice_history(
    history: History,
    *,
    start_year: int,
    end_year: int | None,
) -> History:
    if end_year is not None and end_year < start_year:
        raise ValueError(f"end_year {end_year} precedes start_year {start_year}")
    scoped = History()
    for date in sorted(history):
        if date.year < start_year:
            continue
        if end_year is not None and date.year > end_year:
            continue
        scoped[date] = history[date]
    if not scoped:
        suffix = "onward" if end_year is None else f"--{end_year}"
        raise ValueError(f"History contains no data in {start_year} {suffix}")
    return scoped

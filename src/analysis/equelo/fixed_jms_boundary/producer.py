"""Orchestrate the standalone Juryo--Makushita boundary experiment."""

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

from ..fixed_boundary.history import build_supported_history
from ..fixed_boundary.model import build_jms_prior_world, build_literal_prior_world
from ..fixed_boundary.output import (
    write_day_end_ratings,
    write_iteration_diagnostics,
    write_prior_map,
)
from ..fixed_boundary.solver import (
    complete_prior_ratings,
    completed_rating_map,
    simulate_with_prior,
    solve_modern_then_combined,
)
from .output import write_comparison_outputs


OUTPUT_ROOT = Path("files/output/Equelo/fixed_jms_boundary")


@dataclass(frozen=True)
class FixedJmsOutputs:
    run_directory: Path
    prior_map_csv: Path
    literal_control_prior_map_csv: Path
    day_end_ratings_json: Path
    manifest_json: Path
    comparison_outputs: dict[str, Path]


def build_fixed_jms_boundary(
    *,
    raw_history: History | None = None,
    output_root: Path = OUTPUT_ROOT,
    min_appearances: int = 60,
    epsilon: float = 1.0,
    max_iter: int = 10_000_000,
    start_year: int = 1989,
    end_year: int | None = None,
) -> FixedJmsOutputs:
    source = get_history() if raw_history is None else raw_history
    scoped = _slice_history(source, start_year=start_year, end_year=end_year)
    actual_end_year = max(date.year for date in scoped)
    run_directory = _create_run_directory(output_root)

    print(f"[fixed-jms] preparing Oracle history for {start_year}--{actual_end_year}")
    history = make_oracle(scoped, collapse_mode=oracle_collapse_mode()).history
    world = build_jms_prior_world(history)
    filtered = build_supported_history(
        history, world, min_appearances=min_appearances
    )
    literal_world = build_literal_prior_world(history)
    literal_filtered = build_supported_history(
        history, literal_world, min_appearances=min_appearances
    )
    params = build_elo_params(k_policy=K_POLICY, q=Q, config_path=K_CONFIG)

    print("[fixed-jms] solving J/Ms boundary fixed point")
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
    print("[fixed-jms] solving like-for-like literal-chii control")
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
    if not all((
        solved.modern.converged,
        solved.combined.converged,
        literal_solved.modern.converged,
        literal_solved.combined.converged,
    )):
        raise ValueError("J/Ms experiment did not converge")

    completed = complete_prior_ratings(
        required_keys=world.keys, source_ratings=solved.combined.ratings
    )
    complete_map = completed_rating_map(completed)
    literal_completed = complete_prior_ratings(
        required_keys=literal_world.keys,
        source_ratings=literal_solved.combined.ratings,
    )
    literal_map = completed_rating_map(literal_completed)

    print("[fixed-jms] building process ratings and outputs")
    process = simulate_with_prior(
        history=history, world=world, params=params, ratings=complete_map
    )
    prior_csv = write_prior_map(
        run_directory / "master_entrant_prior_map.csv",
        completed=completed,
        world=world,
    )
    literal_csv = write_prior_map(
        run_directory / "literal_chii_control_prior_map.csv",
        completed=literal_completed,
        world=literal_world,
    )
    write_iteration_diagnostics(
        run_directory / "fixed_point_iterations.csv", solved
    )
    write_iteration_diagnostics(
        run_directory / "literal_chii_control_iterations.csv", literal_solved
    )
    day_end_json = write_day_end_ratings(
        run_directory / "day_end_ratings.json", process.day_end_ratings
    )
    comparisons = write_comparison_outputs(
        output_root=run_directory,
        history=history,
        world=world,
        experimental=complete_map,
        literal_control=literal_map,
        solve_result=solved,
        literal_solve_result=literal_solved,
    )
    manifest = run_directory / "manifest.json"
    write_json(manifest, {
        "kind": "fixed_jms_boundary_equelo_experiment",
        "generated_at": datetime.now().astimezone().isoformat(),
        "history_scope": {"start_year": start_year, "end_year": actual_end_year},
        "prior_contract": {
            "juryo": "negative position from bottom; bottommost is -1",
            "makushita": "position from top minus one; Ms1e is 0",
            "other_divisions": "annotation-free literal chii",
            "coordinate_source": "Oracle banzuke before support filtering",
        },
        "policy": {
            "min_appearances": min_appearances,
            "epsilon": epsilon,
            "base": INITIAL_ELO,
            "q": Q,
            "k_policy": K_POLICY,
            "simulation_mode": "closed",
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
                "iterations": solved.modern.iterations,
                "final_delta": solved.modern.final_delta,
            },
            "literal_control": {
                "iterations": literal_solved.modern.iterations,
                "final_delta": literal_solved.modern.final_delta,
            },
        },
        "outputs": {
            "prior_map_csv": str(prior_csv),
            "literal_control_prior_map_csv": str(literal_csv),
            "day_end_ratings_json": str(day_end_json),
            **{name: str(path) for name, path in comparisons.items()},
        },
    })
    return FixedJmsOutputs(
        run_directory=run_directory,
        prior_map_csv=prior_csv,
        literal_control_prior_map_csv=literal_csv,
        day_end_ratings_json=day_end_json,
        manifest_json=manifest,
        comparison_outputs=comparisons,
    )


def _create_run_directory(root: Path) -> Path:
    path = root / datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    path.mkdir(parents=True, exist_ok=False)
    return path


def _slice_history(history: History, *, start_year: int, end_year: int | None) -> History:
    scoped = History()
    for date in sorted(history):
        if date.year >= start_year and (end_year is None or date.year <= end_year):
            scoped[date] = history[date]
    if not scoped:
        raise ValueError("Selected J/Ms history scope is empty")
    return scoped

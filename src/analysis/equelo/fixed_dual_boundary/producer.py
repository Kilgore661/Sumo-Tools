"""Produce the joint nearest-boundary Equelo experiment."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.analysis.equelo.config_main import INITIAL_ELO
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import build_elo_params
from src.analysis.equelo.fixed_boundary.history import build_supported_history as build_literal_history
from src.analysis.equelo.fixed_boundary.model import build_literal_prior_world
from src.analysis.equelo.fixed_boundary.output import (
    write_day_end_ratings,
    write_iteration_diagnostics,
    write_prior_map,
)
from src.analysis.equelo.fixed_boundary.solver import (
    complete_prior_ratings,
    completed_rating_map,
    simulate_with_prior as simulate_literal,
    solve_modern_then_combined as solve_literal_combined,
)
from src.analysis.equelo.fixed_supported.build import oracle_collapse_mode
from src.analysis.equelo.fixed_supported.model import K_CONFIG, K_POLICY, Q
from src.analysis.equelo.fixed_supported.output import write_json
from src.infra.live_store.api import get_history
from src.sumo_core.History import History

from .history import build_supported_history
from .model import build_dual_boundary_world
from .output import write_comparison_outputs
from .solver import (
    simulate_with_prior,
    solve_modern_then_combined as solve_dual_combined,
    solve_scoped,
)


OUTPUT_ROOT = Path("files/output/Equelo/fixed_dual_boundary")


@dataclass(frozen=True)
class FixedDualOutputs:
    run_directory: Path
    prior_map_csv: Path
    literal_control_prior_map_csv: Path
    day_end_ratings_json: Path
    manifest_json: Path
    comparison_outputs: dict[str, Path]


def build_fixed_dual_boundary(
    *,
    raw_history: History | None = None,
    output_root: Path = OUTPUT_ROOT,
    min_appearances: int = 60,
    epsilon: float = 1.0,
    max_iter: int = 10_000_000,
    start_year: int = 1989,
    end_year: int | None = None,
    juryo_weighting: str = "nearest",
    modern_start_year: int | None = None,
) -> FixedDualOutputs:
    source = get_history() if raw_history is None else raw_history
    scoped = _slice_history(source, start_year=start_year, end_year=end_year)
    actual_end_year = max(date.year for date in scoped)
    run_directory = _create_run_directory(output_root)
    print(f"[fixed-dual] preparing Oracle history for {start_year}--{actual_end_year}")
    history = make_oracle(scoped, collapse_mode=oracle_collapse_mode()).history

    world = build_dual_boundary_world(history, juryo_weighting=juryo_weighting)
    filtered = build_supported_history(
        history, world, min_appearances=min_appearances
    )
    literal_world = build_literal_prior_world(history)
    literal_filtered = build_literal_history(
        history, literal_world, min_appearances=min_appearances
    )
    params = build_elo_params(k_policy=K_POLICY, q=Q, config_path=K_CONFIG)

    effective_modern_start = start_year if modern_start_year is None else modern_start_year
    if effective_modern_start == start_year:
        print(f"[fixed-dual] solving joint {juryo_weighting}-weight fixed point")
        solved = solve_scoped(
            history=filtered.history,
            world=filtered.world,
            params=params,
            base=INITIAL_ELO,
            epsilon=epsilon,
            max_iter=max_iter,
            progress=True,
        )
    else:
        print(
            f"[fixed-dual] solving {effective_modern_start}--{actual_end_year} "
            f"then refining over {start_year}--{actual_end_year}"
        )
        solved = solve_dual_combined(
            history=filtered.history,
            world=filtered.world,
            params=params,
            base=INITIAL_ELO,
            epsilon=epsilon,
            max_iter=max_iter,
            modern_start_year=effective_modern_start,
            modern_end_year=actual_end_year,
            progress=True,
        )
    print("[fixed-dual] solving like-for-like literal-chii control")
    literal_solved = solve_literal_combined(
        history=literal_filtered.history,
        world=literal_world,
        params=params,
        base=INITIAL_ELO,
        epsilon=epsilon,
        max_iter=max_iter,
        modern_start_year=effective_modern_start,
        modern_end_year=actual_end_year,
        progress=True,
    )
    if not all((
        solved.modern.converged,
        solved.combined.converged,
        literal_solved.modern.converged,
        literal_solved.combined.converged,
    )):
        raise ValueError("Dual-boundary experiment did not converge")

    completed = complete_prior_ratings(
        required_keys=world.keys, source_ratings=solved.combined.ratings
    )
    joint_map = completed_rating_map(completed)
    literal_completed = complete_prior_ratings(
        required_keys=literal_world.keys,
        source_ratings=literal_solved.combined.ratings,
    )
    literal_map = completed_rating_map(literal_completed)

    print("[fixed-dual] building process ratings and outputs")
    process = simulate_with_prior(
        history=history, world=world, params=params, ratings=joint_map
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
    write_iteration_diagnostics(run_directory / "fixed_point_iterations.csv", solved)
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
        joint_ratings=joint_map,
        literal_ratings=literal_map,
        history_label=f"{start_year}--{actual_end_year}",
    )
    manifest = run_directory / "manifest.json"
    write_json(manifest, {
        "kind": "fixed_dual_boundary_equelo_experiment",
        "generated_at": datetime.now().astimezone().isoformat(),
        "history_scope": {"start_year": start_year, "end_year": actual_end_year},
        "solve_scope": {
            "modern_start_year": effective_modern_start,
            "combined_start_year": start_year,
        },
        "prior_contract": {
            "makuuchi": "M/J distance; bottommost Makuuchi is -1",
            "juryo": (
                "nearest boundary with an equal midpoint split"
                if juryo_weighting == "nearest"
                else "linear interpolation between the two boundaries"
            ),
            "makushita": "J/Ms distance; Ms1e is 0",
            "other_divisions": "annotation-free literal chii",
            "boundary_choice": "contemporaneous geometric distance only",
            "juryo_weighting": juryo_weighting,
        },
        "policy": {
            "min_appearances": min_appearances,
            "epsilon": epsilon,
            "base": INITIAL_ELO,
            "q": Q,
            "k_policy": K_POLICY,
            "simulation_mode": "closed",
            "unsupported_weighted_component": (
                "omit and renormalise supported weights during solve; "
                "nearest-supported completion in the full process map"
            ),
        },
        "support": {
            "joint_required_key_count": len(world.keys),
            "joint_supported_key_count": len(filtered.supported_keys),
            "joint_retained_bouts": filtered.retained_bouts,
            "joint_ignored_bouts": filtered.ignored_bouts,
        },
        "solve": {
            "joint": {
                "modern": {
                    "iterations": solved.modern.iterations,
                    "final_delta": solved.modern.final_delta,
                },
                "combined": {
                    "iterations": solved.combined.iterations,
                    "final_delta": solved.combined.final_delta,
                },
            },
            "literal_control": {
                "modern": {
                    "iterations": literal_solved.modern.iterations,
                    "final_delta": literal_solved.modern.final_delta,
                },
                "combined": {
                    "iterations": literal_solved.combined.iterations,
                    "final_delta": literal_solved.combined.final_delta,
                },
            },
        },
        "outputs": {
            "prior_map_csv": str(prior_csv),
            "literal_control_prior_map_csv": str(literal_csv),
            "day_end_ratings_json": str(day_end_json),
            **{name: str(path) for name, path in comparisons.items()},
        },
    })
    return FixedDualOutputs(
        run_directory=run_directory,
        prior_map_csv=prior_csv,
        literal_control_prior_map_csv=literal_csv,
        day_end_ratings_json=day_end_json,
        manifest_json=manifest,
        comparison_outputs=comparisons,
    )


def _slice_history(history: History, *, start_year: int, end_year: int | None) -> History:
    scoped = History()
    for date in sorted(history):
        if date.year >= start_year and (end_year is None or date.year <= end_year):
            scoped[date] = history[date]
    if not scoped:
        raise ValueError("Selected dual-boundary history scope is empty")
    return scoped


def _create_run_directory(root: Path) -> Path:
    path = root / datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    path.mkdir(parents=True, exist_ok=False)
    return path

"""Explicit fixed-supported generation workflow."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.probability.builder import load_ratings_csv
from src.infra.live_store.api import get_history
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .api import (
    master_chii_initial_rating_map_metadata_path,
    master_chii_initial_rating_map_path,
)
from .build import build_process_ratings
from .landmarks import build_typical_equelo_values
from .master_map import (
    rows_from_completed,
    write_master_chii_initial_rating_map,
    write_master_map_metadata,
)
from .model import OUTPUT_ROOT, SUPPORT_THRESHOLD
from .policy import complete_initial_ratings
from .solver import run_supported_solve
from .build import oracle_collapse_mode


@dataclass(frozen=True)
class RefreshOutputs:
    output_root: Path
    solver_run_dir: Path
    master_map_csv: Path
    master_map_metadata_json: Path
    process_outputs: dict[str, Path]
    landmarks_csv: Path | None
    supported_estimates_chart_html: Path | None


def refresh_fixed_supported(
    *,
    output_root: Path = OUTPUT_ROOT,
    min_appearances: int = SUPPORT_THRESHOLD,
    epsilon: float = 1.0,
    max_iter: int = 10000000,
    modern_start_year: int = 1989,
    modern_end_year: int = 2026,
    build_landmarks: bool = True,
) -> RefreshOutputs:
    """Run the explicit slow generation workflow."""

    raw_history = get_history()
    solver_outputs = run_supported_solve(
        raw_history=raw_history,
        min_appearances=min_appearances,
        epsilon=epsilon,
        max_iter=max_iter,
        modern_start_year=modern_start_year,
        modern_end_year=modern_end_year,
        output_root=output_root / "solver_runs",
    )
    if solver_outputs.combined_final_csv is None:
        raise ValueError("Fixed-supported solver did not write a combined final CSV")

    history = make_oracle(
        raw_history,
        collapse_mode=oracle_collapse_mode(),
    ).history
    completed = complete_initial_ratings(
        required_chii=required_chii_for_simulation(history),
        source_ratings=load_ratings_csv(solver_outputs.combined_final_csv),
    )
    rows = rows_from_completed(completed)
    master_map_csv = write_master_chii_initial_rating_map(
        master_chii_initial_rating_map_path(output_root),
        rows,
    )
    direct_count = sum(1 for row in completed if row.source_kind == "direct")
    nearest_supported_count = sum(
        1 for row in completed if row.source_kind == "nearest_supported"
    )
    master_map_metadata_json = write_master_map_metadata(
        master_chii_initial_rating_map_metadata_path(output_root),
        master_map_path=master_map_csv,
        source_csv=solver_outputs.combined_final_csv,
        direct_count=direct_count,
        nearest_supported_count=nearest_supported_count,
        required_chii_count=len(completed),
    )
    process_outputs = build_process_ratings(
        output_root=output_root,
        master_map_path=master_map_csv,
        raw_history=raw_history,
    )
    landmarks_csv = None
    if build_landmarks:
        landmarks_outputs = build_typical_equelo_values(
            output_dir=output_root / "landmarks",
            master_map_path=master_map_csv,
        )
        landmarks_csv = landmarks_outputs.site_landmarks_csv

    return RefreshOutputs(
        output_root=output_root,
        solver_run_dir=solver_outputs.run_dir,
        master_map_csv=master_map_csv,
        master_map_metadata_json=master_map_metadata_json,
        process_outputs=process_outputs,
        landmarks_csv=landmarks_csv,
        supported_estimates_chart_html=solver_outputs.supported_estimates_chart_html,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refresh fixed-supported Equelo production artifacts."
    )
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--min-appearances", type=int, default=SUPPORT_THRESHOLD)
    parser.add_argument("--epsilon", type=float, default=1.0)
    parser.add_argument("--max-iter", type=int, default=10000000)
    parser.add_argument("--modern-start-year", type=int, default=1989)
    parser.add_argument("--modern-end-year", type=int, default=2026)
    parser.add_argument(
        "--skip-landmarks",
        action="store_true",
        help="Refresh process artifacts but do not rebuild Typical Equelo Values.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outputs = refresh_fixed_supported(
        output_root=args.output_root,
        min_appearances=args.min_appearances,
        epsilon=args.epsilon,
        max_iter=args.max_iter,
        modern_start_year=args.modern_start_year,
        modern_end_year=args.modern_end_year,
        build_landmarks=not args.skip_landmarks,
    )
    print("fixed_supported refresh complete")
    print(f"Solver run: {outputs.solver_run_dir}")
    print(f"Master map: {outputs.master_map_csv}")
    print(f"Master map metadata: {outputs.master_map_metadata_json}")
    print(f"Day-end ratings: {outputs.process_outputs['day_end_ratings']}")
    if outputs.supported_estimates_chart_html is not None:
        print(f"Supported estimates chart: {outputs.supported_estimates_chart_html}")
    if outputs.landmarks_csv is not None:
        print(f"Typical Equelo Values: {outputs.landmarks_csv}")


def required_chii_for_simulation(history: History) -> set[Chii]:
    """Return every chii the process-rating simulation may encounter."""

    return {
        chii
        for basho in history.values()
        for chii in basho.banzuke.rikchii.values()
    }


if __name__ == "__main__":
    main()

"""CLI for the joint dual-boundary Equelo experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.persistence.annotated_serialiser import load_history_with_annotations

from .producer import OUTPUT_ROOT, build_fixed_dual_boundary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--min-appearances", type=int, default=60)
    parser.add_argument("--epsilon", type=float, default=1.0)
    parser.add_argument("--max-iter", type=int, default=10_000_000)
    parser.add_argument("--start-year", type=int, default=1989)
    parser.add_argument("--end-year", type=int)
    parser.add_argument("--modern-start-year", type=int)
    parser.add_argument(
        "--juryo-weighting",
        choices=("nearest", "linear"),
        default="nearest",
    )
    args = parser.parse_args()
    history = (
        None
        if args.history_zip is None
        else load_history_with_annotations(str(args.history_zip.with_suffix("")))
    )
    outputs = build_fixed_dual_boundary(
        raw_history=history,
        output_root=args.output_root,
        min_appearances=args.min_appearances,
        epsilon=args.epsilon,
        max_iter=args.max_iter,
        start_year=args.start_year,
        end_year=args.end_year,
        juryo_weighting=args.juryo_weighting,
        modern_start_year=args.modern_start_year,
    )
    print(f"Run directory: {outputs.run_directory}")
    print(f"Manifest: {outputs.manifest_json}")
    for name, path in outputs.comparison_outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()

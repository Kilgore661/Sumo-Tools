"""Command-line entry point for fixed_v2 Equelo artefacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from .build import build_fixed_v2, build_fixed_v2_comparison
from .model import BRIER_ALPHA, FP_SOURCE, OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build fixed_v2 Equelo rating-series artefacts."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Directory for fixed_v2 outputs.",
    )
    parser.add_argument(
        "--comparison-only",
        action="store_true",
        help="Only build the FP/Brier/sanitised comparison artefacts.",
    )
    parser.add_argument(
        "--with-comparison",
        action="store_true",
        help="Also build the FP/Brier/sanitised comparison artefacts.",
    )
    parser.add_argument(
        "--fp-source",
        type=Path,
        default=FP_SOURCE,
        help="Path to the Expt2 fixed-point CSV used for comparison artefacts.",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=BRIER_ALPHA,
        help="Legacy Brier contraction alpha used for the comparison column.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.comparison_only:
        outputs = build_fixed_v2(output_root=args.output_root)
        print(f"Wrote metadata: {outputs['metadata']}")
        print(f"Wrote day-end ratings: {outputs['day_end_ratings']}")
        print(f"Wrote entrant initial ratings: {outputs['entrant_initial_ratings']}")

    if args.comparison_only or args.with_comparison:
        comparison_outputs = build_fixed_v2_comparison(
            fp_source=args.fp_source,
            output_root=args.output_root,
            alpha=args.alpha,
        )
        print(f"Wrote comparison CSV: {comparison_outputs.comparison_csv}")
        print(f"Wrote sanitisation report: {comparison_outputs.sanitisation_report}")


if __name__ == "__main__":
    main()

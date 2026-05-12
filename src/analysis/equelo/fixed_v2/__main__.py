"""Command-line entry point for fixed_v2 Brierless Pivot experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

from .build import build_fixed_v2_comparison
from .model import BRIER_ALPHA, FP_SOURCE, OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build fixed_v2 FP/Brier/sanitised comparison artefacts."
    )
    parser.add_argument(
        "--fp-source",
        type=Path,
        default=FP_SOURCE,
        help="Path to the Expt2 fixed-point CSV."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Directory for fixed_v2 experiment outputs."
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=BRIER_ALPHA,
        help="Brier contraction alpha used for the comparison column."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = build_fixed_v2_comparison(
        fp_source=args.fp_source,
        output_root=args.output_root,
        alpha=args.alpha,
    )
    print(f"Wrote comparison CSV: {outputs.comparison_csv}")
    print(f"Wrote sanitisation report: {outputs.sanitisation_report}")


if __name__ == "__main__":
    main()

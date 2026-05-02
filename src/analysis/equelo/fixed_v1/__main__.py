"""CLI entry point for fixed v1 Equelo rating generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .build import build_fixed_v1
from .model import OUTPUT_ROOT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the fixed v1 Equelo rating artefacts."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Directory to receive metadata.json and day_end_ratings.json.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    written = build_fixed_v1(output_root=args.output_root)

    print("Fixed v1 Equelo ratings generated")
    print(f"Metadata: {written['metadata']}")
    print(f"Day-end ratings: {written['day_end_ratings']}")


if __name__ == "__main__":
    main()

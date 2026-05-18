"""CLI for the make_site2 public-site builder."""

from __future__ import annotations

import argparse
from pathlib import Path

from .builder import DEFAULT_OUTPUT_ROOT, build_brb_shell


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the make_site2 BRB-only static shell."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Output directory for the generated make_site2 site.",
    )
    args = parser.parse_args()
    build_brb_shell(args.output)


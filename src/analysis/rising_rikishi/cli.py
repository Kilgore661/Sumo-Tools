"""Command-line interface for the rising-rikishi producer."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.analysis.rising_rikishi.model import DEFAULT_WINDOWS
from src.analysis.rising_rikishi.producer import build_outputs
from src.analysis.rising_rikishi.writer import OUTPUT_ROOT
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Produce exploratory rising-rikishi Equelo delta CSVs."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Directory for rising-rikishi CSV outputs.",
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Load History from a zip-backed annotated serialisation.",
    )
    parser.add_argument(
        "--windows",
        nargs="+",
        type=int,
        default=DEFAULT_WINDOWS,
        help="Basho window sizes to produce.",
    )
    parser.add_argument(
        "--all-end-basho",
        action="store_true",
        help="Produce files for every possible end basho, not just the latest.",
    )
    return parser


def load_history(path: Path | None) -> History:
    """Load History from a zip-backed path or the live store."""

    if path is None:
        return get_history()
    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def main() -> int:
    """Run the rising-rikishi producer."""

    args = build_parser().parse_args()
    history = load_history(args.history_zip)
    outputs = build_outputs(
        history=history,
        windows=args.windows,
        output_root=args.output_root,
        all_end_basho=args.all_end_basho,
    )
    print("Wrote:")
    for path in outputs:
        print(f"  {path}")
    return 0

"""Command-line entry point for exploratory Equelo n-change tables."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.analysis.equelo.fixed_supported.api import load_day_end_ratings
from src.analysis.equelo.fixed_supported.model import OUTPUT_ROOT as FIXED_SUPPORTED_OUTPUT_ROOT
from src.analysis.equelo.rating_changes.core import (
    DEFAULT_WINDOWS,
    OUTPUT_ROOT,
    build_rating_change_outputs,
)
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(
        description="Produce exploratory fixed-supported Equelo n-change CSVs."
    )
    parser.add_argument(
        "--date",
        help="Target basho date as YYYY-MM or YYYY/MM. Defaults to the latest basho in History.",
    )
    parser.add_argument(
        "--windows",
        nargs="+",
        type=int,
        default=list(DEFAULT_WINDOWS),
        help="Basho windows to output. Default: 1 2 3 4 5 6 12.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Directory for rating-change output CSVs.",
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Use this zip-backed annotated History instead of the live store History.",
    )
    parser.add_argument(
        "--day-end-ratings-root",
        type=Path,
        help="Directory containing fixed-supported day_end_ratings.json.",
    )
    parser.add_argument(
        "--master-map",
        type=Path,
        help="Path to fixed-supported master_chii_initial_rating_map.csv.",
    )
    return parser


def load_history_from_zip(path: Path) -> History:
    """Load a History from a zip-backed annotated serialisation."""

    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def main() -> None:
    """Run the producer."""

    args = build_parser().parse_args()
    history = load_history_from_zip(args.history_zip) if args.history_zip else get_history()
    ratings = (
        load_day_end_ratings(output_root=args.day_end_ratings_root)
        if args.day_end_ratings_root
        else load_day_end_ratings()
    )
    shikona_store = FullShikonaStore.from_sources(history)
    outputs = build_rating_change_outputs(
        day_end_ratings=ratings,
        history=history,
        full_shikona_store=shikona_store,
        target_date_text=args.date,
        windows=tuple(args.windows),
        output_root=args.output_root,
        master_map_path=args.master_map,
        fixed_supported_output_root=args.day_end_ratings_root or FIXED_SUPPORTED_OUTPUT_ROOT,
    )
    print("Wrote:")
    for output in outputs:
        print(f"  {output}")


if __name__ == "__main__":
    main()

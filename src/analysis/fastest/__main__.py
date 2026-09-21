"""Command-line entry point for the first-rank-group milestone matrix."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date, History

from .milestone_matrix import DEFAULT_EPOCH, DEFAULT_OUTPUT_ROOT, produce_milestone_matrix


DEFAULT_HISTORY_DIRECTORY = Path("files/output/Historys")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Produce the all-rikishi first-rank-group milestone CSV."
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Use an explicit full annotated History zip instead of the live store.",
    )
    parser.add_argument(
        "--epoch",
        type=parse_date,
        default=DEFAULT_EPOCH,
        help=f"Supporting boundary banzuke in YYYY/MM format. Default: {DEFAULT_EPOCH}.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Output directory. Default: {DEFAULT_OUTPUT_ROOT}.",
    )
    return parser


def parse_date(value: str) -> Date:
    try:
        year_text, month_text = value.split("/")
        return Date(Year(int(year_text)), Month(int(month_text)))
    except Exception as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date {value!r}; expected YYYY/MM"
        ) from exc


def load_history(path: Path | None) -> tuple[History, str]:
    if path is not None:
        return _load_zip(path), str(path)
    try:
        return get_history(), "live_store"
    except SystemExit:
        candidates = tuple(DEFAULT_HISTORY_DIRECTORY.glob("1958_01 to *.zip"))
        if not candidates:
            raise FileNotFoundError(
                "The live store is unavailable and no full History zip was found in "
                f"{DEFAULT_HISTORY_DIRECTORY}"
            )
        fallback = max(candidates, key=lambda candidate: candidate.stat().st_mtime)
        print(f"Live store unavailable; using {fallback}")
        return _load_zip(fallback), str(fallback)


def _load_zip(path: Path) -> History:
    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def main() -> None:
    args = build_parser().parse_args()
    history, source = load_history(args.history_zip)
    outputs = produce_milestone_matrix(
        history,
        epoch=args.epoch,
        output_root=args.output_root,
    )
    print(f"History source: {source}")
    print(f"Source History range: {min(history)} to {max(history)}")
    print(f"Analysis range: {args.epoch} to {max(history)}")
    print(f"Matrix rows: {outputs.row_count:,}")
    print(f"Missing bios excluded: {outputs.missing_bio_count:,}")
    print(f"Matrix CSV: {outputs.matrix_csv}")
    print(f"Missing-bio audit: {outputs.missing_bios_csv}")
    print(f"Rankings JSON: {outputs.rankings_json}")


if __name__ == "__main__":
    main()

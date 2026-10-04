"""Run the JSA Check absence-window experiment."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from time import perf_counter

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History

from .analysis import analyse_absence_windows
from .model import JsaCheckRunMetadata
from .output import DEFAULT_OUTPUT_ROOT, format_summary, write_outputs
from .source import (
    DEFAULT_STANDINGS_ROOT,
    latest_retirement_csv,
    load_final_records,
    load_retirement_last_appearances,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Load an annotated History zip instead of the live store.",
    )
    parser.add_argument("--start", type=_parse_year_month, default=(1989, 1))
    parser.add_argument("--end", type=_parse_year_month)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--standings-root",
        type=Path,
        default=DEFAULT_STANDINGS_ROOT,
        help="Cached SumoDB banzuke pages containing independent final records.",
    )
    parser.add_argument(
        "--retirement-csv",
        type=Path,
        help=(
            "Rank-at-retirement rikishi artifact. Defaults to the artifact with "
            "the latest ending basho."
        ),
    )
    return parser


def main() -> None:
    started = perf_counter()
    args = build_parser().parse_args()
    history = load_history(args.history_zip)
    final_records = load_final_records(
        args.standings_root,
        start=args.start,
        end=args.end,
    )
    retirement_csv = args.retirement_csv or latest_retirement_csv()
    retirement_last_appearances = load_retirement_last_appearances(retirement_csv)
    result = analyse_absence_windows(
        history,
        final_records,
        retirement_last_appearances,
        start=args.start,
        end=args.end,
    )
    metadata = JsaCheckRunMetadata(
        generated_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        history_source=_history_source(args.history_zip),
        final_records_source=str(args.standings_root.resolve()),
        retirement_source=str(retirement_csv.resolve()),
    )
    outputs = write_outputs(
        result,
        metadata=metadata,
        output_root=args.output_root,
    )
    print(format_summary(result.summary, metadata), end="")
    print(f"CSV: {outputs.rows_csv}")
    print(f"Summary: {outputs.summary_txt}")
    print(f"Total wall-clock time: {perf_counter() - started:.2f} seconds")


def load_history(history_zip: Path | None) -> History:
    """Load the explicitly selected History source."""

    if history_zip is None:
        return get_history()
    resolved = history_zip.resolve()
    zip_path = resolved if resolved.suffix == ".zip" else resolved.with_suffix(".zip")
    if not zip_path.is_file():
        raise FileNotFoundError(f"History zip not found: {zip_path}")
    return load_history_with_annotations(str(zip_path.with_suffix("")))


def _history_source(history_zip: Path | None) -> str:
    if history_zip is None:
        return "live store"
    resolved = history_zip.resolve()
    zip_path = resolved if resolved.suffix == ".zip" else resolved.with_suffix(".zip")
    return str(zip_path)


def _parse_year_month(value: str) -> tuple[int, int]:
    try:
        year_text, month_text = value.split("/", maxsplit=1)
        year, month = int(year_text), int(month_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"Expected YYYY/MM, got {value!r}") from error
    if month not in (1, 3, 5, 7, 9, 11):
        raise argparse.ArgumentTypeError(f"Not a basho month: {value}")
    return year, month


if __name__ == "__main__":
    main()

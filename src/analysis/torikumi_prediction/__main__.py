"""Build empirical opponent-class distributions from canonical History."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from .analysis import analyse
from .output import DEFAULT_OUTPUT_ROOT, write_outputs


DEFAULT_HISTORY_ZIP = Path("files/output/Historys/1958_01 to 2026_11.zip")


def parse_date(value: str) -> Date:
    try:
        year_text, month_text = value.split("/", maxsplit=1)
        return Date(Year(int(year_text)), Month(int(month_text)))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(f"Expected a basho date YYYY/MM, got {value!r}") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, default=DEFAULT_HISTORY_ZIP)
    parser.add_argument("--start", type=parse_date)
    parser.add_argument("--end", type=parse_date)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    history_path = args.history_zip.resolve()
    if history_path.suffix.lower() != ".zip" or not history_path.is_file():
        raise FileNotFoundError(f"History zip not found: {history_path}")
    history = load_history_with_annotations(str(history_path.with_suffix("")))
    result = analyse(history, start=args.start, end=args.end)
    outputs = write_outputs(
        result,
        source={
            "kind": "history_zip",
            "path": str(history_path),
            "sha256": hashlib.sha256(history_path.read_bytes()).hexdigest(),
        },
        output_root=args.output_root,
    )
    print(
        f"Included {result.included_basho_count:,} completed basho "
        f"({result.included_first_basho} to {result.included_last_basho})."
    )
    print(f"Scheduled bouts: {result.scheduled_bout_count:,}")
    print(f"Directed observations: {len(result.observations):,}")
    print(f"Diagnostics: {len(result.diagnostics):,}")
    print(f"Output: {outputs.run_directory.resolve()}")


if __name__ == "__main__":
    main()

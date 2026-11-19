"""Run the greedy late-basho makuuchi torikumi experiment."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from .analysis import analyse_greedy
from .heya import DEFAULT_HEYA_INDEX, load_heya_index
from .output import DEFAULT_OUTPUT_ROOT, write_outputs


DEFAULT_HISTORY_ZIP = Path("files/output/Historys/1958_01 to 2026_11.zip")


def parse_date(value: str) -> Date:
    try:
        year_text, month_text = value.split("/", maxsplit=1)
        return Date(Year(int(year_text)), Month(int(month_text)))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(
            f"Expected a basho date YYYY/MM, got {value!r}"
        ) from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, default=DEFAULT_HISTORY_ZIP)
    parser.add_argument("--heya-index", type=Path, default=DEFAULT_HEYA_INDEX)
    parser.add_argument("--start", type=parse_date)
    parser.add_argument("--end", type=parse_date)
    parser.add_argument("--first-day", type=int, default=11)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    history_path = args.history_zip.resolve()
    heya_path = args.heya_index.resolve()
    if history_path.suffix.lower() != ".zip" or not history_path.is_file():
        raise FileNotFoundError(f"History zip not found: {history_path}")
    if not heya_path.is_file():
        raise FileNotFoundError(
            f"Heya index not found: {heya_path}; run the heya compiler first"
        )

    history = load_history_with_annotations(str(history_path.with_suffix("")))
    heya_index = load_heya_index(heya_path)
    result = analyse_greedy(
        history,
        heya_index,
        start=args.start,
        end=args.end,
        first_day=args.first_day,
    )
    outputs = write_outputs(
        result,
        sources={
            "history": _source(history_path),
            "heya_index": _source(heya_path),
        },
        output_root=args.output_root,
    )
    failures = sum(not row.forecast.success for row in result.cases)
    mean_recovery = sum(row.pair_recovery_rate for row in result.cases) / len(result.cases)
    print(f"Cases: {len(result.cases):,}")
    print(f"Excluded extra-cross-division cases: {len(result.exclusions):,}")
    print(f"Greedy failures: {failures:,}")
    print(f"Mean pair recovery: {mean_recovery:.3%}")
    print(f"Exact cards: {sum(row.exact for row in result.cases):,}")
    print(f"Output: {outputs.run_directory.resolve()}")


def _source(path: Path) -> dict[str, object]:
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    main()

"""Report how often the stronger chii wins, overall and within each division."""

import argparse
import csv
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from .analysis import analyse


def parse_date(value: str) -> Date:
    try:
        year, month = map(int, value.split("/"))
        if year < 1 or month not in (1, 3, 5, 7, 9, 11):
            raise ValueError
        return Date(Year(year), Month(month))
    except ValueError as error:
        raise argparse.ArgumentTypeError("Expected a basho date YYYY/MM") from error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path,
                        default=Path("files/output/Historys/1958_01 to 2026_11.zip"))
    parser.add_argument("--start", type=parse_date, default=parse_date("1989/01"))
    parser.add_argument("--end", type=parse_date, help="Default: latest represented basho")
    parser.add_argument("--output-root", type=Path,
                        default=Path("files/output/analysis/chii_prediction"))
    args = parser.parse_args()
    source = args.history_zip.resolve()
    if not source.is_file() or source.suffix.lower() != ".zip":
        parser.error(f"History zip not found: {source}")
    history = load_history_with_annotations(str(source.with_suffix("")))
    if not history:
        parser.error("History is empty")
    try:
        result = analyse(history, start=args.start, end=args.end or max(history))
    except ValueError as error:
        parser.error(str(error))
    lines = [
        "# How often does the stronger chii win?", "",
        f"History: {result.first_basho} to {result.last_basho} ({result.basho_count} basho).", "",
        "Each represented W/L bout is counted once, including blank kimarite.",
        "Division rows require both rikishi in the same division; cross-division bouts",
        "are separate and included in ALL. Stronger chii means lower canonical ordinal.", "",
        "| Population | Bouts | Higher chii wins | Win percentage | Above 50% (pp) |",
        "|---|---:|---:|---:|---:|",
    ]
    records = []
    for row in result.rows:
        fraction = row.win_fraction
        percentage = "n/a" if fraction is None else f"{100 * fraction:.3f}%"
        advantage = "n/a" if fraction is None else f"{100 * (fraction - 0.5):+.3f}"
        lines.append(f"| {row.population} | {row.bouts:,} | {row.higher_chii_wins:,} | {percentage} | {advantage} |")
        records.append({**asdict(row), "win_fraction": fraction,
                        "advantage_over_50_pp": None if fraction is None else 100 * (fraction - 0.5)})
    lines.extend([
        "", f"Raw results: {result.raw_results:,}.",
        f"Excluded defaults (FS/FP): {result.excluded_fusen:,}; other outcomes: {result.excluded_other_outcomes:,}; W/L bouts missing chii: {result.excluded_missing_chii:,}.", "",
        f"Excluded W/L bouts with equal recorded chii: {result.excluded_equal_chii:,} (no stronger chii can be selected).", "",
        "These are descriptive historical frequencies. Pre-1989 lower-division records",
        "are incomplete; selecting those years does not reconstruct missing bouts.",
    ])
    report = "\n".join(lines) + "\n"
    date_label = f"{result.first_basho.replace('/', '_')}_to_{result.last_basho.replace('/', '_')}"
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / f"report_{date_label}.md").write_text(report, encoding="utf-8")
    with (args.output_root / f"counts_{date_label}.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    manifest = {"history_zip": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "requested_start": str(args.start), "requested_end": str(args.end or max(history)),
                **asdict(result)}
    (args.output_root / f"manifest_{date_label}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(report)
    print(f"Outputs: {args.output_root.resolve()}")


if __name__ == "__main__":
    main()

"""Count represented W/L results whose kimarite is missing."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import re
from typing import Mapping

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Division, MSD, Outcome
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


DIVISIONS = (
    "Makuuchi",
    "Juryo",
    "Makushita",
    "Sandanme",
    "Jonidan",
    "Jonokuchi",
)

DEFAULT_OUTPUT_DIR = Path(
    "src/validation/elo89-expert-account/Matters Arising/Kimarite/output"
)


def count_missing_kimarite(
    history: History,
    *,
    start: Date | None = None,
    end: Date | None = None,
) -> dict[Date, dict[str, int]]:
    """Return blank-kimarite W/L counts by basho and bout division."""

    if start is not None and end is not None and start > end:
        raise ValueError(f"Start date {start} is after end date {end}")

    counts: dict[Date, dict[str, int]] = {}
    dates = [
        date
        for date in sorted(history)
        if (start is None or date >= start) and (end is None or date <= end)
    ]
    if not dates:
        raise ValueError("Selected History interval contains no represented basho")

    for date in dates:
        basho = history[date]
        row = {division: 0 for division in DIVISIONS}
        counts[date] = row
        for day in sorted(basho.summary):
            for bout in basho.summary[day].results_lookup.values():
                if bout.decision != "blank":
                    continue
                if {bout.outcome1, bout.outcome2} != {Outcome.W, Outcome.L}:
                    continue
                division = _bout_division(
                    basho.banzuke.rikchii,
                    bout.rikishi1,
                    bout.rikishi2,
                    date=date,
                    day=day,
                )
                row[division] += 1
    return counts


def write_csv(
    counts: Mapping[Date, Mapping[str, int]],
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    timestamp: datetime | None = None,
) -> tuple[Path, int]:
    """Write the dated table and return its path and grand total."""

    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = (timestamp or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")
    first = min(counts)
    last = max(counts)
    scope = f"{_format_date(first)}_to_{_format_date(last)}"
    path = output_dir / (
        f"missing_kimarite_by_basho_division_{scope}_{stamp}.csv"
    )
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing validation output: {path}")

    column_totals = {division: 0 for division in DIVISIONS}
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("Date", *DIVISIONS, "Total"))
        for date in sorted(counts):
            values = [int(counts[date][division]) for division in DIVISIONS]
            for division, value in zip(DIVISIONS, values, strict=True):
                column_totals[division] += value
            writer.writerow(
                (
                    _format_date(date),
                    *values,
                    sum(values),
                )
            )

        grand_total = sum(column_totals.values())
        writer.writerow(("Total", *(column_totals[d] for d in DIVISIONS), ""))

    return path, grand_total


def load_history(history_zip: Path | None) -> History:
    """Use the live History unless an annotated zip is explicitly selected."""

    if history_zip is None:
        return get_history()

    supplied = history_zip.resolve()
    zip_path = (
        supplied
        if supplied.suffix.lower() == ".zip"
        else supplied.with_suffix(".zip")
    )
    if not zip_path.is_file():
        raise FileNotFoundError(f"History zip not found: {zip_path}")
    return load_history_with_annotations(str(zip_path.with_suffix("")))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    history = load_history(args.history_zip)
    counts = count_missing_kimarite(
        history,
        start=args.start,
        end=args.end,
    )
    path, grand_total = write_csv(counts, args.output_dir)
    print(f"Output: {path.resolve()}")
    print(f"Total missing kimarite: {grand_total}")
    return 0


def _bout_division(rikchii, rikishi1, rikishi2, *, date, day) -> str:
    """Assign a bout to its higher-ranked represented participant's division."""

    chii = [
        candidate
        for candidate in (rikchii.get(rikishi1), rikchii.get(rikishi2))
        if candidate is not None
    ]
    if not chii:
        raise ValueError(
            "Cannot assign missing-kimarite bout to a division: "
            f"{date} Day {int(day)}, rikishi {int(rikishi1)} and {int(rikishi2)} "
            "are both off banzuke"
        )
    return _division_name(min(chii, key=Chii.ordinal))


def _division_name(chii: Chii) -> str:
    if isinstance(chii.level, MSD):
        return "Makuuchi"
    names = {
        Division.JURYO: "Juryo",
        Division.MAKUSHITA: "Makushita",
        Division.SANDANME: "Sandanme",
        Division.JONIDAN: "Jonidan",
        Division.JONOKUCHI: "Jonokuchi",
    }
    try:
        return names[chii.level]
    except KeyError as error:
        raise ValueError(f"Unsupported professional division for {chii}") from error


def _parse_date(value: str) -> Date:
    match = re.fullmatch(r"(\d{4})-(\d{2})", value)
    if match is None:
        raise argparse.ArgumentTypeError("expected YYYY-MM")
    try:
        return Date.from_ints(int(match.group(1)), int(match.group(2)))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def _format_date(date: Date) -> str:
    return f"{int(date.year):4d}-{int(date.month):02d}"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Use this annotated History zip instead of the live store.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--start",
        type=_parse_date,
        help="First represented basho to include, in YYYY-MM format.",
    )
    parser.add_argument(
        "--end",
        type=_parse_date,
        help="Last represented basho to include, in YYYY-MM format.",
    )
    return parser

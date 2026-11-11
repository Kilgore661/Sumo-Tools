"""Produce daily Cumulative Performance Rating metrics for one basho and division."""

from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path

from src.analysis.banzuke_compare.banzuke_diff import division_for_chii
from src.analysis.elo89.api import Elo89Artifacts
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Division
from src.sumo_core.History import Date, History

from .model import cumulative_rows, remove_repetitions
from .output import write_csv


DEFAULT_HISTORY_ZIP = Path("files/output/Historys/1958_01 to 2026_11.zip")
DEFAULT_RATINGS_ROOT = Path("files/output/analysis/site89_bundle/sources/elo89")
DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/cpr")
DIVISIONS = {division.name.lower(): division for division in Division}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--date",
        help="Basho as YYYY-MM or YYYY/MM; defaults to the latest basho with results.",
    )
    selection.add_argument(
        "--all-basho",
        action="store_true",
        help="Write one combined CSV for every basho represented by History and Elo-89.",
    )
    parser.add_argument(
        "--division", choices=tuple(DIVISIONS), default="makuuchi"
    )
    parser.add_argument("--history-zip", type=Path, default=DEFAULT_HISTORY_ZIP)
    parser.add_argument("--ratings-root", type=Path, default=DEFAULT_RATINGS_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--remove-repetitions",
        action="store_true",
        help=(
            "Sort by descending z_score and retain only the highest-Z day "
            "for each rikishi in each basho."
        ),
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    history = _load_history(args.history_zip)
    artifacts = Elo89Artifacts.load(args.ratings_root)
    q = float(artifacts.manifest.get("q", math.nan))
    if not math.isfinite(q) or q <= 0:
        parser.error("Elo-89 manifest contains no positive finite q")
    division = DIVISIONS[args.division]
    ledger_by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
    for bout in artifacts.bout_ledger:
        ledger_by_date[bout["date"]].append(bout)

    if args.all_basho:
        dates = tuple(
            date
            for date in sorted(history)
            if history(date).summary.last_defined() is not None
            and str(date) in artifacts.basho_start_ratings
            and str(date) in artifacts.day_end_ratings
        )
        if not dates:
            parser.error("History and Elo-89 contain no common basho with results")
        rows = tuple(
            row
            for date in dates
            for row in _rows_for_date(
                history=history,
                date=date,
                division=division,
                division_id=args.division,
                artifacts=artifacts,
                ledger=ledger_by_date[str(date)],
                q=q,
            )[0]
        )
        filename = (
            f"{args.division}-no-repetitions.csv"
            if args.remove_repetitions
            else f"{args.division}.csv"
        )
        output = args.output_root / "all-basho" / filename
        print(f"Basho: {dates[0]} to {dates[-1]} ({len(dates)})")
    else:
        try:
            date = resolve_date(history, args.date)
            rows, latest_day, history_day = _rows_for_date(
                history=history,
                date=date,
                division=division,
                division_id=args.division,
                artifacts=artifacts,
                ledger=ledger_by_date[str(date)],
                q=q,
            )
        except ValueError as exc:
            parser.error(str(exc))
        if latest_day < history_day:
            print(
                f"Using {date} through Day {latest_day}; "
                f"History extends through Day {history_day} but Elo-89 ratings do not."
            )
        filename = (
            f"{args.division}-no-repetitions.csv"
            if args.remove_repetitions
            else f"{args.division}.csv"
        )
        output = (
            args.output_root
            / str(date).replace("/", "-")
            / filename
        )
    if args.remove_repetitions:
        rows = remove_repetitions(rows)
        print("Order: descending z_score; one row per rikishi per basho")
    write_csv(rows, output)
    print(f"Rows: {len(rows)}")
    print(output.resolve())


def _rows_for_date(
    *,
    history: History,
    date: Date,
    division: Division,
    division_id: str,
    artifacts: Elo89Artifacts,
    ledger: list[dict[str, str]],
    q: float,
):
    basho = history(date)
    history_day_value = basho.summary.last_defined()
    if history_day_value is None:
        raise ValueError(f"{date} has no days of results")
    history_day = int(history_day_value)
    date_key = str(date)
    start_ratings = artifacts.basho_start_ratings.get(date_key)
    daily_ratings = artifacts.day_end_ratings.get(date_key)
    if start_ratings is None or daily_ratings is None:
        raise ValueError(f"Elo-89 artifacts do not represent {date}")
    rating_days = tuple(sorted(int(day) for day in daily_ratings))
    if not rating_days:
        raise ValueError(f"Elo-89 artifacts contain no daily ratings for {date}")
    latest_day = min(history_day, rating_days[-1])
    roster = tuple(
        rid
        for rid in basho.banzuke.riks
        if division_for_chii(basho.banzuke.get_chii(rid)) == division
    )
    if not roster:
        raise ValueError(f"No {division_id} rikishi found at {date}")
    rows = cumulative_rows(
        basho=date,
        division=division_id,
        latest_day=latest_day,
        rikishi=roster,
        shikona=basho.banzuke.rikshik,
        chii=basho.banzuke.rikchii,
        start_ratings=start_ratings,
        day_end_ratings=daily_ratings,
        ledger=ledger,
        q=q,
    )
    return rows, latest_day, history_day


def resolve_date(history: History, value: str | None) -> Date:
    """Resolve an explicit date or the latest represented basho with results."""

    if value:
        normalised = value.replace("-", "/")
        try:
            year_text, month_text = normalised.split("/", 1)
            date = Date.from_ints(int(year_text), int(month_text))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid basho date: {value!r}") from exc
        if date not in history:
            raise ValueError(f"Basho is not represented in History: {date}")
        return date
    dates = sorted(
        date for date, basho in history.items() if basho.summary.last_defined() is not None
    )
    if not dates:
        raise ValueError("History contains no basho with results")
    return dates[-1]


def _load_history(path: Path) -> History:
    if not path.is_file() and not path.with_suffix(".zip").is_file():
        raise FileNotFoundError(f"History source not found: {path}")
    source = path.with_suffix("") if path.suffix.lower() == ".zip" else path
    return load_history_with_annotations(str(source))


if __name__ == "__main__":
    main()

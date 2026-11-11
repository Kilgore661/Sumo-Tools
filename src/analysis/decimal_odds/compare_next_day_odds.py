"""Compare a next-day external odds file with pre-bout Elo-89 prices."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from src.analysis.elo89 import Elo89Artifacts
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date, History

from .analysis import (
    BoutComparison,
    analyse_odds_payload,
    build_banzuke_name_index,
    rating_snapshot_before_day,
)


DEFAULT_ODDS_ROOT = Path("src/misc/Betting/odds")
DEFAULT_RATINGS_ROOT = Path("files/output/analysis/site89_bundle/sources/elo89")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "odds_json",
        nargs="?",
        type=Path,
        help="Saved next-day odds JSON; defaults to the newest file in src/misc/Betting/odds.",
    )
    parser.add_argument(
        "--ratings-root",
        type=Path,
        default=DEFAULT_RATINGS_ROOT,
        help="Directory containing one published Elo-89 artifact set.",
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Use an annotated History zip instead of the live store.",
    )
    parser.add_argument("--basho", type=_date, help="Basho date as YYYY/MM; defaults to latest History.")
    parser.add_argument(
        "--day",
        type=int,
        choices=range(1, 16),
        metavar="1..15",
        help="Basho day; defaults to the day after the latest completed History day.",
    )
    parser.add_argument("--output-csv", type=Path, help="Also write the comparison rows as CSV.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    odds_path = args.odds_json or newest_odds_file(DEFAULT_ODDS_ROOT)
    payload = json.loads(odds_path.read_text(encoding="utf-8"))
    history = load_history(args.history_zip)
    basho = args.basho or max(history)
    day = args.day or infer_next_day(history, basho)
    ratings = Elo89Artifacts.load(args.ratings_root)
    _values, cutoff = rating_snapshot_before_day(ratings, basho, day)
    comparisons = analyse_odds_payload(
        payload,
        name_index=build_banzuke_name_index(history, basho),
        ratings=ratings,
        basho=basho,
        day=day,
    )

    print(f"Odds file: {odds_path.resolve()}")
    print(f"External source: {payload.get('source', '-')}")
    print(f"Scraped at: {payload.get('scraped_at', '-')}")
    print(f"Elo-89 ratings: {args.ratings_root.resolve()}")
    print(f"Basho/day: {basho} Day {day} ({cutoff})")
    print()
    print_table(comparisons)
    if args.output_csv is not None:
        write_csv(args.output_csv, comparisons, basho=basho, day=day, cutoff=cutoff)
        print(f"\nWrote: {args.output_csv.resolve()}")
    return 0


def newest_odds_file(root: Path) -> Path:
    candidates = sorted(root.glob("*.json"))
    if not candidates:
        raise FileNotFoundError(f"No odds JSON files found in {root}")
    return candidates[-1]


def load_history(history_zip: Path | None) -> History:
    if history_zip is None:
        return get_history()
    resolved = history_zip.resolve()
    if resolved.suffix.lower() != ".zip" or not resolved.is_file():
        raise FileNotFoundError(f"History zip not found: {resolved}")
    return load_history_with_annotations(str(resolved.with_suffix("")))


def infer_next_day(history: History, basho: Date) -> int:
    if basho not in history:
        raise ValueError(f"History has no basho {basho}")
    completed = history[basho].summary.last_defined()
    next_day = 1 if completed is None else int(completed) + 1
    if next_day > 15:
        raise ValueError(
            f"Latest History basho {basho} is complete; specify --basho and --day explicitly"
        )
    return next_day


def print_table(comparisons: tuple[BoutComparison, ...]) -> None:
    heading = (
        f"{'Rikishi':<18} {'Rating':>7} {'Elo p':>7} {'Elo odds':>9} "
        f"{'Market':>8} {'Market p*':>10}"
    )
    print(heading)
    print("-" * len(heading))
    for bout in comparisons:
        for competitor in (bout.first, bout.second):
            print(
                f"{competitor.name:<18} {competitor.rating:>7.1f} "
                f"{competitor.elo_probability:>6.1%} "
                f"{competitor.elo_decimal_odds:>9.3f} "
                f"{competitor.market_decimal_odds:>8.3f} "
                f"{competitor.market_normalized_probability:>9.1%}"
            )
        print(f"  market overround: {bout.market_overround:.1%}")
    print("\n* Market implied probability normalized across the two quoted prices.")


def write_csv(
    path: Path,
    comparisons: tuple[BoutComparison, ...],
    *,
    basho: Date,
    day: int,
    cutoff: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "basho", "day", "rating_cutoff", "event", "event_url", "side",
        "rikishi_id", "shikona", "rating", "elo_probability",
        "elo_decimal_odds", "market_decimal_odds",
        "market_raw_implied_probability", "market_normalized_probability",
        "market_overround",
    )
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for bout in comparisons:
            for side, competitor in (("first", bout.first), ("second", bout.second)):
                writer.writerow(
                    {
                        "basho": str(basho),
                        "day": day,
                        "rating_cutoff": cutoff,
                        "event": bout.event_name,
                        "event_url": bout.event_url,
                        "side": side,
                        "rikishi_id": int(competitor.rikishi_id),
                        "shikona": competitor.name,
                        "rating": competitor.rating,
                        "elo_probability": competitor.elo_probability,
                        "elo_decimal_odds": competitor.elo_decimal_odds,
                        "market_decimal_odds": competitor.market_decimal_odds,
                        "market_raw_implied_probability": competitor.market_raw_implied_probability,
                        "market_normalized_probability": competitor.market_normalized_probability,
                        "market_overround": bout.market_overround,
                    }
                )


def _date(value: str) -> Date:
    try:
        year, month = value.split("/", maxsplit=1)
        return Date(Year(int(year)), Month(int(month)))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(f"Expected YYYY/MM, got {value!r}") from error


if __name__ == "__main__":
    raise SystemExit(main())

"""Compare no-overround bookmaker and pre-bout Elo-89 rating differences."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from src.analysis.elo89 import Elo89Artifacts
from src.infra.torikumi.model import Future
from src.infra.torikumi.persistence import load_future
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date, History

from .analysis import build_banzuke_name_index
from .compare_next_day_odds import load_history
from .rating_differences import (
    OddsEloComparisonError,
    RatingDifferenceComparison,
    build_canonical_opponent_index,
    compare_odds_rows,
)


DEFAULT_INPUT = Path(
    "src/misc/Betting/special_outputs/2026-11-basho-odds.csv"
)
DEFAULT_RATINGS_ROOT = Path("files/output/analysis/site89_bundle/sources/elo89")
DEFAULT_FUTURE = Path("files/output/torikumi/future.json")
DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/decimal_odds")

OUTPUT_FIELDS = (
    "date",
    "day",
    "site",
    "rikishi_1_bookmaker_shikona",
    "rikishi_1_history_shikona",
    "rikishi_1_id",
    "rikishi_1_resolution",
    "rikishi_1_market_decimal_odds",
    "rikishi_1_market_probability",
    "rikishi_1_market_fair_odds",
    "rikishi_1_elo89_rating",
    "rikishi_2_bookmaker_shikona",
    "rikishi_2_history_shikona",
    "rikishi_2_id",
    "rikishi_2_resolution",
    "rikishi_2_market_decimal_odds",
    "rikishi_2_market_probability",
    "rikishi_2_market_fair_odds",
    "rikishi_2_elo89_rating",
    "market_overround",
    "market_q",
    "market_rating_difference_1_minus_2",
    "elo89_rating_difference_1_minus_2",
    "market_minus_elo89_difference",
    "rating_cutoff",
    "identity_warning",
    "source_file",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("odds_csv", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument("--ratings-root", type=Path, default=DEFAULT_RATINGS_ROOT)
    parser.add_argument("--future-json", type=Path, default=DEFAULT_FUTURE)
    parser.add_argument("--basho", type=_date)
    parser.add_argument(
        "--day",
        type=int,
        choices=range(1, 16),
        action="append",
        help="process only this day; repeat to select several days",
    )
    parser.add_argument("--output-csv", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        rows = read_odds_rows(args.odds_csv)
        if args.day:
            wanted = set(args.day)
            rows = [row for row in rows if int(row.get("day", 0)) in wanted]
        if not rows:
            raise OddsEloComparisonError("No odds rows remain after filtering")
        basho = args.basho or infer_basho(rows)
        history = load_history(args.history_zip)
        if basho not in history:
            raise OddsEloComparisonError(f"History has no banzuke for {basho}")
        ratings = Elo89Artifacts.load(args.ratings_root)
        future = load_optional_future(args.future_json, basho)
        banzuke = history[basho].banzuke
        history_names = {
            rikishi_id: str(banzuke.rikshik[rikishi_id])
            for rikishi_id in banzuke.riks
        }
        comparisons = compare_odds_rows(
            rows,
            name_index=build_banzuke_name_index(history, basho),
            history_names=history_names,
            canonical_opponents=build_canonical_opponent_index(
                history, basho, future
            ),
            ratings=ratings,
            basho=basho,
        )
        for warning in dict.fromkeys(
            item.identity_warning for item in comparisons if item.identity_warning
        ):
            print(f"Warning: {warning}", file=sys.stderr)
        output = args.output_csv or (
            DEFAULT_OUTPUT_ROOT
            / f"{str(basho).replace('/', '-')}-odds-elo-differences.csv"
        )
        write_comparisons(output, comparisons)
        print_summary(comparisons)
        print(f"\nWrote: {output.resolve()}")
        return 0
    except (OddsEloComparisonError, FileNotFoundError, ValueError) as error:
        print(f"Fatal error: {error}", file=sys.stderr)
        return 2


def read_odds_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {
            "date",
            "day",
            "site",
            "rikishi_1",
            "rikishi_1_decimal_odds",
            "rikishi_2",
            "rikishi_2_decimal_odds",
        }
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise OddsEloComparisonError(
                "Odds CSV lacks required columns: " + ", ".join(sorted(missing))
            )
        return list(reader)


def infer_basho(rows: list[dict[str, str]]) -> Date:
    values = {row.get("date", "")[:7] for row in rows}
    if len(values) != 1:
        raise OddsEloComparisonError(
            "Cannot infer one basho from odds dates: " + ", ".join(sorted(values))
        )
    value = values.pop()
    try:
        year, month = value.split("-")
        return Date(Year(int(year)), Month(int(month)))
    except (TypeError, ValueError) as error:
        raise OddsEloComparisonError(
            f"Cannot infer basho from odds date prefix {value!r}"
        ) from error


def load_optional_future(path: Path, basho: Date) -> Future | None:
    if not path.is_file():
        return None
    future = load_future(path)
    return future if future.date == basho else None


def write_comparisons(
    path: Path,
    comparisons: tuple[RatingDifferenceComparison, ...],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for item in comparisons:
            writer.writerow(_output_row(item))


def _output_row(item: RatingDifferenceComparison) -> dict[str, object]:
    return {
        "date": item.date,
        "day": item.day,
        "site": item.site,
        "rikishi_1_bookmaker_shikona": item.first.bookmaker_shikona,
        "rikishi_1_history_shikona": item.first.history_shikona,
        "rikishi_1_id": int(item.first.rikishi_id),
        "rikishi_1_resolution": item.first.method,
        "rikishi_1_market_decimal_odds": item.first_market_decimal_odds,
        "rikishi_1_market_probability": item.first_market_probability,
        "rikishi_1_market_fair_odds": item.first_market_fair_odds,
        "rikishi_1_elo89_rating": item.first_elo89_rating,
        "rikishi_2_bookmaker_shikona": item.second.bookmaker_shikona,
        "rikishi_2_history_shikona": item.second.history_shikona,
        "rikishi_2_id": int(item.second.rikishi_id),
        "rikishi_2_resolution": item.second.method,
        "rikishi_2_market_decimal_odds": item.second_market_decimal_odds,
        "rikishi_2_market_probability": item.second_market_probability,
        "rikishi_2_market_fair_odds": item.second_market_fair_odds,
        "rikishi_2_elo89_rating": item.second_elo89_rating,
        "market_overround": item.market_overround,
        "market_q": item.market_q,
        "market_rating_difference_1_minus_2": item.market_rating_difference,
        "elo89_rating_difference_1_minus_2": item.elo89_rating_difference,
        "market_minus_elo89_difference": item.market_minus_elo89_difference,
        "rating_cutoff": item.rating_cutoff,
        "identity_warning": item.identity_warning,
        "source_file": item.source_file,
    }


def print_summary(comparisons: tuple[RatingDifferenceComparison, ...]) -> None:
    heading = (
        f"{'Date':<10} {'Day':>3} {'Site':<12} {'Bout':<35} "
        f"{'Market dR':>10} {'Elo-89 dR':>10} {'Difference':>10}"
    )
    print(heading)
    print("-" * len(heading))
    for item in comparisons:
        bout = f"{item.first.history_shikona} v {item.second.history_shikona}"
        print(
            f"{item.date:<10} {item.day:>3} {item.site:<12} {bout:<35} "
            f"{item.market_rating_difference:>10.1f} "
            f"{item.elo89_rating_difference:>10.1f} "
            f"{item.market_minus_elo89_difference:>10.1f}"
        )


def _date(value: str) -> Date:
    try:
        year, month = value.split("/", maxsplit=1)
        return Date(Year(int(year)), Month(int(month)))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(f"Expected YYYY/MM, got {value!r}") from error


if __name__ == "__main__":
    raise SystemExit(main())

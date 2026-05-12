"""Publish Basho Results Browser data for make_site."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.analysis.sumo_history.basho_results.build import (
    build_index,
    build_payload_rows,
)
from src.analysis.sumo_history.basho_results.dates import represented_dates
from src.analysis.sumo_history.basho_results.ratings import RatingLookup
from src.analysis.sumo_history.basho_results.reports import OUTPUT_ROOT, write_index, write_payload
from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date


def main() -> None:
    args = parse_args()
    output_root = args.output_root
    history = get_history()
    ratings = RatingLookup.load()

    dates = represented_dates(history)
    if args.date is not None:
        selected = find_represented_date(dates, args.date)
        if selected not in dates:
            raise ValueError(f"{selected} is not a represented basho date")
        dates = (selected,)

    index = build_index(history)
    if args.date is not None:
        entry_by_basho = {entry.basho: entry for entry in index.entries}
        index = type(index)(
            schema=index.schema,
            generated_at=index.generated_at,
            default_basho=str(dates[-1]),
            entries=(entry_by_basho[str(dates[-1])],),
        )

    write_index(index, output_root)
    for date in dates:
        rows = build_payload_rows(history=history, date=date, ratings=ratings)
        write_payload(date, rows, output_root)

    print(f"wrote BRB data for {len(dates)} basho to {output_root}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish Basho Results Browser data.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Output root for BRB index and payload files.",
    )
    parser.add_argument(
        "--date",
        help="Optional single basho date in YYYY/MM form.",
    )
    return parser.parse_args()


def find_represented_date(dates: tuple[Date, ...], value: str) -> Date:
    normalised = str(Date(Year(int(value.split("/")[0])), Month(int(value.split("/")[1]))))
    for date in dates:
        if str(date) == normalised:
            return date
    raise ValueError(f"{normalised} is not a represented basho date")


if __name__ == "__main__":
    main()

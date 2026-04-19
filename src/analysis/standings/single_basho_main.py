"""
Command-line entry point for single-basho standings.

Parses command-line arguments, establishes valid inputs for downstream
functions, loads History, selects the requested basho, computes standings,
builds the presentation view, and writes output files.

Conceptually:

    argv -> console messages × output files
"""

import argparse
from pathlib import Path

from src.analysis.standings.single_basho import (
    WinsMode,
    get_single_basho_standings,
)
from src.analysis.standings.single_basho_view import (
    get_single_basho_standings_view,
)
from src.analysis.standings.single_basho_reports import (
    write_single_basho_standings_view_csv,
)
from src.infra.live_store.api import get_history
from .helpers import escape_date


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute single-basho standings.")
    parser.add_argument("--date", help="Basho date YYYY/MM")
    parser.add_argument(
        "--wins",
        choices=["real", "all"],
        default="real",
        help="Primary ranking key",
    )
    parser.add_argument(
        "--output",
        help="Output CSV path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    history = get_history()
    dates = sorted(history.keys())

    if args.date is None:
        date = dates[-1]
    else:
        matching = [d for d in dates if str(d) == args.date]
        if not matching:
            raise ValueError(f"Date '{args.date}' not found in History.")
        date = matching[0]

    basho = history(date)

    if args.wins == "real":
        wins_mode = WinsMode.REAL
    elif args.wins == "all":
        wins_mode = WinsMode.ALL
    else:
        raise ValueError(f"Unsupported wins mode: {args.wins}")

    standings = get_single_basho_standings(
        basho=basho,
        wins_mode=wins_mode,
    )

    view = get_single_basho_standings_view(
        basho=basho,
        standings=standings,
    )

    if args.output is None:
        output_file = Path(
            f"files/output/standings/"
            f"single basho standings view "
            f"({escape_date(date)}, {args.wins}).csv"
        )
    else:
        output_file = Path(args.output)

    write_single_basho_standings_view_csv(view, output_file)

    print(f"Single-basho standings for {date}")
    print(f"Wins mode: {args.wins}")
    print(f"Rows: {len(view.rows)}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()

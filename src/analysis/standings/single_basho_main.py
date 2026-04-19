"""
Command-line entry point for single-basho standings.

Parses command-line arguments, establishes valid inputs for downstream
functions, loads History, selects the requested basho, computes standings,
builds the derived view, and writes output files.

Conceptually:

    argv -> console messages × output files
"""

import argparse
import os
import sys

from src.analysis.standings.single_basho import (
    WinsMode,
    get_single_basho_standings,
)
from src.analysis.standings.single_basho_reports import (
    ensure_output_dir,
    ensure_single_basho_run_output_dir,
    latest_single_basho_csv_file,
    latest_single_basho_json_file,
    single_basho_run_csv_file,
    single_basho_run_json_file,
    write_single_basho_standings_view_csv,
)
from src.analysis.standings.single_basho_view import (
    get_single_basho_standings_view,
)
from src.infra.live_store.api import get_history
from .helpers import copy_file, escape_date, make_run_stamp, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute single-basho standings.")
    parser.add_argument("--date", help="Basho date YYYY/MM")
    parser.add_argument(
        "--wins",
        choices=["real", "all"],
        default="real",
        help="Primary ranking key",
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

    ensure_output_dir()
    run_stamp = make_run_stamp()
    ensure_single_basho_run_output_dir(run_stamp)

    output_file = single_basho_run_csv_file(
        run_stamp=run_stamp,
        date=escape_date(date),
        wins=args.wins,
    )
    run_file = single_basho_run_json_file(run_stamp)

    write_single_basho_standings_view_csv(view, output_file)

    run_payload = {
        "command": getattr(sys, "orig_argv", [sys.executable, *sys.argv]),
        "cwd": os.getcwd(),
    }
    write_json(run_file, run_payload)

    latest_csv = latest_single_basho_csv_file()
    latest_json = latest_single_basho_json_file()

    copy_file(output_file, latest_csv)
    copy_file(run_file, latest_json)

    print(f"Single-basho standings for {date}")
    print(f"Wins mode: {args.wins}")
    print(f"Rows: {len(view.rows)}")
    print(f"Output: {output_file}")
    print(f"Run: {run_file}")
    print(f"Latest CSV: {latest_csv}")
    print(f"Latest JSON: {latest_json}")


if __name__ == "__main__":
    main()

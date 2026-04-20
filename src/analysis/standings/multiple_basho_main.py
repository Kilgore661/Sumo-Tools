"""
Command-line entry point for multiple-basho standings.

Parses command-line arguments, establishes valid inputs for downstream
functions, loads History, selects the requested basho window, computes core
standings totals, derives per-basho metrics, and writes output files.

Conceptually:

    argv -> core standings -> derived standings view -> console messages × output files
"""

import argparse
import os
import sys
from time import time

from src.analysis.standings.multiple_basho import (
    get_multiple_basho_core,
    resolve_date,
    resolve_window_dates,
)


from src.analysis.standings.multiple_basho_reports import (
    ensure_multiple_basho_run_output_dir,
    ensure_output_dir,
    latest_multiple_basho_csv_file,
    latest_multiple_basho_json_file,
    multiple_basho_run_csv_file,
    multiple_basho_run_json_file,
    write_multiple_basho_view_csv,
)
from src.analysis.standings.multiple_basho_view import get_multiple_basho_view
from src.analysis.standings.classes import WinPolicy
from src.infra.live_store.api import get_history
from .helpers import copy_file, escape_date, make_run_stamp, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute multiple-basho standings.")
    parser.add_argument("--date", help="Basho date YYYY/MM")
    parser.add_argument(
        "--direction",
        choices=["BACKWARDS", "FORWARDS"],
        default="BACKWARDS",
        help="Window direction relative to --date",
    )
    parser.add_argument(
        "--num-basho",
        type=int,
        default=1,
        help="Number of basho in the standings window",
    )
    parser.add_argument(
        "--wins",
        choices=["real", "all"],
        default="real",
        help="Primary ranking key",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    t0 = time()
    history = get_history()

    anchor_date = resolve_date(
        history=history,
        direction=args.direction,
        requested_date=args.date,
    )
    selected_dates = resolve_window_dates(
        history=history,
        date=anchor_date,
        direction=args.direction,
        num_basho=args.num_basho,
    )

    if args.wins == "real":
        win_policy = WinPolicy.FOUGHT_ONLY
    elif args.wins == "all":
        win_policy = WinPolicy.CREDITED
    else:
        raise ValueError(f"Unsupported wins mode: {args.wins}")

    core = get_multiple_basho_core(
        history=history,
        selected_dates=selected_dates,
        win_policy=win_policy,
    )
    view = get_multiple_basho_view(
        history=history,
        core=core,
        win_policy=win_policy,
    )

    ensure_output_dir()
    run_stamp = make_run_stamp()
    ensure_multiple_basho_run_output_dir(run_stamp)

    output_file = multiple_basho_run_csv_file(
        run_stamp=run_stamp,
        date=escape_date(anchor_date),
        direction=args.direction,
        num_basho=args.num_basho,
        wins=args.wins,
    )
    run_file = multiple_basho_run_json_file(run_stamp)

    write_multiple_basho_view_csv(view, output_file)

    run_payload = {
        "command": getattr(sys, "orig_argv", [sys.executable, *sys.argv]),
        "cwd": os.getcwd(),
    }
    write_json(run_file, run_payload)

    latest_csv = latest_multiple_basho_csv_file()
    latest_json = latest_multiple_basho_json_file()

    copy_file(output_file, latest_csv)
    copy_file(run_file, latest_json)

    print(f"Multiple-basho standings anchored at {anchor_date}")
    print(f"Direction: {args.direction}")
    print(f"Selected basho: {selected_dates[0]} to {selected_dates[-1]} ({len(selected_dates)} basho)")
    print(f"Wins mode: {args.wins}")
    print(f"Rows: {len(view.rows)}")
    print(f"Output: {output_file}")
    print(f"Run: {run_file}")
    print(f"Latest CSV: {latest_csv}")
    print(f"Latest JSON: {latest_json}")
    print(f"run complete in {time() - t0:.0f}s")


if __name__ == "__main__":
    main()

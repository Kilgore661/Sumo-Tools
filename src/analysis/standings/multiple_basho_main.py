"""
Command-line entry point for multiple-basho standings.

Parses command-line arguments, establishes valid inputs for downstream
functions, loads History, selects a contiguous basho window, computes core
standings totals, derives average-based results, and writes output files.

Conceptually:

    argv -> console messages × output files
"""

import argparse
from pathlib import Path

from src.analysis.standings.multiple_basho import (
    WinsMode,
    get_multiple_basho_core,
)
from src.analysis.standings.multiple_basho_reports import (
    default_multiple_basho_output_file,
    ensure_multiple_basho_run_output_dir,
    new_run_stamp,
    write_multiple_basho_view_csv,
)
from src.analysis.standings.multiple_basho_view import (
    get_multiple_basho_view,
)
from src.infra.live_store.api import get_history


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute multiple-basho standings.")
    parser.add_argument("--date", help="Anchor basho date YYYY/MM")
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
        help="Number of basho in the selected window",
    )
    parser.add_argument(
        "--wins",
        choices=["real", "all"],
        default="real",
        help="Default average ranking key",
    )
    parser.add_argument(
        "--output",
        help="Output CSV path",
    )
    return parser.parse_args()


def resolve_anchor_date(history, requested_date: str | None, direction: str):
    dates = sorted(history.keys())

    if requested_date is None:
        if direction == "BACKWARDS":
            return dates[-1]
        if direction == "FORWARDS":
            return dates[0]
        raise ValueError(f"Unsupported direction: {direction}")

    matching = [date for date in dates if str(date) == requested_date]
    if not matching:
        raise ValueError(f"Date '{requested_date}' not found in History.")

    return matching[0]


def resolve_selected_dates(history, anchor_date, direction: str, num_basho: int) -> tuple:
    if num_basho <= 0:
        raise ValueError("--num-basho must be greater than zero.")

    dates = sorted(history.keys())
    index = dates.index(anchor_date)

    if direction == "BACKWARDS":
        start = max(0, index - num_basho + 1)
        return tuple(dates[start : index + 1])

    if direction == "FORWARDS":
        end = min(len(dates), index + num_basho)
        return tuple(dates[index:end])

    raise ValueError(f"Unsupported direction: {direction}")


def main() -> None:
    args = parse_args()

    history = get_history()

    anchor_date = resolve_anchor_date(
        history=history,
        requested_date=args.date,
        direction=args.direction,
    )

    selected_dates = resolve_selected_dates(
        history=history,
        anchor_date=anchor_date,
        direction=args.direction,
        num_basho=args.num_basho,
    )

    if args.wins == "real":
        wins_mode = WinsMode.REAL
    elif args.wins == "all":
        wins_mode = WinsMode.ALL
    else:
        raise ValueError(f"Unsupported wins mode: {args.wins}")

    core = get_multiple_basho_core(
        history=history,
        selected_dates=selected_dates,
    )

    view = get_multiple_basho_view(
        history=history,
        anchor_date=anchor_date,
        core=core,
        wins_mode=wins_mode,
    )

    if args.output is None:
        run_stamp = new_run_stamp()
        ensure_multiple_basho_run_output_dir(run_stamp)
        output_file = default_multiple_basho_output_file(
            run_stamp=run_stamp,
            date=anchor_date,
            direction=args.direction,
            num_basho=args.num_basho,
            wins=args.wins,
        )
    else:
        output_file = Path(args.output)

    write_multiple_basho_view_csv(view, output_file)

    print(f"Multiple-basho standings anchored at {anchor_date}")
    print(f"Direction: {args.direction}")
    print(f"Selected basho: {selected_dates[0]} to {selected_dates[-1]} ({len(selected_dates)} basho)")
    print(f"Wins mode: {args.wins}")
    print(f"Rows: {len(view.rows)}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import time
from pathlib import Path

from .collect import collect_tallies
from .config import DEFAULT_OUTPUT_ROOT, DEFAULT_START
from .grouping import GroupingName
from .history_io import date_token, load_history, parse_date
from .reports import (
    write_boundary_bridge_distribution,
    write_boundary_bridge_plots,
    write_bridge_distribution,
    write_bridge_plots,
    write_bridge_reach,
    write_day_matrices,
)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Write day-specific torikumi matchup count matrices and derived "
            "probability matrices from scheduled bouts."
        )
    )
    parser.add_argument("--start", default=DEFAULT_START, help="Start basho YYYY/MM.")
    parser.add_argument("--end", default=None, help="Optional end basho YYYY/MM.")
    parser.add_argument(
        "--grouping",
        choices=[grouping.value for grouping in GroupingName] + ["all"],
        default=GroupingName.NO_SIDE.value,
        help="Rank grouping for matrix rows and columns. Use 'all' to write every grouping.",
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        default=None,
        help="Optional zip-backed History path. Defaults to the live store.",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    started_at = time.perf_counter()
    args = build_arg_parser().parse_args()
    start = parse_date(args.start)
    end = parse_date(args.end) if args.end else None
    history = load_history(args.history_zip)
    end_for_token = end if end is not None else max(history)
    period = f"{date_token(start)}-{date_token(end_for_token)}"

    groupings = (
        tuple(GroupingName)
        if args.grouping == "all"
        else (GroupingName(args.grouping),)
    )

    for grouping in groupings:
        tallies = collect_tallies(history, start=start, end=end, grouping=grouping)
        write_day_matrices(
            output_root=args.output_root,
            period=period,
            grouping=grouping,
            tallies=tallies,
        )
        bridge_path = write_bridge_reach(
            output_root=args.output_root,
            period=period,
            grouping=grouping,
            tallies=tallies,
        )
        distribution_path = write_bridge_distribution(
            output_root=args.output_root,
            period=period,
            grouping=grouping,
            tallies=tallies,
        )
        boundary_distribution_path = write_boundary_bridge_distribution(
            output_root=args.output_root,
            period=period,
            grouping=grouping,
            tallies=tallies,
        )
        plot_paths = write_bridge_plots(
            output_root=args.output_root,
            period=period,
            grouping=grouping,
            tallies=tallies,
        )
        boundary_plot_paths = write_boundary_bridge_plots(
            output_root=args.output_root,
            period=period,
            grouping=grouping,
            tallies=tallies,
        )

        print(f"Analysed {tallies.basho_count} basho.")
        print(f"Grouping: {grouping.value}")
        print(f"Groups: {len(tallies.groups)}")
        print(f"Wrote day matrices to {args.output_root}")
        print(f"Wrote bridge reach to {bridge_path}")
        print(f"Wrote bridge distribution to {distribution_path}")
        print(f"Wrote boundary bridge distribution to {boundary_distribution_path}")
        print(f"Wrote bridge plots to {plot_paths[0].parent if plot_paths else args.output_root}")
        print(
            "Wrote boundary bridge plots to "
            f"{boundary_plot_paths[0].parent if boundary_plot_paths else args.output_root}"
        )

    elapsed = time.perf_counter() - started_at
    print(f"Total run time: {elapsed:.2f} seconds")

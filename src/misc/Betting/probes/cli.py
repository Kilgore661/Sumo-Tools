"""Shared command-line surface for the two source-specific probes."""

from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Sequence
from zoneinfo import ZoneInfo

from .connection import ConnectionError, Place
from .runner import (
    AcquisitionResult,
    ProbePlan,
    default_target_date,
    normal_start_window,
    print_plan,
    run_probe,
)


COMMON_PLACE_IDS = (
    "12", "45", "78", "86", "96", "102", "106", "110", "118",
    "120", "121", "126", "127", "130", "146", "181", "203",
)


def build_parser(source: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"Acquire next-day sumo odds from {source} through ranked places"
    )
    parser.add_argument("--target-date", type=date.fromisoformat)
    parser.add_argument("--timezone", default="Europe/London")
    parser.add_argument("--place", action="append", dest="places")
    parser.add_argument("--ignore-window", action="store_true")
    parser.add_argument("--plan", action="store_true", help="print the plan; do no I/O")
    parser.add_argument(
        "--records-dir",
        type=Path,
        default=Path("files/output/misc/Betting/probes"),
    )
    parser.add_argument(
        "--lock-path",
        type=Path,
        default=Path("files/output/misc/Betting/probes/vpn.lock"),
    )
    display = parser.add_mutually_exclusive_group()
    display.add_argument("--headed", dest="headed", action="store_true")
    display.add_argument("--headless", dest="headed", action="store_false")
    parser.set_defaults(headed=True)
    parser.add_argument("--browser-channel", choices=("chrome", "msedge"), default="chrome")
    parser.add_argument("--browser-path", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--profile-dir", type=Path)
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="save source page diagnostics for unclassified browser failures",
    )
    parser.add_argument(
        "--manual-wait-seconds",
        type=float,
        default=60.0,
        help="headed-mode wait for a site human-check or delayed page",
    )
    return parser


def run_source_cli(
    source: str,
    default_places: Sequence[str],
    acquire_factory: Callable[[argparse.Namespace, date], Callable[[Place, str, str], AcquisitionResult]],
    argv: list[str] | None = None,
) -> int:
    parser = build_parser(source)
    args = parser.parse_args(argv)
    timezone = ZoneInfo(args.timezone)
    now = datetime.now(timezone)
    target = args.target_date or default_target_date(now)
    allowed = normal_start_window(now)
    if not allowed and not args.ignore_window and not args.plan:
        parser.error(
            "next-day acquisition runs may start only from 10:00 through 22:00 "
            f"{args.timezone}; use --ignore-window for development"
        )
    selectors = tuple(args.places or default_places)
    plan = ProbePlan(source, target, args.timezone, selectors, allowed)
    print_plan(plan)
    if args.plan:
        return 0
    acquire = acquire_factory(args, target)
    try:
        return run_probe(
            plan,
            acquire,
            records_dir=args.records_dir,
            lock_path=args.lock_path,
        )
    except KeyboardInterrupt:
        return 130
    except ConnectionError as exc:
        print(f"Probe environment failed: {exc}")
        return 3

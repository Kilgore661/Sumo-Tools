from __future__ import annotations

"""CLI entry point for Expt1.

This module is deliberately thin. It performs argument parsing, data loading,
oracle construction, simulation invocation, and console reporting. The reusable
logic lives in :mod:`expt1.simulate` and related modules.
"""

import argparse
import datetime
import json

from src.infra.config import EPOCH
from ....infra.connect import connect
from ....sumo_core.History import Date
from ....sumo_core.BasicPrimitives import RikId, Day, Year, Month

from ..config_main import BIOS_PATH
from .diagnostics import DiagnosticsCollector
from .initialisation import constant_initialiser
from .Oracle import make_oracle
from .params import EloParams
from .simulate import SimulationMode, simulate


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Experiment 1: single-pass Equelo simulation with optional diagnostics"
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument(
        "--closed",
        action="store_true",
        help=(
            "Use closed active-universe semantics. Departures are redistributed "
            "uniformly over the active survivors at basho boundaries."
        ),
    )
    args = parser.parse_args()

    raw_history = connect(args.start, args.end, use_zip=args.zip)

    with open(BIOS_PATH, "r", encoding="utf-8") as f:
        raw_bios = json.load(f)
    bios = {RikId(int(k)): v for k, v in raw_bios.items()}

    Oracle = make_oracle(raw_history, bios)
    params = EloParams.constant()
    mode = SimulationMode.CLOSED if args.closed else SimulationMode.OPEN
    diagnostics = DiagnosticsCollector(params=params, mode_name=mode.value.upper())

    results = simulate(
        history=Oracle.history,
        params=params,
        entrant_initialiser=constant_initialiser(params.b),
        mode=mode,
        observer=diagnostics,
    )
    summary = diagnostics.finalise()

    dates = sorted(results.day_end_ratings.keys())
    if not dates:
        print("No ratings produced.")
        return

    first_date = dates[0]
    last_date = dates[-1]
    print(f"Computed ratings for {len(dates)} basho: {first_date} to {last_date}")

    last_basho = results.day_end_ratings[last_date]
    last_day = max(last_basho.keys())
    n = len(last_basho[last_day])
    print(f"Rikishi rated at end of {last_date} day {last_day}: {n}")

    test_date = Date(Year(2026), Month(3))
    test_day = Day(3)
    test_rikishi = RikId(12451)

    print()
    print("Test query:")
    print(f"  Date:    {test_date}")
    print(f"  Day:     {test_day}")
    print(f"  Rikishi: {test_rikishi}")
    print(f"  Rating:  {results.day_end_ratings[test_date][test_day][test_rikishi]}")

    print()
    print("Diagnostics summary:")
    print(f"  Mode: {mode.value}")
    print(f"  Max abs basho-end mean deviation from b: {summary.max_abs_mean_deviation_from_b:.12f}")
    print(f"  Max abs rating-mass change across scored bout: {summary.max_abs_bout_mass_change:.12f}")
    print(f"  Entry events: {summary.entry_count}")
    print(f"  Retirement events: {summary.retirement_count}")
    print(f"  Ignored fusen bouts: {summary.ignored_fusen_count}")
    print(f"  Ignored blank bouts: {summary.ignored_blank_count}")
    print(f"  Basho summary csv: {summary.basho_summary_csv_path}")
    print(f"  Retirements csv:   {summary.retirements_csv_path}")
    print(f"  Run log:           {summary.run_log_path}")


if __name__ == "__main__":
    main()

from pdb import set_trace

"""CLI entry point for Expt1.

This module is deliberately thin. It performs argument parsing, data loading,
oracle construction, simulation invocation, and console reporting. The reusable
logic lives in :mod:`expt1.simulate` and related modules.
"""

import argparse
import datetime
from pathlib import Path

from src.infra.config import EPOCH
from ....infra.connect import connect
from ....sumo_core.BasicPrimitives import RikId, Day, Year, Month
from ....sumo_core.History import Date

from ..config_main import INITIAL_ELO, INITIAL_Q, CONSTANT_K
from .diagnostics import DiagnosticsCollector
from .initialisation import constant_initialiser
from .Oracle import make_oracle
from .params import DEFAULT_K_CONFIG_PATH, build_elo_params
from .simulate import SimulationMode, simulate


def _build_parser() -> argparse.ArgumentParser:
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
    parser.add_argument(
        "--k-policy",
        choices=("constant", "divisional"),
        default="constant",
        help="Select the K-factor policy.",
    )
    parser.add_argument(
        "--k-value",
        type=float,
        default=None,
        help=(
            "Constant K value. Valid only with --k-policy constant. "
            f"Default: {CONSTANT_K}."
        ),
    )
    parser.add_argument(
        "--k-config",
        type=Path,
        default=None,
        help=(
            "Path to divisional K JSON config. Valid only with --k-policy divisional. "
            f"Default: {DEFAULT_K_CONFIG_PATH}."
        ),
    )
    parser.add_argument("--b", type=float, default=INITIAL_ELO)
    parser.add_argument("--q", type=float, default=INITIAL_Q)
    return parser


def _validate_k_policy_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.k_policy == "constant" and args.k_config is not None:
        parser.error("--k-config is only valid with --k-policy divisional")
    if args.k_policy == "divisional" and args.k_value is not None:
        parser.error("--k-value is only valid with --k-policy constant")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _validate_k_policy_args(args, parser)

    raw_history = connect(args.start, args.end, use_zip=args.zip)

    oracle = make_oracle(raw_history)
    params = build_elo_params(
        k_policy=args.k_policy,
        b=args.b,
        q=args.q,
        k_value=args.k_value,
        config_path=args.k_config,
    )
    mode = SimulationMode.CLOSED if args.closed else SimulationMode.OPEN
    diagnostics = DiagnosticsCollector(
        params=params,
        mode_name=mode.value.upper(),
        k_policy=args.k_policy,
        k_value=args.k_value,
        k_config_path=args.k_config,
    )

    results = simulate(
        history=oracle.history,
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
    print(f"  K policy: {args.k_policy}")
    if args.k_policy == "constant":
        print(f"  K value: {CONSTANT_K if args.k_value is None else args.k_value}")
    else:
        print(f"  K config: {DEFAULT_K_CONFIG_PATH if args.k_config is None else args.k_config}")
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

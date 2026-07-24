"""Command-line interface for clean Elo."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date

from .config import (
    DEFAULT_ELO,
    DEFAULT_FIDE_K_CONFIG_PATH,
    DEFAULT_OUTPUT_ROOT,
)
from .policies import (
    ConstantInitialRatingPolicy,
    ConstantKPolicy,
    FileInitialRatingPolicy,
    FideKPolicy,
)
from .run import run_clean_elo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Persistent, mean-normalised Elo over observed sumo bouts."
    )
    parser.add_argument(
        "--start",
        required=True,
        type=parse_date,
        help="First basho to process, in YYYY/MM format.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
    )
    parser.add_argument(
        "--count-absences",
        nargs="?",
        const=True,
        default=False,
        type=parse_bool,
        metavar="BOOL",
        help=(
            "Count paired fusen and inferred opponentless kyujo. "
            "May be supplied as a flag or with true/false. Default: false."
        ),
    )

    initial_group = parser.add_mutually_exclusive_group()
    initial_group.add_argument(
        "--initial-rating",
        type=float,
        default=None,
        help=f"Constant first rating. Default: {DEFAULT_ELO}.",
    )
    initial_group.add_argument(
        "--initial-ratings-file",
        type=Path,
        help="CSV or JSON rank-to-initial-rating map.",
    )

    k_group = parser.add_mutually_exclusive_group()
    k_group.add_argument(
        "--k-value",
        type=float,
        help="Use a constant k instead of the default FIDE policy.",
    )
    k_group.add_argument(
        "--k-config",
        type=Path,
        help=(
            "FIDE-style divisional k JSON. "
            f"Default: {DEFAULT_FIDE_K_CONFIG_PATH}."
        ),
    )
    return parser


def parse_date(value: str) -> Date:
    try:
        year_text, month_text = value.split("/")
        return Date(Year(int(year_text)), Month(int(month_text)))
    except Exception as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date {value!r}; expected YYYY/MM"
        ) from exc


def parse_bool(value: str) -> bool:
    normalised = value.strip().lower()
    if normalised in {"1", "true", "yes", "y", "on"}:
        return True
    if normalised in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(
        f"Invalid boolean {value!r}; expected true/false or yes/no"
    )


def main() -> None:
    args = build_parser().parse_args()
    initial_policy = (
        FileInitialRatingPolicy.load(args.initial_ratings_file)
        if args.initial_ratings_file is not None
        else ConstantInitialRatingPolicy(
            DEFAULT_ELO if args.initial_rating is None else args.initial_rating
        )
    )
    k_policy = (
        ConstantKPolicy(args.k_value)
        if args.k_value is not None
        else FideKPolicy.load(
            DEFAULT_FIDE_K_CONFIG_PATH
            if args.k_config is None
            else args.k_config
        )
    )

    result, outputs = run_clean_elo(
        history=get_history(),
        start_date=args.start,
        initial_rating_policy=initial_policy,
        k_policy=k_policy,
        output_root=args.output_root,
        count_absences=args.count_absences,
    )
    print(f"Target mean: {result.target_mean:.12f}")
    print(f"Basho files: {len(outputs.basho_csvs)}")
    print(f"Inferred absences: {result.inferred_absence_count}")
    print(f"Run directory: {outputs.output_root}")
    print(f"Manifest: {outputs.manifest_json}")


if __name__ == "__main__":
    main()

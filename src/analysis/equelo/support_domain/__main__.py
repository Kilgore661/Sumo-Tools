"""Build Equelo support-domain evidence reports."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.fixed_v2.build import load_bios, oracle_collapse_mode
from src.analysis.equelo.fixed_v2.model import FP_SOURCE
from src.analysis.equelo.support_domain.measure import measure_support
from src.analysis.equelo.support_domain.reports import (
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_THRESHOLDS,
    write_support_domain_reports,
)
from src.analysis.probability.builder import load_ratings_csv
from src.infra.live_store.api import get_history


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write Equelo support-domain evidence CSVs."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory for support-domain evidence reports.",
    )
    parser.add_argument(
        "--fp-source",
        type=Path,
        default=FP_SOURCE,
        help="Fixed-point ratings CSV to join into support reports.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        action="append",
        dest="thresholds",
        help=(
            "Support threshold s. May be supplied more than once. "
            "Defaults to the standard exploratory set."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_history = get_history()
    oracle = make_oracle(
        raw_history,
        load_bios(),
        collapse_mode=oracle_collapse_mode(),
    )
    measurement = measure_support(oracle.history)
    thresholds = tuple(args.thresholds) if args.thresholds else DEFAULT_THRESHOLDS
    outputs = write_support_domain_reports(
        measurement=measurement,
        fixed_point_ratings=load_ratings_csv(args.fp_source),
        thresholds=thresholds,
        output_root=args.output_root,
    )

    print("Equelo support-domain reports written")
    print(f"Support CSV: {outputs.support_csv}")
    print(f"Threshold summary: {outputs.threshold_summary_csv}")
    for path in outputs.exclusion_csvs:
        print(f"Exclusions: {path}")


if __name__ == "__main__":
    main()

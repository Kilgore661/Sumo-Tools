"""Command-line entry point for the Equelo2 January-1989 boundary audit."""

from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

from .analysis import run_audit


DEFAULT_INPUT = Path(
    "files/output/analysis/equelo2_baseline/"
    "full_history_1958_01_to_2026_07/1989_01_handover.csv"
)
DEFAULT_RATING_LEDGER = DEFAULT_INPUT.parent / "rating_ledger.csv"
DEFAULT_OUTPUT = Path("files/output/analysis/equelo2_boundary_audit/1989_01")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compare matched incumbents' historical and fresh Elo-89 ratings "
            "at the start of the January 1989 basho."
        )
    )
    parser.add_argument("--handover", type=Path, default=DEFAULT_INPUT)
    parser.add_argument(
        "--rating-ledger", type=Path, default=DEFAULT_RATING_LEDGER
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    started = perf_counter()
    outputs = run_audit(
        args.handover,
        args.output,
        rating_ledger_path=args.rating_ledger,
    )
    elapsed = perf_counter() - started
    print(f"Matched rikishi: {outputs.matched_count:,}")
    print(f"Output: {outputs.output_root.resolve()}")
    print(f"Findings: {outputs.findings.resolve()}")
    print(f"Wall clock: {elapsed:.3f} seconds")


if __name__ == "__main__":
    main()

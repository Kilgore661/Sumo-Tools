"""Bootstrap the raw SumoDB source cache for a clean workspace.

This command is a small empirical wrapper around the tracker planner and
downloader. It does not build History, start the live store, or run analysis;
it only ensures the raw HTML files required by the current planner exist.
"""

from __future__ import annotations

import argparse
from datetime import datetime

from src.infra.tracker.config import TrackerConfig
from src.infra.tracker.ledger import InMemoryLedger
from src.infra.tracker.planner import get_retrieval_plan
from src.infra.tracker.scraper.downloader import download
from src.infra.tracker.types import RetrievalResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download raw SumoDB source HTML required for parser2."
    )
    parser.add_argument(
        "--as-of",
        type=datetime.fromisoformat,
        default=None,
        help=(
            "Plan as of this local datetime, in ISO format. "
            "Defaults to the current local time."
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    as_of = args.as_of if args.as_of is not None else datetime.now()

    plan = get_retrieval_plan(
        as_of,
        InMemoryLedger(),
        TrackerConfig(),
    )
    print(
        "[bootstrap_sources] planned "
        f"{len(plan.banzuke_dates)} banzuke pages and "
        f"{len(plan.daily_results)} daily result pages "
        f"as of {as_of.isoformat(sep=' ', timespec='seconds')}"
    )

    result = download(plan)
    print(f"[bootstrap_sources] retrieval result: {result.name}")
    if result == RetrievalResult.FAILURE:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

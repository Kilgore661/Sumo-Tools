"""Command-line entry point for bounded P89 literal-prior fitting."""

from __future__ import annotations

import argparse
from pathlib import Path
import re

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import Date

from ..config import DEFAULT_LAST_PRIOR_BASHO
from .producer import EPSILON, produce_prior


def parse_basho(value: str) -> Date:
    match = re.fullmatch(r"(\d{4})[-/](\d{2})", value.strip())
    if match is None:
        raise argparse.ArgumentTypeError("expected YYYY-MM or YYYY/MM")
    year, month = (int(part) for part in match.groups())
    try:
        return Date.from_ints(year, month)
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def _load_history(path: Path | None):
    if path is None:
        return get_history(), "live store"
    archive = path if path.suffix.lower() == ".zip" else path.with_suffix(".zip")
    if not archive.is_file():
        raise FileNotFoundError(f"History archive does not exist: {archive}")
    return (
        load_history_with_annotations(str(archive.with_suffix(""))),
        f"annotated History zip: {archive.resolve()}",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Use this annotated History zip instead of the live provider.",
    )
    parser.add_argument(
        "--last-prior-basho",
        type=parse_basho,
        default=DEFAULT_LAST_PRIOR_BASHO,
        help=(
            "Last basho included in the prior fit (inclusive; YYYY-MM or "
            f"YYYY/MM; default {DEFAULT_LAST_PRIOR_BASHO})."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    history, source = _load_history(args.history_zip)

    def report(row) -> None:
        print(
            f"iteration {row.iteration:3d}: "
            f"maximum change {row.max_prior_change:.6f}"
        )

    run = produce_prior(
        history,
        last_prior_basho=args.last_prior_basho,
        history_source=source,
        progress=report,
    )
    print(f"Output: {run.root.resolve()}")
    print(f"Convergence threshold: {EPSILON:.6f}")
    print(f"Iterations taken: {run.result.iterations}")
    print(f"Final maximum change: {run.result.final_delta:.6f}")
    print(f"Converged: {run.result.converged}")
    print(f"Total run time: {run.runtime_seconds:.3f} seconds")
    return 0 if run.result.converged else 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Refresh the persisted Future snapshot from SumoDB."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History

from .persistence import DEFAULT_OUTPUT_ROOT
from .scraper import refresh_future


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download and persist available torikumi.")
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Use an explicit annotated History zip instead of the live store.",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)
    history = load_history(args.history_zip)
    future = refresh_future(history, output_root=args.output_root)
    print(args.output_root / "future.json")
    available = ", ".join(str(int(day.day)) for day in future.days) or "none"
    print(f"Available torikumi days: {available}")
    return 0


def load_history(history_zip: Path | None) -> History:
    """Load the selected History, defaulting to the published live store."""

    if history_zip is None:
        return get_history()
    zipless = (
        history_zip.with_suffix("")
        if history_zip.suffix == ".zip"
        else history_zip
    )
    return load_history_with_annotations(str(zipless))


if __name__ == "__main__":
    raise SystemExit(main())


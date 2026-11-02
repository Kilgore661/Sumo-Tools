"""Refresh the persisted Future snapshot from SumoDB."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.live_store.api import get_history
from src.infra.new_banzuke.api import NEW_BANZUKE_JSON, load_new_banzuke
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History

from .persistence import DEFAULT_OUTPUT_ROOT, load_future
from .scraper import TorikumiRefreshError, refresh_future
from .target import resolve_torikumi_target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download and persist available torikumi.")
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Use an explicit annotated History zip instead of the live store.",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--new-banzuke", type=Path, default=NEW_BANZUKE_JSON)
    args = parser.parse_args(argv)
    history = load_history(args.history_zip)
    new_banzuke = (
        load_new_banzuke(args.new_banzuke)
        if args.new_banzuke.is_file()
        else None
    )
    target = resolve_torikumi_target(history, new_banzuke)
    if target is None:
        print("No active or published upcoming basho requires Torikumi refresh")
        return 0
    print(f"Torikumi target: {target.date} ({target.source})")
    try:
        future = refresh_future(
            history,
            target=target,
            output_root=args.output_root,
        )
    except TorikumiRefreshError as exc:
        existing_path = args.output_root / "future.json"
        if existing_path.is_file():
            existing = load_future(existing_path)
            if existing.date == target.date:
                print(
                    f"[torikumi] refresh failed; retaining {target.date} "
                    f"snapshot: {exc}"
                )
                return 0
        print(f"[torikumi] refresh failed for {target.date}: {exc}")
        return 1
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


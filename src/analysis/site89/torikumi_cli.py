"""Add Torikumi data to an existing site89 bundle without rebuilding ratings."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.infra.new_banzuke.api import NEW_BANZUKE_JSON, load_new_banzuke
from src.infra.torikumi import load_future

from .torikumi import update_existing_bundle


DEFAULT_BUNDLE_ROOT = Path("files/output/analysis/site89_bundle")
DEFAULT_FUTURE_PATH = Path("files/output/torikumi/future.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Add rating-annotated Torikumi data to an existing site89 bundle."
    )
    parser.add_argument("--history-zip", type=Path, required=True)
    parser.add_argument("--future", type=Path, default=DEFAULT_FUTURE_PATH)
    parser.add_argument("--bundle-root", type=Path, default=DEFAULT_BUNDLE_ROOT)
    parser.add_argument("--new-banzuke", type=Path, default=NEW_BANZUKE_JSON)
    args = parser.parse_args(argv)
    zipless = (
        args.history_zip.with_suffix("")
        if args.history_zip.suffix == ".zip"
        else args.history_zip
    )
    history = load_history_with_annotations(str(zipless))
    future = load_future(args.future)
    upcoming_banzuke = None
    if future.date not in history:
        if not args.new_banzuke.is_file():
            raise FileNotFoundError(
                f"Upcoming Torikumi {future.date} requires {args.new_banzuke}"
            )
        new_banzuke = load_new_banzuke(args.new_banzuke)
        if new_banzuke.date != future.date:
            raise ValueError(
                f"Torikumi target {future.date} does not match New Banzuke "
                f"{new_banzuke.date}"
            )
        upcoming_banzuke = new_banzuke.to_banzuke()
    paths = update_existing_bundle(
        history=history,
        future=future,
        bundle_root=args.bundle_root,
        upcoming_banzuke=upcoming_banzuke,
    )
    print(f"Published {len(paths) - 1} Torikumi day(s) to {args.bundle_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

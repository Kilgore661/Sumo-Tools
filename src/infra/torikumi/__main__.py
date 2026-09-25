"""Refresh the persisted Future snapshot from SumoDB."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.persistence.annotated_serialiser import load_history_with_annotations

from .persistence import DEFAULT_OUTPUT_ROOT
from .scraper import refresh_future


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download and persist available torikumi.")
    parser.add_argument("--history-zip", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)
    zipless = args.history_zip.with_suffix("") if args.history_zip.suffix == ".zip" else args.history_zip
    history = load_history_with_annotations(str(zipless))
    future = refresh_future(history, output_root=args.output_root)
    print(args.output_root / "future.json")
    print(f"Available torikumi days: {', '.join(str(int(day.day)) for day in future.days) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


"""Build the static GOAT factual dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.goat.facts import build_goat_facts
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations


DEFAULT_OUTPUT_ROOT = Path("files/output/goat")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Load History from a zip instead of the live store.",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def load_history(path: Path):
    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def main() -> None:
    args = build_parser().parse_args()
    history = load_history(args.history_zip) if args.history_zip else get_history()
    outputs = build_goat_facts(history, args.output_root)
    print(f"GOAT facts: {outputs.output_root}")


if __name__ == "__main__":
    main()

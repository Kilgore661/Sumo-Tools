from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.get_bios.api import load_bio_store
from src.infra.get_bios.parser import OUTPUT_JSON as DEFAULT_BIOS_JSON
from src.infra.live_store.api import get_history
from src.infra.parser.parser2_utils import RESULTS_DIR
from src.infra.persistence.annotated_serialiser import load_history_with_annotations

from ..eligible_rikishi import parse_date
from .producer import DEFAULT_OUTPUT_ROOT, produce


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epoch", type=parse_date)
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument("--bios-json", type=Path, default=DEFAULT_BIOS_JSON)
    parser.add_argument("--results-root", type=Path, default=Path(RESULTS_DIR))
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.history_zip is None:
        history = get_history()
        history_source = "live_store"
    else:
        archive = args.history_zip if args.history_zip.suffix.lower() == ".zip" else args.history_zip.with_suffix(".zip")
        history = load_history_with_annotations(str(archive.with_suffix("")))
        history_source = str(archive)
    paths = produce(
        history,
        load_bio_store(args.bios_json),
        epoch=args.epoch,
        results_root=args.results_root,
        output_root=args.output_root,
        source_manifest={"history": history_source, "bios": str(args.bios_json), "daily_results": str(args.results_root)},
    )
    print(f"Output: {paths.root}")


if __name__ == "__main__":
    main()

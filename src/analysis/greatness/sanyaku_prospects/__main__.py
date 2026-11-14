from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.get_bios.api import load_bio_store
from src.infra.get_bios.career_rows import DEFAULT_RIKISHI_PAGES
from src.infra.get_bios.parser import OUTPUT_JSON as DEFAULT_BIOS_JSON
from src.infra.live_store.api import get_history
from src.infra.parser.parser2_utils import RESULTS_DIR
from src.infra.persistence.annotated_serialiser import load_history_with_annotations

from ..eligible_rikishi import parse_date
from .cached_charts import render_cached_career_charts
from .producer import DEFAULT_OUTPUT_ROOT, produce


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epoch", type=parse_date)
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument("--bios-json", type=Path, default=DEFAULT_BIOS_JSON)
    parser.add_argument("--results-root", type=Path, default=Path(RESULTS_DIR))
    parser.add_argument("--rikishi-pages-root", type=Path, default=DEFAULT_RIKISHI_PAGES)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Recompute the complete analysis bundle before rendering charts.",
    )
    parser.add_argument(
        "--chart-rikishi-id",
        type=int,
        action="append",
        default=[],
        help="Rikishi ID to chart; repeat for more than one career.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    bios = load_bio_store(args.bios_json)
    if not args.rebuild:
        try:
            charts = render_cached_career_charts(
                output_root=args.output_root,
                bios=bios,
                rikishi_ids=tuple(args.chart_rikishi_id),
            )
        except (FileNotFoundError, KeyError, ValueError) as error:
            parser.error(str(error))
        print(f"Cached analysis: {args.output_root}")
        for chart in charts:
            print(f"Chart: {chart}")
        return

    if args.history_zip is None:
        history = get_history()
        history_source = "live_store"
    else:
        archive = args.history_zip if args.history_zip.suffix.lower() == ".zip" else args.history_zip.with_suffix(".zip")
        history = load_history_with_annotations(str(archive.with_suffix("")))
        history_source = str(archive)
    paths = produce(
        history,
        bios,
        epoch=args.epoch,
        results_root=args.results_root,
        output_root=args.output_root,
        source_manifest={
            "history": history_source,
            "bios": str(args.bios_json),
            "daily_results": str(args.results_root),
            "rikishi_pages": str(args.rikishi_pages_root),
        },
        chart_rikishi_ids=tuple(args.chart_rikishi_id),
        career_pages_root=args.rikishi_pages_root,
    )
    print(f"Output: {paths.root}")
    for chart in paths.career_charts:
        print(f"Chart: {chart}")


if __name__ == "__main__":
    main()

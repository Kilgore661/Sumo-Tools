"""Create current-banzuke Elo89 pairwise probability heatmaps."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from src.analysis.elo89.api import Elo89Artifacts
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Division

from .model import build_snapshot
from .render import write_pairwise_html


DEFAULT_HISTORY_ZIP = Path("files/output/Historys/1958_01 to 2026_11.zip")
DEFAULT_RATINGS_ROOT = Path("files/output/analysis/site89_bundle/sources/elo89")
DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/probability/pairwise_matrix")
DIVISIONS = {division.name.lower(): division for division in Division}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, default=DEFAULT_HISTORY_ZIP)
    parser.add_argument("--ratings-root", type=Path, default=DEFAULT_RATINGS_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--division", choices=tuple(DIVISIONS), default="makuuchi")
    args = parser.parse_args()

    history_source = args.history_zip.resolve()
    if not history_source.is_file() or history_source.suffix.lower() != ".zip":
        parser.error(f"History zip not found: {history_source}")
    history = load_history_with_annotations(str(history_source.with_suffix("")))
    if not history:
        parser.error("History is empty")
    date = max(history)
    ratings = Elo89Artifacts.load(args.ratings_root)
    rating_map = ratings.basho_end_ratings.get(str(date))
    if rating_map is None:
        parser.error(f"Elo89 artifacts contain no end ratings for {date}")
    q = float(ratings.manifest.get("q", math.nan))
    if not math.isfinite(q) or q <= 0:
        parser.error("Elo89 manifest contains no positive finite q")

    basho = history(date)
    snapshot = build_snapshot(
        basho=date,
        latest_day=int(basho.summary.last_defined()),
        banzuke=basho.banzuke,
        ratings=rating_map,
        division=DIVISIONS[args.division],
        q=q,
    )
    dated_root = args.output_root / str(date).replace("/", "-")
    paths = tuple(
        write_pairwise_html(
            snapshot=snapshot,
            order=order,
            output_path=dated_root / f"{args.division}_by_{order}.html",
        )
        for order in ("rating", "chii")
    )
    for path in paths:
        print(path.resolve())


if __name__ == "__main__":
    main()

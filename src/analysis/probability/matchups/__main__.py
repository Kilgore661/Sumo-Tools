from __future__ import annotations

import argparse
import datetime
from pathlib import Path

from src.analysis.probability.matchups.empirical import compute_empirical_matchups
from src.analysis.probability.matchups.reports import write_empirical_outputs
from src.infra.config import EPOCH
from src.infra.connect import connect
from src.sumo_core.History import History


OUTPUT_DIR = Path("files/output/probability/matchups")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute observed chii matchup probabilities from oracle-cleaned bouts."
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser


def _slice_history_years(history: History, start: int, end: int) -> History:
    return History({
        date: history(date)
        for date in sorted(history.keys())
        if start <= date.year <= end
    })


def main() -> None:
    args = _build_parser().parse_args()

    raw_history = _slice_history_years(
        history=connect(args.start, args.end, use_zip=args.zip),
        start=args.start,
        end=args.end,
    )
    results = compute_empirical_matchups(
        raw_history=raw_history,
        start_year=args.start,
        end_year=args.end,
    )
    paths = write_empirical_outputs(
        results=results,
        output_dir=args.output_dir,
    )

    print(f"Included probability bouts: {results.metadata.included_probability_bouts}")
    print(f"Same-chii bouts: {results.metadata.same_chii_bouts}")
    print(f"Bout CSV: {paths['bout_csv']}")
    print(f"Chii-pair CSV: {paths['chii_pair_csv']}")
    print(f"Selected-chii CSV: {paths['selected_chii_csv']}")
    print(f"Sideless chii-pair CSV: {paths['sideless_chii_pair_csv']}")
    print(f"Sideless distribution CSV: {paths['sideless_distribution_csv']}")
    print(f"Metadata: {paths['metadata_json']}")


if __name__ == "__main__":
    main()

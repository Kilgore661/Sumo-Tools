from __future__ import annotations

import argparse
from pathlib import Path

from src.analysis.equelo.fixed_v1 import model as fixed_v1_model
from src.analysis.probability.matchups.charts import (
    write_equelo_trace_chart,
    write_observed_trace_chart,
)
from src.analysis.probability.matchups.traces import (
    build_equelo_trace_points,
    build_observed_trace_points,
    build_sideless_ratings,
    filter_observed_points_to_rating_domain,
    write_trace_outputs,
)


OUTPUT_DIR = Path("files/output/probability/matchups")
SIDELESS_PAIR_CSV = OUTPUT_DIR / "empirical_sideless_chii_pairs.csv"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build observed and Equelo sideless chii matchup trace artefacts."
    )
    parser.add_argument("--sideless-pair-csv", type=Path, default=SIDELESS_PAIR_CSV)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--fixed-v1-output-root", type=Path, default=fixed_v1_model.OUTPUT_ROOT)
    parser.add_argument("--q", type=float, default=fixed_v1_model.Q)
    parser.add_argument("--initial-trace", default="Y1")
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    raw_observed_points = build_observed_trace_points(args.sideless_pair_csv)
    sideless_ratings = build_sideless_ratings(output_root=args.fixed_v1_output_root)
    observed_points = filter_observed_points_to_rating_domain(
        raw_observed_points,
        sideless_ratings,
    )
    equelo_points = build_equelo_trace_points(
        observed_points=observed_points,
        sideless_ratings=sideless_ratings,
        q=args.q,
    )
    paths = write_trace_outputs(
        output_dir=args.output_dir,
        observed_points=observed_points,
        sideless_ratings=sideless_ratings,
        equelo_points=equelo_points,
        fixed_v1_output_root=args.fixed_v1_output_root,
        q=args.q,
    )

    observed_chart = write_observed_trace_chart(
        observed_points,
        args.output_dir / "observed_sideless_matchup_traces.html",
        initially_visible=args.initial_trace,
    )
    equelo_chart = write_equelo_trace_chart(
        equelo_points,
        args.output_dir / "equelo_sideless_matchup_traces.html",
        initially_visible=args.initial_trace,
    )

    print(f"Raw observed trace points: {len(raw_observed_points)}")
    print(f"Observed trace points in rating domain: {len(observed_points)}")
    print(f"Observed trace points excluded by rating domain: {len(raw_observed_points) - len(observed_points)}")
    print(f"Equelo trace points: {len(equelo_points)}")
    print(f"Observed trace CSV: {paths['observed_trace_csv']}")
    print(f"Equelo ratings CSV: {paths['equelo_ratings_csv']}")
    print(f"Equelo trace CSV: {paths['equelo_trace_csv']}")
    print(f"Trace metadata: {paths['trace_metadata_json']}")
    print(f"Observed chart: {observed_chart}")
    print(f"Equelo chart: {equelo_chart}")


if __name__ == "__main__":
    main()

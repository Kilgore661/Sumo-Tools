"""Command-line entry point for the boundary-monotonicity experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..evidence_bridge import (
    DEFAULT_SUPPORT_THRESHOLD,
    load_makuuchi_juryo_profile,
    resolve_profile_path,
)
from .experiment import (
    DEFAULT_BOOTSTRAP_SAMPLES,
    DEFAULT_BOTTOM_SIZE,
    DEFAULT_DAYS_PER_EVENT,
    DEFAULT_EVENTS,
    DEFAULT_GAP,
    DEFAULT_GROUP_SIZE,
    DEFAULT_HISTORICAL_Q,
    DEFAULT_HISTORICAL_ENDPOINT_DIFFERENCE,
    DEFAULT_HISTORICAL_MAXIMUM_REVERSAL,
    DEFAULT_LEARNING_FRACTION,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_Q,
    DEFAULT_RUNS,
    DEFAULT_SEED,
    DEFAULT_TAIL_GROUPS,
    DEFAULT_TOP_SIZE,
    ExperimentConfig,
    run_experiment,
    write_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Test whether evidence-shaped Makuuchi-Juryo scheduling can "
            "produce a lower-boundary Elo reversal from monotonic skills."
        )
    )
    parser.add_argument("--profile", type=Path, default=None)
    parser.add_argument(
        "--support-threshold",
        type=int,
        default=DEFAULT_SUPPORT_THRESHOLD,
    )
    parser.add_argument("--top-size", type=int, default=DEFAULT_TOP_SIZE)
    parser.add_argument(
        "--bottom-size", type=int, default=DEFAULT_BOTTOM_SIZE
    )
    parser.add_argument(
        "--days-per-event",
        type=int,
        default=DEFAULT_DAYS_PER_EVENT,
    )
    parser.add_argument("--events", type=int, default=DEFAULT_EVENTS)
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--q", type=float, default=DEFAULT_Q)
    parser.add_argument("--gap", type=float, default=DEFAULT_GAP)
    parser.add_argument(
        "--learning-fraction",
        type=float,
        default=DEFAULT_LEARNING_FRACTION,
    )
    parser.add_argument(
        "--tail-groups", type=int, default=DEFAULT_TAIL_GROUPS
    )
    parser.add_argument(
        "--group-size", type=int, default=DEFAULT_GROUP_SIZE
    )
    parser.add_argument(
        "--bootstrap-samples",
        type=int,
        default=DEFAULT_BOOTSTRAP_SAMPLES,
    )
    parser.add_argument(
        "--historical-endpoint-difference",
        type=float,
        default=DEFAULT_HISTORICAL_ENDPOINT_DIFFERENCE,
    )
    parser.add_argument(
        "--historical-maximum-reversal",
        type=float,
        default=DEFAULT_HISTORICAL_MAXIMUM_REVERSAL,
    )
    parser.add_argument(
        "--historical-q",
        type=float,
        default=DEFAULT_HISTORICAL_Q,
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--progress-every", type=int, default=0)
    parser.add_argument(
        "--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = ExperimentConfig(
        top_size=args.top_size,
        bottom_size=args.bottom_size,
        days_per_event=args.days_per_event,
        events=args.events,
        runs=args.runs,
        q=args.q,
        gap=args.gap,
        learning_fraction=args.learning_fraction,
        tail_groups=args.tail_groups,
        group_size=args.group_size,
        bootstrap_samples=args.bootstrap_samples,
        historical_endpoint_difference=(
            args.historical_endpoint_difference
        ),
        historical_maximum_reversal=(
            args.historical_maximum_reversal
        ),
        historical_q=args.historical_q,
        seed=args.seed,
        progress_every=args.progress_every,
    )
    config.validate()
    profile_path = resolve_profile_path(args.profile)
    profile = load_makuuchi_juryo_profile(
        path=profile_path,
        support_threshold=args.support_threshold,
        top_size=config.top_size,
    )
    result = run_experiment(profile=profile, config=config)
    outputs = write_outputs(
        result=result,
        profile=profile,
        output_root=args.output_root,
    )
    print(f"Run directory: {outputs.run_directory}")
    for scenario in result.scenarios:
        summary = scenario.summary
        print(
            f"{summary.scenario}: "
            f"ensemble_endpoint={summary.ensemble_endpoint_reversal:.3f}, "
            f"ensemble_max={summary.ensemble_maximum_reversal:.3f}, "
            f"endpoint_target_rate={summary.endpoint_target_rate:.4f}, "
            f"maximum_target_rate={summary.maximum_target_rate:.4f}, "
            f"mean_bridge_bouts={summary.mean_bridge_bouts_per_run_event:.3f}"
        )
    print(f"Summary: {outputs.scenario_summary_csv}")
    print(f"Boundary groups: {outputs.boundary_groups_csv}")
    print(f"Run reversals: {outputs.run_reversals_csv}")

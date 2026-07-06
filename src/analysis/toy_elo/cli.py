from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path

from .audit import make_run_dir, write_manifest
from .metrics import (
    MetricsRow,
    build_metrics,
    first_stable_event,
    persistence_after_first_stable,
)
from .model import BaselineModel
from .simulation import simulate_ensemble
from .tables import write_metrics_table, write_ratings_table


DEFAULT_OUTPUT = Path("files/output/toy_elo_simulation/ensemble_mean.csv")
DEFAULT_SAMPLE_OUTPUT = Path("files/output/toy_elo_simulation/sample_run.csv")
DEFAULT_METRICS_OUTPUT = Path("files/output/toy_elo_simulation/convergence_metrics.csv")
DEFAULT_OUTPUT_ROOT = Path("files/output/toy_elo_simulation")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show fixed-k Elo approaching hidden logistic skills in ensemble mean."
    )
    parser.add_argument("--players", type=int, default=10)
    parser.add_argument("--max-rating", type=float, default=360.0)
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--learning-fraction", type=float, default=0.125)
    parser.add_argument("--events", type=int, default=200)
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument("--stable-epsilon", type=float, default=4.0)
    parser.add_argument("--slope-epsilon", type=float, default=0.05)
    parser.add_argument("--stable-window", type=int, default=25)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def print_summary(
    *,
    model: BaselineModel,
    skills: list[float],
    means: list[list[float]],
    sample_rows: list[list[float]],
    metrics: list[MetricsRow],
    stable_epsilon: float,
    slope_epsilon: float,
    stable_window: int,
) -> None:
    checkpoints = sorted({0, 1, 2, 5, 10, 25, 50, 100, len(means) - 1})
    checkpoints = [point for point in checkpoints if point < len(means)]

    print(f"Players: {model.player_count}")
    print(f"Rating span m: {model.max_rating:.2f}")
    print(f"Baseline b: {model.baseline:.2f}")
    print(f"Adjacent gap: {model.gap:.2f}")
    print(f"q: {model.q:.2f}")
    print(f"Implied p_adj: {100.0 * model.adjacent_win_probability:.2f}%")
    print(f"k: {model.k:.2f} ({model.learning_fraction:.4f} * gap)")
    print(
        f"Stable rule: mean gap RMSE <= {stable_epsilon:.2f}, "
        f"|{stable_window}-round slope| <= {slope_epsilon:.3f}, "
        f"for {stable_window} consecutive events"
    )
    print()
    print(
        f"{'events':>8} {'mean R0-R1':>12} {'sample R0-R1':>14} "
        f"{'mean RMSE':>10} {'sample RMSE':>11} {'stable':>7}"
    )
    for iteration in checkpoints:
        mean_gap = means[iteration][0] - means[iteration][1] if len(skills) > 1 else 0.0
        sample_gap = sample_rows[iteration][0] - sample_rows[iteration][1] if len(skills) > 1 else 0.0
        metric = metrics[iteration]
        print(
            f"{iteration:>8} "
            f"{mean_gap:>12.2f} "
            f"{sample_gap:>14.2f} "
            f"{float(metric['mean_gap_rmse']):>10.2f} "
            f"{float(metric['sample_gap_rmse']):>11.2f} "
            f"{str(bool(metric['stable_window_met'])):>7}"
        )

    first_event = first_stable_event(metrics)
    persistence = persistence_after_first_stable(metrics)
    print()
    if first_event is None:
        print("Stable window first reached: never")
    else:
        print(f"Stable window first reached: event {first_event}")
    if persistence is None:
        print("Persistence after first stable window: n/a")
    else:
        print(f"Persistence after first stable window: {100.0 * persistence:.1f}%")


def main() -> None:
    args = build_parser().parse_args()
    started_at = datetime.now().astimezone()
    start_time = time.perf_counter()
    run_dir = make_run_dir(args.output_root, seed=args.seed, timestamp=started_at)
    output = run_dir / DEFAULT_OUTPUT.name
    sample_output = run_dir / DEFAULT_SAMPLE_OUTPUT.name
    metrics_output = run_dir / DEFAULT_METRICS_OUTPUT.name
    manifest_output = run_dir / "manifest.json"

    model = BaselineModel(
        player_count=args.players,
        max_rating=args.max_rating,
        q=args.q,
        learning_fraction=args.learning_fraction,
    )
    skills, means, sample_rows = simulate_ensemble(
        model=model,
        events=args.events,
        runs=args.runs,
        seed=args.seed,
        progress_every=args.progress_every,
    )
    metrics = build_metrics(
        skills=skills,
        means=means,
        sample_rows=sample_rows,
        stable_epsilon=args.stable_epsilon,
        slope_epsilon=args.slope_epsilon,
        stable_window=args.stable_window,
    )
    write_ratings_table(output, means)
    write_ratings_table(sample_output, sample_rows)
    write_metrics_table(metrics_output, metrics)
    first_event = first_stable_event(metrics)
    persistence = persistence_after_first_stable(metrics)
    finished_at = datetime.now().astimezone()
    write_manifest(
        manifest_output,
        {
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "elapsed_seconds": round(time.perf_counter() - start_time, 6),
            "parameters": {
                "players": args.players,
                "max_rating": args.max_rating,
                "q": args.q,
                "learning_fraction": args.learning_fraction,
                "events": args.events,
                "runs": args.runs,
                "seed": args.seed,
                "stable_epsilon": args.stable_epsilon,
                "slope_epsilon": args.slope_epsilon,
                "stable_window": args.stable_window,
            },
            "derived": {
                "baseline": model.baseline,
                "gap": model.gap,
                "k": model.k,
                "adjacent_win_probability": model.adjacent_win_probability,
                "matches_per_event": args.players * (args.players - 1) // 2,
                "matches_per_run": args.events * args.players * (args.players - 1) // 2,
                "total_simulated_matches": args.runs * args.events * args.players * (args.players - 1) // 2,
            },
            "stability": {
                "first_stable_event": first_event,
                "persistence_after_first_stable": persistence,
                "final_mean_gap_rmse": float(metrics[-1]["mean_gap_rmse"]),
                "final_sample_gap_rmse": float(metrics[-1]["sample_gap_rmse"]),
            },
            "outputs": {
                "run_dir": str(run_dir),
                "ensemble_mean": str(output),
                "sample_run": str(sample_output),
                "convergence_metrics": str(metrics_output),
                "manifest": str(manifest_output),
            },
        },
    )
    print_summary(
        model=model,
        skills=skills,
        means=means,
        sample_rows=sample_rows,
        metrics=metrics,
        stable_epsilon=args.stable_epsilon,
        slope_epsilon=args.slope_epsilon,
        stable_window=args.stable_window,
    )
    print(f"\nWrote run output to {run_dir}")
    print(f"Wrote ensemble mean ratings to {output}")
    print(f"Wrote one individual run to {sample_output}")
    print(f"Wrote convergence metrics to {metrics_output}")
    print(f"Wrote manifest to {manifest_output}")

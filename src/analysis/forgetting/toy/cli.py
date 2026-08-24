"""Command-line interface for the first forgetting toy experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

from .experiment import DEFAULT_OUTPUT_ROOT, run_development_experiment
from .model import ToyWorld


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Replay one persisted fixed-skill toy history from true and flat "
            "initial ratings and measure initialization forgetting."
        )
    )
    parser.add_argument("--players", type=int, default=10)
    parser.add_argument("--latent-gap", type=float, default=40.0)
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--k", type=float, default=5.0)
    parser.add_argument("--events", type=int, default=500)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--persistence-events", type=int, default=25)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_development_experiment(
        world=ToyWorld(
            player_count=args.players,
            latent_gap=args.latent_gap,
            q=args.q,
            k=args.k,
        ),
        events=args.events,
        seed=args.seed,
        persistence_events=args.persistence_events,
        output_root=args.output_root,
    )
    initial = result.metrics[0]
    final = result.metrics[-1]
    print(f"Wrote forgetting development run to {result.run_directory.resolve()}")
    print(
        "All-pair forecast disagreement: "
        f"{initial.forecast_distance:.6f} -> {final.forecast_distance:.6f}"
    )
    print(
        "Centred rating-state disagreement: "
        f"{initial.state_distance:.6f} -> {final.state_distance:.6f}"
    )
    for row in result.landmarks:
        label = (
            f"{100 * row.target:.0f}% reduction"
            if row.kind == "fractional_reduction"
            else f"absolute {row.target:g}"
        )
        reached = "censored" if row.right_censored else f"event {row.first_event}"
        print(f"{label}: {reached}")


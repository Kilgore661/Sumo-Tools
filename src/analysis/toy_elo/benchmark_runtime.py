from __future__ import annotations

import argparse
import csv
import statistics
import time
from datetime import datetime
from pathlib import Path

from .audit import make_run_dir, write_manifest
from .model import BaselineModel
from .runtime_model import match_count
from .simulation import simulate_ensemble


DEFAULT_OUTPUT_ROOT = Path("files/output/toy_elo_runtime_benchmark")


def parse_ints(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark toy Elo runtime for a grid of n, r, and h.")
    parser.add_argument("--players", default="10,20,40,60")
    parser.add_argument("--runs", default="20,100")
    parser.add_argument("--events", default="20,100")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--learning-fraction", type=float, default=0.125)
    parser.add_argument("--gap", type=float, default=40.0)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def benchmark_case(
    *,
    players: int,
    runs: int,
    events: int,
    repeats: int,
    q: float,
    learning_fraction: float,
    gap: float,
    seed: int,
) -> dict[str, float | int]:
    model = BaselineModel(
        player_count=players,
        max_rating=gap * (players - 1),
        q=q,
        learning_fraction=learning_fraction,
    )
    elapsed_values = []
    for repeat in range(repeats):
        start = time.perf_counter()
        simulate_ensemble(
            model=model,
            events=events,
            runs=runs,
            seed=seed + repeat,
            progress_every=0,
        )
        elapsed_values.append(time.perf_counter() - start)

    matches = match_count(players=players, runs=runs, events=events)
    median_seconds = statistics.median(elapsed_values)
    return {
        "players": players,
        "runs": runs,
        "events": events,
        "matches": matches,
        "repeats": repeats,
        "min_seconds": min(elapsed_values),
        "median_seconds": median_seconds,
        "max_seconds": max(elapsed_values),
        "seconds_per_match": median_seconds / matches,
        "matches_per_second": matches / median_seconds,
    }


def write_rows(path: Path, rows: list[dict[str, float | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "players",
        "runs",
        "events",
        "matches",
        "repeats",
        "min_seconds",
        "median_seconds",
        "max_seconds",
        "seconds_per_match",
        "matches_per_second",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = build_parser().parse_args()
    started_at = datetime.now().astimezone()
    run_dir = make_run_dir(args.output_root, seed=args.seed, timestamp=started_at)
    rows = []

    for players in parse_ints(args.players):
        for runs in parse_ints(args.runs):
            for events in parse_ints(args.events):
                row = benchmark_case(
                    players=players,
                    runs=runs,
                    events=events,
                    repeats=args.repeats,
                    q=args.q,
                    learning_fraction=args.learning_fraction,
                    gap=args.gap,
                    seed=args.seed,
                )
                rows.append(row)
                print(
                    f"n={players} r={runs} h={events} "
                    f"matches={row['matches']} median={row['median_seconds']:.4f}s "
                    f"({row['matches_per_second']:.0f} matches/s)"
                )

    seconds_per_match = statistics.median(float(row["seconds_per_match"]) for row in rows)
    output = run_dir / "runtime_benchmark.csv"
    manifest = run_dir / "manifest.json"
    write_rows(output, rows)
    write_manifest(
        manifest,
        {
            "started_at": started_at.isoformat(),
            "finished_at": datetime.now().astimezone().isoformat(),
            "parameters": {
                "players": args.players,
                "runs": args.runs,
                "events": args.events,
                "repeats": args.repeats,
                "q": args.q,
                "learning_fraction": args.learning_fraction,
                "gap": args.gap,
                "seed": args.seed,
            },
            "calibration": {
                "median_seconds_per_match": seconds_per_match,
                "median_matches_per_second": 1 / seconds_per_match,
            },
            "outputs": {
                "run_dir": str(run_dir),
                "benchmark_csv": str(output),
                "manifest": str(manifest),
            },
        },
    )
    print()
    print(f"Median seconds/match: {seconds_per_match:.9f}")
    print(f"Median matches/s: {1 / seconds_per_match:.0f}")
    print(f"Wrote benchmark CSV to {output}")
    print(f"Wrote manifest to {manifest}")


if __name__ == "__main__":
    main()

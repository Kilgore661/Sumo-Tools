from __future__ import annotations

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

from .audit import make_run_dir, write_manifest
from .metrics import build_metrics, first_stable_event, persistence_after_first_stable
from .model import BaselineModel
from .progress import format_duration
from .runtime_model import DEFAULT_SECONDS_PER_MATCH, estimate_seconds, match_count
from .simulation import simulate_ensemble


DEFAULT_OUTPUT_ROOT = Path("files/output/toy_elo_convergence_sweep")


def default_players() -> list[int]:
    return [*range(10, 101, 10), *range(150, 601, 50)]


def parse_ints(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def event_values(*, start: int, step: int, stop: int) -> list[int]:
    return list(range(start, stop + 1, step))


def event_bucket(value: int, *, start: int, step: int) -> int:
    if value <= start:
        return start
    offset = value - start
    return start + ((offset + step - 1) // step) * step


def write_attempt_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "players",
                "runs",
                "search_start_events",
                "tested_events",
                "converged",
                "first_stable_event",
                "implied_event_bucket",
                "persistence_after_first_stable",
                "final_mean_gap_rmse",
                "final_sample_gap_rmse",
                "matches",
                "estimated_seconds",
                "elapsed_seconds",
            ]
        )


def append_attempt(path: Path, row: dict[str, float | int | bool | None]) -> None:
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                row["players"],
                row["runs"],
                row["search_start_events"],
                row["tested_events"],
                int(bool(row["converged"])),
                "" if row["first_stable_event"] is None else row["first_stable_event"],
                "" if row["implied_event_bucket"] is None else row["implied_event_bucket"],
                "" if row["persistence_after_first_stable"] is None else row["persistence_after_first_stable"],
                row["final_mean_gap_rmse"],
                row["final_sample_gap_rmse"],
                row["matches"],
                row["estimated_seconds"],
                row["elapsed_seconds"],
            ]
        )


def write_summary(path: Path, rows: list[dict[str, float | int | bool | None]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "players",
                "converged",
                "search_start_events",
                "tested_events",
                "first_stable_event",
                "implied_event_bucket",
                "persistence_after_first_stable",
                "final_mean_gap_rmse",
                "elapsed_seconds",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["players"],
                    int(bool(row["converged"])),
                    "" if row["search_start_events"] is None else row["search_start_events"],
                    "" if row["tested_events"] is None else row["tested_events"],
                    "" if row["first_stable_event"] is None else row["first_stable_event"],
                    "" if row["implied_event_bucket"] is None else row["implied_event_bucket"],
                    "" if row["persistence_after_first_stable"] is None else row["persistence_after_first_stable"],
                    "" if row["final_mean_gap_rmse"] is None else row["final_mean_gap_rmse"],
                    "" if row["elapsed_seconds"] is None else row["elapsed_seconds"],
                ]
            )


def run_attempt(
    *,
    players: int,
    runs: int,
    events: int,
    q: float,
    learning_fraction: float,
    gap: float,
    seed: int,
    stable_epsilon: float,
    slope_epsilon: float,
    stable_window: int,
    event_start: int,
    event_step: int,
    search_start_events: int,
) -> dict[str, float | int | bool | None]:
    model = BaselineModel(
        player_count=players,
        max_rating=gap * (players - 1),
        q=q,
        learning_fraction=learning_fraction,
    )
    start = time.perf_counter()
    skills, means, sample_rows = simulate_ensemble(
        model=model,
        events=events,
        runs=runs,
        seed=seed,
        progress_every=0,
    )
    metrics = build_metrics(
        skills=skills,
        means=means,
        sample_rows=sample_rows,
        stable_epsilon=stable_epsilon,
        slope_epsilon=slope_epsilon,
        stable_window=stable_window,
    )
    first_event = first_stable_event(metrics)
    implied_bucket = (
        None
        if first_event is None
        else event_bucket(first_event, start=event_start, step=event_step)
    )
    persistence = persistence_after_first_stable(metrics)
    matches = match_count(players=players, runs=runs, events=events)
    return {
        "players": players,
        "runs": runs,
        "search_start_events": search_start_events,
        "tested_events": events,
        "converged": first_event is not None,
        "first_stable_event": first_event,
        "implied_event_bucket": implied_bucket,
        "persistence_after_first_stable": persistence,
        "final_mean_gap_rmse": float(metrics[-1]["mean_gap_rmse"]),
        "final_sample_gap_rmse": float(metrics[-1]["sample_gap_rmse"]),
        "matches": matches,
        "estimated_seconds": estimate_seconds(players=players, runs=runs, events=events),
        "elapsed_seconds": time.perf_counter() - start,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Find an event count that reaches stability for each n.")
    parser.add_argument("--players", default=",".join(str(value) for value in default_players()))
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--event-start", type=int, default=50)
    parser.add_argument("--event-step", type=int, default=50)
    parser.add_argument("--event-stop", type=int, default=1000)
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--learning-fraction", type=float, default=0.125)
    parser.add_argument("--gap", type=float, default=40.0)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--stable-epsilon", type=float, default=4.0)
    parser.add_argument("--slope-epsilon", type=float, default=0.05)
    parser.add_argument("--stable-window", type=int, default=25)
    parser.add_argument(
        "--no-monotone-event-start",
        action="store_true",
        help="Always start each n at --event-start instead of reusing the previous converged event count.",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    started_at = datetime.now().astimezone()
    run_dir = make_run_dir(args.output_root, seed=args.seed, timestamp=started_at)
    attempts_path = run_dir / "attempts.csv"
    summary_path = run_dir / "summary.csv"
    manifest_path = run_dir / "manifest.json"
    players_values = parse_ints(args.players)
    event_grid = event_values(start=args.event_start, step=args.event_step, stop=args.event_stop)

    write_attempt_header(attempts_path)
    summary_rows: list[dict[str, float | int | bool | None]] = []
    write_summary(summary_path, summary_rows)
    write_manifest(
        manifest_path,
        {
            "started_at": started_at.isoformat(),
            "parameters": vars(args) | {"output_root": str(args.output_root)},
            "outputs": {
                "run_dir": str(run_dir),
                "attempts": str(attempts_path),
                "summary": str(summary_path),
                "manifest": str(manifest_path),
            },
            "status": "running",
        },
    )
    print(f"Convergence sweep output: {run_dir}", flush=True)
    print(
        f"Players: {players_values}; runs={args.runs}; "
        f"events={event_grid[0]}..{event_grid[-1]} step {args.event_step}; "
        f"monotone_start={not args.no_monotone_event_start}",
        flush=True,
    )

    next_event_start = event_grid[0]
    for player_index, players in enumerate(players_values, start=1):
        print(
            f"\n=== n={players} ({player_index}/{len(players_values)}) ===",
            flush=True,
        )
        best_row: dict[str, float | int | bool | None] | None = None
        active_event_grid = [
            events
            for events in event_grid
            if args.no_monotone_event_start or events >= next_event_start
        ]
        if active_event_grid and active_event_grid[0] != event_grid[0]:
            print(
                f"Starting at events={active_event_grid[0]} "
                f"because previous n implied bucket={next_event_start}",
                flush=True,
            )
        search_start_events = active_event_grid[0] if active_event_grid else next_event_start
        for event_index, events in enumerate(active_event_grid, start=1):
            matches = match_count(players=players, runs=args.runs, events=events)
            estimated_seconds = estimate_seconds(players=players, runs=args.runs, events=events)
            print(
                f"Trying n={players}, events={events} "
                f"({event_index}/{len(active_event_grid)} for this n), runs={args.runs}; "
                f"matches={matches}; eta~{format_duration(estimated_seconds)}",
                flush=True,
            )
            row = run_attempt(
                players=players,
                runs=args.runs,
                events=events,
                q=args.q,
                learning_fraction=args.learning_fraction,
                gap=args.gap,
                seed=args.seed,
                stable_epsilon=args.stable_epsilon,
                slope_epsilon=args.slope_epsilon,
                stable_window=args.stable_window,
                event_start=args.event_start,
                event_step=args.event_step,
                search_start_events=search_start_events,
            )
            append_attempt(attempts_path, row)
            print(
                f"  converged={row['converged']} first={row['first_stable_event']} "
                f"bucket={row['implied_event_bucket']} "
                f"final_rmse={float(row['final_mean_gap_rmse']):.3f} "
                f"elapsed={format_duration(float(row['elapsed_seconds']))}; "
                f"attempts={attempts_path}",
                flush=True,
            )
            best_row = row
            if row["converged"]:
                print(
                    f"  n={players} complete at tested_events={events}; "
                    f"implied_event_bucket={row['implied_event_bucket']}",
                    flush=True,
                )
                if not args.no_monotone_event_start:
                    next_event_start = int(row["implied_event_bucket"] or events)
                break

        summary_rows.append(
            {
                "players": players,
                "converged": bool(best_row and best_row["converged"]),
                "search_start_events": None if best_row is None else best_row["search_start_events"],
                "tested_events": None if best_row is None else best_row["tested_events"],
                "first_stable_event": None if best_row is None else best_row["first_stable_event"],
                "implied_event_bucket": None if best_row is None else best_row["implied_event_bucket"],
                "persistence_after_first_stable": None
                if best_row is None
                else best_row["persistence_after_first_stable"],
                "final_mean_gap_rmse": None if best_row is None else best_row["final_mean_gap_rmse"],
                "elapsed_seconds": None if best_row is None else best_row["elapsed_seconds"],
            }
        )
        write_summary(summary_path, summary_rows)
        print(f"Summary updated: {summary_path}", flush=True)

    write_manifest(
        manifest_path,
        {
            "started_at": started_at.isoformat(),
            "finished_at": datetime.now().astimezone().isoformat(),
            "parameters": vars(args) | {"output_root": str(args.output_root)},
            "outputs": {
                "run_dir": str(run_dir),
                "attempts": str(attempts_path),
                "summary": str(summary_path),
                "manifest": str(manifest_path),
            },
            "status": "complete",
        },
    )
    print(f"Wrote attempts to {attempts_path}")
    print(f"Wrote summary to {summary_path}")


if __name__ == "__main__":
    main()

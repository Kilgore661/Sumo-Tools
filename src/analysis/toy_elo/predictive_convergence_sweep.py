from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .audit import make_run_dir, write_manifest
from .convergence_sweep import (
    append_attempt,
    default_players,
    event_bucket,
    parse_ints,
    run_attempt,
    write_attempt_header,
    write_summary,
)
from .progress import format_duration
from .runtime_model import estimate_seconds, match_count


DEFAULT_OUTPUT_ROOT = Path("files/output/toy_elo_predictive_convergence_sweep")
DEFAULT_QUADRATIC = (0.106468633733679, -1.0373921331466, 120.586077749013)


def quadratic_prediction(players: int, coefficients: tuple[float, float, float]) -> float:
    a, b, c = coefficients
    return a * players * players + b * players + c


def parse_coefficients(value: str) -> tuple[float, float, float]:
    parts = [float(part.strip()) for part in value.split(",") if part.strip()]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("expected three comma-separated coefficients: a,b,c")
    return parts[0], parts[1], parts[2]


def predicted_start(
    *,
    players: int,
    coefficients: tuple[float, float, float],
    event_start: int,
    event_step: int,
    backoff_events: int,
) -> int:
    predicted_event = quadratic_prediction(players, coefficients)
    backed_off = int(predicted_event) - backoff_events
    raw_start = max(event_start, backed_off)
    return event_bucket(raw_start, start=event_start, step=event_step)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find convergence using a quadratic first-stable-event predictor."
    )
    parser.add_argument("--players", default=",".join(str(value) for value in default_players()))
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--event-start", type=int, default=50)
    parser.add_argument("--event-step", type=int, default=50)
    parser.add_argument(
        "--event-stop",
        type=int,
        default=None,
        help="Optional safety ceiling. By default the sweep keeps increasing events until convergence.",
    )
    parser.add_argument(
        "--quadratic",
        type=parse_coefficients,
        default=DEFAULT_QUADRATIC,
        help="Prediction coefficients a,b,c for a*n^2 + b*n + c.",
    )
    parser.add_argument(
        "--prediction-backoff-events",
        type=int,
        default=50,
        help="Start this many events before the predicted first stable event.",
    )
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--learning-fraction", type=float, default=0.125)
    parser.add_argument("--gap", type=float, default=40.0)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--stable-epsilon", type=float, default=4.0)
    parser.add_argument("--slope-epsilon", type=float, default=0.05)
    parser.add_argument("--stable-window", type=int, default=25)
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

    write_attempt_header(attempts_path)
    summary_rows: list[dict[str, float | int | bool | None]] = []
    write_summary(summary_path, summary_rows)
    write_manifest(
        manifest_path,
        {
            "started_at": started_at.isoformat(),
            "parameters": {
                **vars(args),
                "quadratic": list(args.quadratic),
                "output_root": str(args.output_root),
            },
            "outputs": {
                "run_dir": str(run_dir),
                "attempts": str(attempts_path),
                "summary": str(summary_path),
                "manifest": str(manifest_path),
            },
            "status": "running",
        },
    )

    ceiling = "none" if args.event_stop is None else str(args.event_stop)
    print(f"Predictive convergence sweep output: {run_dir}", flush=True)
    print(
        f"Players: {players_values}; runs={args.runs}; "
        f"event_step={args.event_step}; event_stop={ceiling}; "
        f"quadratic={args.quadratic}; backoff_events={args.prediction_backoff_events}",
        flush=True,
    )

    for player_index, players in enumerate(players_values, start=1):
        predicted = quadratic_prediction(players, args.quadratic)
        search_start = predicted_start(
            players=players,
            coefficients=args.quadratic,
            event_start=args.event_start,
            event_step=args.event_step,
            backoff_events=args.prediction_backoff_events,
        )
        if args.event_stop is not None and search_start > args.event_stop:
            search_start = args.event_stop
        print(
            f"\n=== n={players} ({player_index}/{len(players_values)}) ===",
            flush=True,
        )
        print(
            f"Predicted first stable event ~{predicted:.1f}; "
            f"starting at events={search_start}",
            flush=True,
        )

        best_row: dict[str, float | int | bool | None] | None = None
        events = search_start
        attempt_index = 1
        while args.event_stop is None or events <= args.event_stop:
            matches = match_count(players=players, runs=args.runs, events=events)
            estimated_seconds = estimate_seconds(players=players, runs=args.runs, events=events)
            print(
                f"Trying n={players}, events={events} "
                f"(attempt {attempt_index}), runs={args.runs}; "
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
                search_start_events=search_start,
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
                break

            events += args.event_step
            attempt_index += 1

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
            "parameters": {
                **vars(args),
                "quadratic": list(args.quadratic),
                "output_root": str(args.output_root),
            },
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

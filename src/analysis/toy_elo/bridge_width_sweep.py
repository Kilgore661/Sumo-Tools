from __future__ import annotations

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

from .audit import make_run_dir, write_manifest
from .bridge import (
    BridgeEnsemble,
    bridge_match_count,
    bridge_slots,
    build_bridge_metrics,
    build_bridge_pairs,
    division_sizes,
    validate_match_counts,
)
from .convergence_sweep import event_bucket, parse_ints
from .fit_quadratic import fit_quadratic, predict, read_points, r_squared
from .model import BaselineModel
from .progress import format_duration
from .runtime_model import estimate_seconds
from .split_division_sweep import (
    DEFAULT_BASELINE,
    first_event,
    read_baseline_rows,
)


DEFAULT_OUTPUT_ROOT = Path("files/output/toy_elo_bridge_width_sweep")

ATTEMPT_FIELDS = [
    "players",
    "top_size",
    "bottom_size",
    "bridge_width",
    "bridge_slots",
    "bridge_match_count_per_event",
    "runs",
    "search_start_events",
    "tested_events",
    "target",
    "converged",
    "top_first_stable_event",
    "bottom_first_stable_event",
    "internal_first_stable_event",
    "whole_first_stable_event",
    "bridge_first_stable_event",
    "global_first_stable_event",
    "implied_event_bucket",
    "baseline_full_first_stable_event",
    "predicted_division_events",
    "top_final_rmse",
    "top_final_slope",
    "top_stable_now",
    "bottom_final_rmse",
    "bottom_final_slope",
    "bottom_stable_now",
    "internal_stable_now",
    "whole_final_rmse",
    "whole_final_slope",
    "whole_stable_now",
    "cross_final_rmse",
    "division_offset_error",
    "boundary_rating_gap",
    "boundary_skill_gap",
    "boundary_gap_error",
    "boundary_gap_error_slope",
    "division_mean_rating_gap",
    "division_mean_skill_gap",
    "division_mean_gap_error",
    "division_mean_gap_error_slope",
    "bridge_stable_now",
    "matches",
    "estimated_seconds",
    "elapsed_seconds",
]

FINAL_RATING_FIELDS = [
    "player",
    "division",
    "rating",
    "hidden_skill",
    "rating_gap_to_next",
    "hidden_gap_to_next",
    "gap_error_to_next",
    "descending_to_next",
]


def resolve_target(target: str, slots: int) -> str:
    if target == "auto":
        return "internal" if slots == 0 else "bridge"
    return target


def write_attempt_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(ATTEMPT_FIELDS)


def append_attempt(path: Path, row: dict[str, float | int | bool | str | None]) -> None:
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["" if row[field] is None else row[field] for field in ATTEMPT_FIELDS])


def write_summary(path: Path, rows: list[dict[str, float | int | bool | str | None]]) -> None:
    write_attempt_header(path)
    for row in rows:
        append_attempt(path, row)


def final_ratings_path(run_dir: Path, players: int, bridge_width: int) -> Path:
    return run_dir / f"final_ratings_n{players}_d{bridge_width}.csv"


def write_final_ratings(
    *,
    path: Path,
    top_size: int,
    ratings: list[float],
    skills: list[float],
) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FINAL_RATING_FIELDS)
        for player, rating in enumerate(ratings):
            next_player = player + 1
            has_next = next_player < len(ratings)
            rating_gap = rating - ratings[next_player] if has_next else None
            hidden_gap = skills[player] - skills[next_player] if has_next else None
            gap_error = (
                None
                if rating_gap is None or hidden_gap is None
                else rating_gap - hidden_gap
            )
            writer.writerow(
                [
                    player,
                    "top" if player < top_size else "bottom",
                    rating,
                    skills[player],
                    "" if rating_gap is None else rating_gap,
                    "" if hidden_gap is None else hidden_gap,
                    "" if gap_error is None else gap_error,
                    "" if rating_gap is None else ("yes" if rating_gap >= 0 else "no"),
                ]
            )


def summarize_attempt(
    *,
    players: int,
    top_size: int,
    bridge_width: int,
    slots: int,
    target: str,
    runs: int,
    events: int,
    skills: list[float],
    means: list[list[float]],
    sample_rows: list[list[float]],
    stable_epsilon: float,
    slope_epsilon: float,
    stable_window: int,
    bridge_offset_epsilon: float,
    bridge_boundary_epsilon: float,
    event_start: int,
    event_step: int,
    search_start_events: int,
    baseline_full_first: int | None,
    predicted_division_events: float,
    elapsed_seconds: float,
) -> dict[str, float | int | bool | str | None]:
    bottom_size = players - top_size
    top_players = list(range(top_size))
    bottom_players = list(range(top_size, players))

    metrics = build_bridge_metrics(
        skills=skills,
        means=means,
        sample_rows=sample_rows,
        top_players=top_players,
        bottom_players=bottom_players,
        stable_epsilon=stable_epsilon,
        slope_epsilon=slope_epsilon,
        stable_window=stable_window,
        bridge_offset_epsilon=bridge_offset_epsilon,
        bridge_boundary_epsilon=bridge_boundary_epsilon,
    )
    top_first = first_event(metrics, "top_stable_window_met")
    bottom_first = first_event(metrics, "bottom_stable_window_met")
    internal_first = first_event(metrics, "internal_stable_window_met")
    whole_first = first_event(metrics, "whole_stable_window_met")
    bridge_first = first_event(metrics, "bridge_stable_window_met")
    global_first = internal_first if slots == 0 else whole_first
    target_firsts = {
        "internal": internal_first,
        "bridge": bridge_first,
        "global": global_first,
    }
    target_first = target_firsts[target]
    implied_bucket = (
        None
        if target_first is None
        else event_bucket(target_first, start=event_start, step=event_step)
    )
    final = metrics[-1]
    matches = bridge_match_count(players, top_size, events, runs)
    full_matches = runs * events * players * (players - 1) / 2
    return {
        "players": players,
        "top_size": top_size,
        "bottom_size": bottom_size,
        "bridge_width": bridge_width,
        "bridge_slots": slots,
        "bridge_match_count_per_event": slots * 2,
        "runs": runs,
        "search_start_events": search_start_events,
        "tested_events": events,
        "target": target,
        "converged": int(target_first is not None),
        "top_first_stable_event": top_first,
        "bottom_first_stable_event": bottom_first,
        "internal_first_stable_event": internal_first,
        "whole_first_stable_event": whole_first,
        "bridge_first_stable_event": bridge_first,
        "global_first_stable_event": global_first,
        "implied_event_bucket": implied_bucket,
        "baseline_full_first_stable_event": baseline_full_first,
        "predicted_division_events": predicted_division_events,
        "top_final_rmse": final["top_rmse"],
        "top_final_slope": final["top_slope"],
        "top_stable_now": int(bool(final["top_stable_now"])),
        "bottom_final_rmse": final["bottom_rmse"],
        "bottom_final_slope": final["bottom_slope"],
        "bottom_stable_now": int(bool(final["bottom_stable_now"])),
        "internal_stable_now": int(bool(final["internal_stable_now"])),
        "whole_final_rmse": final["whole_rmse"],
        "whole_final_slope": final["whole_slope"],
        "whole_stable_now": int(bool(final["whole_stable_now"])),
        "cross_final_rmse": final["cross_rmse"],
        "division_offset_error": final["division_offset_error"],
        "boundary_rating_gap": final["boundary_rating_gap"],
        "boundary_skill_gap": final["boundary_skill_gap"],
        "boundary_gap_error": final["boundary_gap_error"],
        "boundary_gap_error_slope": final["boundary_gap_error_slope"],
        "division_mean_rating_gap": final["division_mean_rating_gap"],
        "division_mean_skill_gap": final["division_mean_skill_gap"],
        "division_mean_gap_error": final["division_mean_gap_error"],
        "division_mean_gap_error_slope": final["division_mean_gap_error_slope"],
        "bridge_stable_now": int(bool(final["bridge_stable_now"])),
        "matches": matches,
        "estimated_seconds": estimate_seconds(players=players, runs=runs, events=events)
        * (matches / full_matches),
        "elapsed_seconds": elapsed_seconds,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sweep bridged two-division Elo schedules.")
    parser.add_argument("--players", default="40,60,80,100,150")
    parser.add_argument("--bridge-widths", default="0,10,20,30")
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--event-start", type=int, default=50)
    parser.add_argument("--event-step", type=int, default=50)
    parser.add_argument("--event-stop", type=int, default=None)
    parser.add_argument("--prediction-backoff-events", type=int, default=50)
    parser.add_argument(
        "--convergence-target",
        choices=["auto", "internal", "bridge", "global"],
        default="auto",
    )
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--learning-fraction", type=float, default=0.125)
    parser.add_argument("--gap", type=float, default=40.0)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--stable-epsilon", type=float, default=4.0)
    parser.add_argument("--slope-epsilon", type=float, default=0.05)
    parser.add_argument("--stable-window", type=int, default=25)
    parser.add_argument("--bridge-offset-epsilon", type=float, default=10.0)
    parser.add_argument("--bridge-boundary-epsilon", type=float, default=10.0)
    parser.add_argument("--progress-every", type=int, default=0)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def serializable_parameters(args: argparse.Namespace) -> dict[str, object]:
    values = vars(args).copy()
    values["baseline"] = str(args.baseline)
    values["output_root"] = str(args.output_root)
    return values


def validate_bridge_widths(players_values: list[int], bridge_width_values: list[int]) -> None:
    for players in players_values:
        top_size, bottom_size = division_sizes(players)
        for bridge_width in bridge_width_values:
            bridge_slots(top_size, bottom_size, bridge_width)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    players_values = parse_ints(args.players)
    bridge_width_values = parse_ints(args.bridge_widths)
    try:
        validate_bridge_widths(players_values, bridge_width_values)
    except ValueError as exc:
        parser.error(str(exc))

    baseline_points = read_points(
        args.baseline,
        x_column="players",
        y_column="first_stable_event",
        only_converged=True,
        exclude_players=set(),
    )
    coefficients = fit_quadratic(baseline_points)
    baseline_r2 = r_squared(baseline_points, coefficients)
    baseline_rows = read_baseline_rows(args.baseline)

    started_at = datetime.now().astimezone()
    run_dir = make_run_dir(args.output_root, seed=args.seed, timestamp=started_at)
    attempts_path = run_dir / "attempts.csv"
    summary_path = run_dir / "summary.csv"
    manifest_path = run_dir / "manifest.json"
    summary_rows: list[dict[str, float | int | bool | str | None]] = []
    write_attempt_header(attempts_path)
    write_summary(summary_path, summary_rows)

    manifest_base = {
        "started_at": started_at.isoformat(),
        "parameters": serializable_parameters(args),
        "baseline_fit": {
            "quadratic": list(coefficients),
            "r_squared": baseline_r2,
        },
        "outputs": {
            "run_dir": str(run_dir),
            "attempts": str(attempts_path),
            "summary": str(summary_path),
            "manifest": str(manifest_path),
        },
    }
    write_manifest(manifest_path, {**manifest_base, "status": "running"})

    ceiling = "none" if args.event_stop is None else str(args.event_stop)
    print(f"Bridge-width sweep output: {run_dir}", flush=True)
    print(
        f"Players: {players_values}; bridge_widths={bridge_width_values}; "
        f"runs={args.runs}; event_step={args.event_step}; event_stop={ceiling}; "
        f"target={args.convergence_target}; baseline={args.baseline}",
        flush=True,
    )
    print(f"Baseline fit: {coefficients}; R^2={baseline_r2:.6f}", flush=True)

    total_start = time.perf_counter()
    total_cases = len(players_values) * len(bridge_width_values)
    case_index = 0
    for players in players_values:
        top_size, bottom_size = division_sizes(players)
        predicted_division_events = max(
            predict(top_size, coefficients),
            predict(bottom_size, coefficients),
        )
        search_start = event_bucket(
            max(args.event_start, int(predicted_division_events) - args.prediction_backoff_events),
            start=args.event_start,
            step=args.event_step,
        )
        if args.event_stop is not None and search_start > args.event_stop:
            search_start = args.event_stop
        baseline_full_first = (
            int(baseline_rows[players]["first_stable_event"])
            if players in baseline_rows and baseline_rows[players].get("first_stable_event")
            else None
        )

        for bridge_width in bridge_width_values:
            case_start = time.perf_counter()
            case_index += 1
            top_slots, bottom_slots, slots = bridge_slots(top_size, bottom_size, bridge_width)
            target = resolve_target(args.convergence_target, slots)
            print(
                f"\n=== n={players}, d={bridge_width}% ({case_index}/{total_cases}), "
                f"divisions={top_size}+{bottom_size}, slots={slots} "
                f"(top={top_slots}, bottom={bottom_slots}) ===",
                flush=True,
            )
            print(
                f"Predicted isolated-division convergence ~{predicted_division_events:.1f}; "
                f"starting at events={search_start}; full baseline={baseline_full_first}; "
                f"target={target}",
                flush=True,
            )

            pairs = build_bridge_pairs(
                top_size=top_size,
                bottom_size=bottom_size,
                slots=slots,
            )
            validate_match_counts(
                pairs=pairs,
                top_size=top_size,
                bottom_size=bottom_size,
            )
            model = BaselineModel(
                player_count=players,
                max_rating=args.gap * (players - 1),
                q=args.q,
                learning_fraction=args.learning_fraction,
            )
            ensemble = BridgeEnsemble(
                model=model,
                pairs=pairs,
                runs=args.runs,
                seed=args.seed,
            )
            best_row: dict[str, float | int | bool | str | None] | None = None
            events = search_start
            attempt_index = 1
            while args.event_stop is None or events <= args.event_stop:
                matches = bridge_match_count(players, top_size, events, args.runs)
                print(
                    f"Trying n={players}, d={bridge_width}%, events={events} "
                    f"(attempt {attempt_index}), runs={args.runs}; matches={matches}",
                    flush=True,
                )
                start = time.perf_counter()
                ensemble.extend_to(events, progress_every=args.progress_every)
                row = summarize_attempt(
                    players=players,
                    top_size=top_size,
                    bridge_width=bridge_width,
                    slots=slots,
                    target=target,
                    runs=args.runs,
                    events=events,
                    skills=ensemble.skills,
                    means=ensemble.means,
                    sample_rows=ensemble.sample_rows,
                    stable_epsilon=args.stable_epsilon,
                    slope_epsilon=args.slope_epsilon,
                    stable_window=args.stable_window,
                    bridge_offset_epsilon=args.bridge_offset_epsilon,
                    bridge_boundary_epsilon=args.bridge_boundary_epsilon,
                    event_start=args.event_start,
                    event_step=args.event_step,
                    search_start_events=search_start,
                    baseline_full_first=baseline_full_first,
                    predicted_division_events=predicted_division_events,
                    elapsed_seconds=time.perf_counter() - start,
                )
                append_attempt(attempts_path, row)
                print(
                    f"  converged={bool(row['converged'])} "
                    f"internal={row['internal_first_stable_event']} "
                    f"bridge={row['bridge_first_stable_event']} "
                    f"global={row['global_first_stable_event']} "
                    f"whole_rmse={float(row['whole_final_rmse']):.3f} "
                    f"offset_error={float(row['division_offset_error']):.3f} "
                    f"boundary_gap={float(row['boundary_rating_gap']):.3f} "
                    f"elapsed={format_duration(float(row['elapsed_seconds']))}",
                    flush=True,
                )
                best_row = row
                if row["converged"]:
                    break
                events += args.event_step
                attempt_index += 1

            if best_row is not None:
                ratings_path = final_ratings_path(run_dir, players, bridge_width)
                write_final_ratings(
                    path=ratings_path,
                    top_size=top_size,
                    ratings=ensemble.means[-1],
                    skills=ensemble.skills,
                )
                summary_rows.append(best_row)
                write_summary(summary_path, summary_rows)
                print(f"Summary updated: {summary_path}", flush=True)
                print(f"Final ratings written: {ratings_path}", flush=True)
                print(
                    f"Case elapsed total: {format_duration(time.perf_counter() - case_start)}",
                    flush=True,
                )

    total_elapsed = time.perf_counter() - total_start
    write_manifest(
        manifest_path,
        {
            **manifest_base,
            "finished_at": datetime.now().astimezone().isoformat(),
            "status": "complete",
            "elapsed_seconds": total_elapsed,
        },
    )
    print(f"Wrote attempts to {attempts_path}")
    print(f"Wrote summary to {summary_path}")
    print(f"Total elapsed: {format_duration(total_elapsed)}")


if __name__ == "__main__":
    main()

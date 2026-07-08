from __future__ import annotations

import argparse
import csv
import random
import time
from datetime import datetime
from pathlib import Path

from .audit import make_run_dir, write_manifest
from .convergence_sweep import event_bucket, parse_ints
from .elo import expected_score, update_ratings
from .fit_quadratic import fit_quadratic, predict, read_points, r_squared
from .metrics import all_pair_gap_rmse
from .model import BaselineModel
from .progress import ProgressTimer, format_duration
from .runtime_model import estimate_seconds


DEFAULT_BASELINE = Path(
    "src/analysis/toy_elo/files/full_round_robin_convergence_20260706_101659.csv"
)
DEFAULT_OUTPUT_ROOT = Path("files/output/toy_elo_split_division_sweep")


def round_robin_pairs(players: list[int]) -> list[tuple[int, int]]:
    return [
        (players[index_a], players[index_b])
        for index_a in range(len(players))
        for index_b in range(index_a + 1, len(players))
    ]


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def subset(values: list[float], players: list[int]) -> list[float]:
    return [values[player] for player in players]


def cross_gap_rmse(
    ratings: list[float],
    skills: list[float],
    top_players: list[int],
    bottom_players: list[int],
) -> float:
    squared_error_sum = 0.0
    pair_count = 0
    for player_a in top_players:
        for player_b in bottom_players:
            rating_gap = ratings[player_a] - ratings[player_b]
            skill_gap = skills[player_a] - skills[player_b]
            squared_error_sum += (rating_gap - skill_gap) ** 2
            pair_count += 1
    return (squared_error_sum / pair_count) ** 0.5 if pair_count else 0.0


def division_offset_error(
    ratings: list[float],
    skills: list[float],
    top_players: list[int],
    bottom_players: list[int],
) -> float:
    rating_offset = mean(subset(ratings, top_players)) - mean(subset(ratings, bottom_players))
    skill_offset = mean(subset(skills, top_players)) - mean(subset(skills, bottom_players))
    return rating_offset - skill_offset


def split_match_count(players: int, top_size: int, events: int, runs: int) -> int:
    bottom_size = players - top_size
    matches_per_event = top_size * (top_size - 1) // 2 + bottom_size * (bottom_size - 1) // 2
    return runs * events * matches_per_event


def simulate_one_split_run(
    *,
    model: BaselineModel,
    skills: list[float],
    top_players: list[int],
    bottom_players: list[int],
    events: int,
    rng: random.Random,
) -> list[list[float]]:
    ratings = [model.baseline for _ in skills]
    rows = [ratings.copy()]
    pairs = round_robin_pairs(top_players) + round_robin_pairs(bottom_players)

    for _ in range(events):
        rng.shuffle(pairs)
        for player_a, player_b in pairs:
            p_a_wins = expected_score(skills[player_a], skills[player_b], q=model.q)
            winner = player_a if rng.random() < p_a_wins else player_b
            update_ratings(
                ratings,
                player_a,
                player_b,
                winner=winner,
                k=model.k,
                q=model.q,
            )
        rows.append(ratings.copy())

    return rows


def simulate_split_ensemble(
    *,
    model: BaselineModel,
    top_players: list[int],
    bottom_players: list[int],
    events: int,
    runs: int,
    seed: int,
    progress_every: int,
) -> tuple[list[float], list[list[float]], list[list[float]]]:
    skills = model.hidden_skills()
    sums = [[0.0 for _ in range(model.player_count)] for _ in range(events + 1)]
    sample_rows: list[list[float]] | None = None
    progress = ProgressTimer(runs, report_every=progress_every)

    for run in range(runs):
        rng = random.Random(seed + run)
        rows = simulate_one_split_run(
            model=model,
            skills=skills,
            top_players=top_players,
            bottom_players=bottom_players,
            events=events,
            rng=rng,
        )
        if sample_rows is None:
            sample_rows = rows
        for iteration, ratings in enumerate(rows):
            for player, rating in enumerate(ratings):
                sums[iteration][player] += rating
        progress.report(run + 1)

    means = [[rating_sum / runs for rating_sum in row] for row in sums]
    return skills, means, sample_rows or []


def metric_slope(rows: list[dict[str, float | int | bool]], metric: str, iteration: int, window: int) -> float:
    if iteration < window:
        return 0.0
    return (float(rows[iteration][metric]) - float(rows[iteration - window][metric])) / window


def first_true_window(flags: list[bool], window: int) -> int | None:
    for index in range(window - 1, len(flags)):
        if all(flags[index - window + 1 : index + 1]):
            return index
    return None


def later_event(first: int | None, second: int | None) -> int | None:
    if first is None or second is None:
        return None
    return max(first, second)


def build_split_metrics(
    *,
    skills: list[float],
    means: list[list[float]],
    sample_rows: list[list[float]],
    top_players: list[int],
    bottom_players: list[int],
    stable_epsilon: float,
    slope_epsilon: float,
    stable_window: int,
) -> list[dict[str, float | int | bool]]:
    rows: list[dict[str, float | int | bool]] = []

    for event, mean_ratings in enumerate(means):
        top_rmse = all_pair_gap_rmse(subset(mean_ratings, top_players), subset(skills, top_players))
        bottom_rmse = all_pair_gap_rmse(subset(mean_ratings, bottom_players), subset(skills, bottom_players))
        whole_rmse = all_pair_gap_rmse(mean_ratings, skills)
        cross_rmse = cross_gap_rmse(mean_ratings, skills, top_players, bottom_players)
        offset_error = division_offset_error(mean_ratings, skills, top_players, bottom_players)
        sample_whole_rmse = all_pair_gap_rmse(sample_rows[event], skills)

        row: dict[str, float | int | bool] = {
            "event": event,
            "top_rmse": top_rmse,
            "bottom_rmse": bottom_rmse,
            "whole_rmse": whole_rmse,
            "cross_rmse": cross_rmse,
            "division_offset_error": offset_error,
            "sample_whole_rmse": sample_whole_rmse,
        }
        row["top_slope"] = metric_slope(rows + [row], "top_rmse", event, stable_window)
        row["bottom_slope"] = metric_slope(rows + [row], "bottom_rmse", event, stable_window)
        row["top_stable_now"] = (
            top_rmse <= stable_epsilon and abs(float(row["top_slope"])) <= slope_epsilon
        )
        row["bottom_stable_now"] = (
            bottom_rmse <= stable_epsilon and abs(float(row["bottom_slope"])) <= slope_epsilon
        )
        row["internal_stable_now"] = bool(row["top_stable_now"] and row["bottom_stable_now"])
        rows.append(row)

    top_flags = [bool(row["top_stable_now"]) for row in rows]
    bottom_flags = [bool(row["bottom_stable_now"]) for row in rows]
    top_first = first_true_window(top_flags, stable_window)
    bottom_first = first_true_window(bottom_flags, stable_window)
    internal_first = later_event(top_first, bottom_first)

    for row in rows:
        event = int(row["event"])
        row["top_stable_window_met"] = top_first is not None and event >= top_first
        row["bottom_stable_window_met"] = bottom_first is not None and event >= bottom_first
        row["internal_stable_window_met"] = internal_first is not None and event >= internal_first

    return rows


def first_event(rows: list[dict[str, float | int | bool]], key: str) -> int | None:
    for row in rows:
        if row[key]:
            return int(row["event"])
    return None


def persistence_after(rows: list[dict[str, float | int | bool]], first: int | None, key: str) -> float | None:
    if first is None or first >= len(rows) - 1:
        return None
    later = rows[first + 1 :]
    return sum(1 for row in later if row[key]) / len(later)


def read_baseline_rows(path: Path) -> dict[int, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return {int(row["players"]): row for row in csv.DictReader(f)}


def write_attempt_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(
            [
                "players",
                "top_size",
                "bottom_size",
                "runs",
                "search_start_events",
                "tested_events",
                "converged",
                "top_first_stable_event",
                "bottom_first_stable_event",
                "internal_first_stable_event",
                "internal_implied_event_bucket",
                "baseline_full_first_stable_event",
                "predicted_division_events",
                "top_final_rmse",
                "bottom_final_rmse",
                "whole_final_rmse",
                "cross_final_rmse",
                "division_offset_error",
                "matches",
                "estimated_seconds",
                "elapsed_seconds",
            ]
        )


def append_attempt(path: Path, row: dict[str, float | int | bool | None]) -> None:
    fields = [
        "players",
        "top_size",
        "bottom_size",
        "runs",
        "search_start_events",
        "tested_events",
        "converged",
        "top_first_stable_event",
        "bottom_first_stable_event",
        "internal_first_stable_event",
        "internal_implied_event_bucket",
        "baseline_full_first_stable_event",
        "predicted_division_events",
        "top_final_rmse",
        "bottom_final_rmse",
        "whole_final_rmse",
        "cross_final_rmse",
        "division_offset_error",
        "matches",
        "estimated_seconds",
        "elapsed_seconds",
    ]
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["" if row[field] is None else row[field] for field in fields])


def write_summary(path: Path, rows: list[dict[str, float | int | bool | None]]) -> None:
    write_attempt_header(path)
    path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    for row in rows:
        append_attempt(path, row)


def run_attempt(
    *,
    players: int,
    top_size: int,
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
    baseline_full_first: int | None,
    predicted_division_events: float,
    progress_every: int,
) -> dict[str, float | int | bool | None]:
    bottom_size = players - top_size
    top_players = list(range(top_size))
    bottom_players = list(range(top_size, players))
    model = BaselineModel(
        player_count=players,
        max_rating=gap * (players - 1),
        q=q,
        learning_fraction=learning_fraction,
    )
    start = time.perf_counter()
    skills, means, sample_rows = simulate_split_ensemble(
        model=model,
        top_players=top_players,
        bottom_players=bottom_players,
        events=events,
        runs=runs,
        seed=seed,
        progress_every=progress_every,
    )
    metrics = build_split_metrics(
        skills=skills,
        means=means,
        sample_rows=sample_rows,
        top_players=top_players,
        bottom_players=bottom_players,
        stable_epsilon=stable_epsilon,
        slope_epsilon=slope_epsilon,
        stable_window=stable_window,
    )
    top_first = first_event(metrics, "top_stable_window_met")
    bottom_first = first_event(metrics, "bottom_stable_window_met")
    internal_first = first_event(metrics, "internal_stable_window_met")
    implied_bucket = (
        None
        if internal_first is None
        else event_bucket(internal_first, start=event_start, step=event_step)
    )
    final = metrics[-1]
    return {
        "players": players,
        "top_size": top_size,
        "bottom_size": bottom_size,
        "runs": runs,
        "search_start_events": search_start_events,
        "tested_events": events,
        "converged": int(internal_first is not None),
        "top_first_stable_event": top_first,
        "bottom_first_stable_event": bottom_first,
        "internal_first_stable_event": internal_first,
        "internal_implied_event_bucket": implied_bucket,
        "baseline_full_first_stable_event": baseline_full_first,
        "predicted_division_events": predicted_division_events,
        "top_final_rmse": final["top_rmse"],
        "bottom_final_rmse": final["bottom_rmse"],
        "whole_final_rmse": final["whole_rmse"],
        "cross_final_rmse": final["cross_rmse"],
        "division_offset_error": final["division_offset_error"],
        "matches": split_match_count(players, top_size, events, runs),
        "estimated_seconds": estimate_seconds(
            players=players,
            runs=runs,
            events=events,
        )
        * (split_match_count(players, top_size, events, runs) / (runs * events * players * (players - 1) / 2)),
        "elapsed_seconds": time.perf_counter() - start,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sweep two isolated Elo divisions with no interdivision matches.")
    parser.add_argument("--players", default="20,30,40,50,60,70,80,90,100,150")
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--event-start", type=int, default=50)
    parser.add_argument("--event-step", type=int, default=50)
    parser.add_argument("--event-stop", type=int, default=None)
    parser.add_argument("--prediction-backoff-events", type=int, default=50)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--learning-fraction", type=float, default=0.125)
    parser.add_argument("--gap", type=float, default=40.0)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--stable-epsilon", type=float, default=4.0)
    parser.add_argument("--slope-epsilon", type=float, default=0.05)
    parser.add_argument("--stable-window", type=int, default=25)
    parser.add_argument("--progress-every", type=int, default=0)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
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
    players_values = parse_ints(args.players)
    summary_rows: list[dict[str, float | int | bool | None]] = []
    write_attempt_header(attempts_path)
    write_summary(summary_path, summary_rows)
    write_manifest(
        manifest_path,
        {
            "started_at": started_at.isoformat(),
            "parameters": {
                **vars(args),
                "baseline": str(args.baseline),
                "output_root": str(args.output_root),
            },
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
            "status": "running",
        },
    )

    ceiling = "none" if args.event_stop is None else str(args.event_stop)
    print(f"Split-division sweep output: {run_dir}", flush=True)
    print(
        f"Players: {players_values}; runs={args.runs}; event_step={args.event_step}; "
        f"event_stop={ceiling}; baseline={args.baseline}",
        flush=True,
    )
    print(f"Baseline fit: {coefficients}; R^2={baseline_r2:.6f}", flush=True)

    for player_index, players in enumerate(players_values, start=1):
        top_size = players // 2
        bottom_size = players - top_size
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
        print(
            f"\n=== n={players} ({player_index}/{len(players_values)}), "
            f"divisions={top_size}+{bottom_size} ===",
            flush=True,
        )
        print(
            f"Predicted isolated-division convergence ~{predicted_division_events:.1f}; "
            f"starting at events={search_start}; full baseline={baseline_full_first}",
            flush=True,
        )

        best_row: dict[str, float | int | bool | None] | None = None
        events = search_start
        attempt_index = 1
        while args.event_stop is None or events <= args.event_stop:
            matches = split_match_count(players, top_size, events, args.runs)
            print(
                f"Trying n={players}, events={events} (attempt {attempt_index}), "
                f"runs={args.runs}; split_matches={matches}",
                flush=True,
            )
            row = run_attempt(
                players=players,
                top_size=top_size,
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
                baseline_full_first=baseline_full_first,
                predicted_division_events=predicted_division_events,
                progress_every=args.progress_every,
            )
            append_attempt(attempts_path, row)
            print(
                f"  converged={bool(row['converged'])} "
                f"top={row['top_first_stable_event']} bottom={row['bottom_first_stable_event']} "
                f"internal={row['internal_first_stable_event']} "
                f"whole_rmse={float(row['whole_final_rmse']):.3f} "
                f"cross_rmse={float(row['cross_final_rmse']):.3f} "
                f"elapsed={format_duration(float(row['elapsed_seconds']))}",
                flush=True,
            )
            best_row = row
            if row["converged"]:
                break
            events += args.event_step
            attempt_index += 1

        if best_row is not None:
            summary_rows.append(best_row)
            write_summary(summary_path, summary_rows)
            print(f"Summary updated: {summary_path}", flush=True)

    write_manifest(
        manifest_path,
        {
            "started_at": started_at.isoformat(),
            "finished_at": datetime.now().astimezone().isoformat(),
            "parameters": {
                **vars(args),
                "baseline": str(args.baseline),
                "output_root": str(args.output_root),
            },
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
            "status": "complete",
        },
    )
    print(f"Wrote attempts to {attempts_path}")
    print(f"Wrote summary to {summary_path}")


if __name__ == "__main__":
    main()

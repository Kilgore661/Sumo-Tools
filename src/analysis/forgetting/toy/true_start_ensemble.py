"""Aggregate the true-start baseline over independent synthetic histories."""

from __future__ import annotations

import argparse
import csv
import html
import json
import random
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .elo import replay_history
from .history import generate_history
from .metrics import centred_state_distance, pair_probabilities, vector_rmse
from .model import ToyWorld
from .outputs import _plotly_chart, make_run_directory
from .report_identity import refresh_run_reports


DEFAULT_OUTPUT_ROOT = Path(
    "files/output/analysis/forgetting/toy/true_start_ensemble"
)


@dataclass(frozen=True)
class ReplicateEvent:
    replicate: int
    seed: int
    event: int
    global_bouts: int
    truth_relative_state_rmse: float
    truth_relative_probability_rmse: float
    adjacent_order_inversions: int
    all_pair_order_inversions: int


@dataclass(frozen=True)
class EnsembleEvent:
    event: int
    global_bouts_per_run: int
    replicate_count: int
    state_mean: float
    state_median: float
    state_standard_deviation: float
    state_q05: float
    state_q25: float
    state_q75: float
    state_q95: float
    probability_mean: float
    probability_median: float
    probability_standard_deviation: float
    probability_q05: float
    probability_q25: float
    probability_q75: float
    probability_q95: float
    adjacent_inversion_run_fraction: float
    all_pair_inversion_mean: float


@dataclass(frozen=True)
class FinalPlayerMeanError:
    player: int
    latent_skill: float
    mean_final_rating: float
    mean_signed_error: float
    final_rating_standard_deviation: float
    mean_signed_error_standard_error: float
    z_score_against_zero: float


@dataclass(frozen=True)
class FinalMeanErrorProgress:
    replicate_count: int
    mean_rating_error_rmse: float
    maximum_absolute_mean_error: float


@dataclass(frozen=True)
class TrueStartEnsembleResult:
    run_directory: Path
    world: ToyWorld
    events: int
    runs: int
    master_seed: int
    replicate_seeds: tuple[int, ...]
    replicate_events: tuple[ReplicateEvent, ...]
    event_summary: tuple[EnsembleEvent, ...]
    final_player_mean_errors: tuple[FinalPlayerMeanError, ...]
    final_mean_error_progress: tuple[FinalMeanErrorProgress, ...]
    elapsed_seconds: float


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("cannot calculate a quantile of an empty sequence")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("quantile probability must lie in [0, 1]")
    ordered = sorted(float(value) for value in values)
    position = probability * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _inversion_counts(ratings: Sequence[float]) -> tuple[int, int]:
    adjacent = sum(
        ratings[player] < ratings[player + 1]
        for player in range(len(ratings) - 1)
    )
    all_pair = sum(
        ratings[player_a] < ratings[player_b]
        for player_a in range(len(ratings))
        for player_b in range(player_a + 1, len(ratings))
    )
    return adjacent, all_pair


def _replicate_rows(
    *,
    world: ToyWorld,
    events: int,
    replicate: int,
    seed: int,
) -> tuple[tuple[ReplicateEvent, ...], tuple[float, ...]]:
    history = generate_history(world=world, events=events, seed=seed)
    run = replay_history(
        history,
        label="true",
        initial_ratings=world.latent_skills,
        q=world.q,
        k=world.k,
        retain_forecasts=False,
    )
    true_probabilities = pair_probabilities(world.latent_skills, q=world.q)
    rows: list[ReplicateEvent] = []
    for snapshot in run.snapshots:
        adjacent, all_pair = _inversion_counts(snapshot.ratings)
        rows.append(
            ReplicateEvent(
                replicate=replicate,
                seed=seed,
                event=snapshot.event,
                global_bouts=snapshot.global_bouts,
                truth_relative_state_rmse=centred_state_distance(
                    snapshot.ratings,
                    world.latent_skills,
                ),
                truth_relative_probability_rmse=vector_rmse(
                    pair_probabilities(snapshot.ratings, q=world.q),
                    true_probabilities,
                ),
                adjacent_order_inversions=adjacent,
                all_pair_order_inversions=all_pair,
            )
        )
    return tuple(rows), run.snapshots[-1].ratings


def build_final_mean_error_diagnostic(
    final_ratings: Sequence[Sequence[float]],
    latent_skills: Sequence[float],
) -> tuple[tuple[FinalPlayerMeanError, ...], tuple[FinalMeanErrorProgress, ...]]:
    if not final_ratings:
        raise ValueError("at least one final rating vector is required")
    if any(len(ratings) != len(latent_skills) for ratings in final_ratings):
        raise ValueError("final ratings and latent skills must have equal dimensions")

    running_sums = [0.0] * len(latent_skills)
    progress: list[FinalMeanErrorProgress] = []
    for replicate_count, ratings in enumerate(final_ratings, start=1):
        for player, rating in enumerate(ratings):
            running_sums[player] += rating
        mean_ratings = [total / replicate_count for total in running_sums]
        mean_errors = [
            rating - latent
            for rating, latent in zip(mean_ratings, latent_skills)
        ]
        progress.append(
            FinalMeanErrorProgress(
                replicate_count=replicate_count,
                mean_rating_error_rmse=vector_rmse(mean_ratings, latent_skills),
                maximum_absolute_mean_error=max(abs(error) for error in mean_errors),
            )
        )

    final_count = len(final_ratings)
    players: list[FinalPlayerMeanError] = []
    for player, latent in enumerate(latent_skills):
        ratings = [float(run[player]) for run in final_ratings]
        mean_rating = statistics.fmean(ratings)
        standard_deviation = statistics.stdev(ratings) if final_count > 1 else 0.0
        standard_error = standard_deviation / (final_count**0.5)
        mean_error = mean_rating - latent
        players.append(
            FinalPlayerMeanError(
                player=player + 1,
                latent_skill=float(latent),
                mean_final_rating=mean_rating,
                mean_signed_error=mean_error,
                final_rating_standard_deviation=standard_deviation,
                mean_signed_error_standard_error=standard_error,
                z_score_against_zero=(
                    mean_error / standard_error if standard_error else 0.0
                ),
            )
        )
    return tuple(players), tuple(progress)


def aggregate_replicate_events(
    rows: Sequence[ReplicateEvent],
) -> tuple[EnsembleEvent, ...]:
    if not rows:
        raise ValueError("at least one replicate event is required")
    grouped: dict[int, list[ReplicateEvent]] = {}
    for row in rows:
        grouped.setdefault(row.event, []).append(row)

    summaries: list[EnsembleEvent] = []
    for event, event_rows in sorted(grouped.items()):
        states = [row.truth_relative_state_rmse for row in event_rows]
        probabilities = [row.truth_relative_probability_rmse for row in event_rows]
        summaries.append(
            EnsembleEvent(
                event=event,
                global_bouts_per_run=event_rows[0].global_bouts,
                replicate_count=len(event_rows),
                state_mean=statistics.fmean(states),
                state_median=statistics.median(states),
                state_standard_deviation=(
                    statistics.stdev(states) if len(states) > 1 else 0.0
                ),
                state_q05=_quantile(states, 0.05),
                state_q25=_quantile(states, 0.25),
                state_q75=_quantile(states, 0.75),
                state_q95=_quantile(states, 0.95),
                probability_mean=statistics.fmean(probabilities),
                probability_median=statistics.median(probabilities),
                probability_standard_deviation=(
                    statistics.stdev(probabilities) if len(probabilities) > 1 else 0.0
                ),
                probability_q05=_quantile(probabilities, 0.05),
                probability_q25=_quantile(probabilities, 0.25),
                probability_q75=_quantile(probabilities, 0.75),
                probability_q95=_quantile(probabilities, 0.95),
                adjacent_inversion_run_fraction=sum(
                    row.adjacent_order_inversions > 0 for row in event_rows
                )
                / len(event_rows),
                all_pair_inversion_mean=statistics.fmean(
                    row.all_pair_order_inversions for row in event_rows
                ),
            )
        )
    return tuple(summaries)


def _write_rows(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    materialized = list(rows)
    if not materialized:
        raise ValueError(f"cannot write empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(materialized[0]))
        writer.writeheader()
        writer.writerows(materialized)


def _selected_summary_table(result: TrueStartEnsembleResult) -> str:
    requested = {0, 1, 2, 5, 10, 25, 50, 100, 200, result.events}
    rows = []
    for row in result.event_summary:
        if row.event not in requested:
            continue
        rows.append(
            f"| {row.event} | {row.global_bouts_per_run} | {row.state_mean:.3f} | "
            f"{row.state_median:.3f} | {row.state_q05:.3f}--{row.state_q95:.3f} | "
            f"{row.probability_mean:.4f} | {row.probability_q05:.4f}--{row.probability_q95:.4f} | "
            f"{100 * row.adjacent_inversion_run_fraction:.1f}% |"
        )
    return "\n".join(rows)


def _report_markdown(result: TrueStartEnsembleResult) -> str:
    final = result.event_summary[-1]
    final_mean_error = result.final_mean_error_progress[-1]
    player_rows = "\n".join(
        f"| {row.player} | {row.latent_skill:.1f} | {row.mean_final_rating:.3f} | "
        f"{row.mean_signed_error:+.3f} | {row.mean_signed_error_standard_error:.3f} | "
        f"{row.z_score_against_zero:+.2f} |"
        for row in result.final_player_mean_errors
    )
    return f"""# True-Start Toy Ensemble

## Purpose

This Stage 1 development experiment aggregates truth-relative error separately
within {result.runs} independent true-start histories. It does not average
ratings before calculating error and does not measure forgetting.

## Run

- Master seed: {result.master_seed}
- Replicates: {result.runs}
- Events per replicate: {result.events}
- Global bouts per replicate: {result.events * result.world.pairs_per_event}
- Total simulated bouts: {result.runs * result.events * result.world.pairs_per_event}
- Players: {result.world.player_count}
- Latent gap: {result.world.latent_gap:g}
- q: {result.world.q:g}
- K: {result.world.k:g}
- Total run time: {result.elapsed_seconds:.3f} seconds

Every replicate begins with displayed ratings equal to latent skills. Each then
uses an independent complete-round-robin order and independently sampled bout
outcomes generated from those same latent skills.

## Selected aggregate snapshots

| Event | Bouts/run | State mean | State median | State 5--95% | Probability mean | Probability 5--95% | Runs with adjacent inversion |
|---:|---:|---:|---:|---:|---:|---:|---:|
{_selected_summary_table(result)}

At event {final.event}, the mean truth-relative rating-state RMSE is
`{final.state_mean:.6f}` points and the mean all-pair probability RMSE is
`{final.probability_mean:.6f}`, or {100 * final.probability_mean:.2f}
percentage points RMS. The central 90% ranges across runs are
`{final.state_q05:.6f}`--`{final.state_q95:.6f}` rating points and
`{final.probability_q05:.6f}`--`{final.probability_q95:.6f}` probability.

## Signed-error sanity check

The table below first averages each player's final displayed rating across all
{result.runs} runs and only then subtracts latent skill. Positive and negative
errors can therefore cancel across histories.

| Player | Latent skill | Mean final rating | Mean signed error | Standard error | z against 0 |
|---:|---:|---:|---:|---:|---:|
{player_rows}

The RMSE between the vector of mean final ratings and latent skill is
`{final_mean_error.mean_rating_error_rmse:.6f}` points. The largest absolute
player mean error is `{final_mean_error.maximum_absolute_mean_error:.6f}`
points. Compare this with the mean within-run RMSE of `{final.state_mean:.6f}`
points. The cumulative-replicate chart shows whether the former generally
shrinks as independent histories are added. The standard errors and z scores
are Monte Carlo diagnostics, not an independence assumption across players;
the zero-sum Elo updates couple their errors.

## Interpretation boundary

These curves describe the distribution of natural fixed-`K` fluctuation from a
perfectly informed start in this declared toy world. They are not evidence that
Elo is predictively useful, and they do not measure initialization forgetting.
"""


def _ensemble_chart(
    div_id: str,
    title: str,
    rows: Sequence[EnsembleEvent],
    *,
    mean_field: str,
    median_field: str,
    low_field: str,
    high_field: str,
    y_axis_title: str,
) -> str:
    def values(field: str) -> list[float]:
        return [float(getattr(row, field)) for row in rows]

    chart = _plotly_chart(
        div_id,
        title,
        [row.event for row in rows],
        [
            {
                "name": "5th percentile",
                "y": values(low_field),
                "line": {"width": 0},
                "hoverinfo": "skip",
                "showlegend": False,
            },
            {
                "name": "5th–95th percentiles",
                "y": values(high_field),
                "line": {"width": 0},
                "fill": "tonexty",
                "fillcolor": "rgba(99, 179, 237, 0.35)",
            },
            {
                "name": "Mean",
                "y": values(mean_field),
                "line": {"color": "#2457a7", "width": 2},
            },
            {
                "name": "Median",
                "y": values(median_field),
                "line": {"color": "#b04a3a", "width": 1.5},
            },
        ],
        y_axis_title=y_axis_title,
    )
    return chart + "<p>Mean and median; shaded band: 5th–95th percentiles across runs.</p>"


def _report_html(markdown_report: str, result: TrueStartEnsembleResult) -> str:
    rows = result.event_summary
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>True-Start Toy Ensemble</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ max-width: 960px; margin: 2rem auto; padding: 0 1rem; font-family: system-ui, sans-serif; line-height: 1.5; }}
    .plot {{ width: 100%; min-height: 360px; border: 1px solid #ddd; }}
    pre {{ white-space: pre-wrap; background: #f4f4f4; padding: 1rem; }}
  </style>
</head>
<body>
  <h1>True-Start Toy Ensemble</h1>
  <p>Each run's error is calculated before aggregation. This is a natural-fluctuation baseline, not a forgetting comparison.</p>
  {_ensemble_chart("ensemble-state-rmse", "Truth-relative rating-state RMSE", rows, mean_field="state_mean", median_field="state_median", low_field="state_q05", high_field="state_q95", y_axis_title="Rating-state RMSE (rating points)")}
  {_ensemble_chart("ensemble-probability-rmse", "All-pair probability RMSE against latent probabilities", rows, mean_field="probability_mean", median_field="probability_median", low_field="probability_q05", high_field="probability_q95", y_axis_title="All-pair probability RMSE")}
  {_plotly_chart("mean-signed-error-check", "Final-rating signed-error cancellation", [row.replicate_count for row in result.final_mean_error_progress], [{"name": "RMSE of mean signed errors", "y": [row.mean_rating_error_rmse for row in result.final_mean_error_progress], "line": {"color": "#d97706"}}], y_axis_title="RMSE of player mean errors (rating points)", x_axis_title="Replicates included")}
  <h2>Audit summary</h2>
  <pre>{html.escape(markdown_report)}</pre>
</body>
</html>
"""


def _write_outputs(
    result: TrueStartEnsembleResult,
    *,
    started_at: datetime,
    finished_at: datetime,
    write_tables: bool = True,
) -> None:
    root = result.run_directory
    if write_tables:
        _write_rows(
            root / "replicate_seeds.csv",
            (
                {"replicate": index, "seed": seed}
                for index, seed in enumerate(result.replicate_seeds, start=1)
            ),
        )
        _write_rows(
            root / "replicate_event_metrics.csv",
            map(asdict, result.replicate_events),
        )
        _write_rows(root / "event_summary.csv", map(asdict, result.event_summary))
        _write_rows(
            root / "final_player_mean_errors.csv",
            map(asdict, result.final_player_mean_errors),
        )
        _write_rows(
            root / "final_mean_error_progress.csv",
            map(asdict, result.final_mean_error_progress),
        )
    report = _report_markdown(result)
    (root / "report.md").write_text(report, encoding="utf-8")
    (root / "report.html").write_text(_report_html(report, result), encoding="utf-8")
    manifest = {
        "experiment": "forgetting toy true-start ensemble",
        "experimental_contract_version": 1,
        "run_role": "development",
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "elapsed_seconds": result.elapsed_seconds,
        "world": {
            "player_count": result.world.player_count,
            "latent_gap": result.world.latent_gap,
            "latent_skills": list(result.world.latent_skills),
            "q": result.world.q,
            "k": result.world.k,
        },
        "ensemble": {
            "events_per_replicate": result.events,
            "replicate_count": result.runs,
            "master_seed": result.master_seed,
            "total_simulated_bouts": (
                result.runs * result.events * result.world.pairs_per_event
            ),
            "aggregation": (
                "truth-relative RMSE calculated within each run before "
                "mean, median, standard deviation, and quantile aggregation"
            ),
            "quantile_method": "linear interpolation over ordered replicate values",
        },
        "outputs": {
            "replicate_seeds": "replicate_seeds.csv",
            "replicate_event_metrics": "replicate_event_metrics.csv",
            "event_summary": "event_summary.csv",
            "final_player_mean_errors": "final_player_mean_errors.csv",
            "final_mean_error_progress": "final_mean_error_progress.csv",
            "report_markdown": "report.md",
            "report_html": "report.html",
            "manifest": "manifest.json",
        },
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    refresh_run_reports(root, manifest)


def run_true_start_ensemble(
    *,
    world: ToyWorld = ToyWorld(),
    events: int = 500,
    runs: int = 100,
    seed: int = 1,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    progress_every: int = 10,
) -> TrueStartEnsembleResult:
    if events < 1:
        raise ValueError("events must be at least 1")
    if runs < 1:
        raise ValueError("runs must be at least 1")
    if progress_every < 0:
        raise ValueError("progress_every must not be negative")

    started_at = datetime.now().astimezone()
    timer_started = time.perf_counter()
    run_directory = make_run_directory(
        output_root,
        role="development",
        seed=seed,
        timestamp=started_at,
    )
    seed_rng = random.Random(seed)
    replicate_seeds = tuple(seed_rng.getrandbits(64) for _ in range(runs))
    replicate_events: list[ReplicateEvent] = []
    final_ratings: list[tuple[float, ...]] = []
    for replicate, replicate_seed in enumerate(replicate_seeds, start=1):
        rows, final_rating_vector = _replicate_rows(
            world=world,
            events=events,
            replicate=replicate,
            seed=replicate_seed,
        )
        replicate_events.extend(rows)
        final_ratings.append(final_rating_vector)
        if progress_every and (replicate % progress_every == 0 or replicate == runs):
            print(f"Completed true-start replicate {replicate}/{runs}", flush=True)

    event_summary = aggregate_replicate_events(replicate_events)
    final_player_mean_errors, final_mean_error_progress = (
        build_final_mean_error_diagnostic(final_ratings, world.latent_skills)
    )
    elapsed_before_output = time.perf_counter() - timer_started
    timed = TrueStartEnsembleResult(
        run_directory=run_directory,
        world=world,
        events=events,
        runs=runs,
        master_seed=seed,
        replicate_seeds=replicate_seeds,
        replicate_events=tuple(replicate_events),
        event_summary=event_summary,
        final_player_mean_errors=final_player_mean_errors,
        final_mean_error_progress=final_mean_error_progress,
        elapsed_seconds=elapsed_before_output,
    )
    _write_outputs(timed, started_at=started_at, finished_at=datetime.now().astimezone())
    total_elapsed = time.perf_counter() - timer_started
    result = TrueStartEnsembleResult(
        run_directory=run_directory,
        world=world,
        events=events,
        runs=runs,
        master_seed=seed,
        replicate_seeds=replicate_seeds,
        replicate_events=tuple(replicate_events),
        event_summary=event_summary,
        final_player_mean_errors=final_player_mean_errors,
        final_mean_error_progress=final_mean_error_progress,
        elapsed_seconds=total_elapsed,
    )
    # Rewrite only the small report and manifest with the output-inclusive time.
    _write_outputs(
        result,
        started_at=started_at,
        finished_at=datetime.now().astimezone(),
        write_tables=False,
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Aggregate natural fixed-K fluctuation across independent "
            "true-start toy histories."
        )
    )
    parser.add_argument("--players", type=int, default=10)
    parser.add_argument("--latent-gap", type=float, default=40.0)
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--k", type=float, default=5.0)
    parser.add_argument("--events", type=int, default=500)
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    total_started = time.perf_counter()
    result = run_true_start_ensemble(
        world=ToyWorld(
            player_count=args.players,
            latent_gap=args.latent_gap,
            q=args.q,
            k=args.k,
        ),
        events=args.events,
        runs=args.runs,
        seed=args.seed,
        output_root=args.output_root,
        progress_every=args.progress_every,
    )
    final = result.event_summary[-1]
    print(f"Wrote true-start ensemble to {result.run_directory.resolve()}")
    print(
        f"Final mean rating-state RMSE: {final.state_mean:.6f}; "
        f"mean probability RMSE: {final.probability_mean:.6f}"
    )
    print(
        "RMSE after averaging final ratings across runs: "
        f"{result.final_mean_error_progress[-1].mean_rating_error_rmse:.6f}"
    )
    print(f"Total run time: {time.perf_counter() - total_started:.3f} seconds")


if __name__ == "__main__":
    main()

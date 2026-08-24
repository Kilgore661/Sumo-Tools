"""Aggregate alternative starts and paired forgetting against T0."""

from __future__ import annotations

import argparse
import html
import json
import math
import random
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .elo import replay_history
from .history import generate_history
from .metrics import build_event_metrics, build_forgetting_landmarks
from .model import ToyWorld
from .outputs import _plotly_chart, make_run_directory
from .report_identity import refresh_run_reports
from .true_start_ensemble import (
    FinalMeanErrorProgress,
    FinalPlayerMeanError,
    _quantile,
    _write_rows,
    build_final_mean_error_diagnostic,
)


DEFAULT_CONSTANT_OUTPUT_ROOT = Path(
    "files/output/analysis/forgetting/toy/constant_start_ensemble"
)
DEFAULT_INVERTED_OUTPUT_ROOT = Path(
    "files/output/analysis/forgetting/toy/inverted_start_ensemble"
)
DEFAULT_OUTPUT_ROOT = DEFAULT_CONSTANT_OUTPUT_ROOT


@dataclass(frozen=True)
class PairedReplicateEvent:
    replicate: int
    seed: int
    event: int
    global_bouts: int
    true_state_rmse: float
    true_probability_rmse: float
    t_prime_state_rmse: float
    t_prime_probability_rmse: float
    paired_state_rmse: float
    paired_probability_rmse: float
    paired_probability_fraction_remaining: float


@dataclass(frozen=True)
class ReplicateForgettingLandmark:
    replicate: int
    seed: int
    kind: str
    target: float
    tolerance: float
    first_event: int | None
    first_global_bout: int | None
    recrossed: bool | None
    later_fraction_below: float | None
    remaining_events: int | None
    right_censored: bool


@dataclass(frozen=True)
class PairedEventSummary:
    event: int
    global_bouts_per_run: int
    replicate_count: int
    true_state_mean: float
    true_probability_mean: float
    t_prime_state_mean: float
    t_prime_state_median: float
    t_prime_state_q05: float
    t_prime_state_q95: float
    t_prime_probability_mean: float
    t_prime_probability_median: float
    t_prime_probability_q05: float
    t_prime_probability_q95: float
    paired_state_mean: float
    paired_state_median: float
    paired_state_q05: float
    paired_state_q95: float
    paired_probability_mean: float
    paired_probability_median: float
    paired_probability_q05: float
    paired_probability_q95: float
    paired_fraction_mean: float
    paired_fraction_median: float
    paired_fraction_q05: float
    paired_fraction_q95: float


@dataclass(frozen=True)
class ForgettingSummary:
    kind: str
    target: float
    tolerance: float
    replicate_count: int
    observed_count: int
    right_censored_count: int
    observed_fraction: float
    first_event_mean: float | None
    first_event_median: float | None
    first_event_q05: float | None
    first_event_q95: float | None
    recrossed_fraction: float | None


@dataclass(frozen=True)
class ConstantStartEnsembleResult:
    run_directory: Path
    world: ToyWorld
    events: int
    runs: int
    master_seed: int
    persistence_events: int
    comparison_code: str
    comparison_name: str
    comparison_initial_ratings: tuple[float, ...]
    replicate_seeds: tuple[int, ...]
    replicate_events: tuple[PairedReplicateEvent, ...]
    event_summary: tuple[PairedEventSummary, ...]
    replicate_landmarks: tuple[ReplicateForgettingLandmark, ...]
    forgetting_summary: tuple[ForgettingSummary, ...]
    t_prime_final_player_mean_errors: tuple[FinalPlayerMeanError, ...]
    t_prime_final_mean_error_progress: tuple[FinalMeanErrorProgress, ...]
    elapsed_seconds: float


def _replicate(
    *,
    world: ToyWorld,
    events: int,
    replicate: int,
    seed: int,
    persistence_events: int,
    comparison_code: str,
    comparison_initial_ratings: Sequence[float],
) -> tuple[
    tuple[PairedReplicateEvent, ...],
    tuple[ReplicateForgettingLandmark, ...],
    tuple[float, ...],
]:
    history = generate_history(world=world, events=events, seed=seed)
    true_run = replay_history(
        history,
        label="T0",
        initial_ratings=world.latent_skills,
        q=world.q,
        k=world.k,
        retain_forecasts=False,
    )
    t_prime_run = replay_history(
        history,
        label=comparison_code,
        initial_ratings=comparison_initial_ratings,
        q=world.q,
        k=world.k,
        retain_forecasts=False,
    )
    metrics = build_event_metrics(
        true_run=true_run,
        flat_run=t_prime_run,
        latent_skills=world.latent_skills,
        q=world.q,
    )
    rows = tuple(
        PairedReplicateEvent(
            replicate=replicate,
            seed=seed,
            event=row.event,
            global_bouts=row.global_bouts,
            true_state_rmse=row.true_state_error,
            true_probability_rmse=row.true_probability_error,
            t_prime_state_rmse=row.flat_state_error,
            t_prime_probability_rmse=row.flat_probability_error,
            paired_state_rmse=row.state_distance,
            paired_probability_rmse=row.forecast_distance,
            paired_probability_fraction_remaining=row.forecast_fraction_remaining,
        )
        for row in metrics
    )
    landmarks = tuple(
        ReplicateForgettingLandmark(
            replicate=replicate,
            seed=seed,
            **asdict(landmark),
        )
        for landmark in build_forgetting_landmarks(
            metrics,
            persistence_events=persistence_events,
        )
    )
    return rows, landmarks, t_prime_run.snapshots[-1].ratings


def _describe(values: Sequence[float]) -> tuple[float, float, float, float]:
    return (
        statistics.fmean(values),
        statistics.median(values),
        _quantile(values, 0.05),
        _quantile(values, 0.95),
    )


def aggregate_event_rows(
    rows: Sequence[PairedReplicateEvent],
) -> tuple[PairedEventSummary, ...]:
    if not rows:
        raise ValueError("at least one replicate event is required")
    grouped: dict[int, list[PairedReplicateEvent]] = {}
    for row in rows:
        grouped.setdefault(row.event, []).append(row)

    summaries: list[PairedEventSummary] = []
    for event, event_rows in sorted(grouped.items()):
        t_state = _describe([row.t_prime_state_rmse for row in event_rows])
        t_probability = _describe(
            [row.t_prime_probability_rmse for row in event_rows]
        )
        paired_state = _describe([row.paired_state_rmse for row in event_rows])
        paired_probability = _describe(
            [row.paired_probability_rmse for row in event_rows]
        )
        paired_fraction = _describe(
            [row.paired_probability_fraction_remaining for row in event_rows]
        )
        summaries.append(
            PairedEventSummary(
                event=event,
                global_bouts_per_run=event_rows[0].global_bouts,
                replicate_count=len(event_rows),
                true_state_mean=statistics.fmean(
                    row.true_state_rmse for row in event_rows
                ),
                true_probability_mean=statistics.fmean(
                    row.true_probability_rmse for row in event_rows
                ),
                t_prime_state_mean=t_state[0],
                t_prime_state_median=t_state[1],
                t_prime_state_q05=t_state[2],
                t_prime_state_q95=t_state[3],
                t_prime_probability_mean=t_probability[0],
                t_prime_probability_median=t_probability[1],
                t_prime_probability_q05=t_probability[2],
                t_prime_probability_q95=t_probability[3],
                paired_state_mean=paired_state[0],
                paired_state_median=paired_state[1],
                paired_state_q05=paired_state[2],
                paired_state_q95=paired_state[3],
                paired_probability_mean=paired_probability[0],
                paired_probability_median=paired_probability[1],
                paired_probability_q05=paired_probability[2],
                paired_probability_q95=paired_probability[3],
                paired_fraction_mean=paired_fraction[0],
                paired_fraction_median=paired_fraction[1],
                paired_fraction_q05=paired_fraction[2],
                paired_fraction_q95=paired_fraction[3],
            )
        )
    return tuple(summaries)


def aggregate_landmarks(
    rows: Sequence[ReplicateForgettingLandmark],
) -> tuple[ForgettingSummary, ...]:
    grouped: dict[tuple[str, float], list[ReplicateForgettingLandmark]] = {}
    for row in rows:
        grouped.setdefault((row.kind, row.target), []).append(row)

    summaries: list[ForgettingSummary] = []
    for (kind, target), group in grouped.items():
        observed = [row for row in group if row.first_event is not None]
        first_events = [float(row.first_event) for row in observed if row.first_event is not None]
        recrossed = [bool(row.recrossed) for row in observed if row.recrossed is not None]
        summaries.append(
            ForgettingSummary(
                kind=kind,
                target=target,
                tolerance=group[0].tolerance,
                replicate_count=len(group),
                observed_count=len(observed),
                right_censored_count=len(group) - len(observed),
                observed_fraction=len(observed) / len(group),
                first_event_mean=(statistics.fmean(first_events) if first_events else None),
                first_event_median=(statistics.median(first_events) if first_events else None),
                first_event_q05=(_quantile(first_events, 0.05) if first_events else None),
                first_event_q95=(_quantile(first_events, 0.95) if first_events else None),
                recrossed_fraction=(statistics.fmean(recrossed) if recrossed else None),
            )
        )
    return tuple(sorted(summaries, key=lambda row: (row.kind, row.target)))


def _band_chart(
    div_id: str,
    title: str,
    rows: Sequence[object],
    *,
    mean_field: str,
    median_field: str,
    low_field: str,
    high_field: str,
    y_axis_title: str,
) -> str:
    def values(field: str) -> list[float]:
        return [float(getattr(row, field)) for row in rows]

    return _plotly_chart(
        div_id,
        title,
        [int(getattr(row, "event")) for row in rows],
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


def _selected_rows(result: ConstantStartEnsembleResult) -> str:
    selected = {0, 1, 2, 5, 10, 25, 50, 100, 200, result.events}
    return "\n".join(
        f"| {row.event} | {row.global_bouts_per_run} | {row.t_prime_state_mean:.3f} | "
        f"{row.t_prime_state_q05:.3f}–{row.t_prime_state_q95:.3f} | "
        f"{row.t_prime_probability_mean:.4f} | "
        f"{row.t_prime_probability_q05:.4f}–{row.t_prime_probability_q95:.4f} |"
        for row in result.event_summary
        if row.event in selected
    )


def _landmark_table(result: ConstantStartEnsembleResult) -> str:
    return "\n".join(
        f"| {row.kind} | {row.target:g} | {row.tolerance:.6f} | "
        f"{100 * row.observed_fraction:.1f}% | "
        f"{row.first_event_median if row.first_event_median is not None else 'NA'} | "
        f"{row.first_event_q05 if row.first_event_q05 is not None else 'NA'}–"
        f"{row.first_event_q95 if row.first_event_q95 is not None else 'NA'} | "
        f"{100 * row.recrossed_fraction:.1f}% |"
        if row.recrossed_fraction is not None
        else f"| {row.kind} | {row.target:g} | {row.tolerance:.6f} | 0.0% | NA | NA | NA |"
        for row in result.forgetting_summary
    )


def _t_prime_markdown(result: ConstantStartEnsembleResult) -> str:
    final = result.event_summary[-1]
    final_mean = result.t_prime_final_mean_error_progress[-1]
    player_rows = "\n".join(
        f"| {row.player} | {row.latent_skill:.1f} | {row.mean_final_rating:.3f} | "
        f"{row.mean_signed_error:+.3f} | {row.mean_signed_error_standard_error:.3f} | "
        f"{row.z_score_against_zero:+.2f} |"
        for row in result.t_prime_final_player_mean_errors
    )
    return f"""# {result.comparison_code} {result.comparison_name} Ensemble

## Purpose

This is Output 1. It describes {result.comparison_code} on its own, relative to
known latent skill. It uses {result.comparison_name.lower()} initialization. It
does not measure forgetting; the separate paired report compares T0 with
{result.comparison_code}.

## Run

- Master seed: {result.master_seed}
- Replicates: {result.runs}
- Events per replicate: {result.events}
- Bouts per event: {result.world.pairs_per_event}
- Initial ratings: {list(result.comparison_initial_ratings)}
- Players: {result.world.player_count}
- Latent gap: {result.world.latent_gap:g}
- q: {result.world.q:g}
- K: {result.world.k:g}
- Total run time: {result.elapsed_seconds:.3f} seconds

## Selected aggregate snapshots

| Event | Bouts/run | State mean | State 5–95% | Probability mean | Probability 5–95% |
|---:|---:|---:|---:|---:|---:|
{_selected_rows(result)}

At event {final.event}, {result.comparison_code} has mean truth-relative rating-state RMSE
`{final.t_prime_state_mean:.6f}` and mean probability RMSE
`{final.t_prime_probability_mean:.6f}`.

## Final ensemble signed-error diagnostic

| Player | Latent skill | Mean final rating | Mean signed error | Standard error | z against 0 |
|---:|---:|---:|---:|---:|---:|
{player_rows}

The RMSE between {result.comparison_code}'s ensemble-mean final rating vector and latent skill is
`{final_mean.mean_rating_error_rmse:.6f}` points.
"""


def _paired_markdown(result: ConstantStartEnsembleResult) -> str:
    initial = result.event_summary[0]
    final = result.event_summary[-1]
    return f"""# T0 versus {result.comparison_code} Paired Forgetting Ensemble

## Purpose

This is Output 2. In every replicate, T0 and {result.comparison_code} replay the same schedule and
outcomes. Their disagreement therefore isolates memory of initialization.

## Run

- Master seed: {result.master_seed}
- Replicates: {result.runs}
- Events per replicate: {result.events}
- Persistence requirement: {result.persistence_events} consecutive events
- T0 initialization: latent skills
- {result.comparison_code} initialization: {result.comparison_name.lower()}
- Total run time: {result.elapsed_seconds:.3f} seconds

Initial mean paired rating-state RMSE is `{initial.paired_state_mean:.6f}` and
initial mean paired probability RMSE is `{initial.paired_probability_mean:.6f}`.
At event {final.event}, these are `{final.paired_state_mean:.6f}` and
`{final.paired_probability_mean:.6f}` respectively.

## Forgetting landmarks

Landmarks use paired all-pair probability RMSE and require the tolerance to be
met for {result.persistence_events} consecutive events. Quantiles describe the
first qualifying event among observed replicates; censored replicates are
reported through the observed percentage.

| Kind | Target | Tolerance | Observed | Median event | Event 5–95% | Later recrossing |
|---|---:|---:|---:|---:|---:|---:|
{_landmark_table(result)}
"""


def _html_shell(title: str, body: str, markdown_report: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ max-width: 1000px; margin: 2rem auto; padding: 0 1rem;
            font-family: system-ui, sans-serif; line-height: 1.5; }}
    .plot {{ width: 100%; min-height: 360px; border: 1px solid #ddd; }}
    pre {{ white-space: pre-wrap; background: #f4f4f4; padding: 1rem; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  {body}
  <h2>Audit summary</h2>
  <pre>{html.escape(markdown_report)}</pre>
</body>
</html>
"""


def _t_prime_html(report: str, result: ConstantStartEnsembleResult) -> str:
    rows = result.event_summary
    code = result.comparison_code
    body = (
        f"<p>Output 1: {code} alone relative to latent skill. This is not a forgetting comparison.</p>"
        + _band_chart(
            "t-prime-state",
            f"{code} truth-relative rating-state RMSE",
            rows,
            mean_field="t_prime_state_mean",
            median_field="t_prime_state_median",
            low_field="t_prime_state_q05",
            high_field="t_prime_state_q95",
            y_axis_title="Rating-state RMSE (rating points)",
        )
        + _band_chart(
            "t-prime-probability",
            f"{code} probability RMSE against latent probabilities",
            rows,
            mean_field="t_prime_probability_mean",
            median_field="t_prime_probability_median",
            low_field="t_prime_probability_q05",
            high_field="t_prime_probability_q95",
            y_axis_title="All-pair probability RMSE",
        )
        + _plotly_chart(
            "t-prime-signed-error",
            f"{code} final-rating signed-error cancellation",
            [row.replicate_count for row in result.t_prime_final_mean_error_progress],
            [{
                "name": "RMSE of mean signed errors",
                "y": [
                    row.mean_rating_error_rmse
                    for row in result.t_prime_final_mean_error_progress
                ],
                "line": {"color": "#d97706"},
            }],
            y_axis_title="RMSE of player mean errors (rating points)",
            x_axis_title="Replicates included",
        )
    )
    return _html_shell(f"{code} {result.comparison_name} Ensemble", body, report)


def _paired_html(report: str, result: ConstantStartEnsembleResult) -> str:
    rows = result.event_summary
    code = result.comparison_code
    body = (
        f"<p>Output 2: paired T0-versus-{code} disagreement on identical histories.</p>"
        + _band_chart(
            "paired-state",
            f"T0 versus {code} rating-state disagreement",
            rows,
            mean_field="paired_state_mean",
            median_field="paired_state_median",
            low_field="paired_state_q05",
            high_field="paired_state_q95",
            y_axis_title="Paired rating-state RMSE (rating points)",
        )
        + _band_chart(
            "paired-probability",
            f"T0 versus {code} probability disagreement",
            rows,
            mean_field="paired_probability_mean",
            median_field="paired_probability_median",
            low_field="paired_probability_q05",
            high_field="paired_probability_q95",
            y_axis_title="Paired all-pair probability RMSE",
        )
        + _band_chart(
            "paired-fraction",
            f"T0 versus {code} probability disagreement remaining",
            rows,
            mean_field="paired_fraction_mean",
            median_field="paired_fraction_median",
            low_field="paired_fraction_q05",
            high_field="paired_fraction_q95",
            y_axis_title="Fraction of initial disagreement",
        )
    )
    return _html_shell(f"T0 versus {code} Paired Forgetting Ensemble", body, report)


def _write_outputs(
    result: ConstantStartEnsembleResult,
    *,
    started_at: datetime,
    finished_at: datetime,
    write_tables: bool = True,
) -> None:
    root = result.run_directory
    stem = result.comparison_code.lower()
    if write_tables:
        _write_rows(
            root / "replicate_seeds.csv",
            ({"replicate": i, "seed": seed} for i, seed in enumerate(result.replicate_seeds, 1)),
        )
        _write_rows(root / "replicate_event_metrics.csv", map(asdict, result.replicate_events))
        _write_rows(root / "event_summary.csv", map(asdict, result.event_summary))
        _write_rows(
            root / "replicate_forgetting_landmarks.csv",
            map(asdict, result.replicate_landmarks),
        )
        _write_rows(root / "forgetting_summary.csv", map(asdict, result.forgetting_summary))
        _write_rows(
            root / f"{stem}_final_player_mean_errors.csv",
            map(asdict, result.t_prime_final_player_mean_errors),
        )
        _write_rows(
            root / f"{stem}_final_mean_error_progress.csv",
            map(asdict, result.t_prime_final_mean_error_progress),
        )

    t_prime_report = _t_prime_markdown(result)
    paired_report = _paired_markdown(result)
    (root / f"{stem}_report.md").write_text(t_prime_report, encoding="utf-8")
    (root / f"{stem}_report.html").write_text(
        _t_prime_html(t_prime_report, result), encoding="utf-8"
    )
    (root / "paired_report.md").write_text(paired_report, encoding="utf-8")
    (root / "paired_report.html").write_text(
        _paired_html(paired_report, result), encoding="utf-8"
    )

    manifest = {
        "experiment": (
            f"forgetting toy {result.comparison_code} ensemble and paired comparison"
        ),
        "experimental_contract_version": 1,
        "run_role": (
            "canonical"
            if (result.runs, result.events, result.master_seed) == (800, 500, 1)
            else "development"
        ),
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
            "persistence_events": result.persistence_events,
            "total_simulated_bouts": result.runs * result.events * result.world.pairs_per_event,
            "paired_histories": True,
        },
        "initializations": {
            "T0": list(result.world.latent_skills),
            result.comparison_code: list(result.comparison_initial_ratings),
        },
        "outputs": {
            "replicate_seeds": "replicate_seeds.csv",
            f"{stem}_report_markdown": f"{stem}_report.md",
            f"{stem}_report_html": f"{stem}_report.html",
            "paired_report_markdown": "paired_report.md",
            "paired_report_html": "paired_report.html",
            "replicate_event_metrics": "replicate_event_metrics.csv",
            "event_summary": "event_summary.csv",
            "replicate_forgetting_landmarks": "replicate_forgetting_landmarks.csv",
            "forgetting_summary": "forgetting_summary.csv",
            f"{stem}_final_player_mean_errors": f"{stem}_final_player_mean_errors.csv",
            f"{stem}_final_mean_error_progress": f"{stem}_final_mean_error_progress.csv",
            "manifest": "manifest.json",
        },
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    refresh_run_reports(root, manifest)


def run_constant_start_ensemble(
    *,
    world: ToyWorld = ToyWorld(),
    events: int = 500,
    runs: int = 800,
    seed: int = 1,
    persistence_events: int = 25,
    output_root: Path | None = None,
    progress_every: int = 50,
    initialization: str = "constant",
    custom_code: str | None = None,
    custom_name: str | None = None,
    custom_initial_ratings: Sequence[float] | None = None,
) -> ConstantStartEnsembleResult:
    if events < 1 or runs < 1 or persistence_events < 1:
        raise ValueError("events, runs, and persistence_events must be positive")
    if progress_every < 0:
        raise ValueError("progress_every must not be negative")
    if initialization == "constant":
        comparison_code = "TC"
        comparison_name = "Constant-Midpoint"
        comparison_initial_ratings = world.flat_initial_ratings
        output_root = output_root or DEFAULT_CONSTANT_OUTPUT_ROOT
    elif initialization == "inverted":
        comparison_code = "TI"
        comparison_name = "Inverted Latent-Strength"
        comparison_initial_ratings = world.inverted_initial_ratings
        output_root = output_root or DEFAULT_INVERTED_OUTPUT_ROOT
    elif initialization == "custom":
        if not custom_code or not custom_code.isalnum():
            raise ValueError("custom_code must be a non-empty alphanumeric label")
        if not custom_name:
            raise ValueError("custom_name must not be empty")
        if custom_initial_ratings is None:
            raise ValueError("custom_initial_ratings are required")
        if len(custom_initial_ratings) != world.player_count:
            raise ValueError("custom initial rating count must match the population")
        if any(not math.isfinite(float(value)) for value in custom_initial_ratings):
            raise ValueError("custom initial ratings must be finite")
        if output_root is None:
            raise ValueError("custom initialization requires an output_root")
        comparison_code = custom_code.upper()
        comparison_name = custom_name
        comparison_initial_ratings = tuple(
            float(value) for value in custom_initial_ratings
        )
    else:
        raise ValueError("initialization must be 'constant', 'inverted', or 'custom'")

    started_at = datetime.now().astimezone()
    timer_started = time.perf_counter()
    role = "canonical" if (runs, events, seed) == (800, 500, 1) else "development"
    run_directory = make_run_directory(
        output_root,
        role=role,
        seed=seed,
        timestamp=started_at,
    )
    seed_rng = random.Random(seed)
    replicate_seeds = tuple(seed_rng.getrandbits(64) for _ in range(runs))
    replicate_events: list[PairedReplicateEvent] = []
    replicate_landmarks: list[ReplicateForgettingLandmark] = []
    t_prime_final_ratings: list[tuple[float, ...]] = []
    for replicate, replicate_seed in enumerate(replicate_seeds, 1):
        rows, landmarks, final_ratings = _replicate(
            world=world,
            events=events,
            replicate=replicate,
            seed=replicate_seed,
            persistence_events=persistence_events,
            comparison_code=comparison_code,
            comparison_initial_ratings=comparison_initial_ratings,
        )
        replicate_events.extend(rows)
        replicate_landmarks.extend(landmarks)
        t_prime_final_ratings.append(final_ratings)
        if progress_every and (replicate % progress_every == 0 or replicate == runs):
            print(
                f"Completed {comparison_code} paired replicate {replicate}/{runs}",
                flush=True,
            )

    event_summary = aggregate_event_rows(replicate_events)
    forgetting_summary = aggregate_landmarks(replicate_landmarks)
    player_errors, error_progress = build_final_mean_error_diagnostic(
        t_prime_final_ratings, world.latent_skills
    )

    def make_result(elapsed: float) -> ConstantStartEnsembleResult:
        return ConstantStartEnsembleResult(
            run_directory=run_directory,
            world=world,
            events=events,
            runs=runs,
            master_seed=seed,
            persistence_events=persistence_events,
            comparison_code=comparison_code,
            comparison_name=comparison_name,
            comparison_initial_ratings=tuple(comparison_initial_ratings),
            replicate_seeds=replicate_seeds,
            replicate_events=tuple(replicate_events),
            event_summary=event_summary,
            replicate_landmarks=tuple(replicate_landmarks),
            forgetting_summary=forgetting_summary,
            t_prime_final_player_mean_errors=player_errors,
            t_prime_final_mean_error_progress=error_progress,
            elapsed_seconds=elapsed,
        )

    result = make_result(time.perf_counter() - timer_started)
    _write_outputs(result, started_at=started_at, finished_at=datetime.now().astimezone())
    result = make_result(time.perf_counter() - timer_started)
    _write_outputs(
        result,
        started_at=started_at,
        finished_at=datetime.now().astimezone(),
        write_tables=False,
    )
    return result


def run_inverted_start_ensemble(
    *,
    world: ToyWorld = ToyWorld(),
    events: int = 500,
    runs: int = 800,
    seed: int = 1,
    persistence_events: int = 25,
    output_root: Path | None = None,
    progress_every: int = 50,
) -> ConstantStartEnsembleResult:
    return run_constant_start_ensemble(
        world=world,
        events=events,
        runs=runs,
        seed=seed,
        persistence_events=persistence_events,
        output_root=output_root,
        progress_every=progress_every,
        initialization="inverted",
    )


def build_parser(*, default_initialization: str = "constant") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run TC or TI alone and paired against the T0 reference."
    )
    parser.add_argument("--players", type=int, default=10)
    parser.add_argument("--latent-gap", type=float, default=40.0)
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--k", type=float, default=5.0)
    parser.add_argument("--events", type=int, default=500)
    parser.add_argument("--runs", type=int, default=800)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--persistence-events", type=int, default=25)
    parser.add_argument("--progress-every", type=int, default=50)
    parser.add_argument(
        "--initialization",
        choices=("constant", "inverted"),
        default=default_initialization,
    )
    parser.add_argument("--output-root", type=Path)
    return parser


def main(*, default_initialization: str = "constant") -> None:
    args = build_parser(default_initialization=default_initialization).parse_args()
    result = run_constant_start_ensemble(
        world=ToyWorld(
            player_count=args.players,
            latent_gap=args.latent_gap,
            q=args.q,
            k=args.k,
        ),
        events=args.events,
        runs=args.runs,
        seed=args.seed,
        persistence_events=args.persistence_events,
        output_root=args.output_root,
        progress_every=args.progress_every,
        initialization=args.initialization,
    )
    final = result.event_summary[-1]
    print(f"Wrote {result.comparison_code} ensemble to {result.run_directory.resolve()}")
    print(
        f"Final {result.comparison_code} state RMSE: {final.t_prime_state_mean:.6f}; "
        f"probability RMSE: {final.t_prime_probability_mean:.6f}"
    )
    print(
        f"Final paired state RMSE: {final.paired_state_mean:.6f}; "
        f"probability RMSE: {final.paired_probability_mean:.6f}"
    )
    print(f"Total run time: {result.elapsed_seconds:.3f} seconds")


if __name__ == "__main__":
    main()

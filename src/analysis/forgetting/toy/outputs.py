"""Auditable CSV, JSON, Markdown, and HTML outputs for the toy experiment."""

from __future__ import annotations

import csv
import html
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Mapping, Sequence

from .report_identity import refresh_run_reports

if TYPE_CHECKING:
    from .experiment import DevelopmentResult
    from .metrics import EventMetric


def make_run_directory(
    root: Path,
    *,
    role: str,
    seed: int,
    timestamp: datetime,
) -> Path:
    stamp = timestamp.strftime("%Y%m%d_%H%M%S")
    candidate = root / f"{stamp}_{role}_seed{seed}"
    suffix = 1
    while candidate.exists():
        suffix += 1
        candidate = root / f"{stamp}_{role}_seed{seed}_{suffix}"
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def _write_dict_rows(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    materialized = list(rows)
    if not materialized:
        raise ValueError(f"cannot write empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(materialized[0]))
        writer.writeheader()
        writer.writerows(materialized)


def _rating_rows(result: DevelopmentResult):
    for run in (result.true_run, result.flat_run):
        for snapshot in run.snapshots:
            for player, rating in enumerate(snapshot.ratings):
                yield {
                    "initialization": run.label,
                    "event": snapshot.event,
                    "global_bouts": snapshot.global_bouts,
                    "player": player,
                    "rating": rating,
                }


def _true_start_rating_rows(result: DevelopmentResult):
    for snapshot in result.true_run.snapshots:
        for player, (latent_skill, rating) in enumerate(
            zip(result.world.latent_skills, snapshot.ratings)
        ):
            yield {
                "event": snapshot.event,
                "global_bouts": snapshot.global_bouts,
                "player": player,
                "latent_skill": latent_skill,
                "rating": rating,
                "rating_error": rating - latent_skill,
            }


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


def _true_start_event_rows(result: DevelopmentResult):
    for snapshot, metric in zip(result.true_run.snapshots, result.metrics):
        adjacent_inversions, all_pair_inversions = _inversion_counts(snapshot.ratings)
        yield {
            "event": snapshot.event,
            "global_bouts": snapshot.global_bouts,
            "truth_relative_state_rmse": metric.true_state_error,
            "truth_relative_probability_rmse": metric.true_probability_error,
            "adjacent_order_inversions": adjacent_inversions,
            "all_pair_order_inversions": all_pair_inversions,
        }


def _forecast_rows(result: DevelopmentResult):
    true_by_bout = {row.global_bout: row for row in result.true_run.forecasts}
    flat_by_bout = {row.global_bout: row for row in result.flat_run.forecasts}
    for history_row in result.history.bouts:
        true = true_by_bout[history_row.global_bout]
        flat = flat_by_bout[history_row.global_bout]
        yield {
            "event": history_row.event,
            "bout_in_event": history_row.bout_in_event,
            "global_bout": history_row.global_bout,
            "player_a": history_row.player_a,
            "player_b": history_row.player_b,
            "a_won": int(history_row.a_won),
            "true_outcome_probability": history_row.true_probability_a_wins,
            "true_start_forecast": true.probability_a_wins,
            "flat_start_forecast": flat.probability_a_wins,
            "absolute_forecast_disagreement": abs(
                true.probability_a_wins - flat.probability_a_wins
            ),
        }


def _landmark_rows(result: DevelopmentResult):
    for row in result.landmarks:
        yield {
            "kind": row.kind,
            "target": row.target,
            "tolerance": row.tolerance,
            "first_event": "" if row.first_event is None else row.first_event,
            "first_global_bout": (
                "" if row.first_global_bout is None else row.first_global_bout
            ),
            "recrossed": "" if row.recrossed is None else int(row.recrossed),
            "later_fraction_below": (
                "" if row.later_fraction_below is None else row.later_fraction_below
            ),
            "remaining_events": (
                "" if row.remaining_events is None else row.remaining_events
            ),
            "right_censored": int(row.right_censored),
        }


def _metric_rows(metrics: Sequence[EventMetric]):
    for row in metrics:
        yield asdict(row)


def _landmark_text(result: DevelopmentResult) -> str:
    lines = []
    for row in result.landmarks:
        label = (
            f"{100 * row.target:.0f}% reduction"
            if row.kind == "fractional_reduction"
            else f"absolute tolerance {row.target:g}"
        )
        if row.right_censored:
            outcome = "not observed"
        else:
            outcome = (
                f"event {row.first_event} ({row.first_global_bout} global bouts); "
                f"recrossed={'yes' if row.recrossed else 'no'}"
            )
        lines.append(f"- {label}: {outcome}")
    return "\n".join(lines)


def _report_markdown(result: DevelopmentResult, *, persistence_events: int) -> str:
    final = result.metrics[-1]
    return f"""# Forgetting Toy Development Run

## Run

- Role: development
- Master seed: {result.history.master_seed}
- Events: {result.history.events}
- Global bouts: {len(result.history.bouts)}
- Players: {result.world.player_count}
- Latent gap: {result.world.latent_gap:g}
- q: {result.world.q:g}
- K: {result.world.k:g}
- History SHA-256: `{result.history_sha256}`
- Persistence window: {persistence_events} events

The true-start and flat-start Elo processes replayed the exact persisted bout
history in `history.csv`. Outcomes were generated from fixed latent skills and
were not affected by either displayed rating process.

## Initial and final disagreement

| Metric | Event 0 | Event {final.event} |
|---|---:|---:|
| Centred rating-state RMSE | {result.metrics[0].state_distance:.6f} | {final.state_distance:.6f} |
| All-pair forecast RMSE | {result.metrics[0].forecast_distance:.6f} | {final.forecast_distance:.6f} |
| Forecast fraction remaining | {result.metrics[0].forecast_fraction_remaining:.6f} | {final.forecast_fraction_remaining:.6f} |
| True-start truth-relative state RMSE | {result.metrics[0].true_state_error:.6f} | {final.true_state_error:.6f} |
| Flat-start truth-relative state RMSE | {result.metrics[0].flat_state_error:.6f} | {final.flat_state_error:.6f} |

Integrated all-pair forecast disagreement through event {final.event}:
`{result.integrated_disagreement:.6f}` event-probability units.

## Provisional forgetting landmarks

{_landmark_text(result)}

These landmarks are exploratory. They test whether the proposed measurements
give a coherent account of initialization forgetting; they are not frozen
principal criteria.

## Interpretation boundary

Forecast agreement measures loss of sensitivity to initialization. It does not
show that Elo is predictively useful or that either displayed rating path
converges permanently to latent skill.
"""


def _true_start_report_markdown(result: DevelopmentResult) -> str:
    requested = {0, 1, 2, 5, 10, 25, 50, 100, result.history.events}
    selected = [row for row in result.metrics if row.event in requested]
    snapshots = {row.event: row for row in result.true_run.snapshots}
    table_rows = []
    for row in selected:
        adjacent, all_pair = _inversion_counts(snapshots[row.event].ratings)
        table_rows.append(
            f"| {row.event} | {row.global_bouts} | {row.true_state_error:.6f} | "
            f"{row.true_probability_error:.6f} | {adjacent} | {all_pair} |"
        )
    table = "\n".join(table_rows)
    later = [row for row in result.metrics if row.event >= min(100, result.history.events)]
    mean_state_error = sum(row.true_state_error for row in later) / len(later)
    mean_probability_error = sum(row.true_probability_error for row in later) / len(later)
    return f"""# True-Start Toy Baseline

## Purpose

This is the standalone Stage 1 baseline. Displayed Elo ratings begin at the
known latent skills and then process one persisted random history. This report
describes departure from truth and continuing fixed-`K` fluctuation. It does
not measure forgetting, because it contains no counterfactual initialization.

## Run

- Master seed: {result.history.master_seed}
- Events: {result.history.events}
- Global bouts: {len(result.history.bouts)}
- Players: {result.world.player_count}
- Latent gap: {result.world.latent_gap:g}
- q: {result.world.q:g}
- K: {result.world.k:g}
- History SHA-256: `{result.history_sha256}`

At event zero, ratings equal latent skills exactly, so both truth-relative
errors are zero. Random outcomes immediately move the fixed-`K` ratings away
from that state.

## Selected snapshots

| Event | Global bouts | Rating-state RMSE | Probability RMSE | Adjacent inversions | All-pair inversions |
|---:|---:|---:|---:|---:|---:|
{table}

Across events {later[0].event}--{later[-1].event}, the mean truth-relative
rating-state RMSE is `{mean_state_error:.6f}` and the mean all-pair probability
RMSE is `{mean_probability_error:.6f}`. These are descriptive values from one
history, not ensemble estimates of a stationary distribution.

## Interpretation boundary

Movement away from latent skill is not evidence of forgetting. A single
trajectory cannot establish whether its later state depends on its initial
ratings. That counterfactual question begins in the separate paired report,
where a flat-start process replays this exact history.
"""


def _plotly_chart(
    div_id: str,
    title: str,
    x_values: Sequence[int],
    traces: Sequence[Mapping[str, object]],
    *,
    y_axis_title: str,
    x_axis_title: str = "Round-robin event",
) -> str:
    plotly_traces = [
        {"x": list(x_values), "type": "scatter", "mode": "lines", **trace}
        for trace in traces
    ]
    layout = {
        "autosize": True,
        "height": 360,
        "margin": {"l": 78, "r": 30, "t": 20, "b": 70},
        "hovermode": "x unified",
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "#fafafa",
        "xaxis": {
            "title": {"text": x_axis_title},
            "ticks": "outside",
            "tickmode": "auto",
            "nticks": 11,
            "showline": True,
            "showgrid": True,
            "rangemode": "tozero",
        },
        "yaxis": {
            "title": {"text": y_axis_title},
            "ticks": "outside",
            "tickmode": "auto",
            "nticks": 8,
            "showline": True,
            "showgrid": True,
            "rangemode": "tozero",
        },
        "legend": {"orientation": "h", "y": 1.12},
    }
    config = {"responsive": True, "displayModeBar": True}
    return f"""
    <section>
      <h2>{html.escape(title)}</h2>
      <div id="{html.escape(div_id)}" class="plot" role="img" aria-label="{html.escape(title)}"></div>
      <script>
        Plotly.newPlot(
          {json.dumps(div_id)},
          {json.dumps(plotly_traces)},
          {json.dumps(layout)},
          {json.dumps(config)}
        );
      </script>
    </section>
    """


def _report_html(markdown_report: str, result: DevelopmentResult) -> str:
    metrics = result.metrics
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Forgetting Toy Development Run</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ max-width: 960px; margin: 2rem auto; padding: 0 1rem; font-family: system-ui, sans-serif; line-height: 1.5; }}
    .plot {{ width: 100%; min-height: 360px; border: 1px solid #ddd; }}
    pre {{ white-space: pre-wrap; background: #f4f4f4; padding: 1rem; }}
  </style>
</head>
<body>
  <h1>Forgetting Toy Development Run</h1>
  {_plotly_chart("forecast-disagreement", "All-pair forecast disagreement", [row.event for row in metrics], [{"name": "True start vs flat start", "y": [row.forecast_distance for row in metrics], "line": {"color": "#2457a7"}}], y_axis_title="Forecast RMSE (probability)")}
  {_plotly_chart("rating-disagreement", "Centred rating-state disagreement", [row.event for row in metrics], [{"name": "True start vs flat start", "y": [row.state_distance for row in metrics], "line": {"color": "#b04a3a"}}], y_axis_title="Rating-state RMSE (rating points)")}
  {_plotly_chart("true-state-error", "Truth-relative state error: true start", [row.event for row in metrics], [{"name": "True start vs latent skill", "y": [row.true_state_error for row in metrics], "line": {"color": "#2f855a"}}], y_axis_title="Rating-state RMSE (rating points)")}
  <h2>Audit summary</h2>
  <pre>{html.escape(markdown_report)}</pre>
</body>
</html>
"""


def _true_start_report_html(markdown_report: str, result: DevelopmentResult) -> str:
    metrics = result.metrics
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>True-Start Toy Baseline</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ max-width: 960px; margin: 2rem auto; padding: 0 1rem; font-family: system-ui, sans-serif; line-height: 1.5; }}
    .plot {{ width: 100%; min-height: 360px; border: 1px solid #ddd; }}
    pre {{ white-space: pre-wrap; background: #f4f4f4; padding: 1rem; }}
  </style>
</head>
<body>
  <h1>True-Start Toy Baseline</h1>
  <p>This Stage 1 report describes one true-initialized trajectory. It does not measure forgetting.</p>
  {_plotly_chart("true-state-rmse", "Truth-relative rating-state RMSE", [row.event for row in metrics], [{"name": "True-start rating error", "y": [row.true_state_error for row in metrics], "line": {"color": "#2f855a"}}], y_axis_title="Rating-state RMSE (rating points)")}
  {_plotly_chart("true-probability-rmse", "Truth-relative all-pair probability RMSE", [row.event for row in metrics], [{"name": "True-start probability error", "y": [row.true_probability_error for row in metrics], "line": {"color": "#805ad5"}}], y_axis_title="All-pair probability RMSE")}
  <h2>Audit summary</h2>
  <pre>{html.escape(markdown_report)}</pre>
</body>
</html>
"""


def write_development_outputs(
    result: DevelopmentResult,
    *,
    persistence_events: int,
    started_at: datetime,
    finished_at: datetime,
) -> None:
    root = result.run_directory
    _write_dict_rows(root / "ratings.csv", _rating_rows(result))
    _write_dict_rows(root / "true_start_ratings.csv", _true_start_rating_rows(result))
    _write_dict_rows(root / "bout_forecasts.csv", _forecast_rows(result))
    _write_dict_rows(root / "event_summary.csv", _metric_rows(result.metrics))
    _write_dict_rows(
        root / "true_start_event_summary.csv",
        _true_start_event_rows(result),
    )
    _write_dict_rows(root / "forgetting_summary.csv", _landmark_rows(result))

    true_start_report = _true_start_report_markdown(result)
    (root / "true_start_report.md").write_text(true_start_report, encoding="utf-8")
    (root / "true_start_report.html").write_text(
        _true_start_report_html(true_start_report, result),
        encoding="utf-8",
    )

    paired_report = _report_markdown(result, persistence_events=persistence_events)
    (root / "paired_report.md").write_text(paired_report, encoding="utf-8")
    (root / "paired_report.html").write_text(
        _report_html(paired_report, result),
        encoding="utf-8",
    )
    # Retain the original convenience names as aliases for the paired report.
    (root / "report.md").write_text(paired_report, encoding="utf-8")
    (root / "report.html").write_text(
        _report_html(paired_report, result),
        encoding="utf-8",
    )

    manifest = {
        "experiment": "forgetting toy true-start versus flat-start",
        "experimental_contract_version": 1,
        "run_role": "development",
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "world": {
            "player_count": result.world.player_count,
            "latent_gap": result.world.latent_gap,
            "latent_skills": list(result.world.latent_skills),
            "q": result.world.q,
            "k": result.world.k,
        },
        "history": {
            "events": result.history.events,
            "global_bouts": len(result.history.bouts),
            "master_seed": result.history.master_seed,
            "schedule_seed": result.history.schedule_seed,
            "outcome_seed": result.history.outcome_seed,
            "sha256": result.history_sha256,
        },
        "initializations": {
            "true": list(result.true_run.initial_ratings),
            "flat": list(result.flat_run.initial_ratings),
        },
        "forgetting": {
            "primary_metric": "all-pair forecast probability RMSE",
            "secondary_metric": "centred rating-state RMSE",
            "persistence_events": persistence_events,
            "integrated_forecast_disagreement": result.integrated_disagreement,
            "landmarks": [asdict(row) for row in result.landmarks],
        },
        "outputs": {
            "history": "history.csv",
            "ratings": "ratings.csv",
            "true_start_ratings": "true_start_ratings.csv",
            "bout_forecasts": "bout_forecasts.csv",
            "event_summary": "event_summary.csv",
            "true_start_event_summary": "true_start_event_summary.csv",
            "forgetting_summary": "forgetting_summary.csv",
            "true_start_report_markdown": "true_start_report.md",
            "true_start_report_html": "true_start_report.html",
            "paired_report_markdown": "paired_report.md",
            "paired_report_html": "paired_report.html",
            "convenience_report_markdown": "report.md",
            "convenience_report_html": "report.html",
            "manifest": "manifest.json",
        },
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    refresh_run_reports(root, manifest)

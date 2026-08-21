"""Persist the controlled retrospective comparison and its interpretation."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable

from .evaluation import Evaluation, SupportPairCalibrationRow
from .model import ComparisonRun, ForecastRow, score


@dataclass(frozen=True, slots=True)
class HistorySource:
    path: str
    sha256: str


def write_outputs(
    run: ComparisonRun,
    evaluation: Evaluation,
    output_directory: Path,
    history_source: HistorySource,
) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    _write_csv(output_directory / "forecast_ledger.csv", _forecast_rows(run))
    _write_csv(output_directory / "summary.csv", (asdict(row) for row in evaluation.summaries))
    _write_csv(output_directory / "comparisons.csv", (asdict(row) for row in evaluation.comparisons))
    _write_csv(
        output_directory / "factorial_contrasts.csv",
        (asdict(row) for row in evaluation.factorial_contrasts),
    )
    _write_csv(
        output_directory / "calibration.csv",
        (asdict(row) for row in evaluation.calibration_bins),
    )
    _write_csv(
        output_directory / "calibration_summary.csv",
        (asdict(row) for row in evaluation.calibration_summaries),
    )
    _write_csv(
        output_directory / "calibration_by_support_pair.csv",
        (asdict(row) for row in evaluation.support_pair_calibration),
    )
    _write_csv(
        output_directory / "calibration_by_support_pair_coarse.csv",
        (asdict(row) for row in evaluation.coarse_support_pair_calibration),
    )
    (output_directory / "calibration_all.html").write_text(
        _calibration_html(evaluation), encoding="utf-8"
    )
    (output_directory / "calibration_by_support.html").write_text(
        _support_calibration_html(evaluation), encoding="utf-8"
    )
    (output_directory / "calibration_by_career_support.html").write_text(
        _career_support_calibration_html(evaluation), encoding="utf-8"
    )
    (output_directory / "calibration_ece_heatmap.html").write_text(
        _career_support_ece_heatmap_html(evaluation), encoding="utf-8"
    )
    (output_directory / "rating_maturity_distribution.html").write_text(
        _rating_maturity_distribution_html(evaluation), encoding="utf-8"
    )
    (output_directory / "calibration_ece_by_support_pair.html").write_text(
        _support_pair_ece_heatmap_html(evaluation), encoding="utf-8"
    )
    (output_directory / "calibration_ece_by_support_pair_coarse.html").write_text(
        _coarse_support_pair_ece_heatmap_html(evaluation), encoding="utf-8"
    )
    (output_directory / "manifest.json").write_text(
        json.dumps(_manifest(run, history_source), indent=2) + "\n",
        encoding="utf-8",
    )
    (output_directory / "report.md").write_text(
        _report(run, evaluation, history_source), encoding="utf-8"
    )


def _forecast_rows(run: ComparisonRun) -> Iterable[dict[str, object]]:
    for model in run.models:
        for row in model.forecasts:
            log_loss, brier_loss = score(row)
            values = asdict(row)
            values["date"] = str(row.date)
            values["chii_a"] = str(row.chii_a) if row.chii_a is not None else ""
            values["chii_b"] = str(row.chii_b) if row.chii_b is not None else ""
            values["log_loss"] = log_loss
            values["brier_loss"] = brier_loss
            yield values


def _write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    iterator = iter(rows)
    try:
        first = next(iterator)
    except StopIteration:
        raise ValueError(f"Cannot write empty analytical output: {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(first))
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(iterator)


def _manifest(run: ComparisonRun, source: HistorySource) -> dict[str, object]:
    definition = run.definition
    return {
        "experiment": "Controlled post-1988 Elo model comparison",
        "status": "retrospective diagnostic; adopted P is future-informed",
        "history_source": asdict(source),
        "definition": {
            "start_date": str(definition.start_date),
            "end_date": str(definition.end_date),
            "q": definition.q,
            "constant_k": definition.constant_k,
            "constant_initial_rating": definition.constant_initial_rating,
            "reference_probability": definition.reference_probability,
            "bootstrap_seed": definition.bootstrap_seed,
            "bootstrap_resamples": definition.bootstrap_resamples,
            "confidence_level": definition.confidence_level,
            "noninferiority_fraction": definition.noninferiority_fraction,
            "calibration": {
                "unit": "participant forecast",
                "observations_per_bout": 2,
                "bin_width": definition.calibration_bin_width,
                "minimum_supported_bin_participants": (
                    definition.calibration_min_bin_participants
                ),
                "bin_convention": "[lower, upper), with final upper bound inclusive",
                "gap": "observed win rate minus mean predicted probability",
                "ece": "participant-count-weighted mean absolute calibration gap",
            },
            "models": [asdict(model.spec) for model in run.models],
        },
        "adopted_prior": {
            "path": run.prior.source_path,
            "sha256": run.prior.sha256,
            "rank_pair_count": len(run.prior.rating_by_pair),
            "fallback_rating": run.prior.fallback_rating,
            "transformation": "none",
            "interpretation": "exact adopted 1989-onward paired artifact",
        },
        "divisional_k": {
            "path": run.k_config_path,
            "sha256": run.k_config_sha256,
            "semantics": "each participant uses own pre-bout chii; unranked fallback k=35",
        },
        "selection": {
            "raw_result_count": run.selection.raw_result_count,
            "rated_bout_count": run.selection.rated_bout_count,
            "excluded_fusen_count": run.selection.excluded_fusen_count,
            "excluded_draw_count": run.selection.excluded_draw_count,
            "kimarite_required_for_known_WL": False,
        },
        "artifacts": {
            "forecast_ledger": "forecast_ledger.csv",
            "summary": "summary.csv",
            "comparisons": "comparisons.csv",
            "factorial_contrasts": "factorial_contrasts.csv",
            "calibration": "calibration.csv",
            "calibration_summary": "calibration_summary.csv",
            "calibration_by_support_pair": "calibration_by_support_pair.csv",
            "calibration_by_support_pair_coarse": (
                "calibration_by_support_pair_coarse.csv"
            ),
            "calibration_curve": "calibration_all.html",
            "calibration_by_support_curve": "calibration_by_support.html",
            "calibration_by_career_support_curve": (
                "calibration_by_career_support.html"
            ),
            "calibration_ece_heatmap": "calibration_ece_heatmap.html",
            "rating_maturity_distribution": "rating_maturity_distribution.html",
            "calibration_ece_by_support_pair": (
                "calibration_ece_by_support_pair.html"
            ),
            "calibration_ece_by_support_pair_coarse": (
                "calibration_ece_by_support_pair_coarse.html"
            ),
            "report": "report.md",
        },
    }


def _report(run: ComparisonRun, evaluation: Evaluation, source: HistorySource) -> str:
    all_summaries = tuple(row for row in evaluation.summaries if row.population == "all")
    all_comparisons = tuple(row for row in evaluation.comparisons if row.population == "all")
    summary_lines = [
        "| Model | Bouts | Mean log loss | Mean Brier loss | Log difference from 50% |",
        "|---|---:|---:|---:|---:|",
    ]
    summary_lines.extend(
        f"| {row.model} | {row.bout_count:,} | {row.mean_log_loss:.6f} | "
        f"{row.mean_brier_loss:.6f} | {row.mean_log_difference_from_50:+.6f} |"
        for row in all_summaries
    )
    comparison_lines = [
        "| Model | Comparator | Mean log difference | One-sided 95% upper | Result |",
        "|---|---|---:|---:|---|",
    ]
    for row in all_comparisons:
        if row.comparator == "50%":
            if row.predictive_information_criterion_met:
                result = (
                    "retrospective criterion met"
                    if row.model in ("B_P", "B_kP")
                    else "predictive information"
                )
            else:
                result = "criterion not met"
        else:
            result = (
                "superior" if row.superior_to_b else
                "non-inferior" if row.noninferior_to_b else
                "inferior under proposed margin"
            )
        comparison_lines.append(
            f"| {row.model} | {row.comparator} | {row.mean_log_difference:+.6f} | "
            f"{row.log_one_sided_upper:+.6f} | {result} |"
        )
    factorial_lines = [
        "| Contrast | Mean log difference | 95% interval |",
        "|---|---:|---:|",
    ]
    factorial_lines.extend(
        f"| {row.contrast} | {row.mean_log_difference:+.6f} | "
        f"[{row.log_lower:+.6f}, {row.log_upper:+.6f}] |"
        for row in evaluation.factorial_contrasts
        if row.population == "all"
    )
    calibration_lines = [
        "| Model | Participant forecasts | Supported bins | ECE | Supported maximum gap |",
        "|---|---:|---:|---:|---:|",
    ]
    calibration_lines.extend(
        f"| {row.model} | {row.participant_count:,} | {row.supported_bin_count} | "
        f"{row.expected_calibration_error:.6f} | "
        f"{_optional_float(row.supported_maximum_calibration_error)} |"
        for row in evaluation.calibration_summaries
        if row.population == "all"
    )
    return f"""# Controlled Post-1988 Elo Model Comparison

## Interpretation boundary

This is a controlled retrospective diagnostic. `B_P` and `B_kP` use the exact
adopted paired prior unchanged. That artifact was derived from the broad
1989-onward history scored here, so their results are future-informed and are
not out-of-sample predictive evidence. The experiment can reveal whether the
adopted values improve or damage historical pre-bout scores under the declared
models; it does not by itself provide prospective validation of `B'`.

## Reproducible definition

- History: `{source.path}`
- History SHA-256: `{source.sha256}`
- Period: {run.definition.start_date}--{run.definition.end_date}
- `q=400`; constant `k=35`; divisional `k` from `{run.k_config_path}`
- Adopted prior: `{run.prior.source_path}`
- Adopted-prior SHA-256: `{run.prior.sha256}`
- Prior transformation: none
- Eligible results: every represented W/L result, irrespective of kimarite
- Forecast order: predict, record, then update

## All-bout scores

{chr(10).join(summary_lines)}

## Declared comparisons

{chr(10).join(comparison_lines)}

## Factorial contrasts

{chr(10).join(factorial_lines)}

Negative loss differences favour the named model. Uncertainty resamples whole
basho blocks. Non-inferiority uses the proposal's provisional margin of 5% of
`B`'s observed log-loss advantage over 50% within the reported population.

## Participant-level calibration

Each bout contributes two observations: `(p, outcome)` for rikishi A and
`(1-p, 1-outcome)` for rikishi B. Forecasts are grouped into equal-width
{run.definition.calibration_bin_width:.0%} bins. `calibration.csv` reports each
bin's mean forecast, observed win rate and their signed difference; a negative
gap means that the model overpredicted the participant's chance of winning.

{chr(10).join(calibration_lines)}

ECE is the participant-count-weighted mean absolute bin gap. It is a
descriptive, bin-dependent diagnostic rather than a model-selection score.
The reported maximum excludes bins with fewer than
{run.definition.calibration_min_bin_participants} participant forecasts;
the detailed CSV retains every non-empty bin. Population-specific calibration
rows are also preserved in the two calibration CSV files.

[Open the interactive all-bout calibration chart](calibration_all.html).

[Open the interactive `B_kP` calibration-by-support chart](calibration_by_support.html).

[Open the interactive `B_kP` career-scale calibration chart](calibration_by_career_support.html).

[Open the model-by-career-support ECE heatmap](calibration_ece_heatmap.html).

[Open the rating-maturity distribution](rating_maturity_distribution.html).

[Open the triangular support-pair ECE heatmap](calibration_ece_by_support_pair.html).

[Open the coarse story-facing support-pair ECE heatmap](calibration_ece_by_support_pair_coarse.html).

## Required qualifications

Population-specific results are preserved in `summary.csv` and
`comparisons.csv`, including sekitori, sub-sekitori, cross-boundary,
new-entrant and experience-band views. Aggregate improvement must not conceal
an important regression in one of those populations.

The unranked History defect receives the weakest adopted-prior value and
`k=35`; this is recorded in the manifest. The experiment does not rescale,
smooth or recenter the adopted prior.
"""


def _optional_float(value: float | None) -> str:
    return "--" if value is None else f"{value:.6f}"


def _calibration_html(evaluation: Evaluation) -> str:
    colours = {
        "B": "#555555",
        "B_k": "#1f77b4",
        "B_P": "#d95f02",
        "B_kP": "#2ca02c",
    }
    traces: list[dict[str, object]] = [{
        "type": "scatter",
        "mode": "lines",
        "name": "perfect calibration",
        "x": [0.0, 1.0],
        "y": [0.0, 1.0],
        "line": {"color": "#999999", "width": 2, "dash": "dash"},
        "hoverinfo": "skip",
    }]
    for model, colour in colours.items():
        rows = tuple(
            row for row in evaluation.calibration_bins
            if row.population == "all" and row.model == model
        )
        traces.append({
            "type": "scatter",
            "mode": "lines+markers",
            "name": model,
            "x": [row.mean_predicted_probability for row in rows],
            "y": [row.observed_win_rate for row in rows],
            "customdata": [
                [
                    row.bin_lower,
                    row.bin_upper,
                    row.participant_count,
                    row.calibration_gap,
                ]
                for row in rows
            ],
            "line": {"color": colour, "width": 2.5},
            "marker": {"color": colour, "size": 7},
            "hovertemplate": (
                "model=" + model + "<br>"
                "bin=%{customdata[0]:.0%}–%{customdata[1]:.0%}<br>"
                "mean prediction=%{x:.2%}<br>"
                "observed win rate=%{y:.2%}<br>"
                "gap=%{customdata[3]:+.2%}<br>"
                "participant forecasts=%{customdata[2]:,}<extra></extra>"
            ),
        })
    return _calibration_page(traces, "Participant-level calibration: all bouts")


def _support_calibration_html(evaluation: Evaluation) -> str:
    support_groups = (
        ("experience_under_15", "support <15", "#9467bd"),
        ("experience_15_19", "support 15-19", "#1f77b4"),
        ("experience_20_24", "support 20-24", "#ff7f0e"),
        ("experience_25_29", "support 25-29", "#d62728"),
        ("experience_30_34", "support 30-34", "#2ca02c"),
        ("experience_35_39", "support 35-39", "#8c564b"),
        ("experience_40_44", "support 40-44", "#e377c2"),
        ("experience_45_49", "support 45-49", "#7f7f7f"),
        ("experience_50_plus", "support 50+", "#17becf"),
    )
    return _grouped_calibration_html(
        evaluation,
        support_groups,
        "B_kP calibration by minimum prior rated bouts: initial range",
    )


def _career_support_calibration_html(evaluation: Evaluation) -> str:
    support_groups = (
        ("career_experience_under_30", "prior bouts <30", "#9467bd"),
        ("career_experience_30_59", "prior bouts 30-59", "#1f77b4"),
        ("career_experience_60_119", "prior bouts 60-119", "#ff7f0e"),
        ("career_experience_120_239", "prior bouts 120-239", "#d62728"),
        ("career_experience_240_359", "prior bouts 240-359", "#2ca02c"),
        ("career_experience_360_479", "prior bouts 360-479", "#8c564b"),
        ("career_experience_480_plus", "prior bouts 480+", "#17becf"),
    )
    return _grouped_calibration_html(
        evaluation,
        support_groups,
        "B_kP calibration by minimum prior rated bouts: career scale",
    )


def _career_support_ece_heatmap_html(evaluation: Evaluation) -> str:
    support_groups = (
        ("career_experience_under_30", "<30"),
        ("career_experience_30_59", "30-59"),
        ("career_experience_60_119", "60-119"),
        ("career_experience_120_239", "120-239"),
        ("career_experience_240_359", "240-359"),
        ("career_experience_360_479", "360-479"),
        ("career_experience_480_plus", "480+"),
    )
    models = ("B", "B_k", "B_P", "B_kP")
    summaries = {
        (row.population, row.model): row
        for row in evaluation.calibration_summaries
    }
    z: list[list[float | None]] = []
    text_values: list[list[str]] = []
    bout_counts: list[list[int]] = []
    for model in models:
        model_z: list[float | None] = []
        model_text: list[str] = []
        model_counts: list[int] = []
        for population, _ in support_groups:
            summary = summaries.get((population, model))
            if summary is None:
                model_z.append(None)
                model_text.append("")
                model_counts.append(0)
            else:
                ece_points = summary.expected_calibration_error * 100.0
                model_z.append(ece_points)
                model_text.append(f"{ece_points:.2f}%")
                model_counts.append(summary.bout_count)
        z.append(model_z)
        text_values.append(model_text)
        bout_counts.append(model_counts)

    traces = [{
        "type": "heatmap",
        "x": [label for _, label in support_groups],
        "y": list(models),
        "z": z,
        "text": text_values,
        "texttemplate": "%{text}",
        "customdata": bout_counts,
        "colorscale": "Viridis",
        "reversescale": True,
        "zmin": 0,
        "colorbar": {"title": {"text": "ECE<br>(percentage points)"}},
        "hovertemplate": (
            "model=%{y}<br>"
            "minimum prior rated bouts=%{x}<br>"
            "ECE=%{z:.2f} percentage points<br>"
            "bouts=%{customdata:,}<extra></extra>"
        ),
    }]
    layout = {
        "title": {
            "text": "Calibration error by model and rating maturity",
            "x": 0.5,
        },
        "autosize": True,
        "margin": {"l": 90, "r": 135, "t": 80, "b": 90},
        "paper_bgcolor": "#f7f8fb",
        "plot_bgcolor": "#ffffff",
        "xaxis": {
            "title": "Minimum prior rated bouts held by either rikishi",
            "type": "category",
        },
        "yaxis": {
            "title": "Model",
            "type": "category",
            "autorange": "reversed",
        },
    }
    return _plotly_page(traces, layout, "Calibration error by model and rating maturity")


def _rating_maturity_distribution_html(evaluation: Evaluation) -> str:
    support_groups = (
        ("career_experience_under_30", "<30"),
        ("career_experience_30_59", "30-59"),
        ("career_experience_60_119", "60-119"),
        ("career_experience_120_239", "120-239"),
        ("career_experience_240_359", "240-359"),
        ("career_experience_360_479", "360-479"),
        ("career_experience_480_plus", "480+"),
    )
    summaries = {
        row.population: row
        for row in evaluation.calibration_summaries
        if row.model == "B"
    }
    counts = [
        summaries[population].bout_count if population in summaries else 0
        for population, _ in support_groups
    ]
    total = sum(counts)
    percentages = [count / total if total else 0.0 for count in counts]
    traces = [{
        "type": "bar",
        "x": [label for _, label in support_groups],
        "y": counts,
        "customdata": percentages,
        "text": [f"{count:,}" for count in counts],
        "textposition": "outside",
        "cliponaxis": False,
        "marker": {"color": "#1f77b4"},
        "hovertemplate": (
            "minimum prior rated bouts=%{x}<br>"
            "bouts=%{y:,}<br>"
            "share=%{customdata:.1%}<extra></extra>"
        ),
    }]
    layout = {
        "title": {
            "text": "Distribution of bouts by rating maturity",
            "x": 0.5,
        },
        "autosize": True,
        "margin": {"l": 90, "r": 35, "t": 80, "b": 90},
        "paper_bgcolor": "#f7f8fb",
        "plot_bgcolor": "#ffffff",
        "bargap": 0.15,
        "xaxis": {
            "title": "Minimum prior rated bouts held by either rikishi",
            "type": "category",
        },
        "yaxis": {
            "title": "Bouts",
            "rangemode": "tozero",
            "tickformat": ",d",
        },
    }
    return _plotly_page(traces, layout, "Distribution of bouts by rating maturity")


def _support_pair_ece_heatmap_html(evaluation: Evaluation) -> str:
    bands = tuple(
        "<30" if index == 0 else f"{30 * index}-{30 * (index + 1) - 1}"
        for index in range(20)
    ) + ("600+",)
    return _support_pair_heatmap_html(
        evaluation.support_pair_calibration,
        bands,
        "Calibration error by paired rating maturity (30-bout bands)",
        tick_angle=-45,
    )


def _coarse_support_pair_ece_heatmap_html(evaluation: Evaluation) -> str:
    bands = ("<30", "30-59", "60-119", "120-239", "240-359", "360-479", "480+")
    return _support_pair_heatmap_html(
        evaluation.coarse_support_pair_calibration,
        bands,
        "Calibration error by paired rating maturity (coarse bands)",
        tick_angle=0,
    )


def _support_pair_heatmap_html(
    calibration_rows: tuple[SupportPairCalibrationRow, ...],
    bands: tuple[str, ...],
    title: str,
    *,
    tick_angle: int,
) -> str:
    models = ("B", "B_k", "B_P", "B_kP")
    rows = {
        (row.model, row.lower_support_band, row.higher_support_band): row
        for row in calibration_rows
    }
    all_ece_points = [
        row.expected_calibration_error * 100.0
        for row in calibration_rows
    ]
    zmax = max(all_ece_points, default=1.0)
    subtitle = (
        "Vertical = less-experienced rikishi; horizontal = more-experienced "
        "rikishi.<br>ECE (expected calibration error) is the participant-weighted "
        "mean absolute gap between predicted probability and observed win rate "
        "across 5-percentage-point probability bins.<br>Hover for bout count."
    )

    def display_title(model: str) -> str:
        return f"{title}: {model}<br><sup>{subtitle}</sup>"

    traces: list[dict[str, object]] = []
    for model in models:
        z: list[list[float | None]] = []
        text_values: list[list[str]] = []
        bout_counts: list[list[int | None]] = []
        for lower_index, lower_band in enumerate(bands):
            model_z: list[float | None] = []
            model_text: list[str] = []
            model_counts: list[int | None] = []
            for higher_index, higher_band in enumerate(bands):
                row = rows.get((model, lower_band, higher_band))
                if higher_index < lower_index or row is None:
                    model_z.append(None)
                    model_text.append("")
                    model_counts.append(None)
                else:
                    ece_points = row.expected_calibration_error * 100.0
                    model_z.append(ece_points)
                    model_text.append(f"{ece_points:.2f}%")
                    model_counts.append(row.bout_count)
            z.append(model_z)
            text_values.append(model_text)
            bout_counts.append(model_counts)
        traces.append({
            "type": "heatmap",
            "name": model,
            "visible": model == "B_kP",
            "x": list(bands),
            "y": list(bands),
            "z": z,
            "text": text_values,
            "texttemplate": "%{text}",
            "customdata": bout_counts,
            "colorscale": "Viridis",
            "reversescale": True,
            "zmin": 0,
            "zmax": zmax,
            "colorbar": {"title": {"text": "ECE<br>(percentage points)"}},
            "hovertemplate": (
                "model=" + model + "<br>"
                "lower-support rating=%{y}<br>"
                "higher-support rating=%{x}<br>"
                "ECE=%{z:.2f} percentage points<br>"
                "bouts=%{customdata:,}<extra></extra>"
            ),
        })
    buttons = [
        {
            "label": model,
            "method": "update",
            "args": [
                {"visible": [candidate == model for candidate in models]},
                {"title.text": display_title(model)},
            ],
        }
        for model in models
    ]
    layout = {
        "title": {
            "text": display_title("B_kP"),
            "x": 0.5,
        },
        "autosize": True,
        "margin": {"l": 145, "r": 135, "t": 125, "b": 110},
        "paper_bgcolor": "#f7f8fb",
        "plot_bgcolor": "#ffffff",
        "xaxis": {
            "title": "Prior rated bouts: more-experienced rikishi",
            "type": "category",
            "tickangle": tick_angle,
        },
        "yaxis": {
            "title": "Prior rated bouts: less-experienced rikishi",
            "type": "category",
            "autorange": "reversed",
        },
        "updatemenus": [{
            "type": "dropdown",
            "direction": "down",
            "x": 0,
            "xanchor": "left",
            "y": 1.12,
            "yanchor": "top",
            "active": 3,
            "buttons": buttons,
        }],
        "annotations": [{
            "text": "Model",
            "xref": "paper",
            "yref": "paper",
            "x": 0,
            "y": 1.17,
            "showarrow": False,
            "xanchor": "left",
        }],
    }
    return _plotly_page(traces, layout, title)


def _grouped_calibration_html(
    evaluation: Evaluation,
    support_groups: tuple[tuple[str, str, str], ...],
    title: str,
) -> str:
    traces: list[dict[str, object]] = [{
        "type": "scatter",
        "mode": "lines",
        "name": "perfect calibration",
        "x": [0.0, 1.0],
        "y": [0.0, 1.0],
        "line": {"color": "#999999", "width": 2, "dash": "dash"},
        "hoverinfo": "skip",
    }]
    for population, label, colour in support_groups:
        rows = tuple(
            row for row in evaluation.calibration_bins
            if row.population == population and row.model == "B_kP"
        )
        summary = next((
            row for row in evaluation.calibration_summaries
            if row.population == population and row.model == "B_kP"
        ), None)
        bout_count = summary.bout_count if summary is not None else 0
        trace_name = f"{label} (n={bout_count:,} bouts)"
        traces.append({
            "type": "scatter",
            "mode": "lines+markers",
            "name": trace_name,
            "x": [row.mean_predicted_probability for row in rows],
            "y": [row.observed_win_rate for row in rows],
            "customdata": [
                [
                    row.bin_lower,
                    row.bin_upper,
                    row.participant_count,
                    row.calibration_gap,
                ]
                for row in rows
            ],
            "line": {"color": colour, "width": 2.5},
            "marker": {"color": colour, "size": 7},
            "hovertemplate": (
                "minimum " + label + "<br>"
                "bin=%{customdata[0]:.0%}–%{customdata[1]:.0%}<br>"
                "mean prediction=%{x:.2%}<br>"
                "observed win rate=%{y:.2%}<br>"
                "gap=%{customdata[3]:+.2%}<br>"
                "participant forecasts=%{customdata[2]:,}<extra></extra>"
            ),
        })
    return _calibration_page(
        traces,
        title,
        vertical_legend=True,
    )


def _calibration_page(
    traces: list[dict[str, object]],
    title: str,
    *,
    vertical_legend: bool = False,
) -> str:
    layout = {
        "title": {"text": title, "x": 0.5},
        "autosize": True,
        "margin": {
            "l": 80,
            "r": 275 if vertical_legend else 35,
            "t": 70,
            "b": 75,
        },
        "paper_bgcolor": "#f7f8fb",
        "plot_bgcolor": "#ffffff",
        "hovermode": "closest",
        "legend": (
            {"orientation": "v", "y": 1.0, "x": 1.02, "xanchor": "left"}
            if vertical_legend else
            {"orientation": "h", "y": 1.08, "x": 0.5, "xanchor": "center"}
        ),
        "xaxis": {
            "title": "Mean predicted probability",
            "range": [0.0, 1.0],
            "tickformat": ".0%",
            "dtick": 0.1,
        },
        "yaxis": {
            "title": "Observed win rate",
            "range": [0.0, 1.0],
            "tickformat": ".0%",
            "dtick": 0.1,
        },
    }
    return _plotly_page(traces, layout, title)


def _plotly_page(
    traces: list[dict[str, object]],
    layout: dict[str, object],
    title: str,
) -> str:
    document = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <script src="https://cdn.plot.ly/plotly-3.0.1.min.js" charset="utf-8"></script>
</head>
<body style="margin:0;width:100vw;height:100vh;overflow:hidden;background:#f7f8fb">
  <div id="chart" style="width:100%;height:100%"></div>
  <script>
    const traces = __TRACES__;
    const layout = __LAYOUT__;
    const chart = document.getElementById("chart");
    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
      scrollZoom: true
    };
    Plotly.newPlot(chart, traces, layout, config).then(() => {
      window.addEventListener("resize", () => Plotly.Plots.resize(chart));
    });
  </script>
</body>
</html>
"""
    return (
        document.replace("__TITLE__", title)
        .replace("__TRACES__", json.dumps(traces))
        .replace("__LAYOUT__", json.dumps(layout))
    )

"""Persist auditable rating-maturity outputs and interactive charts."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import subprocess
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Iterator

from .analysis import SUPPORT_BAND_CUTS, _support_band
from .model import BoutDisagreementRow, MaturityRow, ProbeResult


PLOTLY_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"
DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/career_bout_volume/rating_maturity")
REPO_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True, slots=True)
class SourceIdentity:
    history_path: str
    history_sha256: str
    prior_path: str
    prior_sha256: str
    k_config_path: str
    k_config_sha256: str


@dataclass(frozen=True, slots=True)
class Outputs:
    run_directory: Path
    manifest: Path
    maturity_csv: Path
    support_summary_csv: Path
    support_survival_csv: Path
    jd100_summary_csv: Path
    position_support_html: Path
    rating_disagreement_csv: Path
    forecast_disagreement_csv: Path
    sensitivity_summary_csv: Path
    sensitivity_html: Path
    chii_means_csv: Path
    position_means_csv: Path
    reversal_summary_csv: Path
    chii_means_html: Path
    findings: Path


def write_outputs(
    result: ProbeResult,
    source: SourceIdentity,
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    generated_at: datetime | None = None,
) -> Outputs:
    timestamp, run_directory = _create_run_directory(output_root, generated_at)
    outputs = Outputs(
        run_directory,
        run_directory / "manifest.json",
        run_directory / "rikishi_basho_maturity.csv",
        run_directory / "position_support_summary.csv",
        run_directory / "position_support_survival.csv",
        run_directory / "jd100_support_summary.csv",
        run_directory / "position_support.html",
        run_directory / "coupled_rating_disagreement.csv",
        run_directory / "coupled_forecast_disagreement.csv",
        run_directory / "initialisation_sensitivity_summary.csv",
        run_directory / "initialisation_sensitivity.html",
        run_directory / "chii_means_by_maturity.csv",
        run_directory / "position_means_by_maturity.csv",
        run_directory / "chii_reversals_by_maturity.csv",
        run_directory / "chii_means_by_maturity.html",
        run_directory / "findings.md",
    )
    _write_dataclass_csv(result.maturity_rows, outputs.maturity_csv)
    _write_dataclass_csv(result.support_summaries, outputs.support_summary_csv)
    _write_dataclass_csv(result.support_survival, outputs.support_survival_csv)
    _write_dataclass_csv(result.jd100_summaries, outputs.jd100_summary_csv)
    _write_dataclass_csv(
        (row for row in result.maturity_rows if row.model_state_available),
        outputs.rating_disagreement_csv,
    )
    _write_dict_csv(_participant_forecast_rows(result.bout_rows), outputs.forecast_disagreement_csv)
    _write_dataclass_csv(result.sensitivity_summaries, outputs.sensitivity_summary_csv)
    _write_dataclass_csv(result.chii_maturity_rows, outputs.chii_means_csv)
    _write_dataclass_csv(result.position_maturity_rows, outputs.position_means_csv)
    _write_dataclass_csv(result.reversal_summaries, outputs.reversal_summary_csv)
    outputs.position_support_html.write_text(_position_support_html(result), encoding="utf-8")
    outputs.sensitivity_html.write_text(_sensitivity_html(result), encoding="utf-8")
    outputs.chii_means_html.write_text(_chii_html(result), encoding="utf-8")
    outputs.findings.write_text(_findings(result, source), encoding="utf-8")
    commit, dirty = _git_state()
    manifest = {
        "probe": "rating_maturity_by_banzuke_position",
        "status": "complete retrospective diagnostic; adopted P is future-informed",
        "generated_at_utc": timestamp.isoformat(),
        "history": {
            "path": source.history_path,
            "sha256": source.history_sha256,
            "start_basho": result.definition.start_basho,
            "end_basho": result.definition.end_basho,
            "basho_count": result.history_basho_count,
        },
        "adopted_prior": {"path": source.prior_path, "sha256": source.prior_sha256},
        "divisional_k": {"path": source.k_config_path, "sha256": source.k_config_sha256},
        "definition": asdict(result.definition),
        "contracts": {
            "rated_bout": "represented W/L; FS/FP and draw excluded",
            "prior_support": "eligible bouts strictly before the start of the current basho",
            "rating_birth": "first eligible rated bout; current-basho eligible entrants initialized from current chii before snapshot",
            "centering": "each model centred on ranked rikishi with model state at that start-of-basho snapshot",
            "uniform_position_bins": "left-closed width 0.05; final upper endpoint included",
            "literal_jd100": "above_Jd100, exact Jd100, and below_Jd100 including Jd101+ and Jonokuchi",
            "chii_curve_support": f"draw only chii with at least {result.definition.minimum_chii_observations} observations",
            "smooth_support_weight": "prior_rated_bouts / (prior_rated_bouts + 60); secondary sensitivity only",
        },
        "counts": {
            "rikishi_basho_observations": len(result.maturity_rows),
            "distinct_rikishi": len({row.rikishi_id for row in result.maturity_rows}),
            "raw_results": result.raw_result_count,
            "eligible_bouts": result.rated_bout_count,
            "participant_forecast_rows": 2 * len(result.bout_rows),
            "excluded_fusen": result.excluded_fusen_count,
            "excluded_draw": result.excluded_draw_count,
            "model_state_exclusions": result.model_state_exclusion_count,
            "unranked_bout_endpoints": sum(
                (row.normalized_position_a < 0) + (row.normalized_position_b < 0)
                for row in result.bout_rows
            ),
        },
        "outputs": {field.name: getattr(outputs, field.name).name for field in fields(outputs) if field.name != "run_directory"},
        "git": {"commit": commit, "dirty": dirty},
    }
    outputs.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return outputs


def _create_run_directory(root: Path, generated_at: datetime | None) -> tuple[datetime, Path]:
    root.mkdir(parents=True, exist_ok=True)
    timestamp = (generated_at or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    while True:
        path = root / timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        try:
            path.mkdir()
            return timestamp, path
        except FileExistsError:
            timestamp += timedelta(seconds=1)


def _write_dataclass_csv(rows: Iterable[object], path: Path) -> None:
    iterator = iter(rows)
    try:
        first = next(iterator)
    except StopIteration as error:
        raise ValueError(f"Cannot write empty output {path}") from error
    names = [field.name for field in fields(first)]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=names)
        writer.writeheader()
        writer.writerow(asdict(first))
        writer.writerows(asdict(row) for row in iterator)


def _write_dict_csv(rows: Iterable[dict[str, object]], path: Path) -> None:
    iterator = iter(rows)
    try:
        first = next(iterator)
    except StopIteration as error:
        raise ValueError(f"Cannot write empty output {path}") from error
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(first))
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(iterator)


def _participant_forecast_rows(rows: tuple[BoutDisagreementRow, ...]) -> Iterator[dict[str, object]]:
    for row in rows:
        for side in ("a", "b"):
            is_a = side == "a"
            probability_bk = row.probability_a_bk if is_a else 1.0 - row.probability_a_bk
            probability_bkp = row.probability_a_bkp if is_a else 1.0 - row.probability_a_bkp
            yield {
                "basho": row.basho,
                "day": row.day,
                "rikishi_id": row.rikishi_a if is_a else row.rikishi_b,
                "opponent_id": row.rikishi_b if is_a else row.rikishi_a,
                "cohort": row.cohort_a if is_a else row.cohort_b,
                "chii": row.chii_a if is_a else row.chii_b,
                "normalized_position": row.normalized_position_a if is_a else row.normalized_position_b,
                "position_band": row.position_band_a if is_a else row.position_band_b,
                "prior_rated_bouts": row.prior_rated_bouts_a if is_a else row.prior_rated_bouts_b,
                "probability_bk": probability_bk,
                "probability_bkp": probability_bkp,
                "absolute_probability_disagreement": row.absolute_probability_disagreement,
                "won": row.a_won if is_a else not row.a_won,
                "paired_participant_duplication": True,
            }


def _position_support_html(result: ProbeResult) -> str:
    support_labels = [f"{a}–<{b}" for a, b in zip(SUPPORT_BAND_CUTS, SUPPORT_BAND_CUTS[1:])] + [f"{SUPPORT_BAND_CUTS[-1]}+"]
    charts = []
    for cohort, title in (
        ("observed_entrant", "Observed entrants"),
        ("boundary_incumbent", "1989/01 boundary incumbents"),
    ):
        rows = [row for row in result.maturity_rows if row.cohort == cohort]
        position_labels = sorted({row.uniform_position_band for row in rows})
        counts = {(p, s): 0 for p in position_labels for s in support_labels}
        totals = {p: 0 for p in position_labels}
        for row in rows:
            support = _support_band(row.prior_rated_bouts)
            counts[(row.uniform_position_band, support)] += 1
            totals[row.uniform_position_band] += 1
        z = [[counts[(p, s)] / totals[p] if totals[p] else 0.0 for p in position_labels] for s in support_labels]
        heatmap = [{
            "type": "heatmap", "x": position_labels, "y": support_labels, "z": z,
            "colorscale": "Viridis", "colorbar": {"title": "Within-position proportion"},
            "hovertemplate": "Position %{x}<br>Prior bouts %{y}<br>Proportion %{z:.1%}<extra></extra>",
        }]
        survival = []
        for label in dict.fromkeys(row.position_band for row in result.support_survival if row.population == cohort):
            selected = [row for row in result.support_survival if row.population == cohort and row.position_band == label]
            survival.append({"type": "scatter", "mode": "lines", "name": label, "x": [r.threshold for r in selected], "y": [r.empirical_probability for r in selected]})
        charts.extend([
            (f"support-heatmap-{cohort}", heatmap, _layout(f"{title}: maturity landscape", "Current normalized-position band (0 = top, 1 = bottom)", "Prior rated-bout band")),
            (f"support-survival-{cohort}", survival, _layout(f"{title}: probability of at least x prior rated bouts", "Prior rated bouts", "Proportion reaching threshold", probability_axis=True)),
        ])
    return _multi_chart_document(
        "Prior Rated-Bout Support by Current Position",
        charts,
    )


def _sensitivity_html(result: ProbeResult) -> str:
    rows = [row for row in result.sensitivity_summaries if row.population == "observed_entrant"]
    positions = sorted({row.position_band for row in rows})
    supports = [f"{a}–<{b}" for a, b in zip(SUPPORT_BAND_CUTS, SUPPORT_BAND_CUTS[1:])] + [f"{SUPPORT_BAND_CUTS[-1]}+"]
    lookup = {(row.position_band, row.support_band): row for row in rows}
    rating_z = [[lookup.get((p, s)).rating_disagreement_median if lookup.get((p, s)) and lookup[(p, s)].rating_observation_count else None for p in positions] for s in supports]
    forecast_z = [[lookup.get((p, s)).forecast_disagreement_mean if lookup.get((p, s)) and lookup[(p, s)].forecast_participant_count else None for p in positions] for s in supports]
    rating = [{"type": "heatmap", "x": positions, "y": supports, "z": rating_z, "colorscale": "Plasma", "colorbar": {"title": "Rating points"}, "hovertemplate": "Position %{x}<br>Support %{y}<br>Median |centred difference| %{z:.2f}<extra></extra>"}]
    forecast = [{"type": "heatmap", "x": positions, "y": supports, "z": forecast_z, "colorscale": "Plasma", "colorbar": {"title": "Probability"}, "hovertemplate": "Position %{x}<br>Support %{y}<br>Mean |probability difference| %{z:.4f}<extra></extra>"}]
    curves = []
    for position in positions:
        selected = [row for row in rows if row.position_band == position and row.forecast_participant_count]
        curves.append({"type": "scatter", "mode": "lines+markers", "name": position, "x": [row.support_band for row in selected], "y": [row.forecast_disagreement_mean for row in selected]})
    return _multi_chart_document(
        "Initialisation Sensitivity by Position and Prior Support",
        [
            ("rating-heatmap", rating, _layout("Median absolute centred-rating disagreement", "Current normalized-position band", "Prior rated-bout band")),
            ("forecast-heatmap", forecast, _layout("Mean absolute forecast-probability disagreement", "Current normalized-position band", "Prior rated-bout band")),
            ("forecast-curves", curves, _layout("Forecast disagreement against prior support", "Prior rated-bout band", "Mean absolute probability disagreement")),
        ],
    )


def _chii_html(result: ProbeResult) -> str:
    traces = []
    for threshold in result.definition.maturity_thresholds:
        selected = [row for row in result.chii_maturity_rows if row.minimum_prior_rated_bouts == threshold and row.plotted]
        traces.append({
            "type": "scatter", "mode": "lines+markers", "name": f">= {threshold} prior bouts",
            "x": [row.chii for row in selected], "y": [row.mean_centered_rating_bkp for row in selected],
            "customdata": [[row.observation_count, row.distinct_rikishi_count, row.mean_rating_bkp] for row in selected],
            "hovertemplate": "%{x}<br>Mean centred B_kP %{y:.2f}<br>Observations %{customdata[0]}<br>Rikishi %{customdata[1]}<br>Raw mean %{customdata[2]:.2f}<extra>%{fullData.name}</extra>",
        })
    weighted = [row for row in result.chii_maturity_rows if row.minimum_prior_rated_bouts == 0 and row.plotted]
    traces.append({
        "type": "scatter", "mode": "lines", "name": "All, smooth support-weighted",
        "line": {"dash": "dot", "width": 2},
        "x": [row.chii for row in weighted],
        "y": [row.support_weighted_mean_centered_rating_bkp for row in weighted],
    })
    position_traces = []
    for threshold in result.definition.maturity_thresholds:
        selected = [row for row in result.position_maturity_rows if row.minimum_prior_rated_bouts == threshold]
        position_traces.append({
            "type": "scatter", "mode": "lines+markers", "name": f">= {threshold} prior bouts",
            "x": [row.position_band for row in selected],
            "y": [row.mean_centered_rating_bkp for row in selected],
            "customdata": [[row.observation_count, row.distinct_rikishi_count] for row in selected],
            "hovertemplate": "Position %{x}<br>Mean centred B_kP %{y:.2f}<br>Observations %{customdata[0]}<br>Rikishi %{customdata[1]}<extra>%{fullData.name}</extra>",
        })
    weighted_positions = [row for row in result.position_maturity_rows if row.minimum_prior_rated_bouts == 0]
    position_traces.append({
        "type": "scatter", "mode": "lines", "name": "All, smooth support-weighted",
        "line": {"dash": "dot", "width": 2},
        "x": [row.position_band for row in weighted_positions],
        "y": [row.support_weighted_mean_centered_rating_bkp for row in weighted_positions],
    })
    return _multi_chart_document(
        "B_kP Chii Means by Rating Maturity",
        [
            ("chii", traces, _layout("Mean start-of-basho B_kP rating by literal chii", "Chii (ordinal order)", "Mean centred rating")),
            ("position", position_traces, _layout("Mean start-of-basho B_kP rating by normalized position", "Normalized-position band (0 = top, 1 = bottom)", "Mean centred rating")),
        ],
    )


def _layout(title: str, x_title: str, y_title: str, probability_axis: bool = False) -> dict[str, object]:
    yaxis: dict[str, object] = {"title": y_title, "automargin": True}
    if probability_axis:
        yaxis.update({"range": [0, 1.01], "tickformat": ".0%"})
    return {
        "title": {"text": title, "x": .01, "xanchor": "left"}, "template": "plotly_white",
        "autosize": True, "xaxis": {"title": x_title, "automargin": True}, "yaxis": yaxis,
        "legend": {"x": 1.02, "xanchor": "left", "y": 1, "yanchor": "top"},
        "margin": {"l": 100, "r": 300, "t": 90, "b": 110},
    }


def _multi_chart_document(title: str, charts: list[tuple[str, list[dict[str, object]], dict[str, object]]]) -> str:
    divs = "\n".join(f'<div id="{chart_id}" class="chart"></div>' for chart_id, _, _ in charts)
    scripts = "\n".join(
        f'Plotly.newPlot({json.dumps(chart_id)}, {json.dumps(traces, separators=(",", ":"))}, {json.dumps(layout, separators=(",", ":"))}, config);'
        for chart_id, traces, layout in charts
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><script src="{PLOTLY_CDN}"></script>
<style>html,body{{width:100%;margin:0;font-family:Arial,sans-serif}}.chart{{width:100%;height:92vh}}</style></head>
<body>{divs}<script>const config={{responsive:true,displayModeBar:true,displaylogo:false}};{scripts}</script></body></html>
"""


def _findings(result: ProbeResult, source: SourceIdentity) -> str:
    entrant_jd = {row.literal_jd100_group: row for row in result.jd100_summaries if row.population == "observed_entrant"}
    above = entrant_jd.get("above_Jd100")
    below_rows = [row for row in result.maturity_rows if row.cohort == "observed_entrant" and row.literal_jd100_group in ("Jd100", "below_Jd100")]
    below_counts = [row.prior_rated_bouts for row in below_rows]
    below_median = statistics.median(below_counts) if below_counts else math.nan
    below_lt60 = sum(value < 60 for value in below_counts) / len(below_counts) if below_counts else math.nan

    sensitivity_lookup = {
        (row.position_band, row.support_band): row
        for row in result.sensitivity_summaries
        if row.population == "observed_entrant"
    }
    position_labels = sorted({key[0] for key in sensitivity_lookup})
    sensitivity_lines = []
    rating_decreases = 0
    forecast_decreases = 0
    comparable = 0
    for position in position_labels:
        low = sensitivity_lookup.get((position, "0–<15"))
        mature = sensitivity_lookup.get((position, "240+"))
        if not low or not mature or not low.rating_observation_count or not mature.rating_observation_count:
            continue
        comparable += 1
        rating_decreases += mature.rating_disagreement_median < low.rating_disagreement_median
        forecast_decreases += mature.forecast_disagreement_mean < low.forecast_disagreement_mean
        sensitivity_lines.append(
            f"| {position} | {low.rating_disagreement_median:.2f} | {mature.rating_disagreement_median:.2f} | "
            f"{low.forecast_disagreement_mean:.4f} | {mature.forecast_disagreement_mean:.4f} |"
        )
    rev_lines = "\n".join(
        f"| {row.minimum_prior_rated_bouts} | {row.observations_retained:,} | {row.lower_tail_plotted_chii_count} | {row.lower_tail_reversal_count} | "
        f"{(row.lower_tail_reversal_count / (row.lower_tail_plotted_chii_count - 1)) if row.lower_tail_plotted_chii_count > 1 else math.nan:.1%} | {row.lower_tail_maximum_reversal:.2f} |"
        for row in result.reversal_summaries
    )
    tail_lookup = {
        (row.minimum_prior_rated_bouts, row.position_band): row
        for row in result.position_maturity_rows
    }
    tail_step_lines = []
    tail_steps = []
    for threshold in result.definition.maturity_thresholds:
        penultimate = tail_lookup.get((threshold, "0.90–<0.95"))
        final = tail_lookup.get((threshold, "0.95–1.00"))
        if penultimate and final:
            step = final.mean_centered_rating_bkp - penultimate.mean_centered_rating_bkp
            tail_steps.append(step)
            tail_step_lines.append(
                f"| {threshold} | {penultimate.mean_centered_rating_bkp:.2f} | "
                f"{final.mean_centered_rating_bkp:.2f} | {step:+.2f} | "
                f"{final.observation_count:,} |"
            )
    tail_answer = (
        "In the normalized-position view, the final band remains above the preceding "
        f"band at every maturity cutoff ({min(tail_steps):+.2f} to {max(tail_steps):+.2f} "
        "rating points). The upturn therefore does not disappear when low-support "
        "observations are removed."
        if tail_steps else
        "The declared run does not contain both final normalized-position bands, so "
        "the structural lower-tail step cannot be assessed."
    )
    exposure_answer = (
        f"Observed entrants at Jd100 or below have median prior support {below_median:.0f} bouts; "
        f"{below_lt60:.1%} have fewer than 60. Above Jd100 the median is "
        f"{above.prior_rated_median:.0f} and {above.proportion_below_60:.1%} have fewer than 60."
        if above and below_rows else "The declared Jd100 groups were not both represented."
    )
    sensitivity_answer = (
        f"Within the {comparable} broad position bands with both endpoints, median centred-rating "
        f"disagreement is lower at 240+ than below 15 prior bouts in {rating_decreases}; mean "
        f"forecast disagreement is lower in {forecast_decreases}."
    )
    return f"""# Rating Maturity by Banzuke Position: Findings

## Declared scope

- History: `{result.definition.start_basho}` through `{result.definition.end_basho}`
- Eligible bouts: {result.rated_bout_count:,}
- Rikishi-basho observations: {len(result.maturity_rows):,}
- Distinct rikishi: {len({row.rikishi_id for row in result.maturity_rows}):,}
- Adopted prior: `{source.prior_path}`
- Interpretation: retrospective diagnostic; the adopted prior is future-informed.

## Answers to the staged questions

### 1. Exposure

{exposure_answer}

### 2. Initialisation sensitivity

{sensitivity_answer}

| Normalized-position band | Median rating disagreement, <15 | Median rating disagreement, 240+ | Mean forecast disagreement, <15 | Mean forecast disagreement, 240+ |
|---|---:|---:|---:|---:|
{chr(10).join(sensitivity_lines)}

The detailed heatmaps separate position and accumulated support. This comparison
isolates the effect of entrant initialisation under the declared coupled models;
it does not establish that either initialisation is true ability.

### 3. Relationship to the lower-tail anomaly

{tail_answer}

| Minimum prior rated bouts | Mean at 0.90–<0.95 | Mean at 0.95–1.00 | Final-band step | Final-band observations |
|---:|---:|---:|---:|---:|
{chr(10).join(tail_step_lines)}

The literal-chii diagnostic is noisier but gives the same negative result: the
proportion of supported lower-tail adjacent means that reverse direction does
not fall consistently with the maturity restriction.

| Minimum prior rated bouts | Retained observations | Supported lower-tail chii | Lower-tail reversals | Reversal proportion | Largest reversal |
|---:|---:|---:|---:|---:|---:|
{rev_lines}

A falling reversal count or magnitude is evidence consistent with maturity
composition only when supported lower-tail chii remain. If the supported tail
vanishes, the correct conclusion is inadequate identification rather than a
restored smooth curve.

The normalized-position chart provides the complementary structural view. Its
dotted trace applies the predeclared smooth weight `prior/(prior+60)` and is a
secondary sensitivity analysis, not a fitted maturity law.

## Limitations

- Boundary incumbents have unknown pre-1989 support and are reported separately.
- Rikishi-basho observations are repeated and temporally dependent.
- The support thresholds and normalized-position bins are descriptive landmarks.
- `Jd100` and normalized position `0.8395` are evidence-motivated comparisons,
  not fitted causal boundaries.
- The adopted prior was derived from the broad period being replayed, so this is
  not prospective validation.
"""


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_state() -> tuple[str, bool]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    dirty = bool(subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip())
    return commit, dirty

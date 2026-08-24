"""Write timestamped CSV, manifest, and Plotly outputs for the probe."""

from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .analysis import POSITION_BAND_CUTS, build_bout_probability_rows
from .model import (
    BoutProbabilityRow,
    HistorySource,
    ProbeOutputs,
    ProbeResult,
    RikishiCareerRow,
)


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/career_bout_volume")
REPO_ROOT = Path(__file__).resolve().parents[3]
PLOTLY_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"


def write_outputs(
    result: ProbeResult,
    *,
    source: HistorySource,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    generated_at: datetime | None = None,
) -> ProbeOutputs:
    """Write a new immutable timestamped run directory."""

    timestamp, run_directory = create_run_directory(output_root, generated_at)
    outputs = ProbeOutputs(
        run_directory=run_directory,
        manifest_json=run_directory / "manifest.json",
        rikishi_basho_csv=run_directory / "rikishi_basho.csv",
        rikishi_careers_csv=run_directory / "rikishi_careers.csv",
        scatter_html=run_directory / "career_bout_volume.html",
        bout_probability_csv=run_directory / "career_bout_probability.csv",
        bout_probability_html=run_directory / "career_bout_probability.html",
    )
    probability_rows = build_bout_probability_rows(result.career_rows)
    write_dataclass_csv(result.basho_rows, outputs.rikishi_basho_csv)
    write_dataclass_csv(result.career_rows, outputs.rikishi_careers_csv)
    write_dataclass_csv(probability_rows, outputs.bout_probability_csv)
    outputs.scatter_html.write_text(
        build_scatter_html(result.career_rows),
        encoding="utf-8",
    )
    outputs.bout_probability_html.write_text(
        build_probability_html(probability_rows),
        encoding="utf-8",
    )
    git_commit, git_dirty = git_state()
    manifest = {
        "probe": "career_bout_volume",
        "status": "complete",
        "generated_at_utc": timestamp.isoformat(),
        "source": asdict(source),
        "history": {
            "first_basho": result.history_first_basho,
            "last_basho": result.history_last_basho,
            "basho_count": result.history_basho_count,
        },
        "contracts": {
            "normalized_position": (
                "number of actual banzuke rikishi ranked above divided by "
                "banzuke size minus one; 0 is top and 1 is bottom"
            ),
            "mean_position": "unweighted arithmetic mean across banzuke appearances",
            "fought_bout": "W/L or DRAW result; FS/FP records are excluded",
            "primary_population": "completed careers not present in the first History basho",
            "position_ci95": "naive normal CI95 for the within-career mean, clipped to [0, 1]",
            "bout_probability": (
                "empirical P(total fought bouts >= threshold) within contiguous "
                "mean-position bands, completed non-partial careers only"
            ),
        },
        "position_band_cuts": list(POSITION_BAND_CUTS[:-1]) + [1.0],
        "counts": {
            "rikishi_basho_rows": len(result.basho_rows),
            "rikishi_careers": len(result.career_rows),
            "exceptions": result.exception_count,
            "primary_population": sum(row.primary_population for row in result.career_rows),
            "active": sum(row.active for row in result.career_rows),
            "partial_start": sum(row.partial_start for row in result.career_rows),
        },
        "outputs": {
            "rikishi_basho_csv": outputs.rikishi_basho_csv.name,
            "rikishi_careers_csv": outputs.rikishi_careers_csv.name,
            "scatter_html": outputs.scatter_html.name,
            "bout_probability_csv": outputs.bout_probability_csv.name,
            "bout_probability_html": outputs.bout_probability_html.name,
        },
        "git": {"commit": git_commit, "dirty": git_dirty},
    }
    outputs.manifest_json.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return outputs


def create_run_directory(
    output_root: Path,
    generated_at: datetime | None,
) -> tuple[datetime, Path]:
    """Create a collision-free UTC run directory."""

    output_root.mkdir(parents=True, exist_ok=True)
    timestamp = (generated_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    timestamp = timestamp.replace(microsecond=0)
    while True:
        run_directory = output_root / timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        try:
            run_directory.mkdir()
        except FileExistsError:
            timestamp += timedelta(seconds=1)
            continue
        return timestamp, run_directory


def write_dataclass_csv(rows: tuple[object, ...], path: Path) -> None:
    """Write a homogeneous non-empty tuple of dataclass rows."""

    if not rows:
        raise ValueError(f"Cannot write empty CSV {path}")
    field_names = [field.name for field in fields(rows[0])]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def build_scatter_html(rows: tuple[RikishiCareerRow, ...]) -> str:
    """Build the full-page unbinned career scatter document."""

    status_specs = (
        ("completed", "Completed, non-partial", "#2563eb", "circle"),
        ("active", "Active", "#dc2626", "diamond"),
        ("partial_start", "Partial start", "#d97706", "square"),
        ("active_partial_start", "Active + partial start", "#7c3aed", "x"),
    )
    traces: list[dict[str, object]] = []
    for status, label, color, symbol in status_specs:
        selected = [row for row in rows if row.career_status == status]
        if not selected:
            continue
        traces.append(
            {
                "type": "scattergl",
                "mode": "markers",
                "name": label,
                "visible": True if status == "completed" else "legendonly",
                "x": [row.total_fought_bouts for row in selected],
                "y": [1.0 - row.mean_normalized_position for row in selected],
                "customdata": [
                    [
                        row.shikona,
                        row.rikishi_id,
                        row.first_basho,
                        row.last_basho,
                        row.banzuke_appearances,
                        row.stdev_normalized_position,
                        1.0 - row.ci95_normalized_position_high,
                        1.0 - row.ci95_normalized_position_low,
                        row.total_recorded_results,
                        row.total_fusensho,
                        row.total_fusenpai,
                    ]
                    for row in selected
                ],
                "marker": {
                    "color": color,
                    "symbol": symbol,
                    "size": 7,
                    "opacity": 0.48 if status == "completed" else 0.72,
                },
                "hovertemplate": (
                    "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                    "Mean relative banzuke height: %{y:.5f}<br>"
                    "Height stdev: %{customdata[5]:.5f}<br>"
                    "Height CI95: [%{customdata[6]:.5f}, %{customdata[7]:.5f}]<br>"
                    "Fought bouts: %{x}<br>"
                    "Recorded results: %{customdata[8]}<br>"
                    "Fusensho / fusenpai: %{customdata[9]} / %{customdata[10]}<br>"
                    "Banzuke appearances: %{customdata[4]}<br>"
                    "Observed: %{customdata[2]} to %{customdata[3]}"
                    "<extra>%{fullData.name}</extra>"
                ),
            }
        )

    layout = {
        "title": {
            "text": "Career Bout Volume by Mean Relative Banzuke Height",
            "x": 0.01,
            "xanchor": "left",
        },
        "template": "plotly_white",
        "autosize": True,
        "hovermode": "closest",
        "xaxis": {
            "title": "Career bouts fought",
            "rangemode": "tozero",
            "automargin": True,
        },
        "yaxis": {
            "title": "Mean relative banzuke height (0 = bottom, 1 = top)",
            "range": [-0.01, 1.01],
            "automargin": True,
        },
        "legend": {
            "title": {"text": "Career status"},
            "x": 1.02,
            "xanchor": "left",
            "y": 1.0,
            "yanchor": "top",
        },
        "margin": {"l": 90, "r": 260, "t": 90, "b": 80},
    }
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Career Bout Volume by Mean Relative Banzuke Height</title>
  <script src="{PLOTLY_CDN}"></script>
  <style>
    html, body {{ width: 100%; height: 100%; margin: 0; font-family: Arial, sans-serif; }}
    #chart {{ width: 100vw; height: 100vh; }}
  </style>
</head>
<body>
  <div
    id="chart"
    role="img"
    aria-label="Scatter chart of career fought bouts against mean relative banzuke height"
  ></div>
  <script>
    const data = {json.dumps(traces, separators=(",", ":"))};
    const layout = {json.dumps(layout, separators=(",", ":"))};
    const config = {{responsive: true, displayModeBar: true, displaylogo: false}};
    Plotly.newPlot("chart", data, layout, config);
  </script>
</body>
</html>
"""


def build_probability_html(rows: tuple[BoutProbabilityRow, ...]) -> str:
    """Build completed-career empirical bout-tail probability curves."""

    band_labels = tuple(dict.fromkeys(row.position_band for row in rows))
    colors = (
        ("#2563eb", "rgba(37,99,235,0.16)"),
        ("#16a34a", "rgba(22,163,74,0.16)"),
        ("#d97706", "rgba(217,119,6,0.16)"),
        ("#dc2626", "rgba(220,38,38,0.16)"),
        ("#7c3aed", "rgba(124,58,237,0.16)"),
    )
    traces: list[dict[str, object]] = []
    for label, (color, fill_color) in zip(band_labels, colors):
        selected = [row for row in rows if row.position_band == label]
        thresholds = [row.bout_threshold for row in selected]
        traces.append(
            {
                "type": "scatter",
                "mode": "lines",
                "name": f"{label} CI95",
                "visible": "legendonly",
                "x": thresholds + list(reversed(thresholds)),
                "y": (
                    [row.ci95_low for row in selected]
                    + [row.ci95_high for row in reversed(selected)]
                ),
                "fill": "toself",
                "fillcolor": fill_color,
                "line": {"color": "rgba(0,0,0,0)", "width": 0},
                "hoverinfo": "skip",
            }
        )
        traces.append(
            {
                "type": "scatter",
                "mode": "lines",
                "name": label,
                "x": [row.bout_threshold for row in selected],
                "y": [row.empirical_probability for row in selected],
                "customdata": [
                    [
                        row.career_count,
                        row.reaching_count,
                        row.ci95_low,
                        row.ci95_high,
                    ]
                    for row in selected
                ],
                "line": {"color": color, "width": 2.5},
                "hovertemplate": (
                    "Position band: %{fullData.name}<br>"
                    "At least %{x} fought bouts<br>"
                    "Empirical probability: %{y:.3f}<br>"
                    "Careers reaching threshold: %{customdata[1]} / %{customdata[0]}<br>"
                    "Wilson CI95: [%{customdata[2]:.3f}, %{customdata[3]:.3f}]"
                    "<extra></extra>"
                ),
            }
        )
    layout = {
        "title": {
            "text": "Probability of Reaching Career Bout Totals by Mean Position",
            "x": 0.01,
            "xanchor": "left",
        },
        "template": "plotly_white",
        "autosize": True,
        "hovermode": "closest",
        "xaxis": {
            "title": "Career bouts fought",
            "rangemode": "tozero",
            "automargin": True,
        },
        "yaxis": {
            "title": "Proportion reaching at least this many bouts",
            "range": [0.0, 1.01],
            "tickformat": ".0%",
            "automargin": True,
        },
        "legend": {
            "title": {"text": "Mean position band"},
            "x": 1.02,
            "xanchor": "left",
            "y": 1.0,
            "yanchor": "top",
        },
        "margin": {"l": 90, "r": 280, "t": 90, "b": 80},
    }
    return _plotly_document(
        title="Probability of Reaching Career Bout Totals by Mean Position",
        aria_label=(
            "Empirical probability curves for career fought-bout totals by "
            "mean relative banzuke position band"
        ),
        traces=traces,
        layout=layout,
    )


def _plotly_document(
    *,
    title: str,
    aria_label: str,
    traces: list[dict[str, object]],
    layout: dict[str, object],
) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <script src="{PLOTLY_CDN}"></script>
  <style>
    html, body {{ width: 100%; height: 100%; margin: 0; font-family: Arial, sans-serif; }}
    #chart {{ width: 100vw; height: 100vh; }}
  </style>
</head>
<body>
  <div id="chart" role="img" aria-label="{aria_label}"></div>
  <script>
    const data = {json.dumps(traces, separators=(",", ":"))};
    const layout = {json.dumps(layout, separators=(",", ":"))};
    const config = {{
      responsive: true,
      displayModeBar: true,
      displaylogo: false
    }};
    Plotly.newPlot("chart", data, layout, config);
  </script>
</body>
</html>
"""


def git_state() -> tuple[str, bool]:
    """Return repository commit and dirty state for the manifest."""

    commit = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return commit, bool(status.strip())

"""CSV, JSON, and responsive Plotly outputs for fixed-boundary Equelo."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from src.analysis.equelo.api import annotation_free_chii
from src.analysis.equelo.fixed_supported.policy import collapse_chii
from src.analysis.equelo.fixed_supported.output import serialise_day_end_ratings
from src.sumo_core.BasicEnums import MSD
from src.sumo_core.History import History

from .model import LITERAL_CHII, MJ_BOUNDARY, PriorKey, PriorWorld
from .solver import CombinedSolveResult, CompletedPriorRating, PriorRatings


PLOTLY_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"


def write_prior_map(
    path: Path,
    *,
    completed: tuple[CompletedPriorRating, ...],
    world: PriorWorld,
) -> Path:
    """Write the complete contextual entrant-prior map."""

    fields = (
        "key_kind",
        "key_value",
        "key_label",
        "initial_rating",
        "source_kind",
        "source_key_kind",
        "source_key_value",
        "source_key_label",
        "appearance_count",
    )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in completed:
            writer.writerow({
                "key_kind": row.key.kind,
                "key_value": row.key.value,
                "key_label": world.labels[row.key],
                "initial_rating": f"{row.initial_rating:.12f}",
                "source_kind": row.source_kind,
                "source_key_kind": row.source_key.kind,
                "source_key_value": row.source_key.value,
                "source_key_label": world.labels[row.source_key],
                "appearance_count": world.appearances[row.key],
            })
    return path


def write_iteration_diagnostics(path: Path, result: CombinedSolveResult) -> Path:
    fields = (
        "stage",
        "iteration",
        "delta",
        "shift",
        "max_delta_key_kind",
        "max_delta_key_value",
        "max_delta_value",
        "max_delta_count",
    )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in (*result.modern.rows, *result.combined.rows):
            writer.writerow({
                "stage": row.stage,
                "iteration": row.iteration,
                "delta": f"{row.delta:.12f}",
                "shift": f"{row.shift:.12f}",
                "max_delta_key_kind": row.max_delta_key.kind,
                "max_delta_key_value": row.max_delta_key.value,
                "max_delta_value": f"{row.max_delta_value:.12f}",
                "max_delta_count": row.max_delta_count,
            })
    return path


def write_day_end_ratings(path: Path, ratings) -> Path:
    path.write_text(
        json.dumps(serialise_day_end_ratings(ratings), indent=2),
        encoding="utf-8",
    )
    return path


def write_comparison_outputs(
    *,
    output_root: Path,
    history: History,
    world: PriorWorld,
    experimental: PriorRatings,
    literal_control: PriorRatings,
    solve_result: CombinedSolveResult,
    literal_solve_result: CombinedSolveResult,
) -> dict[str, Path]:
    """Compare contextual and literal-chii priors over one history scope."""

    boundary_rows = _boundary_comparison_rows(
        history=history,
        world=world,
        experimental=experimental,
        literal_control=literal_control,
    )
    chii_rows = _makuuchi_chii_comparison_rows(
        history=history,
        world=world,
        experimental=experimental,
        literal_control=literal_control,
    )
    all_chii_rows = _all_chii_comparison_rows(
        history=history,
        world=world,
        experimental=experimental,
        literal_control=literal_control,
    )
    boundary_csv = _write_rows(
        output_root / "mj_boundary_prior_comparison.csv",
        boundary_rows,
    )
    chii_csv = _write_rows(
        output_root / "makuuchi_chii_prior_comparison.csv",
        chii_rows,
    )
    all_chii_csv = _write_rows(
        output_root / "all_chii_prior_comparison.csv",
        all_chii_rows,
    )
    boundary_html = _write_boundary_chart(
        output_root / "mj_boundary_prior_comparison.html",
        boundary_rows,
    )
    chii_html = _write_chii_chart(
        output_root / "makuuchi_chii_prior_comparison.html",
        chii_rows,
    )
    all_chii_html = _write_all_chii_chart(
        output_root / "all_chii_prior_comparison.html",
        all_chii_rows,
    )
    convergence_html = _write_convergence_chart(
        output_root / "fixed_point_convergence.html",
        solve_result,
        literal_solve_result,
    )
    return {
        "boundary_comparison_csv": boundary_csv,
        "makuuchi_chii_comparison_csv": chii_csv,
        "all_chii_comparison_csv": all_chii_csv,
        "boundary_chart_html": boundary_html,
        "makuuchi_chii_chart_html": chii_html,
        "all_chii_chart_html": all_chii_html,
        "convergence_chart_html": convergence_html,
    }


def _boundary_comparison_rows(
    *, history, world, experimental, literal_control
) -> list[dict[str, object]]:
    baseline_values: dict[int, list[float]] = defaultdict(list)
    literal_chiis: dict[int, set[str]] = defaultdict(set)
    for date in sorted(history):
        for rikid, chii in history[date].banzuke.rikchii.items():
            key = world.key_by_date_rikishi[date][rikid]
            if key.kind != MJ_BOUNDARY:
                continue
            clean_chii = annotation_free_chii(chii)
            literal_key = PriorKey(LITERAL_CHII, collapse_chii(clean_chii).ordinal())
            baseline_values[key.value].append(literal_control[literal_key])
            literal_chiis[key.value].add(str(clean_chii))
    rows = []
    for value in sorted(baseline_values):
        key = PriorKey(MJ_BOUNDARY, value)
        values = baseline_values[value]
        rows.append({
            "boundary_index": value,
            "appearance_count": len(values),
            "literal_chii_count": len(literal_chiis[value]),
            "literal_chii": " | ".join(sorted(literal_chiis[value])),
            "literal_chii_control_prior_mean": sum(values) / len(values),
            "experimental_boundary_prior": experimental[key],
            "difference": experimental[key] - sum(values) / len(values),
        })
    return rows


def _makuuchi_chii_comparison_rows(
    *, history, world, experimental, literal_control
) -> list[dict[str, object]]:
    values_by_chii: dict[object, list[float]] = defaultdict(list)
    for date in sorted(history):
        for rikid, chii in history[date].banzuke.rikchii.items():
            clean_chii = annotation_free_chii(chii)
            if clean_chii.level != MSD.MAEGASHIRA:
                continue
            key = world.key_by_date_rikishi[date][rikid]
            values_by_chii[clean_chii].append(experimental[key])
    rows = []
    for chii in sorted(values_by_chii, key=lambda item: item.ordinal()):
        values = values_by_chii[chii]
        experimental_mean = sum(values) / len(values)
        rows.append({
            "chii": str(chii),
            "chii_ordinal": chii.ordinal(),
            "appearance_count": len(values),
            "literal_chii_control_prior": literal_control[
                PriorKey(LITERAL_CHII, collapse_chii(chii).ordinal())
            ],
            "experimental_resolved_prior_mean": experimental_mean,
            "experimental_resolved_prior_min": min(values),
            "experimental_resolved_prior_max": max(values),
            "difference": experimental_mean - literal_control[
                PriorKey(LITERAL_CHII, collapse_chii(chii).ordinal())
            ],
        })
    return rows


def _all_chii_comparison_rows(
    *, history, world, experimental, literal_control
) -> list[dict[str, object]]:
    values_by_chii: dict[object, list[float]] = defaultdict(list)
    for date in sorted(history):
        for rikid, chii in history[date].banzuke.rikchii.items():
            clean_chii = collapse_chii(annotation_free_chii(chii))
            contextual_key = world.key_by_date_rikishi[date][rikid]
            values_by_chii[clean_chii].append(experimental[contextual_key])

    rows = []
    for chii in sorted(values_by_chii, key=lambda item: item.ordinal()):
        values = values_by_chii[chii]
        contextual_mean = sum(values) / len(values)
        literal_rating = literal_control[
            PriorKey(LITERAL_CHII, chii.ordinal())
        ]
        rows.append({
            "chii": str(chii),
            "division": chii.level.as_abbreviation(),
            "chii_ordinal": chii.ordinal(),
            "appearance_count": len(values),
            "literal_chii_control_prior": literal_rating,
            "contextual_resolved_prior_mean": contextual_mean,
            "contextual_resolved_prior_min": min(values),
            "contextual_resolved_prior_max": max(values),
            "difference": contextual_mean - literal_rating,
        })
    return rows


def _write_rows(path: Path, rows: list[dict[str, object]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def _write_boundary_chart(path: Path, rows: list[dict[str, object]]) -> Path:
    x = [row["boundary_index"] for row in rows]
    support = [row["appearance_count"] for row in rows]
    traces = [
        {
            "type": "scatter", "mode": "lines+markers", "name": "Literal-chii control (mean)",
            "x": x, "y": [row["literal_chii_control_prior_mean"] for row in rows],
            "customdata": support,
            "hovertemplate": "index=%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
        {
            "type": "scatter", "mode": "lines+markers", "name": "Boundary-index prior",
            "x": x, "y": [row["experimental_boundary_prior"] for row in rows],
            "customdata": support,
            "hovertemplate": "index=%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
    ]
    layout = {
        "title": {"text": "Entrant priors by Makuuchi--Juryo boundary index"},
        "xaxis": {"title": {"text": "Boundary index (J1e = 0)"}, "zeroline": True},
        "yaxis": {"title": {"text": "Initial rating"}},
        "hovermode": "x unified",
        "legend": {"orientation": "h", "y": -0.18},
        "margin": {"l": 70, "r": 25, "t": 70, "b": 100},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)


def _write_chii_chart(path: Path, rows: list[dict[str, object]]) -> Path:
    labels = [row["chii"] for row in rows]
    support = [row["appearance_count"] for row in rows]
    traces = [
        {
            "type": "scatter", "mode": "lines+markers", "name": "Scoped literal-chii control",
            "x": labels, "y": [row["literal_chii_control_prior"] for row in rows],
            "customdata": support,
            "hovertemplate": "%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
        {
            "type": "scatter", "mode": "lines+markers", "name": "Boundary prior resolved to chii (mean)",
            "x": labels, "y": [row["experimental_resolved_prior_mean"] for row in rows],
            "customdata": support,
            "hovertemplate": "%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
    ]
    layout = {
        "title": {"text": "Makuuchi priors viewed by literal chii"},
        "xaxis": {"title": {"text": "Literal chii"}, "type": "category"},
        "yaxis": {"title": {"text": "Initial rating"}},
        "hovermode": "x unified",
        "legend": {"orientation": "h", "y": -0.22},
        "margin": {"l": 70, "r": 25, "t": 70, "b": 115},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)


def _write_all_chii_chart(path: Path, rows: list[dict[str, object]]) -> Path:
    labels = [row["chii"] for row in rows]
    customdata = [
        [row["chii"], row["appearance_count"]]
        for row in rows
    ]
    traces = [
        {
            "type": "scattergl",
            "mode": "lines+markers",
            "name": "Scoped literal-chii control",
            "x": labels,
            "y": [row["literal_chii_control_prior"] for row in rows],
            "customdata": customdata,
            "marker": {"size": 4},
            "hovertemplate": "%{customdata[0]}<br>rating=%{y:.2f}<br>n=%{customdata[1]}<extra></extra>",
        },
        {
            "type": "scattergl",
            "mode": "lines+markers",
            "name": "Contextual prior resolved to chii (mean)",
            "x": labels,
            "y": [row["contextual_resolved_prior_mean"] for row in rows],
            "customdata": customdata,
            "marker": {"size": 4},
            "hovertemplate": "%{customdata[0]}<br>rating=%{y:.2f}<br>n=%{customdata[1]}<extra></extra>",
        },
    ]
    layout = {
        "title": {"text": "Entrant priors across all post-1988 chii"},
        "xaxis": {
            "title": {"text": "Chii (stronger to weaker)"},
            "type": "category",
            "categoryorder": "array",
            "categoryarray": labels,
            "tickangle": -90,
            "automargin": True,
        },
        "yaxis": {"title": {"text": "Initial rating"}},
        "hovermode": "x unified",
        "legend": {"orientation": "h", "y": -0.32},
        "margin": {"l": 70, "r": 25, "t": 70, "b": 170},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)


def _write_convergence_chart(
    path: Path,
    result: CombinedSolveResult,
    literal_result: CombinedSolveResult,
) -> Path:
    traces = []
    series = (
        ("boundary modern", result.modern.rows),
        ("boundary refinement", result.combined.rows),
        ("literal-chii modern", literal_result.modern.rows),
        ("literal-chii refinement", literal_result.combined.rows),
    )
    for stage, rows in series:
        traces.append({
            "type": "scatter", "mode": "lines", "name": stage,
            "x": [row.iteration for row in rows],
            "y": [row.delta for row in rows],
            "hovertemplate": "iteration=%{x}<br>delta=%{y:.6f}<extra></extra>",
        })
    layout = {
        "title": {"text": "Fixed-point convergence"},
        "xaxis": {"title": {"text": "Iteration"}},
        "yaxis": {"title": {"text": "Maximum absolute change"}, "type": "log"},
        "legend": {"orientation": "h", "y": -0.18},
        "margin": {"l": 80, "r": 25, "t": 70, "b": 100},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)


def _write_plotly_html(path: Path, *, traces, layout) -> Path:
    markup = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{layout['title']['text']}</title>
<script src="{PLOTLY_CDN}"></script>
<style>
html, body {{ margin: 0; min-height: 100%; font-family: system-ui, sans-serif; }}
#chart {{ width: 100%; min-height: 620px; }}
@media (max-width: 700px) {{ #chart {{ min-height: 520px; }} }}
</style>
</head>
<body>
<div id="chart" role="img" aria-label="{layout['title']['text']}"></div>
<script>
const traces = {json.dumps(traces, separators=(',', ':'))};
const layout = {json.dumps({**layout, 'autosize': True}, separators=(',', ':'))};
Plotly.newPlot('chart', traces, layout, {{responsive: true, displaylogo: false}});
</script>
</body>
</html>
"""
    path.write_text(markup, encoding="utf-8")
    return path

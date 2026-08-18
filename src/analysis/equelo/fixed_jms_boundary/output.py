"""Comparison outputs for the Juryo--Makushita boundary experiment."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from src.analysis.equelo.api import annotation_free_chii
from src.analysis.equelo.fixed_supported.policy import collapse_chii
from src.sumo_core.BasicEnums import Division

from ..fixed_boundary.model import JMS_BOUNDARY, LITERAL_CHII, PriorKey, PriorWorld
from ..fixed_boundary.output import _write_plotly_html, _write_rows
from ..fixed_boundary.solver import CombinedSolveResult, PriorRatings


def write_comparison_outputs(
    *,
    output_root: Path,
    history,
    world: PriorWorld,
    experimental: PriorRatings,
    literal_control: PriorRatings,
    solve_result: CombinedSolveResult,
    literal_solve_result: CombinedSolveResult,
) -> dict[str, Path]:
    boundary_rows = _boundary_rows(history, world, experimental, literal_control)
    chii_rows = _chii_rows(history, world, experimental, literal_control)
    boundary_csv = _write_rows(
        output_root / "jms_boundary_prior_comparison.csv", boundary_rows
    )
    chii_csv = _write_rows(
        output_root / "juryo_makushita_chii_prior_comparison.csv", chii_rows
    )
    boundary_html = _write_boundary_chart(
        output_root / "jms_boundary_prior_comparison.html", boundary_rows
    )
    chii_html = _write_chii_chart(
        output_root / "juryo_makushita_chii_prior_comparison.html", chii_rows
    )
    convergence_html = _write_convergence_chart(
        output_root / "fixed_point_convergence.html",
        solve_result,
        literal_solve_result,
    )
    return {
        "boundary_comparison_csv": boundary_csv,
        "chii_comparison_csv": chii_csv,
        "boundary_chart_html": boundary_html,
        "chii_chart_html": chii_html,
        "convergence_chart_html": convergence_html,
    }


def _literal_rating(chii, literal_control: PriorRatings) -> float:
    clean = collapse_chii(annotation_free_chii(chii))
    return literal_control[PriorKey(LITERAL_CHII, clean.ordinal())]


def _boundary_rows(history, world, experimental, literal_control):
    literal_values: dict[int, list[float]] = defaultdict(list)
    labels: dict[int, set[str]] = defaultdict(set)
    for date in sorted(history):
        for rikid, chii in history[date].banzuke.rikchii.items():
            key = world.key_by_date_rikishi[date][rikid]
            if key.kind != JMS_BOUNDARY:
                continue
            literal_values[key.value].append(_literal_rating(chii, literal_control))
            labels[key.value].add(str(collapse_chii(annotation_free_chii(chii))))
    rows = []
    for value in sorted(literal_values):
        key = PriorKey(JMS_BOUNDARY, value)
        values = literal_values[value]
        literal_mean = sum(values) / len(values)
        rows.append({
            "boundary_index": value,
            "appearance_count": len(values),
            "literal_chii": " | ".join(sorted(labels[value])),
            "literal_chii_control_prior_mean": literal_mean,
            "experimental_boundary_prior": experimental[key],
            "difference": experimental[key] - literal_mean,
        })
    return rows


def _chii_rows(history, world, experimental, literal_control):
    values_by_chii: dict[object, list[float]] = defaultdict(list)
    for date in sorted(history):
        for rikid, chii in history[date].banzuke.rikchii.items():
            clean = collapse_chii(annotation_free_chii(chii))
            if clean.level not in {Division.JURYO, Division.MAKUSHITA}:
                continue
            key = world.key_by_date_rikishi[date][rikid]
            values_by_chii[clean].append(experimental[key])
    rows = []
    for chii in sorted(values_by_chii, key=lambda item: item.ordinal()):
        values = values_by_chii[chii]
        contextual_mean = sum(values) / len(values)
        literal_rating = _literal_rating(chii, literal_control)
        rows.append({
            "chii": str(chii),
            "chii_ordinal": chii.ordinal(),
            "appearance_count": len(values),
            "literal_chii_control_prior": literal_rating,
            "contextual_resolved_prior_mean": contextual_mean,
            "contextual_resolved_prior_min": min(values),
            "contextual_resolved_prior_max": max(values),
            "difference": contextual_mean - literal_rating,
        })
    return rows


def _write_boundary_chart(path: Path, rows) -> Path:
    x = [row["boundary_index"] for row in rows]
    support = [row["appearance_count"] for row in rows]
    traces = [
        {
            "type": "scatter", "mode": "lines+markers",
            "name": "Scoped literal-chii control (mean)",
            "x": x,
            "y": [row["literal_chii_control_prior_mean"] for row in rows],
            "customdata": support,
            "hovertemplate": "index=%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
        {
            "type": "scatter", "mode": "lines+markers",
            "name": "J/Ms boundary prior",
            "x": x,
            "y": [row["experimental_boundary_prior"] for row in rows],
            "customdata": support,
            "hovertemplate": "index=%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
    ]
    layout = {
        "title": {"text": "Entrant priors by Juryo--Makushita boundary index"},
        "xaxis": {"title": {"text": "Boundary index (Ms1e = 0)"}, "zeroline": True},
        "yaxis": {"title": {"text": "Initial rating"}},
        "hovermode": "x unified",
        "legend": {"orientation": "h", "y": -0.18},
        "margin": {"l": 70, "r": 25, "t": 70, "b": 100},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)


def _write_chii_chart(path: Path, rows) -> Path:
    labels = [row["chii"] for row in rows]
    support = [row["appearance_count"] for row in rows]
    traces = [
        {
            "type": "scattergl", "mode": "lines+markers",
            "name": "Scoped literal-chii control",
            "x": labels,
            "y": [row["literal_chii_control_prior"] for row in rows],
            "customdata": support,
            "marker": {"size": 4},
            "hovertemplate": "%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
        {
            "type": "scattergl", "mode": "lines+markers",
            "name": "J/Ms prior resolved to chii (mean)",
            "x": labels,
            "y": [row["contextual_resolved_prior_mean"] for row in rows],
            "customdata": support,
            "marker": {"size": 4},
            "hovertemplate": "%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
    ]
    layout = {
        "title": {"text": "Juryo and Makushita priors viewed by literal chii"},
        "xaxis": {
            "title": {"text": "Literal chii"},
            "type": "category",
            "categoryorder": "array",
            "categoryarray": labels,
            "tickangle": -90,
            "automargin": True,
        },
        "yaxis": {"title": {"text": "Initial rating"}},
        "hovermode": "x unified",
        "legend": {"orientation": "h", "y": -0.30},
        "margin": {"l": 70, "r": 25, "t": 70, "b": 165},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)


def _write_convergence_chart(path: Path, boundary, literal) -> Path:
    traces = []
    for name, rows in (
        ("J/Ms primary", boundary.modern.rows),
        ("J/Ms refinement", boundary.combined.rows),
        ("literal primary", literal.modern.rows),
        ("literal refinement", literal.combined.rows),
    ):
        traces.append({
            "type": "scatter", "mode": "lines", "name": name,
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

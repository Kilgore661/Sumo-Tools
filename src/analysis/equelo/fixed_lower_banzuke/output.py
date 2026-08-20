"""Comparison artifacts for the continuous lower-banzuke experiment."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from src.analysis.equelo.api import annotation_free_chii
from src.analysis.equelo.fixed_boundary.model import (
    LITERAL_CHII,
    LOWER_BANZUKE,
    PriorKey,
    PriorWorld,
)
from src.analysis.equelo.fixed_boundary.output import _write_plotly_html, _write_rows
from src.analysis.equelo.fixed_boundary.solver import CombinedSolveResult, PriorRatings
from src.analysis.equelo.fixed_supported.policy import collapse_chii


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
    index_rows = _index_rows(history, world, experimental, literal_control)
    chii_rows = _chii_rows(history, world, experimental, literal_control)
    index_csv = _write_rows(
        output_root / "lower_banzuke_index_comparison.csv", index_rows
    )
    chii_csv = _write_rows(
        output_root / "lower_banzuke_chii_comparison.csv", chii_rows
    )
    index_html = _write_index_chart(
        output_root / "lower_banzuke_index_comparison.html", index_rows
    )
    chii_html = _write_chii_chart(
        output_root / "lower_banzuke_chii_comparison.html", chii_rows
    )
    convergence_html = _write_convergence_chart(
        output_root / "fixed_point_convergence.html",
        solve_result,
        literal_solve_result,
    )
    return {
        "index_comparison_csv": index_csv,
        "chii_comparison_csv": chii_csv,
        "index_chart_html": index_html,
        "chii_chart_html": chii_html,
        "convergence_chart_html": convergence_html,
    }


def _literal_rating(chii, literal_control: PriorRatings) -> float:
    clean = collapse_chii(annotation_free_chii(chii))
    return literal_control[PriorKey(LITERAL_CHII, clean.ordinal())]


def _index_rows(history, world, experimental, literal_control):
    literal_values: dict[int, list[float]] = defaultdict(list)
    labels: dict[int, set[str]] = defaultdict(set)
    for date in sorted(history):
        for rikid, chii in history[date].banzuke.rikchii.items():
            key = world.key_by_date_rikishi[date][rikid]
            if key.kind != LOWER_BANZUKE:
                continue
            literal_values[key.value].append(_literal_rating(chii, literal_control))
            labels[key.value].add(str(collapse_chii(annotation_free_chii(chii))))
    rows = []
    for value in sorted(literal_values):
        key = PriorKey(LOWER_BANZUKE, value)
        values = literal_values[value]
        literal_mean = sum(values) / len(values)
        rows.append({
            "lower_index": value,
            "appearance_count": len(values),
            "literal_chii": " | ".join(sorted(labels[value])),
            "literal_chii_control_prior_mean": literal_mean,
            "experimental_lower_prior": experimental[key],
            "difference": experimental[key] - literal_mean,
        })
    return rows


def _chii_rows(history, world, experimental, literal_control):
    values_by_chii: dict[object, list[float]] = defaultdict(list)
    for date in sorted(history):
        for rikid, chii in history[date].banzuke.rikchii.items():
            key = world.key_by_date_rikishi[date][rikid]
            if key.kind != LOWER_BANZUKE:
                continue
            clean = collapse_chii(annotation_free_chii(chii))
            values_by_chii[clean].append(experimental[key])
    rows = []
    for chii in sorted(values_by_chii, key=lambda item: item.ordinal()):
        values = values_by_chii[chii]
        contextual_mean = sum(values) / len(values)
        literal_rating = _literal_rating(chii, literal_control)
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


def _write_index_chart(path: Path, rows) -> Path:
    x = [row["lower_index"] for row in rows]
    support = [row["appearance_count"] for row in rows]
    traces = [
        {
            "type": "scattergl", "mode": "markers",
            "name": "Literal-chii control (mean)",
            "x": x,
            "y": [row["literal_chii_control_prior_mean"] for row in rows],
            "customdata": support,
            "hovertemplate": "index=%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
        {
            "type": "scattergl", "mode": "markers",
            "name": "Continuous lower-banzuke prior",
            "x": x,
            "y": [row["experimental_lower_prior"] for row in rows],
            "customdata": support,
            "hovertemplate": "index=%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
    ]
    layout = {
        "title": {"text": "Entrant priors by continuous lower-banzuke index"},
        "xaxis": {"title": {"text": "Lower index (Ms1e = 0)"}, "zeroline": True},
        "yaxis": {"title": {"text": "Initial rating"}},
        "hovermode": "closest",
        "legend": {"orientation": "h", "y": -0.18},
        "margin": {"l": 70, "r": 25, "t": 70, "b": 100},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)


def _write_chii_chart(path: Path, rows) -> Path:
    labels = [row["chii"] for row in rows]
    support = [row["appearance_count"] for row in rows]
    traces = [
        {
            "type": "scattergl", "mode": "markers",
            "name": "Scoped literal-chii control",
            "x": labels,
            "y": [row["literal_chii_control_prior"] for row in rows],
            "customdata": support,
            "marker": {"size": 4},
            "hovertemplate": "%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
        {
            "type": "scattergl", "mode": "markers",
            "name": "Lower-index prior resolved to chii (mean)",
            "x": labels,
            "y": [row["contextual_resolved_prior_mean"] for row in rows],
            "customdata": support,
            "marker": {"size": 4},
            "hovertemplate": "%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
    ]
    layout = {
        "title": {"text": "Continuous lower-banzuke priors viewed by literal chii"},
        "xaxis": {
            "title": {"text": "Literal chii (stronger to weaker)"},
            "type": "category",
            "categoryorder": "array",
            "categoryarray": labels,
            "tickangle": -90,
            "automargin": True,
        },
        "yaxis": {"title": {"text": "Initial rating"}},
        "hovermode": "closest",
        "legend": {"orientation": "h", "y": -0.30},
        "margin": {"l": 70, "r": 25, "t": 70, "b": 165},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)


def _write_convergence_chart(path: Path, boundary, literal) -> Path:
    traces = []
    for name, rows in (
        ("lower primary", boundary.modern.rows),
        ("lower refinement", boundary.combined.rows),
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

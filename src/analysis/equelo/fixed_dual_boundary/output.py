"""Comparison charts for the joint dual-boundary experiment."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from src.analysis.boundary_positions import competitive_division
from src.analysis.equelo.api import annotation_free_chii
from src.analysis.equelo.fixed_boundary.model import LITERAL_CHII, PriorKey
from src.analysis.equelo.fixed_boundary.output import _write_plotly_html, _write_rows
from src.analysis.equelo.fixed_supported.policy import collapse_chii

from .model import assignment_rating


def write_comparison_outputs(
    *,
    output_root: Path,
    history,
    world,
    joint_ratings,
    literal_ratings,
    history_label: str = "post-1988",
) -> dict[str, Path]:
    chii_rows = _chii_rows(history, world, joint_ratings, literal_ratings)
    focus_rows = [
        row for row in chii_rows if row["competitive_division"] in {"M", "J", "Ms"}
    ]
    pair_rows = _pair_rows(history, world, joint_ratings, literal_ratings)
    focus_pair_rows = [
        row for row in pair_rows if row["competitive_division"] in {"M", "J", "Ms"}
    ]
    chii_csv = _write_rows(output_root / "all_chii_joint_comparison.csv", chii_rows)
    focus_csv = _write_rows(
        output_root / "makuuchi_juryo_makushita_joint_comparison.csv", focus_rows
    )
    pair_csv = _write_rows(
        output_root / "makuuchi_juryo_makushita_pair_comparison.csv", focus_pair_rows
    )
    all_html = _write_chart(
        output_root / "all_chii_joint_comparison.html",
        chii_rows,
        title=f"Joint-boundary entrant priors across all {history_label} chii",
        label_key="chii",
    )
    focus_html = _write_chart(
        output_root / "makuuchi_juryo_makushita_joint_comparison.html",
        focus_rows,
        title="Joint-boundary priors from Makuuchi through Makushita",
        label_key="chii",
    )
    pair_html = _write_chart(
        output_root / "makuuchi_juryo_makushita_pair_comparison.html",
        focus_pair_rows,
        title="Joint-boundary priors by east/west chii pair",
        label_key="chii_pair",
    )
    return {
        "all_chii_csv": chii_csv,
        "focus_chii_csv": focus_csv,
        "focus_pair_csv": pair_csv,
        "all_chii_chart_html": all_html,
        "focus_chii_chart_html": focus_html,
        "focus_pair_chart_html": pair_html,
    }


def _chii_rows(history, world, joint_ratings, literal_ratings):
    contextual = defaultdict(list)
    for date in sorted(history):
        for rikid, chii in history[date].banzuke.rikchii.items():
            clean = collapse_chii(annotation_free_chii(chii))
            assignment = world.assignments_by_date_rikishi[date][rikid]
            contextual[clean].append(assignment_rating(assignment, joint_ratings))
    rows = []
    for chii in sorted(contextual, key=lambda item: item.ordinal()):
        values = contextual[chii]
        literal = literal_ratings[PriorKey(LITERAL_CHII, chii.ordinal())]
        mean = sum(values) / len(values)
        rows.append({
            "chii": str(chii),
            "chii_ordinal": chii.ordinal(),
            "competitive_division": competitive_division(chii),
            "appearance_count": len(values),
            "literal_chii_control_prior": literal,
            "joint_boundary_prior_mean": mean,
            "joint_boundary_prior_min": min(values),
            "joint_boundary_prior_max": max(values),
            "difference": mean - literal,
        })
    return rows


def _pair_rows(history, world, joint_ratings, literal_ratings):
    joint_values = defaultdict(list)
    literal_values = defaultdict(list)
    pair_ordinals = {}
    pair_divisions = {}
    for date in sorted(history):
        for rikid, chii in history[date].banzuke.rikchii.items():
            clean = collapse_chii(annotation_free_chii(chii))
            abbreviation = clean.level.as_abbreviation()
            pair = (abbreviation, clean.number)
            assignment = world.assignments_by_date_rikishi[date][rikid]
            joint_values[pair].append(assignment_rating(assignment, joint_ratings))
            literal_values[pair].append(
                literal_ratings[PriorKey(LITERAL_CHII, clean.ordinal())]
            )
            pair_ordinals[pair] = min(pair_ordinals.get(pair, clean.ordinal()), clean.ordinal())
            pair_divisions[pair] = competitive_division(clean)
    rows = []
    for pair in sorted(joint_values, key=lambda item: pair_ordinals[item]):
        joint = joint_values[pair]
        literal = literal_values[pair]
        joint_mean = sum(joint) / len(joint)
        literal_mean = sum(literal) / len(literal)
        rows.append({
            "chii_pair": f"{pair[0]}{pair[1]}",
            "chii_ordinal": pair_ordinals[pair],
            "competitive_division": pair_divisions[pair],
            "appearance_count": len(joint),
            "literal_chii_control_prior": literal_mean,
            "joint_boundary_prior_mean": joint_mean,
            "joint_boundary_prior_min": min(joint),
            "joint_boundary_prior_max": max(joint),
            "difference": joint_mean - literal_mean,
        })
    return rows


def _write_chart(path: Path, rows, *, title: str, label_key: str) -> Path:
    labels = [row[label_key] for row in rows]
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
            "name": "Joint dual-boundary prior",
            "x": labels,
            "y": [row["joint_boundary_prior_mean"] for row in rows],
            "customdata": support,
            "marker": {"size": 4},
            "hovertemplate": "%{x}<br>rating=%{y:.2f}<br>n=%{customdata}<extra></extra>",
        },
    ]
    layout = {
        "title": {"text": title},
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
        "legend": {"orientation": "h", "y": -0.31},
        "margin": {"l": 70, "r": 25, "t": 70, "b": 170},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)

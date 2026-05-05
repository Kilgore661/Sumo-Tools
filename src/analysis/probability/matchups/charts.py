from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from src.analysis.probability.matchups.traces import EqueloTracePoint, ObservedTracePoint


def write_observed_trace_chart(
    points: tuple[ObservedTracePoint, ...],
    output_path: Path,
    *,
    initially_visible: str = "Y1",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    traces = []

    for selected_chii, rows in _group_points(points):
        visible = True if selected_chii == initially_visible else "legendonly"
        xs = [row.opponent_chii for row in rows]
        ys = [row.p_selected_wins for row in rows]
        error_plus = [row.ci95_upper - row.p_selected_wins for row in rows]
        error_minus = [row.p_selected_wins - row.ci95_lower for row in rows]
        customdata = [
            (
                row.selected_chii,
                row.opponent_chii,
                row.n_obs,
                row.n_selected_wins,
                row.ci95_lower,
                row.ci95_upper,
            )
            for row in rows
        ]
        traces.append(
            {
                "x": xs,
                "y": ys,
                "mode": "lines+markers",
                "name": selected_chii,
                "visible": visible,
                "type": "scatter",
                "error_y": {
                    "type": "data",
                    "symmetric": False,
                    "array": error_plus,
                    "arrayminus": error_minus,
                    "visible": True,
                },
                "customdata": customdata,
                "hovertemplate": (
                    "Selected=%{customdata[0]}<br>"
                    "Opponent=%{customdata[1]}<br>"
                    "P(selected wins)=%{y:.3f}<br>"
                    "CI95=[%{customdata[4]:.3f}, %{customdata[5]:.3f}]<br>"
                    "Wins=%{customdata[3]:,} / %{customdata[2]:,}"
                    "<extra></extra>"
                ),
            }
        )

    _write_plotly_html(
        output_path=output_path,
        traces=traces,
        title="Observed Sideless Chii Matchup Traces",
        yaxis_title="Observed P(selected chii wins)",
        categoryarray=_opponent_categoryarray(points),
    )
    return output_path


def write_equelo_trace_chart(
    points: tuple[EqueloTracePoint, ...],
    output_path: Path,
    *,
    initially_visible: str = "Y1",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    traces = []

    for selected_chii, rows in _group_points(points):
        visible = True if selected_chii == initially_visible else "legendonly"
        xs = [row.opponent_chii for row in rows]
        ys = [row.p_selected_wins for row in rows]
        customdata = [
            (
                row.selected_chii,
                row.opponent_chii,
                row.selected_rating,
                row.opponent_rating,
            )
            for row in rows
        ]
        traces.append(
            {
                "x": xs,
                "y": ys,
                "mode": "lines+markers",
                "name": selected_chii,
                "visible": visible,
                "type": "scatter",
                "customdata": customdata,
                "hovertemplate": (
                    "Selected=%{customdata[0]}<br>"
                    "Opponent=%{customdata[1]}<br>"
                    "P(selected wins)=%{y:.3f}<br>"
                    "Selected rating=%{customdata[2]:.1f}<br>"
                    "Opponent rating=%{customdata[3]:.1f}"
                    "<extra></extra>"
                ),
            }
        )

    _write_plotly_html(
        output_path=output_path,
        traces=traces,
        title="Equelo Sideless Chii Matchup Traces",
        yaxis_title="Equelo-implied P(selected chii wins)",
        categoryarray=_opponent_categoryarray(points),
    )
    return output_path


def _group_points(points: Iterable) -> list[tuple[str, list]]:
    grouped: dict[str, list] = {}
    ordinals: dict[str, int] = {}
    for point in points:
        grouped.setdefault(point.selected_chii, []).append(point)
        ordinals[point.selected_chii] = point.selected_ordinal

    result: list[tuple[str, list]] = []
    for selected_chii in sorted(grouped, key=lambda chii: ordinals[chii]):
        result.append(
            (
                selected_chii,
                sorted(grouped[selected_chii], key=lambda point: point.opponent_ordinal),
            )
        )
    return result


def _write_plotly_html(
    *,
    output_path: Path,
    traces: list[dict],
    title: str,
    yaxis_title: str,
    categoryarray: list[str],
) -> None:
    layout = {
        "title": title,
        "xaxis": {
            "title": "Opponent sideless chii",
            "type": "category",
            "categoryorder": "array",
            "categoryarray": categoryarray,
        },
        "yaxis": {"title": yaxis_title, "range": [0, 1], "tickformat": ".0%"},
        "hovermode": "closest",
        "legend": {"title": {"text": "Selected chii"}},
        "margin": {"l": 70, "r": 30, "t": 70, "b": 90},
    }
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <style>
    html, body {{ margin: 0; height: 100%; font-family: Arial, sans-serif; }}
    #chart {{ width: 100vw; height: 100vh; }}
  </style>
</head>
<body>
  <div id="chart"></div>
  <script>
    const traces = {json.dumps(traces)};
    const layout = {json.dumps(layout)};
    Plotly.newPlot("chart", traces, layout, {{responsive: true}});
  </script>
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")


def _opponent_categoryarray(points: Iterable) -> list[str]:
    ordinals: dict[str, int] = {}
    for point in points:
        ordinals[point.opponent_chii] = point.opponent_ordinal
    return [
        chii
        for chii, _ in sorted(ordinals.items(), key=lambda item: item[1])
    ]

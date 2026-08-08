"""Render Proposal 1 result models with Plotly's CDN JavaScript bundle."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from src.sumo_core.History import Date

from .definition import Proposal1Definition
from .series import CumulativeLossRow, RollingLossRow
from .uncertainty import UncertaintyRow


class PredictiveBehaviourResult(Protocol):
    definition: Proposal1Definition
    rolling_losses: tuple[RollingLossRow, ...]
    cumulative_losses: tuple[CumulativeLossRow, ...]
    uncertainty: tuple[UncertaintyRow, ...]


def write_predictive_behaviour_chart(
    result: PredictiveBehaviourResult,
    filename: Path,
    *,
    title: str = "Basic Elo predictive behaviour: q=400, k=35",
) -> None:
    """Write paired-loss curves; values are calculated upstream."""

    traces: list[dict[str, object]] = []
    colours = {6: "#3366cc", 12: "#dc3912", 24: "#109618"}
    uncertainty = {
        (row.window_basho, row.end_date): row
        for row in result.uncertainty
    }
    for window in result.definition.rolling_windows:
        rolling = tuple(
            row for row in result.rolling_losses
            if row.window_basho == window
        )
        colour = colours[window]
        dates = [_plot_date(row.end_date) for row in rolling]
        for axis, metric, lower, upper in (
            ("y", "log_loss_difference", "log_loss_difference_lower", "log_loss_difference_upper"),
            ("y2", "brier_difference", "brier_difference_lower", "brier_difference_upper"),
        ):
            intervals = [uncertainty[(window, row.end_date)] for row in rolling]
            traces.append(
                {
                    "type": "scatter",
                    "x": dates + dates[::-1],
                    "y": [getattr(row, upper) for row in intervals]
                    + [getattr(row, lower) for row in reversed(intervals)],
                    "xaxis": "x" if axis == "y" else "x2",
                    "yaxis": axis,
                    "fill": "toself",
                    "fillcolor": _transparent(colour),
                    "line": {"color": "rgba(0,0,0,0)"},
                    "hoverinfo": "skip",
                    "legendgroup": str(window),
                    "showlegend": False,
                }
            )
            traces.append(
                {
                    "type": "scatter",
                    "x": dates,
                    "y": [getattr(row, f"mean_{metric}") for row in rolling],
                    "xaxis": "x" if axis == "y" else "x2",
                    "yaxis": axis,
                    "mode": "lines",
                    "line": {"color": colour, "width": 2},
                    "name": f"{window} basho",
                    "legendgroup": str(window),
                    "showlegend": axis == "y",
                    "customdata": [row.bout_count for row in rolling],
                    "hovertemplate": "%{x|%Y/%m}<br>difference=%{y:.5f}<br>bouts=%{customdata}<extra></extra>",
                }
            )

    cumulative_dates = [
        _plot_date(row.end_date) for row in result.cumulative_losses
    ]
    for axis, metric in (
        ("y", "mean_log_loss_difference"),
        ("y2", "mean_brier_difference"),
    ):
        traces.append(
            {
                "type": "scatter",
                "x": cumulative_dates,
                "y": [getattr(row, metric) for row in result.cumulative_losses],
                "xaxis": "x" if axis == "y" else "x2",
                "yaxis": axis,
                "mode": "lines",
                "line": {"color": "#555", "width": 2, "dash": "dot"},
                "name": "Cumulative from 1989/01",
                "legendgroup": "cumulative",
                "showlegend": axis == "y",
                "customdata": [row.bout_count for row in result.cumulative_losses],
                "hovertemplate": "%{x|%Y/%m}<br>difference=%{y:.5f}<br>bouts=%{customdata}<extra></extra>",
            }
        )

    layout = {
        "title": {
            "text": title + (
                "<br><sup>Negative differences favour Basic Elo; shaded bands "
                "are pointwise basho-block bootstrap intervals.</sup>"
            ),
            "x": 0.5,
            "xanchor": "center",
            "y": 0.98,
            "yanchor": "top",
        },
        "template": "plotly_white",
        "height": 850,
        "hovermode": "x unified",
        "legend": {
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": 1.16,
            "yanchor": "middle",
        },
        "margin": {"l": 75, "r": 30, "t": 175, "b": 60},
        "xaxis": {
            "domain": [0, 1],
            "anchor": "y",
            "type": "date",
            "tickformat": "%Y/%m",
            "showticklabels": False,
        },
        "yaxis": {
            "domain": [0.56, 1],
            "title": "Log-loss difference",
            "zeroline": True,
            "zerolinecolor": "#222",
        },
        "xaxis2": {
            "domain": [0, 1],
            "anchor": "y2",
            "type": "date",
            "tickformat": "%Y/%m",
            "title": "Basho",
        },
        "yaxis2": {
            "domain": [0, 0.44],
            "title": "Brier-loss difference",
            "zeroline": True,
            "zerolinecolor": "#222",
        },
        "annotations": [
            {"text": "Mean log-loss difference from a 50% forecast", "x": 0.5, "y": 1.04, "xref": "paper", "yref": "paper", "showarrow": False},
            {"text": "Mean Brier-loss difference from a 50% forecast", "x": 0.5, "y": 0.48, "xref": "paper", "yref": "paper", "showarrow": False},
        ],
    }
    document = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Basic Elo predictive behaviour</title>
  <script src="https://cdn.plot.ly/plotly-3.0.1.min.js" charset="utf-8"></script>
</head>
<body style="margin:0">
  <div id="chart" style="width:100%;min-height:850px"></div>
  <script>
    const traces = __TRACES__;
    const layout = __LAYOUT__;
    Plotly.newPlot("chart", traces, layout, {responsive: true, displaylogo: false});
  </script>
</body>
</html>
"""
    filename.write_text(
        document.replace("__TRACES__", json.dumps(traces)).replace(
            "__LAYOUT__", json.dumps(layout)
        ),
        encoding="utf-8",
    )


def _transparent(hex_colour: str) -> str:
    red, green, blue = (
        int(hex_colour[index:index + 2], 16)
        for index in (1, 3, 5)
    )
    return f"rgba({red},{green},{blue},0.13)"


def _plot_date(date: Date) -> str:
    return f"{int(date.year):04d}-{int(date.month):02d}-01"

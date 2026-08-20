"""Render a persisted east/west-paired boundary-merge dataset."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from src.analysis.equelo.fixed_boundary.output import PLOTLY_CDN


def write_paired_merge_chart(
    source_csv: Path,
    output_html: Path | None = None,
) -> Path:
    """Render producer-owned paired values without calculating ratings."""

    with source_csv.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"Paired boundary-merge CSV contains no rows: {source_csv}")
    destination = source_csv.with_suffix(".html") if output_html is None else output_html
    labels = [row["rank_pair"] for row in rows]
    customdata = [[row["member_chii"], row["source"]] for row in rows]
    traces = [
        _trace(rows, labels, "mj_resolved_rating", "M/J paired estimate", "#2457a7"),
        _trace(
            rows,
            labels,
            "aligned_lower_resolved_rating",
            "Aligned lower-banzuke paired estimate",
            "#d95f02",
        ),
        {
            "type": "scattergl",
            "mode": "lines+markers",
            "name": "Paired retained construction",
            "x": labels,
            "y": [_optional_float(row["pre_smoothing_rating"]) for row in rows],
            "customdata": customdata,
            "marker": {"size": 5, "color": "#111111"},
            "line": {"width": 2, "color": "#111111"},
            "hovertemplate": (
                "%{x}<br>paired=%{y:.2f}<br>members=%{customdata[0]}"
                "<br>source=%{customdata[1]}<extra></extra>"
            ),
        },
    ]
    layout = {
        "title": {
            "text": "East/west-paired retained boundary merge",
            "x": 0.01,
            "xanchor": "left",
        },
        "autosize": True,
        "xaxis": {
            "title": {"text": "Rank pair (stronger to weaker)"},
            "type": "category",
            "categoryorder": "array",
            "categoryarray": labels,
            "tickangle": -90,
            "automargin": True,
        },
        "yaxis": {"title": {"text": "Initial rating"}, "automargin": True},
        "hovermode": "closest",
        "legend": {"orientation": "h", "x": 0, "y": 1.08},
        "margin": {"l": 75, "r": 35, "t": 105, "b": 145},
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "#f7f8fa",
    }
    config = {"responsive": True, "displaylogo": False, "scrollZoom": True}
    markup = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>East/west-paired retained boundary merge</title>
<script src="{PLOTLY_CDN}"></script>
<style>
html, body {{ width: 100%; height: 100%; margin: 0; font-family: system-ui, sans-serif; }}
#chart {{ width: 100vw; height: 100vh; min-height: 620px; }}
</style>
</head>
<body>
<div id="chart" role="img" aria-label="East/west-paired retained boundary merge"></div>
<script>
const traces = {json.dumps(traces, separators=(',', ':'))};
const layout = {json.dumps(layout, separators=(',', ':'))};
const config = {json.dumps(config, separators=(',', ':'))};
Plotly.newPlot('chart', traces, layout, config);
</script>
</body>
</html>
"""
    destination.write_text(markup, encoding="utf-8")
    return destination


def _trace(rows, labels, column: str, name: str, color: str) -> dict[str, object]:
    return {
        "type": "scattergl",
        "mode": "lines+markers",
        "name": name,
        "x": labels,
        "y": [_optional_float(row[column]) for row in rows],
        "marker": {"size": 4},
        "line": {"width": 1, "color": color},
        "hovertemplate": "%{x}<br>rating=%{y:.2f}<extra></extra>",
    }


def _optional_float(value: str) -> float | None:
    return None if value == "" else float(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_csv", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output = write_paired_merge_chart(args.source_csv, args.output)
    print(f"Chart: {output}")


if __name__ == "__main__":
    main()

"""Render a persisted literal-chii boundary-merge dataset."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from src.analysis.equelo.fixed_boundary.output import PLOTLY_CDN


def write_boundary_merge_chart(
    source_csv: Path,
    output_html: Path | None = None,
    *,
    cutoff_chii: str = "Jd100e",
    lower_shift: float | None = None,
) -> Path:
    """Render the producer-owned CSV without calculating any rating values."""

    with source_csv.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"Boundary-merge CSV contains no rows: {source_csv}")
    required = {
        "chii",
        "mj_resolved_rating",
        "aligned_lower_resolved_rating",
        "mj_weight",
        "pre_smoothing_rating",
        "source",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Boundary-merge CSV is missing columns: {sorted(missing)}")

    destination = source_csv.with_suffix(".html") if output_html is None else output_html
    destination.parent.mkdir(parents=True, exist_ok=True)
    labels = [row["chii"] for row in rows]
    customdata = [[row["chii"], row["source"], row["mj_weight"]] for row in rows]
    traces = [
        {
            "type": "scattergl",
            "mode": "lines+markers",
            "name": "M/J resolved estimate",
            "x": labels,
            "y": [_optional_float(row["mj_resolved_rating"]) for row in rows],
            "marker": {"size": 4},
            "line": {"width": 1, "color": "#2457a7"},
            "hovertemplate": "%{x}<br>M/J=%{y:.2f}<extra></extra>",
        },
        {
            "type": "scattergl",
            "mode": "lines+markers",
            "name": "Aligned lower-banzuke estimate",
            "x": labels,
            "y": [
                _optional_float(row["aligned_lower_resolved_rating"])
                for row in rows
            ],
            "marker": {"size": 4},
            "line": {"width": 1, "color": "#d95f02"},
            "hovertemplate": "%{x}<br>aligned lower=%{y:.2f}<extra></extra>",
        },
        {
            "type": "scattergl",
            "mode": "lines+markers",
            "name": "Pre-smoothing construction",
            "x": labels,
            "y": [_optional_float(row["pre_smoothing_rating"]) for row in rows],
            "customdata": customdata,
            "marker": {"size": 5, "color": "#111111"},
            "line": {"width": 2, "color": "#111111"},
            "hovertemplate": (
                "%{customdata[0]}<br>constructed=%{y:.2f}"
                "<br>source=%{customdata[1]}<br>M/J weight=%{customdata[2]}"
                "<extra></extra>"
            ),
        },
    ]
    shift_text = "" if lower_shift is None else f"Lower shift {lower_shift:+.3f}; "
    layout = {
        "title": {
            "text": (
                "Pre-smoothing boundary merge on literal chii"
                f"<br><sup>{shift_text}linear Juryo blend; flat below {cutoff_chii}</sup>"
            ),
            "x": 0.01,
            "xanchor": "left",
        },
        "autosize": True,
        "xaxis": {
            "title": {"text": "Literal chii (stronger to weaker)"},
            "type": "category",
            "categoryorder": "array",
            "categoryarray": labels,
            "tickangle": -90,
            "automargin": True,
        },
        "yaxis": {"title": {"text": "Initial rating"}, "automargin": True},
        "hovermode": "closest",
        "legend": {"orientation": "h", "x": 0, "y": 1.08},
        "shapes": [{
            "type": "line",
            "xref": "x",
            "x0": cutoff_chii,
            "x1": cutoff_chii,
            "yref": "paper",
            "y0": 0,
            "y1": 1,
            "line": {"color": "#666666", "width": 1, "dash": "dash"},
        }],
        "margin": {"l": 75, "r": 35, "t": 120, "b": 145},
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "#f7f8fa",
    }
    config = {"responsive": True, "displaylogo": False, "scrollZoom": True}
    markup = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pre-smoothing boundary merge on literal chii</title>
<script src="{PLOTLY_CDN}"></script>
<style>
html, body {{ width: 100%; height: 100%; margin: 0; font-family: system-ui, sans-serif; }}
#chart {{ width: 100vw; height: 100vh; min-height: 620px; }}
</style>
</head>
<body>
<div id="chart" role="img" aria-label="Pre-smoothing boundary merge on literal chii"></div>
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


def _optional_float(value: str) -> float | None:
    return None if value == "" else float(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_csv", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--cutoff-chii", default="Jd100e")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output = write_boundary_merge_chart(
        args.source_csv,
        args.output,
        cutoff_chii=args.cutoff_chii,
    )
    print(f"Chart: {output}")


if __name__ == "__main__":
    main()

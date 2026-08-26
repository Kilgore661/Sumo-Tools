"""Render a full-width Plotly chart from a recentering prior comparison CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_INPUT = Path(
    "files/output/analysis/equelo_population_policy/recentering/prior_comparison.csv"
)
VARIANTS = (
    ("uniform", "Uniform (alpha = 0)", "#202020", 2.4),
    ("support_0_25", "Support^0.25", "#2f6fdd", 1.8),
    ("support_0_5", "Support^0.5", "#d9822b", 1.8),
    ("support_1", "Support^1", "#bd2d32", 1.8),
)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output = args.output or args.input.with_suffix(".html")
    write_chart(args.input, output)
    print(output.resolve())
    return 0


def write_chart(input_path: Path, output_path: Path) -> None:
    grouped: dict[str, list[dict[str, str]]] = {name: [] for name, *_ in VARIANTS}
    with input_path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["variant"] in grouped:
                grouped[row["variant"]].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row["ordinal"]))
    if not grouped["uniform"]:
        raise ValueError(f"No recentering rows in {input_path}")

    traces = []
    for name, label, colour, width in VARIANTS:
        rows = grouped[name]
        traces.append({
            "name": label,
            "type": "scatter",
            "mode": "lines",
            "x": [row["chii"] for row in rows],
            "y": [float(row["rating"]) for row in rows],
            "customdata": [
                [int(row["observations"]), float(row["change_from_uniform"])]
                for row in rows
            ],
            "line": {"color": colour, "width": width},
            "hovertemplate": (
                "<b>%{x}</b><br>Rating: %{y:.2f}<br>Observations: %{customdata[0]}"
                "<br>Change from uniform: %{customdata[1]:+.2f}"
                "<extra>%{fullData.name}</extra>"
            ),
        })

    title = "Final chii-to-rating maps by recentering alpha"
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js" charset="utf-8"></script>
<style>
html,body{{width:100%;height:100%;margin:0;font-family:system-ui,sans-serif;background:#fafafa;color:#202020}}
body{{display:flex;flex-direction:column}}header{{padding:12px 18px 4px}}h1{{font-size:20px;margin:0 0 3px}}
p{{font-size:13px;margin:0;color:#555}}#chart{{flex:1 1 auto;min-height:500px;width:100%}}
</style></head><body><header><h1>{title}</h1>
<p>Converged fixed-point priors; hover for exact chii and support. Drag to zoom; double-click to reset.</p>
</header><div id="chart"></div><script>
const traces={json.dumps(traces, separators=(',', ':'))};
const layout={{autosize:true,margin:{{l:70,r:24,t:18,b:90}},paper_bgcolor:'#fafafa',plot_bgcolor:'#fff',
hovermode:'closest',legend:{{orientation:'h',x:0,y:1.02,xanchor:'left',yanchor:'bottom'}},
xaxis:{{title:'Chii',type:'category',categoryorder:'array',categoryarray:{json.dumps([row['chii'] for row in grouped['uniform']])},tickangle:-55,showgrid:false}},
yaxis:{{title:'Rating',gridcolor:'#e8e8e8',zeroline:false}}}};
const config={{responsive:true,displayModeBar:true,displaylogo:false,scrollZoom:true,
toImageButtonOptions:{{format:'png',filename:'chii_rating_recentering_comparison',scale:2}}}};
Plotly.newPlot('chart',traces,layout,config);
</script></body></html>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())

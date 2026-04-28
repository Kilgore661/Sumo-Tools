import csv
import json
from pathlib import Path

from src.analysis.persistence.classes import PersistenceResults
from src.sumo_core.BasicEnums import Division


def _division_label(division: Division) -> str:
    return division.name.capitalize()


def write_persistence_csv(
    results: PersistenceResults,
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "date",
                "division",
                "num_basho",
                "frequency",
                "mean_persistence",
                "stdev_persistence",
            ]
        )

        for row in results.rows:
            writer.writerow(
                [
                    str(row.date),
                    _division_label(row.division),
                    row.num_basho,
                    row.frequency,
                    row.mean_persistence,
                    row.stdev_persistence,
                ]
            )

    return output_path


def write_persistence_chart(
    results: PersistenceResults,
    output_path: Path,
    title: str,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    traces = []

    for division in Division:
        rows = [
            row
            for row in results.rows
            if row.division == division
        ]

        traces.append(
            {
                "type": "scatter",
                "mode": "lines",
                "name": _division_label(division),
                "visible": True if division == Division.MAKUUCHI else "legendonly",
                "x": [str(row.date) for row in rows],
                "y": [row.mean_persistence for row in rows],
                "customdata": [
                    [
                        row.stdev_persistence,
                        row.frequency,
                    ]
                    for row in rows
                ],
                "hovertemplate": (
                    "Date=%{x}<br>"
                    "Division=%{fullData.name}<br>"
                    "Mean persistence=%{y:.6f}<br>"
                    "Stdev=%{customdata[0]:.6f}<br>"
                    "Frequency=%{customdata[1]}<extra></extra>"
                ),
            }
        )

    traces_json = json.dumps(traces)
    title_json = json.dumps(title)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      color-scheme: dark;
    }}

    html, body {{
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      background: #111827;
      color: #e5e7eb;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    .page {{
      box-sizing: border-box;
      width: 100%;
      min-height: 100vh;
      padding: 20px;
    }}

    #chart {{
      width: 100%;
      height: calc(100vh - 40px);
      min-height: 560px;
      background: #111827;
    }}
  </style>
</head>
<body>
  <div class="page">
    <div id="chart"></div>
  </div>
  <script>
    const traces = {traces_json};
    const layout = {{
      title: {title_json},
      paper_bgcolor: "#111827",
      plot_bgcolor: "#111827",
      font: {{
        color: "#e5e7eb"
      }},
      xaxis: {{
        title: "Basho",
        type: "category",
        gridcolor: "#374151",
        linecolor: "#4b5563",
        automargin: true
      }},
      yaxis: {{
        title: "Mean persistence",
        range: [0, 1],
        gridcolor: "#374151",
        linecolor: "#4b5563",
        automargin: true
      }},
      legend: {{
        orientation: "v",
        yanchor: "top",
        y: 1,
        xanchor: "left",
        x: 1.02
      }},
      margin: {{
        l: 70,
        r: 150,
        t: 70,
        b: 90
      }},
      hovermode: "closest"
    }};
    const config = {{
      responsive: true,
      displaylogo: false
    }};
    Plotly.newPlot("chart", traces, layout, config);
  </script>
</body>
</html>
"""

    output_path.write_text(html, encoding="utf-8")
    return output_path

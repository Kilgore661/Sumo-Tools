"""Division Stability page renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path

from ..classes import Page


def write_division_stability_page(
    page: Page,
    target_path: Path,
    asset_prefix: str = "",
) -> None:
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<link rel="icon" type="image/x-icon" href="../Sumo/meep.png">',
            f'<link rel="stylesheet" href="{asset_prefix}site-page.css">',
            f"<title>{escape(page.title)}</title>",
            "<style>",
            ".tool-content { display: flex; flex-direction: column; align-items: stretch; }",
            ".chart-panel { width: 100%; flex: 1 1 auto; min-width: 0; min-height: 0; display: flex; flex-direction: column; border: 1px solid var(--site-line-soft); background: rgba(255, 255, 255, 0.025); }",
            ".chart-header { flex: 0 0 auto; padding: 10px 12px 0; }",
            "#chart-title { margin: 0; font-size: 1.05rem; font-weight: 700; }",
            "#chart-subtitle { margin: 4px 0 0; color: var(--page-muted); font-size: 0.9rem; }",
            "#chart { width: 100%; flex: 1 1 auto; min-width: 0; min-height: 420px; }",
            "</style>",
            '<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>',
            "</head>",
            "<body>",
            '<div class="tool-shell">',
            '<header class="tool-title-bar">',
            f"<h1>{escape(page.title)}</h1>",
            f"<p>{escape(page.summary)}</p>",
            "</header>",
            '<main class="tool-content">',
            '<div class="chart-panel">',
            '<div class="chart-header">',
            '<h2 id="chart-title"></h2>',
            '<p id="chart-subtitle"></p>',
            "</div>",
            '<div id="chart"></div>',
            "</div>",
            "</main>",
            "</div>",
            "<script>",
            DIVISION_STABILITY_JS,
            "</script>",
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


DIVISION_STABILITY_JS = r"""
const chart = document.getElementById("chart");
const chartTitle = document.getElementById("chart-title");
const chartSubtitle = document.getElementById("chart-subtitle");

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(",");
  return lines.slice(1).filter(Boolean).map(line => {
    const values = line.split(",");
    const row = {};
    headers.forEach((header, index) => { row[header] = values[index]; });
    return row;
  });
}

function numeric(value) {
  return Number.parseFloat(value);
}

function rowsForDivision(rows, division) {
  return rows.filter(row => row.division === division);
}

function orderedDates(rows) {
  const seen = new Set();
  const dates = [];
  for (const row of rows) {
    if (seen.has(row.date)) continue;
    seen.add(row.date);
    dates.push(row.date);
  }
  return dates;
}

function tracesForRows(pageConfig, rows) {
  const chartConfig = pageConfig.chart;
  const defaultVisible = new Set(pageConfig.default_visible || []);
  return pageConfig.division_order.map(division => {
    const divisionRows = rowsForDivision(rows, division);
    return {
      type: "scatter",
      mode: "lines",
      name: division,
      visible: defaultVisible.has(division) ? true : "legendonly",
      x: divisionRows.map(row => row[chartConfig.x_field]),
      y: divisionRows.map(row => numeric(row[chartConfig.y_field])),
      customdata: divisionRows.map(row => [
        numeric(row.num_basho),
        numeric(row.frequency),
        numeric(row.stdev_persistence)
      ]),
      hovertemplate:
        "Date=%{x}<br>" +
        "Division=%{fullData.name}<br>" +
        "Mean persistence=%{y:.6f}<br>" +
        "Num basho=%{customdata[0]}<br>" +
        "Frequency=%{customdata[1]}<br>" +
        "Stdev=%{customdata[2]:.6f}<extra></extra>"
    };
  });
}

function layoutFor(pageConfig, rows) {
  const chartConfig = pageConfig.chart;
  return {
    title: null,
    paper_bgcolor: "#081426",
    plot_bgcolor: "#0d1e36",
    font: { color: "#f3f7ff" },
    xaxis: {
      title: chartConfig.x_label,
      type: chartConfig.x_type,
      categoryorder: "array",
      categoryarray: orderedDates(rows),
      tickangle: chartConfig.x_tickangle,
      automargin: true
    },
    yaxis: {
      title: chartConfig.y_label,
      range: [chartConfig.y_min, chartConfig.y_max],
      tickformat: chartConfig.y_tickformat
    },
    hovermode: "closest",
    legend: {
      title: { text: chartConfig.legend_title },
      orientation: "v",
      yanchor: "top",
      y: 1,
      xanchor: "left",
      x: 1.02,
      itemclick: "toggle",
      itemdoubleclick: false
    },
    margin: { l: 70, r: 150, t: 40, b: 90 }
  };
}

function isolateTrace(curveNumber) {
  const target = chart.data[curveNumber];
  if (!target) return;
  const visibility = chart.data.map((trace, index) =>
    index === curveNumber ? true : "legendonly"
  );
  Plotly.restyle(chart, { visible: visibility });
}

async function initialise() {
  const pageConfig = await fetch("data/page.json").then(response => response.json());
  await fetch("data/metadata.json").then(response => response.json());
  const source = pageConfig.data_sources[0];
  const rows = await fetch(`data/${source.data}`)
    .then(response => response.text())
    .then(parseCsv);

  chartTitle.textContent = source.label || pageConfig.title;
  chartSubtitle.textContent = pageConfig.subtitle || "";

  Plotly.newPlot(
    chart,
    tracesForRows(pageConfig, rows),
    layoutFor(pageConfig, rows),
    { responsive: true, displaylogo: false }
  ).then(() => {
    if (chart.removeAllListeners) {
      chart.removeAllListeners("plotly_legenddoubleclick");
    }
    chart.on("plotly_legenddoubleclick", event => {
      isolateTrace(event.curveNumber);
      return false;
    });
    Plotly.Plots.resize(chart);
  });
}

window.addEventListener("resize", () => Plotly.Plots.resize(chart));
initialise();
"""


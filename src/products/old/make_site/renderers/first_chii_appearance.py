"""First Chii Appearance page renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path

from ..classes import Page


def write_first_chii_appearance_page(
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
            FIRST_CHII_APPEARANCE_JS,
            "</script>",
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


FIRST_CHII_APPEARANCE_JS = r"""
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

function monthIndex(row, chartConfig) {
  return numeric(row[chartConfig.y_field]);
}

function monthIndexToLabel(monthIndex, chartConfig) {
  const totalMonths = chartConfig.base_month - 1 + monthIndex;
  const year = chartConfig.base_year + Math.floor(totalMonths / 12);
  const month = (totalMonths % 12) + 1;
  return `${String(year).padStart(4, "0")}/${String(month).padStart(2, "0")}`;
}

function rowsByOrdinal(rows, chartConfig) {
  return [...rows].sort((a, b) =>
    numeric(a[chartConfig.x_order_field]) - numeric(b[chartConfig.x_order_field])
  );
}

function sparseTickText(labels, maxLabels) {
  const step = Math.max(1, Math.ceil(labels.length / maxLabels));
  return labels.map((label, index) => index % step === 0 ? label : "");
}

function yTicks(maxMonthIndex, chartConfig) {
  const tickVals = [];
  const step = 24;
  for (let value = 0; value <= maxMonthIndex; value += step) {
    tickVals.push(value);
  }
  if (!tickVals.includes(maxMonthIndex)) {
    tickVals.push(maxMonthIndex);
  }
  return {
    values: tickVals,
    labels: tickVals.map(value => monthIndexToLabel(value, chartConfig))
  };
}

function traceForRows(pageConfig, rows) {
  const chartConfig = pageConfig.chart;
  const orderedRows = rowsByOrdinal(rows, chartConfig);
  return {
    type: "bar",
    x: orderedRows.map(row => row[chartConfig.x_field]),
    y: orderedRows.map(row => monthIndex(row, chartConfig)),
    customdata: orderedRows.map(row => [
      numeric(row[chartConfig.x_order_field]),
      numeric(row[chartConfig.y_year_field]),
      numeric(row[chartConfig.y_month_field])
    ]),
    hovertemplate:
      "Chii=%{x}<br>" +
      "Ordinal=%{customdata[0]}<br>" +
      "First appearance=%{customdata[1]:04d}/%{customdata[2]:02d}<extra></extra>"
  };
}

function layoutFor(pageConfig, rows, trace) {
  const chartConfig = pageConfig.chart;
  const xLabels = trace.x;
  const maxY = Math.max(...trace.y, 0);
  const ticks = yTicks(maxY, chartConfig);
  return {
    title: null,
    paper_bgcolor: "#081426",
    plot_bgcolor: "#0d1e36",
    font: { color: "#f3f7ff" },
    xaxis: {
      title: chartConfig.x_label,
      type: chartConfig.x_type,
      categoryorder: "array",
      categoryarray: xLabels,
      tickvals: xLabels,
      ticktext: sparseTickText(xLabels, chartConfig.max_x_tick_labels),
      tickangle: chartConfig.x_tickangle,
      automargin: true
    },
    yaxis: {
      title: chartConfig.y_label,
      range: [0, maxY],
      tickmode: "array",
      tickvals: ticks.values,
      ticktext: ticks.labels,
      automargin: true
    },
    hovermode: "closest",
    showlegend: false,
    margin: { l: 90, r: 30, t: 40, b: 120 }
  };
}

async function initialise() {
  const pageConfig = await fetch("data/page.json").then(response => response.json());
  await fetch("data/metadata.json").then(response => response.json());
  const source = pageConfig.data_sources[0];
  const rows = await fetch(`data/${source.data}`)
    .then(response => response.text())
    .then(parseCsv);
  const trace = traceForRows(pageConfig, rows);

  chartTitle.textContent = source.label || pageConfig.title;
  chartSubtitle.textContent = pageConfig.subtitle || "";

  Plotly.newPlot(
    chart,
    [trace],
    layoutFor(pageConfig, rows, trace),
    { responsive: true, displaylogo: false }
  ).then(() => Plotly.Plots.resize(chart));
}

window.addEventListener("resize", () => Plotly.Plots.resize(chart));
initialise();
"""

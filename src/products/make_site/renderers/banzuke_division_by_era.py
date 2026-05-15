"""Banzuke Division by Era page renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path

from ..classes import Page


def write_banzuke_division_by_era_page(
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
            BANZUKE_DIVISION_BY_ERA_JS,
            "</script>",
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


BANZUKE_DIVISION_BY_ERA_JS = r"""
const chart = document.getElementById("chart");
const chartTitle = document.getElementById("chart-title");
const chartSubtitle = document.getElementById("chart-subtitle");
let legendClickTimer = null;
let legendClickCurve = null;

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

function tracesForRows(pageConfig, rows) {
  const chartConfig = pageConfig.chart;
  const stackOrder = chartConfig.stack_order || [...new Set(rows.map(row => row[chartConfig.group_field]))];
  const colours = chartConfig.division_colours || {};
  return stackOrder.map(division => {
    const divisionRows = rows.filter(row => row[chartConfig.group_field] === division);
    return {
      type: "bar",
      name: division,
      x: divisionRows.map(row => row[chartConfig.x_field]),
      y: divisionRows.map(row => numeric(row[chartConfig.y_field])),
      marker: { color: colours[division] },
      customdata: divisionRows.map(row => numeric(row.total_average)),
      hovertemplate:
        "Division=%{fullData.name}<br>" +
        "Era=%{x}<br>" +
        "Average rikishi per basho=%{y:.2f}<br>" +
        "Total average=%{customdata:.2f}<extra></extra>"
    };
  });
}

function layoutFor(pageConfig, rows) {
  const chartConfig = pageConfig.chart;
  const xValues = chartConfig.x_order || [...new Set(rows.map(row => row[chartConfig.x_field]))];
  return {
    title: null,
    barmode: chartConfig.barmode,
    paper_bgcolor: "#081426",
    plot_bgcolor: "#0d1e36",
    font: { color: "#f3f7ff" },
    xaxis: {
      title: chartConfig.x_label,
      type: chartConfig.x_type,
      categoryorder: "array",
      categoryarray: xValues,
      tickangle: chartConfig.x_tickangle,
      automargin: true
    },
    yaxis: {
      title: chartConfig.y_label,
      rangemode: "tozero",
      automargin: true
    },
    hovermode: "closest",
    legend: {
      title: { text: chartConfig.legend_title },
      orientation: "v",
      yanchor: "top",
      y: 1,
      xanchor: "left",
      x: 1.02,
      traceorder: "reversed",
      itemclick: false,
      itemdoubleclick: false
    },
    margin: { l: 80, r: 170, t: 40, b: 90 }
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

function toggleTrace(curveNumber) {
  const target = chart.data[curveNumber];
  if (!target) return;
  const nextVisibility = target.visible === true || target.visible === undefined
    ? "legendonly"
    : true;
  Plotly.restyle(chart, { visible: nextVisibility }, [curveNumber]);
}

function handleLegendClick(event) {
  const curveNumber = event.curveNumber;
  if (legendClickTimer && legendClickCurve === curveNumber) {
    window.clearTimeout(legendClickTimer);
    legendClickTimer = null;
    legendClickCurve = null;
    isolateTrace(curveNumber);
    return false;
  }

  if (legendClickTimer) {
    window.clearTimeout(legendClickTimer);
    toggleTrace(legendClickCurve);
  }

  legendClickCurve = curveNumber;
  legendClickTimer = window.setTimeout(() => {
    toggleTrace(curveNumber);
    legendClickTimer = null;
    legendClickCurve = null;
  }, 275);
  return false;
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
      chart.removeAllListeners("plotly_legendclick");
      chart.removeAllListeners("plotly_legenddoubleclick");
    }
    chart.on("plotly_legendclick", handleLegendClick);
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

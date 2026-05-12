"""Rank at Retirement page renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path

from ..classes import Page


def write_rank_at_retirement_page(page: Page, target_path: Path) -> None:
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<link rel="icon" type="image/x-icon" href="../Sumo/meep.png">',
            f"<title>{escape(page.title)}</title>",
            "<style>",
            ":root { color-scheme: dark; --site-bg: #07142d; --site-panel: #0d1f47; --site-panel-strong: #132b5c; --site-text: #ffffff; --site-muted: #c9d4ee; --site-line: #7f95c0; --site-line-soft: rgba(127, 149, 192, 0.55); }",
            "* { box-sizing: border-box; }",
            "html, body { min-height: 100%; }",
            "body { min-width: 320px; min-height: 100vh; margin: 0; padding: 20px; overflow: hidden; background: var(--site-bg); color: var(--site-text); font-family: Arial, Helvetica, sans-serif; line-height: 1.35; }",
            ".tool-shell { height: calc(100vh - 40px); display: flex; flex-direction: column; border: 1px solid var(--site-line); background: var(--site-panel); }",
            ".tool-title-bar { flex: 0 0 auto; padding: 12px 16px; border-bottom: 1px solid var(--site-line); background: var(--site-panel-strong); font-size: 1.25rem; font-weight: 700; }",
            ".tool-content { flex: 1 1 auto; min-height: 0; padding: 12px; display: flex; flex-direction: column; }",
            ".chart-panel { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; border: 1px solid var(--site-line-soft); background: rgba(255, 255, 255, 0.025); }",
            ".chart-header { flex: 0 0 auto; padding: 10px 12px 0; }",
            "#view-title { margin: 0; font-size: 1.05rem; font-weight: 700; }",
            "#chart { flex: 1 1 auto; min-width: 0; min-height: 280px; }",
            ".note-panel { flex: 0 0 auto; padding: 10px 12px 12px; color: var(--site-muted); font-size: 0.92rem; }",
            ".note-panel a { color: #bcd3ff; }",
            "</style>",
            '<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>',
            "</head>",
            "<body>",
            '<div class="tool-shell">',
            f'<div class="tool-title-bar">{escape(page.title)}</div>',
            '<main class="tool-content">',
            '<div class="chart-panel">',
            '<div class="chart-header"><h2 id="view-title"></h2></div>',
            '<div id="chart"></div>',
            '<div id="note-panel" class="note-panel"></div>',
            "</div>",
            "</main>",
            "</div>",
            "<script>",
            RANK_AT_RETIREMENT_JS,
            "</script>",
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


RANK_AT_RETIREMENT_JS = r"""
const viewTitle = document.getElementById("view-title");
const chart = document.getElementById("chart");
const notePanel = document.getElementById("note-panel");

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

async function initialise() {
  const pageConfig = await fetch("data/page.json").then(response => response.json());
  const source = pageConfig.data_sources[0];
  const rows = await fetch(`data/${source.data}`)
    .then(response => response.text())
    .then(parseCsv);
  viewTitle.textContent = source.label;
  renderChart(pageConfig, rows);
  renderNotes(pageConfig);
}

function renderChart(pageConfig, rows) {
  const order = pageConfig.chart.rank_group_order;
  const rowByGroup = new Map(rows.map(row => [row.rank_group, row]));
  const trace = {
    x: order,
    y: order.map(group => numeric(rowByGroup.get(group)?.count || 0)),
    type: "bar",
    name: "Retired rikishi"
  };
  const layout = {
    title: null,
    paper_bgcolor: "#081426",
    plot_bgcolor: "#0d1e36",
    font: { color: "#f3f7ff" },
    xaxis: { title: pageConfig.chart.x_label, categoryorder: "array", categoryarray: order },
    yaxis: { title: pageConfig.chart.y_label, rangemode: "tozero" },
    margin: { l: 80, r: 30, t: 40, b: 70 }
  };
  Plotly.newPlot(chart, [trace], layout, { responsive: true, displaylogo: false });
}

function renderNotes(pageConfig) {
  const notes = (pageConfig.notes || [])
    .filter(note => note.placement === "below_chart")
    .map(note => note.notes)
    .join("<p></p>");
  notePanel.innerHTML = notes ? `<p>${notes}</p>` : "";
  notePanel.querySelectorAll("a").forEach(link => {
    if (isExternalLink(link.href)) {
      link.target = "_blank";
      link.rel = "noopener";
    }
  });
}

function isExternalLink(href) {
  try {
    return new URL(href).origin !== window.location.origin;
  } catch {
    return false;
  }
}

initialise();
"""



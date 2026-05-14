"""Career Length page renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path

from ..classes import Page


def write_career_length_page(
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
            ".tool-content-inner { width: 100%; height: 100%; min-height: 0; display: flex; flex-direction: column; }",
            ".chart-header { flex: 0 0 auto; padding: 0; }",
            "#view-title { margin: 0 0 10px; font-size: 1.05rem; font-weight: 700; text-align: center; }",
            "#chart { flex: 1 1 auto; width: 100%; min-width: 0; min-height: 280px; }",
            "#table-wrap { flex: 1 1 auto; min-height: 0; overflow: auto; padding: 0; }",
            "#table-wrap table { margin: 0 auto; }",
            "#table-wrap .shikona { text-align: left; }",
            "th { position: sticky; top: 0; z-index: 1; }",
            ".note-panel { flex: 0 0 auto; }",
            "[hidden] { display: none !important; }",
            "</style>",
            '<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>',
            "</head>",
            "<body>",
            '<div class="tool-shell">',
            '<header class="tool-title-bar">',
            f"<h1>{escape(page.title)}</h1>",
            f"<p>{escape(page.summary)}</p>",
            "</header>",
            '<div class="tool-layout">',
            '<aside class="tool-options">',
            "<h2>Options</h2>",
            '<div class="control-group">',
            '<div class="control-label" id="view-label">View</div>',
            '<div id="view-options" class="radio-group" role="radiogroup" aria-labelledby="view-label"></div>',
            "</div>",
            "</aside>",
            '<main class="tool-content">',
            '<div class="tool-content-inner">',
            '<div class="chart-header"><h2 id="view-title"></h2></div>',
            '<div id="chart"></div>',
            '<div id="table-wrap" class="table-wrap" hidden></div>',
            '<div id="note-panel" class="note-panel"></div>',
            "</div>",
            "</main>",
            "</div>",
            "</div>",
            "<script>",
            CAREER_LENGTH_JS,
            "</script>",
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


CAREER_LENGTH_JS = r"""
const viewOptions = document.getElementById("view-options");
const viewTitle = document.getElementById("view-title");
const chart = document.getElementById("chart");
const tableWrap = document.getElementById("table-wrap");
const notePanel = document.getElementById("note-panel");
let pageConfig;

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

function activeSource() {
  return pageConfig.data_sources.find(source => source.id === activeView());
}

function activeView() {
  return document.querySelector("input[name='career-view']:checked")?.value || pageConfig.default_view;
}

function applyUrlState() {
  const view = new URLSearchParams(window.location.search).get("view");
  if (!view || !pageConfig.data_sources.some(source => source.id === view)) {
    return;
  }
  const input = document.querySelector(`input[name='career-view'][value="${view}"]`);
  if (input) {
    input.checked = true;
  }
}

function currentUrlParams() {
  return { view: activeView() };
}

function replaceUrlState() {
  const url = new URL(window.location.href);
  url.search = new URLSearchParams(currentUrlParams()).toString();
  url.hash = "";
  history.replaceState(null, "", url);
  notifyParentUrlState();
}

function pushUrlState() {
  const url = new URL(window.location.href);
  url.search = new URLSearchParams(currentUrlParams()).toString();
  url.hash = "";
  history.pushState(null, "", url);
  notifyParentUrlState();
}

function notifyParentUrlState() {
  if (window.parent === window) return;
  window.parent.postMessage({
    type: "site:url-state",
    page: "career_length",
    params: currentUrlParams()
  }, "*");
}

function baseLayout(yTitle) {
  return {
    title: null,
    paper_bgcolor: "#081426",
    plot_bgcolor: "#0d1e36",
    font: { color: "#f3f7ff" },
    xaxis: { title: pageConfig.chart.x_label, rangemode: "tozero" },
    yaxis: { title: yTitle, rangemode: "tozero" },
    hovermode: "closest",
    legend: { orientation: "v" },
    margin: { l: 70, r: 30, t: 40, b: 70 }
  };
}

function showNotes() {
  const selectedView = activeView();
  const notes = (pageConfig.notes || [])
    .filter(note => note.placement === "below_chart")
    .filter(note => noteIsVisibleForView(note, selectedView))
    .map(note => note.notes);
  notePanel.innerHTML = notes.length ? `
    <h3>Notes</h3>
    <ol>
      ${notes.map(note => `<li>${note}</li>`).join("")}
    </ol>
  ` : "";
  wireNoteLinks();
}

function noteIsVisibleForView(note, selectedView) {
  const noteFor = note.note_for || note.noteFor || "all";
  const modes = noteFor.split(/\s+/);
  return modes.includes("all") || modes.includes(selectedView);
}

function showChart() {
  chart.hidden = false;
  tableWrap.hidden = true;
  tableWrap.innerHTML = "";
}

function showTable() {
  chart.hidden = true;
  tableWrap.hidden = false;
  Plotly.purge(chart);
}

async function loadRows(source) {
  const text = await fetch(`data/${source.data}`).then(response => response.text());
  return parseCsv(text);
}

function renderDistribution(rows) {
  showChart();
  const traces = [
    {
      x: rows.map(row => numeric(row.nearest_years)),
      y: rows.map(row => numeric(row.retired_count)),
      name: "Retired",
      type: "bar"
    },
    {
      x: rows.map(row => numeric(row.nearest_years)),
      y: rows.map(row => numeric(row.active_count)),
      name: "Active",
      type: "bar"
    }
  ];
  const layout = baseLayout("Rikishi count");
  layout.barmode = "stack";
  layout.legend = { orientation: "v", x: 1.02, xanchor: "left", y: 1, yanchor: "top" };
  layout.margin.r = 120;
  Plotly.newPlot(chart, traces, layout, { responsive: true, displaylogo: false })
    .then(() => Plotly.Plots.resize(chart));
}

function renderLine(rows, yField, yTitle, options = {}) {
  showChart();
  const trace = {
    x: rows.map(row => numeric(row.nearest_years)),
    y: rows.map(row => numeric(row[yField])),
    type: "bar",
    name: yTitle
  };
  const layout = baseLayout(yTitle);
  if (yField.includes("probability")) {
    layout.yaxis.tickformat = ".0%";
    layout.yaxis.range = [0, 1];
  }
  if (options.yRange) {
    layout.yaxis.range = options.yRange;
  }
  Plotly.newPlot(chart, [trace], layout, { responsive: true, displaylogo: false })
    .then(() => Plotly.Plots.resize(chart));
}

function renderLongest(rows) {
  showTable();
  viewTitle.textContent = "Longest Career";
  const columns = [
    ["shikona", "Shikona", "shikona"],
    ["first_appearance", "First"],
    ["last_appearance", "Last"],
    ["participation_years", "Years"],
    ["gap_basho_count", "Bg"],
    ["active", "Active"]
  ];
  const head = `<tr>${columns.map(([, label, className = ""]) => `<th class="${className}">${label}</th>`).join("")}</tr>`;
  const body = rows.map(row => `<tr>${columns.map(([key, , className = ""]) => {
    const value = formatTableValue(row, key);
    return `<td class="${className}">${value}</td>`;
  }).join("")}</tr>`).join("");
  tableWrap.innerHTML = `<table><thead>${head}</thead><tbody>${body}</tbody></table>`;
  wireRikishiLinks(tableWrap);
}

function formatTableValue(row, key) {
  if (key === "participation_years") return numeric(row[key]).toFixed(2);
  if (key === "active") return row[key] === "True" ? "&#10003;" : "";
  if (key === "shikona") return rikishiAnchor(row);
  return row[key];
}

function rikishiAnchor(row) {
  const rikishiId = encodeURIComponent(row.rikishi_id);
  const shikona = escapeHtml(row.shikona);
  const graphShikona = encodeURIComponent(row.graph_shikona || row.shikona);
  return `<a class="rikishi-link" href="https://sumodb.sumogames.de/Rikishi.aspx?r=${rikishiId}" data-rikishi-id="${rikishiId}" data-graph-shikona="${graphShikona}" title="Click: SumoDB. Alt-click: Gaspode-san.">${shikona}</a>`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  }[char]));
}

function wireRikishiLinks(scope) {
  scope.querySelectorAll(".rikishi-link").forEach(link => {
    if (link.dataset.linkWired === "true") return;
    link.dataset.linkWired = "true";
    let suppressNextClick = false;
    link.addEventListener("mousedown", event => {
      if (!event.altKey || event.button !== 0) return;
      event.preventDefault();
      event.stopPropagation();
      suppressNextClick = true;
      openShikonaTarget(`http://www.661.org.uk/cgi-bin/index.py?graph=any&new_rik=&r_${link.dataset.graphShikona}=${link.dataset.graphShikona}&graph_type=by_time`);
    });
    link.addEventListener("click", event => {
      event.preventDefault();
      if (suppressNextClick) {
        suppressNextClick = false;
        return;
      }
      openShikonaTarget(`https://sumodb.sumogames.de/Rikishi.aspx?r=${link.dataset.rikishiId}`);
    });
  });
}

function wireNoteLinks() {
  notePanel.querySelectorAll("a").forEach(link => {
    const rikishiId = rikishiIdFromSumoDbLink(link.href);
    if (rikishiId) {
      link.classList.add("rikishi-link");
      link.dataset.rikishiId = encodeURIComponent(rikishiId);
      link.dataset.graphShikona = encodeURIComponent(link.textContent.trim());
      link.title = "Click: SumoDB. Alt-click: Gaspode-san.";
      return;
    }
    if (isExternalLink(link.href)) {
      link.target = "_blank";
      link.rel = "noopener";
    }
  });
  wireRikishiLinks(notePanel);
}

function rikishiIdFromSumoDbLink(href) {
  try {
    const url = new URL(href);
    if (url.hostname !== "sumodb.sumogames.de") return "";
    if (!url.pathname.toLowerCase().endsWith("/rikishi.aspx")) return "";
    return url.searchParams.get("r") || "";
  } catch {
    return "";
  }
}

function isExternalLink(href) {
  try {
    return new URL(href).origin !== window.location.origin;
  } catch {
    return false;
  }
}

function openShikonaTarget(url) {
  const opened = window.open(url, "_blank", "noopener");
  if (opened) opened.focus();
}

async function renderActiveView() {
  const source = activeSource();
  viewTitle.textContent = source.label;
  const rows = await loadRows(source);
  if (source.id === "distribution") renderDistribution(rows);
  if (source.id === "pmf") renderLine(rows, "probability", "Probability", { yRange: [0, 0.2] });
  if (source.id === "cdf") renderLine(rows, "cumulative_probability", "Cumulative probability");
  if (source.id === "survival") renderLine(rows, "survival_probability", "Survival probability");
  if (source.id === "longest") renderLongest(rows);
  showNotes();
}

async function initialise() {
  pageConfig = await fetch("data/page.json").then(response => response.json());
  const viewControl = pageConfig.controls.find(control => control.id === "view");
  for (const value of viewControl.values) {
    const label = document.createElement("label");
    label.className = "radio-option";
    const input = document.createElement("input");
    input.type = "radio";
    input.name = "career-view";
    input.value = value.value;
    input.checked = value.value === viewControl.default;
    const text = document.createElement("span");
    text.textContent = value.label;
    label.append(input, text);
    viewOptions.appendChild(label);
  }
  applyUrlState();
  await renderActiveView();
  replaceUrlState();
}

window.addEventListener("resize", () => Plotly.Plots.resize(chart));
viewOptions.addEventListener("change", async () => {
  await renderActiveView();
  pushUrlState();
});
initialise();
"""



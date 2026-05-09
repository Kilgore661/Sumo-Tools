"""HTML rendering helpers for the static site builder."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Mapping

from .classes import DataRef, NavigationTree, Page, Site, SiteBuildConfig, ViewRef
from .classes.page_parts import CustomView
from .routes import PageRoute, html_href, route_href


SHELL_ASSET_VERSION = "20260506-no-title-bar-full-height"


def write_site_index(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
) -> None:
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<link rel="icon" type="image/x-icon" href="../Sumo/meep.png">',
            '<link rel="stylesheet" href="common/files/site-wide.css">',
            f'<link rel="stylesheet" href="site-shell.css?v={SHELL_ASSET_VERSION}">',
            f"<title>{escape(site.title)}</title>",
            "</head>",
            "<body>",
            '<div class="site-shell">',
            '<aside class="site-nav" aria-label="Site navigation">',
            '<header class="site-brand">',
            f'<div class="site-name">{escape(site.title)}</div>',
            '<div class="site-status">Provisional map</div>',
            "</header>",
            render_navigation(site.navigation, config.base_route, page_routes),
            "</aside>",
            '<main class="site-main">',
            '<section id="welcome-panel" class="welcome-panel"><p>Hello World!</p></section>',
            '<section id="frame-panel" class="frame-panel" hidden>',
            '<iframe id="content-frame" title="Selected site page"></iframe>',
            "</section>",
            "</main>",
            "</div>",
            f'<script src="site-shell.js?v={SHELL_ASSET_VERSION}"></script>',
            "</body>",
            "</html>",
            "",
        )
    )
    target_path = config.output_root / "index.html"
    target_path.write_text(html, encoding="utf-8")


def render_navigation(
    node: NavigationTree,
    base_route: str,
    page_routes: Mapping[str, PageRoute],
) -> str:
    children = "".join(
        render_navigation_node(child, base_route, page_routes) for child in node.children
    )
    return f'<ol class="nav-tree">{children}</ol>'


def render_navigation_node(
    node: NavigationTree,
    base_route: str,
    page_routes: Mapping[str, PageRoute],
) -> str:
    label = escape(node.label)
    if node.page_id is None:
        heading = f"<span>{label}</span>"
    else:
        route = page_routes[node.page_id]
        href = html_href(base_route, route.parts)
        frame_href = route_href(route.parts)
        title = escape(route.page.title)
        summary = escape(route.page.summary)
        nav_class = "nav-link"
        if isinstance(route.page.view, CustomView) and route.page.view.kind == "tbd_page":
            nav_class = "nav-link nav-link-tbd"
        heading = (
            f'<a class="{nav_class}" href="{escape(href)}" '
            f'data-frame-src="{escape(frame_href)}" '
            f'data-title="{title}" data-summary="{summary}">{label}</a>'
        )

    if node.children:
        children = "".join(
            render_navigation_node(child, base_route, page_routes)
            for child in node.children
        )
        return f"<li>{heading}<ol>{children}</ol></li>"
    return f"<li>{heading}</li>"


def write_plotly_json_page(
    page: Page,
    data: DataRef,
    template: str,
    config: DataRef,
    target_path: Path,
) -> None:
    html = template.format(
        title=escape(page.title),
        data_path=data.output_path.as_posix(),
        config_path=config.output_path.as_posix(),
    )
    target_path.write_text(html, encoding="utf-8")


def write_custom_page(page: Page, kind: str, target_path: Path) -> None:
    if kind == "standing_win_probability":
        write_standing_win_probability_page(page, target_path)
        return
    if kind == "career_length":
        write_career_length_page(page, target_path)
        return
    if kind == "rank_at_retirement":
        write_rank_at_retirement_page(page, target_path)
        return
    if kind == "typical_equelo_values":
        write_typical_equelo_values_page(page, target_path)
        return
    if kind == "tbd_page":
        write_tbd_page(page, target_path)
        return

    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<link rel="icon" type="image/x-icon" href="../Sumo/meep.png">',
            f"<title>{escape(page.title)}</title>",
            "</head>",
            "<body>",
            f"<h1>{escape(page.title)}</h1>",
            f"<p>{escape(page.summary)}</p>",
            f"<p>Custom view: {escape(kind)}</p>",
            render_options(page),
            render_data_refs(page.data),
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


def write_tbd_page(page: Page, target_path: Path) -> None:
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
            ":root { color-scheme: dark; --site-bg: #07142d; --site-panel: #0d1f47; --site-panel-strong: #132b5c; --site-text: #ffffff; --site-line: #7f95c0; }",
            "* { box-sizing: border-box; }",
            "body { min-height: 100vh; margin: 0; padding: 20px; background: var(--site-bg); color: var(--site-text); font-family: Arial, Helvetica, sans-serif; }",
            ".tool-shell { min-height: calc(100vh - 40px); border: 1px solid var(--site-line); background: var(--site-panel); }",
            ".tool-title-bar { padding: 12px 16px; border-bottom: 1px solid var(--site-line); background: var(--site-panel-strong); font-size: 1.25rem; font-weight: 700; }",
            ".tbd { padding: 18px; font-size: 1.2rem; }",
            "</style>",
            "</head>",
            "<body>",
            '<div class="tool-shell">',
            f'<div class="tool-title-bar">{escape(page.title)}</div>',
            '<main class="tbd">TBD</main>',
            "</div>",
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


def write_career_length_page(page: Page, target_path: Path) -> None:
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
            ":root { color-scheme: dark; --site-bg: #07142d; --site-panel: #0d1f47; --site-panel-strong: #132b5c; --site-text: #ffffff; --site-muted: #c9d4ee; --site-line: #7f95c0; --site-line-soft: rgba(127, 149, 192, 0.55); --control-bg: #d7e0ef; --control-text: #10264f; --accent: #8fb5ff; }",
            "* { box-sizing: border-box; }",
            "html, body { min-height: 100%; }",
            "body { min-width: 320px; min-height: 100vh; margin: 0; padding: 20px; overflow: hidden; background: var(--site-bg); color: var(--site-text); font-family: Arial, Helvetica, sans-serif; line-height: 1.35; }",
            ".tool-shell { height: calc(100vh - 40px); display: flex; flex-direction: column; border: 1px solid var(--site-line); background: var(--site-panel); }",
            ".tool-title-bar { flex: 0 0 auto; padding: 12px 16px; border-bottom: 1px solid var(--site-line); background: var(--site-panel-strong); font-size: 1.25rem; font-weight: 700; }",
            ".tool-layout { flex: 1 1 auto; min-height: 0; display: grid; grid-template-columns: 230px minmax(0, 1fr); }",
            ".tool-options { padding: 14px; border-right: 1px solid var(--site-line); overflow-y: auto; }",
            ".tool-options h2 { margin: 0 0 14px; font-size: 1rem; }",
            ".control-group { margin-bottom: 16px; }",
            ".control-label { display: block; margin-bottom: 6px; font-weight: 700; }",
            ".radio-group { display: grid; gap: 7px; }",
            ".radio-option { display: grid; grid-template-columns: 18px minmax(0, 1fr); gap: 6px; align-items: center; color: var(--site-muted); }",
            ".radio-option input { width: 14px; height: 14px; margin: 0; accent-color: var(--accent); }",
            ".radio-option span { min-width: 0; overflow-wrap: anywhere; }",
            ".radio-option:has(input:checked) { color: var(--site-text); font-weight: 700; }",
            ".tool-content { min-width: 0; min-height: 0; padding: 12px; overflow: hidden; }",
            ".tool-content-inner { width: 100%; height: 100%; min-height: 0; display: flex; flex-direction: column; border: 1px solid var(--site-line-soft); background: rgba(255, 255, 255, 0.025); }",
            ".chart-header { flex: 0 0 auto; padding: 10px 12px 0; }",
            "#view-title { margin: 0; font-size: 1.05rem; font-weight: 700; }",
            "#chart { flex: 1 1 auto; min-width: 0; min-height: 280px; }",
            "#table-wrap { flex: 1 1 auto; min-height: 0; overflow: auto; padding: 0 12px 12px; }",
            "table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }",
            "th, td { border-bottom: 1px solid var(--site-line-soft); padding: 6px 8px; text-align: left; white-space: nowrap; }",
            "th { position: sticky; top: 0; z-index: 1; background: var(--site-panel-strong); box-shadow: 0 1px 0 var(--site-line-soft); }",
            ".note-panel { flex: 0 0 auto; padding: 10px 12px 12px; color: var(--site-muted); font-size: 0.92rem; }",
            ".note-panel a { color: #bcd3ff; }",
            ".rikishi-link { color: #bcd3ff; }",
            "[hidden] { display: none !important; }",
            "</style>",
            '<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>',
            "</head>",
            "<body>",
            '<div class="tool-shell">',
            f'<div class="tool-title-bar">{escape(page.title)}</div>',
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
            '<div id="table-wrap" hidden></div>',
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
    .map(note => note.notes)
    .join("<p></p>");
  notePanel.innerHTML = notes ? `<p>${notes}</p>` : "";
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
  Plotly.newPlot(chart, traces, layout, { responsive: true, displaylogo: false });
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
  Plotly.newPlot(chart, [trace], layout, { responsive: true, displaylogo: false });
}

function renderLongest(rows) {
  showTable();
  const columns = [
    ["shikona", "Shikona", "shikona"],
    ["first_appearance", "First"],
    ["last_appearance", "Last"],
    ["participation_years", "Years"],
    ["gap_basho_count", "Bg"],
    ["active", "Active"]
  ];
  const head = `<tr>${columns.map(([, label]) => `<th>${label}</th>`).join("")}</tr>`;
  const body = rows.map(row => `<tr>${columns.map(([key]) => {
    const value = formatTableValue(row, key);
    return `<td>${value}</td>`;
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
  await renderActiveView();
}

viewOptions.addEventListener("change", renderActiveView);
initialise();
"""


def write_typical_equelo_values_page(page: Page, target_path: Path) -> None:
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
            ":root { color-scheme: dark; --site-bg: #07142d; --site-panel: #0d1f47; --site-panel-strong: #132b5c; --site-text: #ffffff; --site-muted: #c9d4ee; --site-line: #7f95c0; --site-line-soft: rgba(127, 149, 192, 0.55); --accent: #8fb5ff; }",
            "* { box-sizing: border-box; }",
            "html, body { min-height: 100%; }",
            "body { min-width: 320px; min-height: 100vh; margin: 0; padding: 20px; overflow: hidden; background: var(--site-bg); color: var(--site-text); font-family: Arial, Helvetica, sans-serif; line-height: 1.35; }",
            ".tool-shell { height: calc(100vh - 40px); display: flex; flex-direction: column; border: 1px solid var(--site-line); background: var(--site-panel); }",
            ".tool-title-bar { flex: 0 0 auto; padding: 12px 16px; border-bottom: 1px solid var(--site-line); background: var(--site-panel-strong); font-size: 1.25rem; font-weight: 700; }",
            ".tool-content { flex: 1 1 auto; min-height: 0; padding: 14px; display: flex; flex-direction: column; gap: 12px; overflow: hidden; }",
            ".table-grid { flex: 1 1 auto; min-height: 0; display: flex; justify-content: center; align-items: flex-start; gap: 42px; overflow: auto; }",
            ".table-section { width: max-content; border: 1px solid var(--site-line-soft); background: rgba(255, 255, 255, 0.025); }",
            ".table-section h2 { margin: 0; padding: 9px 10px; border-bottom: 1px solid var(--site-line-soft); background: var(--site-panel-strong); font-size: 1rem; }",
            "table { width: auto; border-collapse: collapse; font-size: 0.95rem; }",
            "th, td { border-bottom: 1px solid var(--site-line-soft); padding: 6px 10px; text-align: left; white-space: nowrap; }",
            "th { background: rgba(19, 43, 92, 0.65); color: var(--site-muted); font-size: 0.82rem; }",
            "th.rating-heading { text-align: center; }",
            "td.rating { text-align: right; font-variant-numeric: tabular-nums; }",
            ".note-panel { flex: 0 0 auto; color: var(--site-muted); font-size: 0.92rem; }",
            ".note-panel p { margin: 0 0 6px; }",
            ".note-panel a { color: #bcd3ff; }",
            "@media (max-width: 760px) { body { overflow: auto; } .tool-shell { min-height: calc(100vh - 40px); height: auto; } .table-grid { flex-direction: column; align-items: stretch; overflow: visible; } }",
            "</style>",
            "</head>",
            "<body>",
            '<div class="tool-shell">',
            f'<div class="tool-title-bar">{escape(page.title)}</div>',
            '<main class="tool-content">',
            '<div id="table-grid" class="table-grid"></div>',
            '<div id="note-panel" class="note-panel"></div>',
            "</main>",
            "</div>",
            "<script>",
            TYPICAL_EQUELO_VALUES_JS,
            "</script>",
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


TYPICAL_EQUELO_VALUES_JS = r"""
const tableGrid = document.getElementById("table-grid");
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

async function initialise() {
  const pageConfig = await fetch("data/page.json").then(response => response.json());
  const source = pageConfig.data_sources[0];
  const rows = await fetch(`data/${source.data}`)
    .then(response => response.text())
    .then(parseCsv);
  renderTables(pageConfig, rows);
  renderNotes(pageConfig);
}

function renderTables(pageConfig, rows) {
  tableGrid.innerHTML = "";
  for (const tableSpec of pageConfig.tables) {
    const sectionRows = rows
      .filter(row => row.table === tableSpec.source_value)
      .sort((a, b) => Number(a.row_order) - Number(b.row_order));
    const section = document.createElement("section");
    section.className = "table-section";
    section.innerHTML = `
      <h2>${escapeHtml(tableSpec.label)}</h2>
      <table>
        <thead>
          <tr>
            <th>${escapeHtml(columnLabel(pageConfig, "label"))}</th>
            <th class="rating-heading">${escapeHtml(columnLabel(pageConfig, "rating"))}</th>
          </tr>
        </thead>
        <tbody>
          ${sectionRows.map(row => `
            <tr>
              <td>${escapeHtml(row.label)}</td>
              <td class="rating">${formatRating(row.rating)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
    tableGrid.appendChild(section);
  }
}

function columnLabel(pageConfig, id) {
  return (pageConfig.columns || []).find(column => column.id === id)?.label || id;
}

function formatRating(value) {
  const n = Number(value);
  return Number.isFinite(n) ? String(Math.round(n)) : value;
}

function renderNotes(pageConfig) {
  const notes = (pageConfig.notes || [])
    .filter(note => note.placement === "below_table")
    .map(note => note.notes)
    .join("</p><p>");
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

function escapeHtml(value) {
  const span = document.createElement("span");
  span.textContent = value ?? "";
  return span.innerHTML;
}

initialise();
"""


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


def write_standing_win_probability_page(page: Page, target_path: Path) -> None:
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
            ":root { color-scheme: dark; --site-bg: #07142d; --site-panel: #0d1f47; --site-panel-strong: #132b5c; --site-text: #ffffff; --site-muted: #c9d4ee; --site-line: #7f95c0; --site-line-soft: rgba(127, 149, 192, 0.55); --control-bg: #d7e0ef; --control-text: #10264f; --accent: #8fb5ff; }",
            "* { box-sizing: border-box; }",
            "html, body { min-height: 100%; }",
            "body { min-width: 320px; min-height: 100vh; margin: 0; padding: 20px; overflow: hidden; background: var(--site-bg); color: var(--site-text); font-family: Arial, Helvetica, sans-serif; line-height: 1.35; }",
            ".tool-shell { height: calc(100vh - 40px); display: flex; flex-direction: column; border: 1px solid var(--site-line); background: var(--site-panel); }",
            ".tool-title-bar { flex: 0 0 auto; padding: 12px 16px; border-bottom: 1px solid var(--site-line); background: var(--site-panel-strong); font-size: 1.25rem; font-weight: 700; }",
            ".tool-layout { flex: 1 1 auto; min-height: 0; display: grid; grid-template-columns: 230px minmax(0, 1fr); }",
            ".tool-options { padding: 14px; border-right: 1px solid var(--site-line); overflow-y: auto; }",
            ".tool-options h2 { margin: 0 0 14px; font-size: 1rem; }",
            ".control-group { margin-bottom: 16px; }",
            ".control-label { display: block; margin-bottom: 6px; font-weight: 700; }",
            ".checkbox-control { display: flex; align-items: center; gap: 7px; cursor: pointer; }",
            ".checkbox-control input { margin: 0; accent-color: var(--accent); }",
            ".control-disabled { color: var(--site-muted); cursor: default; opacity: 0.65; }",
            "select { width: 100%; min-height: 28px; border: 1px solid #aebddb; border-radius: 4px; background: var(--control-bg); color: var(--control-text); font: inherit; padding: 2px 4px; }",
            "select:focus, input:focus { outline: 1px solid var(--site-muted); outline-offset: 1px; }",
            ".tool-content { min-width: 0; min-height: 0; padding: 12px; overflow: hidden; }",
            ".tool-content-inner { width: 100%; height: 100%; min-height: 0; display: flex; flex-direction: column; border: 1px solid var(--site-line-soft); background: rgba(255, 255, 255, 0.025); }",
            ".chart-header { flex: 0 0 auto; padding: 10px 12px 0; }",
            "#chart-title { margin: 0; font-size: 1.05rem; font-weight: 700; }",
            "#chart { flex: 1 1 auto; min-width: 0; min-height: 0; }",
            "</style>",
            '<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>',
            "</head>",
            "<body>",
            '<div class="tool-shell">',
            f'<div class="tool-title-bar">{escape(page.title)}</div>',
            '<div class="tool-layout">',
            '<aside class="tool-options">',
            "<h2>Options</h2>",
            '<div class="control-group">',
            '<label class="control-label" for="source-select">Source</label>',
            '<select id="source-select"></select>',
            "</div>",
            '<div class="control-group">',
            '<label id="error-toggle-control" class="checkbox-control">',
            '<input id="error-toggle" type="checkbox" checked>',
            "<span>Error bars</span>",
            "</label>",
            "</div>",
            '<div class="control-group">',
            '<label class="control-label" for="division-select">Division</label>',
            '<select id="division-select"></select>',
            "</div>",
            "</aside>",
            '<main class="tool-content">',
            '<div class="tool-content-inner">',
            '<div class="chart-header"><h2 id="chart-title"></h2></div>',
            '<div id="chart"></div>',
            "</div>",
            "</main>",
            "</div>",
            "</div>",
            "<script>",
            STANDING_WIN_PROBABILITY_JS,
            "</script>",
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


STANDING_WIN_PROBABILITY_JS = r"""
const chart = document.getElementById("chart");
const sourceSelect = document.getElementById("source-select");
const divisionSelect = document.getElementById("division-select");
const errorToggle = document.getElementById("error-toggle");
const errorToggleControl = document.getElementById("error-toggle-control");
const chartTitle = document.getElementById("chart-title");
let pageConfig;
let activeRows = [];

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(",");
  return lines.slice(1).map(line => {
    const values = line.split(",");
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index];
    });
    return row;
  });
}

function numeric(value) {
  return Number.parseFloat(value);
}

function divisionForChii(chii) {
  if (chii.startsWith("Ms")) return "Makushita";
  if (chii.startsWith("Sd")) return "Sandanme";
  if (chii.startsWith("Jd")) return "Jonidan";
  if (chii.startsWith("Jk")) return "Jonokuchi";
  if (["Y", "O", "S", "K", "M"].some(prefix => chii.startsWith(prefix))) return "Makuuchi";
  if (chii.startsWith("J")) return "Juryo";
  return "Other";
}

function displayChii(chii) {
  const sanyaku = pageConfig.display.sanyaku;
  if (chii.startsWith("Y")) return sanyaku.includes(chii);
  if (chii.startsWith("O")) return sanyaku.includes(chii);
  if (chii.startsWith("S") && !chii.startsWith("Sd")) return sanyaku.includes(chii);
  if (chii.startsWith("K")) return sanyaku.includes(chii);
  return true;
}

function groupRows(rows) {
  const groups = new Map();
  for (const row of rows) {
    if (!displayChii(row.selected_chii) || !displayChii(row.opponent_chii)) continue;
    if (!groups.has(row.selected_chii)) groups.set(row.selected_chii, []);
    groups.get(row.selected_chii).push(row);
  }
  return Array.from(groups.entries())
    .sort((a, b) => numeric(a[1][0].selected_ordinal) - numeric(b[1][0].selected_ordinal))
    .map(([selected, selectedRows]) => [
      selected,
      selectedRows.sort((a, b) => numeric(a.opponent_ordinal) - numeric(b.opponent_ordinal))
    ]);
}

function sourceConfig() {
  return pageConfig.data_sources.find(source => source.id === sourceSelect.value);
}

function traceForRows(selected, rows, source) {
  const trace = {
    x: rows.map(row => row.opponent_chii),
    y: rows.map(row => numeric(row.p_selected_wins)),
    mode: "lines+markers",
    name: selected,
    type: "scatter",
    visible: selected === pageConfig.default_trace ? true : "legendonly",
    meta: { division: divisionForChii(selected) },
    customdata: rows.map(row => source.id === "observed"
      ? [
          row.selected_chii,
          row.opponent_chii,
          numeric(row.opponent_ordinal),
          numeric(row.n_obs),
          numeric(row.n_selected_wins),
          numeric(row.ci95_lower),
          numeric(row.ci95_upper)
        ]
      : [
          row.selected_chii,
          row.opponent_chii,
          numeric(row.opponent_ordinal),
          numeric(row.selected_rating),
          numeric(row.opponent_rating)
        ]
    )
  };

  if (source.id === "observed") {
    trace.error_y = {
      type: "data",
      symmetric: false,
      array: rows.map(row => numeric(row.ci95_upper) - numeric(row.p_selected_wins)),
      arrayminus: rows.map(row => numeric(row.p_selected_wins) - numeric(row.ci95_lower)),
      visible: errorToggle.checked,
      color: "rgba(68, 140, 240, 0.34)",
      thickness: 1,
      width: 4
    };
    trace.hovertemplate =
      "Selected=%{customdata[0]}<br>" +
      "Opponent=%{customdata[1]}<br>" +
      "P(selected wins)=%{y:.3f}<br>" +
      "CI95=[%{customdata[5]:.3f}, %{customdata[6]:.3f}]<br>" +
      "Wins=%{customdata[4]:,} / %{customdata[3]:,}" +
      "<extra></extra>";
  } else {
    trace.hovertemplate =
      "Selected=%{customdata[0]}<br>" +
      "Opponent=%{customdata[1]}<br>" +
      "P(selected wins)=%{y:.3f}<br>" +
      "Selected rating=%{customdata[3]:.1f}<br>" +
      "Opponent rating=%{customdata[4]:.1f}" +
      "<extra></extra>";
  }

  return trace;
}

function traceInDivision(trace, division) {
  return division === "All" || trace.meta.division === division;
}

function visibilityForDivision(division, traces) {
  let firstVisible = true;
  return traces.map(trace => {
    if (!traceInDivision(trace, division)) return false;
    if (trace.name === pageConfig.default_trace) {
      firstVisible = false;
      return true;
    }
    if (firstVisible) {
      firstVisible = false;
      return true;
    }
    return "legendonly";
  });
}

function visibleCategoryArray() {
  const ordinals = new Map();
  const visibleTraces = chart.data.filter(trace =>
    traceInDivision(trace, divisionSelect.value) &&
    (trace.visible === true || trace.visible === undefined)
  );
  const fallbackTraces = chart.data.filter(trace =>
    traceInDivision(trace, divisionSelect.value) && trace.visible !== false
  );
  const traces = visibleTraces.length ? visibleTraces : fallbackTraces;
  for (const trace of traces) {
    for (let i = 0; i < trace.x.length; i += 1) {
      ordinals.set(trace.x[i], trace.customdata[i][2]);
    }
  }
  return Array.from(ordinals.entries())
    .sort((a, b) => a[1] - b[1])
    .map(([label]) => label);
}

function updateVisibleDomain() {
  Plotly.relayout(chart, {
    "xaxis.categoryarray": visibleCategoryArray(),
    "xaxis.autorange": true
  });
}

function isolateTrace(curveNumber) {
  const target = chart.data[curveNumber];
  if (!target || !traceInDivision(target, divisionSelect.value)) return;
  const visibility = chart.data.map((trace, index) => {
    if (!traceInDivision(trace, divisionSelect.value)) return false;
    return index === curveNumber ? true : "legendonly";
  });
  Plotly.restyle(chart, { visible: visibility }).then(updateVisibleDomain);
}

async function loadSource() {
  const source = sourceConfig();
  chartTitle.textContent = source.label;
  errorToggle.disabled = !source.has_error_bars;
  errorToggle.checked = source.has_error_bars && errorToggle.checked;
  errorToggleControl.classList.toggle("control-disabled", !source.has_error_bars);
  const text = await fetch(`data/${source.data}`).then(response => response.text());
  activeRows = parseCsv(text);
  const traces = groupRows(activeRows).map(([selected, rows]) => traceForRows(selected, rows, source));
  const layout = {
    title: null,
    paper_bgcolor: "#081426",
    plot_bgcolor: "#0d1e36",
    font: { color: "#f3f7ff" },
    xaxis: {
      title: "Opponent sideless chii",
      type: "category",
      categoryorder: "array",
      categoryarray: []
    },
    yaxis: {
      title: pageConfig.y_axis.label,
      range: [pageConfig.y_axis.min, pageConfig.y_axis.max],
      tickformat: pageConfig.y_axis.tickformat
    },
    hovermode: "closest",
    legend: {
      title: { text: "Selected chii" },
      itemclick: "toggle",
      itemdoubleclick: false
    },
    margin: { l: 70, r: 30, t: 70, b: 90 }
  };
  Plotly.newPlot(chart, traces, layout, { responsive: true, displaylogo: false })
    .then(() => {
      if (chart.removeAllListeners) {
        chart.removeAllListeners("plotly_restyle");
        chart.removeAllListeners("plotly_legenddoubleclick");
      }
      chart.on("plotly_restyle", updateVisibleDomain);
      chart.on("plotly_legenddoubleclick", event => {
        isolateTrace(event.curveNumber);
        return false;
      });
      Plotly.restyle(chart, { visible: visibilityForDivision(divisionSelect.value, traces) })
        .then(updateVisibleDomain);
    });
}

async function initialise() {
  pageConfig = await fetch("data/page.json").then(response => response.json());
  const sourceControl = pageConfig.controls.find(control => control.id === "source");
  const divisionControl = pageConfig.controls.find(control => control.id === "division");
  for (const value of sourceControl.values) {
    const option = document.createElement("option");
    option.value = value.value;
    option.textContent = value.label;
    sourceSelect.appendChild(option);
  }
  for (const value of divisionControl.values) {
    const option = document.createElement("option");
    option.value = value.value;
    option.textContent = value.label;
    divisionSelect.appendChild(option);
  }
  sourceSelect.value = sourceControl.default;
  divisionSelect.value = divisionControl.default;
  await loadSource();
}

sourceSelect.addEventListener("change", loadSource);
divisionSelect.addEventListener("change", () => {
  Plotly.restyle(chart, {
    visible: visibilityForDivision(divisionSelect.value, Array.from(chart.data))
  }).then(updateVisibleDomain);
});
errorToggle.addEventListener("change", event => {
  if (!sourceConfig().has_error_bars) return;
  Plotly.restyle(chart, { "error_y.visible": event.target.checked });
});
initialise();
"""


def render_options(page: Page) -> str:
    if page.options is None:
        return ""
    items = "".join(
        f"<li>{escape(option.label)}: {escape(str(option.default))}</li>"
        for option in page.options.options
    )
    return f"<h2>Options</h2><ol>{items}</ol>"


def render_data_refs(data_refs: tuple[DataRef, ...]) -> str:
    items = "".join(
        (
            f'<li><a href="{escape(data_ref.output_path.as_posix())}">'
            f"{escape(data_ref.id)}</a></li>"
        )
        for data_ref in data_refs
    )
    return f"<h2>Data</h2><ol>{items}</ol>"

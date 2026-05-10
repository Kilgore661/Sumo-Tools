"""Experimental PA-manifest runtime skeleton writer."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, is_dataclass
from html import escape
from pathlib import Path
from typing import Any, Mapping

from .classes import NavigationTree, Site, SiteBuildConfig
from .filesystem import copy_file
from .pa_manifest import ACTIVE_PA_MANIFESTS
from .routes import PageRoute, html_href


RUNTIME_DIR = "runtime-skeleton"
RUNTIME_ASSET_VERSION = "20260509-pa-runtime-skeleton"


def write_pa_runtime_skeleton(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    build_stamp: str,
) -> None:
    """Write a parallel shell showing the intended PA-manifest runtime shape."""

    root = config.output_root / RUNTIME_DIR
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    write_manifest_files(root)
    write_runtime_assets(root)
    write_runtime_index(site, config, page_routes, root, build_stamp)
    for page_id, page_route in page_routes.items():
        if page_id in ACTIVE_PA_MANIFESTS:
            write_runtime_page(
                site,
                config,
                page_routes,
                root,
                page_id,
                page_route,
                build_stamp,
            )
            copy_runtime_page_data(root, page_route)


def copy_runtime_page_data(root: Path, page_route: PageRoute) -> None:
    for data_ref in page_route.page.data:
        target_path = root / Path(data_ref.output_path.as_posix())
        copy_file(data_ref.source_path, target_path)


def write_manifest_files(root: Path) -> None:
    manifests_dir = root / "manifests"
    manifests_dir.mkdir()
    index: dict[str, str] = {}
    for page_id, manifest in sorted(ACTIVE_PA_MANIFESTS.items()):
        manifest_path = manifests_dir / f"{page_id}.json"
        manifest_path.write_text(
            json.dumps(tagged_manifest(page_id, manifest), indent=2),
            encoding="utf-8",
        )
        index[page_id] = f"manifests/{page_id}.json"
    (root / "manifest-index.json").write_text(
        json.dumps(index, indent=2),
        encoding="utf-8",
    )


def tagged_manifest(page_id: str, manifest: Any) -> dict[str, Any]:
    manifest.validate()
    return {
        "tag": page_id,
        "manifest_class": type(manifest).__name__,
        "manifest": dataclass_to_plain(manifest),
    }


def dataclass_to_plain(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, tuple):
        return [dataclass_to_plain(item) for item in value]
    if isinstance(value, list):
        return [dataclass_to_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: dataclass_to_plain(item) for key, item in value.items()}
    return value


def write_runtime_assets(root: Path) -> None:
    css = "\n".join(
        (
            ":root { color-scheme: dark; --bg: #081426; --panel: #10264f; --line: #7892c4; --text: #f5f8ff; --muted: #c4cee3; }",
            "* { box-sizing: border-box; }",
            "html, body { min-height: 100%; }",
            "body { margin: 0; background: var(--bg); color: var(--text); font-family: Arial, Helvetica, sans-serif; }",
            ".runtime-shell { min-height: 100vh; display: grid; grid-template-columns: 310px minmax(0, 1fr); }",
            ".runtime-nav { border-right: 1px solid var(--line); padding: 14px; background: #07142d; overflow: auto; }",
            ".runtime-main { min-width: 0; display: grid; grid-template-rows: auto minmax(0, 1fr); }",
            ".runtime-header { border-bottom: 1px solid var(--line); padding: 14px 16px; background: var(--panel); }",
            ".runtime-header h1 { margin: 0; font-size: 1.2rem; }",
            ".runtime-content { min-height: 0; display: grid; grid-template-columns: 260px minmax(0, 1fr); }",
            ".runtime-options { border-right: 1px solid var(--line); padding: 14px; overflow: auto; }",
            ".runtime-pa { min-width: 0; padding: 14px; overflow: auto; }",
            ".runtime-note { color: var(--muted); }",
            ".control-group { margin-bottom: 16px; }",
            ".control-label { display: block; margin-bottom: 6px; font-weight: 700; }",
            ".radio-group { display: grid; gap: 6px; }",
            ".radio-option, .checkbox-option { display: grid; grid-template-columns: 18px minmax(0, 1fr); gap: 7px; align-items: center; color: var(--muted); }",
            "select { width: 100%; min-height: 30px; border: 1px solid var(--line); border-radius: 4px; background: #dbe5f4; color: #10264f; }",
            ".table-panel { min-width: 0; }",
            ".table-title { margin: 0 0 10px; font-size: 1.05rem; }",
            ".sectioned-table-grid { display: flex; justify-content: center; align-items: flex-start; gap: 36px; overflow: auto; }",
            ".table-section { width: max-content; min-width: 120px; }",
            ".table-section h2 { margin: 0; padding: 8px 10px; border: 1px solid var(--line); border-bottom: 0; background: var(--panel); font-size: 1rem; }",
            ".table-wrap { max-height: calc(100vh - 150px); overflow: auto; border: 1px solid var(--line); }",
            "table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }",
            "th, td { padding: 6px 8px; border-bottom: 1px solid rgba(120, 146, 196, 0.45); white-space: nowrap; }",
            "thead th { position: sticky; top: 0; z-index: 1; background: var(--panel); color: var(--text); }",
            "th.sortable { cursor: pointer; }",
            "td.right, th.right { text-align: right; }",
            "td.center, th.center { text-align: center; }",
            ".notes-panel { margin-top: 12px; color: var(--muted); font-size: 0.9rem; }",
            ".chart-panel { min-width: 0; }",
            ".chart-title { margin: 0 0 10px; font-size: 1.05rem; }",
            ".bar-chart { min-height: 420px; display: grid; grid-template-columns: 70px minmax(0, 1fr); grid-template-rows: minmax(0, 1fr) auto; gap: 8px 10px; border: 1px solid var(--line); padding: 14px; }",
            ".bar-y-label { writing-mode: vertical-rl; transform: rotate(180deg); align-self: center; justify-self: center; color: var(--muted); font-size: 0.85rem; }",
            ".bar-plot { height: 360px; display: flex; align-items: flex-end; gap: 10px; padding: 8px 0 0; border-left: 1px solid rgba(120, 146, 196, 0.55); border-bottom: 1px solid rgba(120, 146, 196, 0.55); }",
            ".bar-item { flex: 1 1 0; min-width: 34px; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 6px; }",
            ".bar-value { color: var(--muted); font-size: 0.78rem; }",
            ".bar { width: 100%; max-width: 54px; min-height: 1px; background: #8fb5ff; border: 1px solid rgba(255,255,255,0.55); }",
            ".bar-label { color: var(--text); font-weight: 700; }",
            ".bar-x-label { grid-column: 2; justify-self: center; color: var(--muted); font-size: 0.85rem; }",
            ".line-chart-wrap { border: 1px solid var(--line); padding: 10px; overflow: auto; }",
            ".line-chart { width: 100%; min-width: 860px; height: 520px; display: block; }",
            ".axis-line, .grid-line { stroke: rgba(196, 206, 227, 0.45); stroke-width: 1; }",
            ".grid-line { stroke-dasharray: 4 5; }",
            ".trace-line { fill: none; stroke-width: 2.2; }",
            ".trace-point { stroke: #07142d; stroke-width: 1; }",
            ".error-bar { stroke: rgba(245, 248, 255, 0.35); stroke-width: 1; }",
            ".axis-label, .tick-label { fill: var(--muted); font-size: 12px; }",
            ".chart-legend { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 8px 14px; color: var(--muted); font-size: 0.85rem; }",
            ".legend-swatch { display: inline-block; width: 20px; height: 3px; margin-right: 6px; vertical-align: middle; }",
            "a { color: #c7dcff; }",
        )
    )
    (root / "pa-runtime.css").write_text(css + "\n", encoding="utf-8")
    (root / "pa-runtime.js").write_text(PA_RUNTIME_JS, encoding="utf-8")


def write_runtime_index(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    root: Path,
    build_stamp: str,
) -> None:
    write_runtime_shell_html(
        site=site,
        config=config,
        page_routes=page_routes,
        target_path=root / "index.html",
        selected_page_id="",
        asset_prefix="",
        build_stamp=build_stamp,
    )


def write_runtime_page(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    root: Path,
    page_id: str,
    page_route: PageRoute,
    build_stamp: str,
) -> None:
    target_path = root.joinpath(*page_route.parts, "index.html")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    asset_prefix = "../" * len(page_route.parts)
    write_runtime_shell_html(
        site=site,
        config=config,
        page_routes=page_routes,
        target_path=target_path,
        selected_page_id=page_id,
        asset_prefix=asset_prefix,
        build_stamp=build_stamp,
    )


def write_runtime_shell_html(
    *,
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    target_path: Path,
    selected_page_id: str,
    asset_prefix: str,
    build_stamp: str,
) -> None:
    title = site.pages.pages[selected_page_id].title if selected_page_id else site.title
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(title)}</title>",
            f'<link rel="stylesheet" href="{asset_prefix}pa-runtime.css?v={RUNTIME_ASSET_VERSION}">',
            "</head>",
            f'<body data-selected-page-id="{escape(selected_page_id)}">',
            '<div class="runtime-shell">',
            '<aside id="site-nav" class="runtime-nav" aria-label="Site navigation">',
            f"<h2>{escape(site.title)}</h2>",
            f'<p class="runtime-note">{escape(build_stamp)}</p>',
            render_runtime_navigation(site.navigation, config, page_routes),
            "</aside>",
            '<main class="runtime-main">',
            '<header class="runtime-header">',
            '<h1 id="page-heading"></h1>',
            '<p id="page-summary" class="runtime-note"></p>',
            "</header>",
            '<section class="runtime-content">',
            '<aside id="options-panel" class="runtime-options"></aside>',
            '<section id="pa-panel" class="runtime-pa"></section>',
            "</section>",
            "</main>",
            "</div>",
            f'<script src="{asset_prefix}pa-runtime.js?v={RUNTIME_ASSET_VERSION}"></script>',
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


def render_runtime_navigation(
    node: NavigationTree,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
) -> str:
    children = "".join(
        render_runtime_navigation_node(child, config, page_routes)
        for child in node.children
    )
    return f"<ol>{children}</ol>"


def render_runtime_navigation_node(
    node: NavigationTree,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
) -> str:
    label = escape(node.label)
    if node.page_id is None or node.page_id not in ACTIVE_PA_MANIFESTS:
        heading = f"<span>{label}</span>"
    else:
        route = page_routes[node.page_id]
        href = html_href(f"{config.base_route.rstrip('/')}/{RUNTIME_DIR}", route.parts)
        heading = (
            f'<a href="{escape(href)}" data-page-id="{escape(node.page_id)}">'
            f"{label}</a>"
        )
    children = "".join(
        render_runtime_navigation_node(child, config, page_routes)
        for child in node.children
    )
    if children:
        return f"<li>{heading}<ol>{children}</ol></li>"
    return f"<li>{heading}</li>"


PA_RUNTIME_JS = r"""
const runtimeState = {
  taggedManifest: null,
  optionState: {},
  sort: null,
  rows: [],
  metadata: null
};

async function bootSiteRuntime() {
  const pageId = resolveInitialPageId();
  const manifestIndex = await loadManifestIndex();
  const taggedManifest = await loadTaggedManifest(pageId, manifestIndex);
  const urlState = readUrlState();
  const optionState = resolveOptionState(taggedManifest, urlState);
  runtimeState.taggedManifest = taggedManifest;
  runtimeState.optionState = optionState;
  runtimeState.sort = defaultSortForManifest(taggedManifest?.manifest, optionState);
  applyUrlSortState(taggedManifest?.manifest, urlState);
  normaliseUrlIfNeeded(pageId, taggedManifest, optionState);
  renderPageShell(taggedManifest);
  renderOptionsPanel(taggedManifest, optionState);
  await renderPublishedArtefact(taggedManifest, optionState);
  registerRuntimeListeners(taggedManifest, optionState);
}

function resolveInitialPageId() {
  return document.body.dataset.selectedPageId || "";
}

async function loadManifestIndex() {
  return fetch(rootRelativeUrl("manifest-index.json")).then(response => response.json());
}

async function loadTaggedManifest(pageId, manifestIndex) {
  if (!pageId) return null;
  const manifestPath = manifestIndex[pageId];
  if (!manifestPath) throw new Error(`No PA manifest registered for ${pageId}`);
  return fetch(rootRelativeUrl(manifestPath)).then(response => response.json());
}

function readUrlState() {
  return Object.fromEntries(new URLSearchParams(window.location.search).entries());
}

function applyUrlSortState(manifest, urlState) {
  if (!manifest || !urlState.sort) return;
  const column = columnById(manifest, urlState.sort);
  if (!column || !column.sortable) return;
  runtimeState.sort = {
    column: column.id,
    descending: urlState.desc === "true"
  };
}

function resolveOptionState(taggedManifest, urlState) {
  if (!taggedManifest) return {};
  const options = collectOptions(taggedManifest);
  return Object.fromEntries(options.map(option => [
    option.id,
    coerceOptionValue(option, urlState[option.url_key || option.id] ?? option.default)
  ]));
}

function normaliseUrlIfNeeded(pageId, taggedManifest, optionState) {
  if (!taggedManifest || !pageId) return;
  const url = new URL(window.location.href);
  const params = new URLSearchParams();
  for (const option of collectOptions(taggedManifest)) {
    params.set(option.url_key || option.id, String(optionState[option.id]));
  }
  if (runtimeState.sort) {
    params.set("sort", runtimeState.sort.column);
    params.set("desc", String(runtimeState.sort.descending));
  }
  const next = `${url.pathname}?${params.toString()}${url.hash}`;
  if (`${url.pathname}${url.search}${url.hash}` !== next) {
    history.replaceState(null, "", next);
  }
}

function renderPageShell(taggedManifest) {
  const heading = document.getElementById("page-heading");
  const summary = document.getElementById("page-summary");
  if (!taggedManifest) {
    heading.textContent = "Select a page";
    summary.textContent = "";
    return;
  }
  heading.textContent = taggedManifest.manifest.heading;
  summary.textContent = `${taggedManifest.manifest_class} / ${taggedManifest.manifest.renderer}`;
}

function renderOptionsPanel(taggedManifest, optionState) {
  const panel = document.getElementById("options-panel");
  if (!taggedManifest) {
    panel.innerHTML = "";
    return;
  }
  const options = collectOptions(taggedManifest);
  panel.innerHTML = options.length ? options.map(option => renderOptionControl(option, optionState)).join("") : `<p class="runtime-note">No options.</p>`;
  wireOptionControls(panel, taggedManifest);
}

async function renderPublishedArtefact(taggedManifest, optionState) {
  const panel = document.getElementById("pa-panel");
  if (!taggedManifest) {
    panel.innerHTML = `<p class="runtime-note">Choose a navigation item.</p>`;
    return;
  }
  switch (taggedManifest.manifest_class) {
    case "TablePA":
      return renderTablePA(taggedManifest.manifest, optionState, panel);
    case "ChartPA":
      return renderChartPA(taggedManifest.manifest, optionState, panel);
    case "MultiViewPA":
      return renderMultiViewPA(taggedManifest.manifest, optionState, panel);
    case "EssayPA":
      return renderEssayPA(taggedManifest.manifest, optionState, panel);
    case "ExcludedPA":
      return renderExcludedPA(taggedManifest.manifest, optionState, panel);
    default:
      throw new Error(`Unsupported PA manifest class ${taggedManifest.manifest_class}`);
  }
}

function collectOptions(taggedManifest) {
  const manifest = taggedManifest.manifest;
  if (taggedManifest.manifest_class === "MultiViewPA") {
    return [manifest.view_option];
  }
  return manifest.options || [];
}

async function renderTablePA(manifest, optionState, panel) {
  if (manifest.renderer === "standings_table") {
    return renderStandingsTable(manifest, optionState, panel);
  }
  if (manifest.renderer === "sectioned_table") {
    return renderSectionedTable(manifest, optionState, panel);
  }
  panel.innerHTML = `<pre>${escapeHtml(JSON.stringify({ render: "TablePA", manifest, optionState }, null, 2))}</pre>`;
}

async function renderChartPA(manifest, optionState, panel) {
  if (manifest.renderer === "standing_win_probability_chart") {
    return renderStandingWinProbabilityChart(manifest, optionState, panel);
  }
  const trace = (manifest.traces || [])[0];
  if (trace?.kind === "bar") {
    return renderSimpleBarChart(manifest, optionState, panel);
  }
  panel.innerHTML = `<pre>${escapeHtml(JSON.stringify({ render: "ChartPA", manifest, optionState }, null, 2))}</pre>`;
}

async function renderMultiViewPA(manifest, optionState, panel) {
  panel.innerHTML = `<pre>${escapeHtml(JSON.stringify({ render: "MultiViewPA", manifest, optionState }, null, 2))}</pre>`;
}

async function renderEssayPA(manifest, optionState, panel) {
  panel.innerHTML = manifest.body_html || `<p class="runtime-note">${escapeHtml(manifest.heading)}</p>`;
}

async function renderExcludedPA(manifest, optionState, panel) {
  panel.innerHTML = `
    <h2>${escapeHtml(manifest.heading)}</h2>
    <p class="runtime-note">${escapeHtml(manifest.reason)}</p>
  `;
}

async function renderSimpleBarChart(manifest, optionState, panel) {
  const source = dataSourceForOptions(manifest, optionState);
  const trace = (manifest.traces || [])[0];
  if (!source || !trace) {
    panel.innerHTML = `<p class="runtime-note">No chart data is configured.</p>`;
    return;
  }
  const rows = await loadCsvRows(source.path);
  const orderedRows = orderRowsForAxis(rows, manifest.x_axis, trace.x);
  const maxValue = Math.max(...orderedRows.map(row => Number(row[trace.y]) || 0), 0);
  panel.innerHTML = `
    <div class="chart-panel">
      <h2 class="chart-title">${escapeHtml(source.label || manifest.heading)}</h2>
      <div class="bar-chart">
        <div class="bar-y-label">${escapeHtml(manifest.y_axis?.label || trace.y)}</div>
        <div class="bar-plot" role="img" aria-label="${escapeHtml(manifest.heading)}">
          ${orderedRows.map(row => renderBar(row, trace, maxValue)).join("")}
        </div>
        <div></div>
        <div class="bar-x-label">${escapeHtml(manifest.x_axis?.label || trace.x)}</div>
      </div>
      ${renderNotes(manifest, optionState)}
    </div>
  `;
}

function orderRowsForAxis(rows, axis, fallbackField) {
  const order = axis?.order_values || [];
  if (!order.length) return rows;
  const rowByValue = new Map(rows.map(row => [row[axis.source_field || fallbackField], row]));
  return order.map(value => rowByValue.get(value)).filter(Boolean);
}

function renderBar(row, trace, maxValue) {
  const rawValue = Number(row[trace.y]) || 0;
  const height = maxValue > 0 ? Math.max(1, (rawValue / maxValue) * 100) : 0;
  return `
    <div class="bar-item">
      <div class="bar-value">${escapeHtml(rawValue)}</div>
      <div class="bar" style="height: ${height}%"></div>
      <div class="bar-label">${escapeHtml(row[trace.x])}</div>
    </div>
  `;
}

async function renderStandingWinProbabilityChart(manifest, optionState, panel) {
  const source = dataSourceForOptions(manifest, optionState);
  const trace = (manifest.traces || [])[0];
  if (!source || !trace) {
    panel.innerHTML = `<p class="runtime-note">No chart data is configured.</p>`;
    return;
  }
  const rows = await loadCsvRows(source.path);
  const visibleRows = rows
    .filter(row => displayStandingChii(row.selected_chii, manifest))
    .filter(row => displayStandingChii(row.opponent_chii, manifest))
    .filter(row => optionState.division === "All" || divisionLabelForChii(row.selected_chii) === optionState.division);
  const grouped = groupRowsBy(visibleRows, trace.group_by);
  const chart = buildLineChartModel(grouped, trace, manifest, optionState);
  panel.innerHTML = `
    <div class="chart-panel">
      <h2 class="chart-title">${escapeHtml(source.label || manifest.heading)}: ${escapeHtml(optionState.division)}</h2>
      <div class="line-chart-wrap">
        ${renderLineChartSvg(chart)}
      </div>
      ${renderLineLegend(chart)}
      ${renderNotes(manifest, optionState)}
    </div>
  `;
}

function groupRowsBy(rows, field) {
  const groups = new Map();
  for (const row of rows) {
    const key = row[field];
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  return [...groups.entries()]
    .sort((a, b) => Number(a[1][0].selected_ordinal) - Number(b[1][0].selected_ordinal))
    .map(([key, groupRows]) => [
      key,
      groupRows.sort((a, b) => Number(a.opponent_ordinal) - Number(b.opponent_ordinal))
    ]);
}

function buildLineChartModel(groupedRows, trace, manifest, optionState) {
  const width = 920;
  const height = 520;
  const margin = { top: 24, right: 24, bottom: 88, left: 72 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const allRows = groupedRows.flatMap(([, rows]) => rows);
  const xValues = [...new Set(allRows.map(row => Number(row.opponent_ordinal)))]
    .filter(Number.isFinite)
    .sort((a, b) => a - b);
  const xMin = xValues[0] ?? 0;
  const xMax = xValues.at(-1) ?? 1;
  const yMin = manifest.y_axis?.minimum ?? 0;
  const yMax = manifest.y_axis?.maximum ?? 1;
  const scaleX = value => margin.left + ((value - xMin) / Math.max(1, xMax - xMin)) * plotWidth;
  const scaleY = value => margin.top + (1 - ((value - yMin) / Math.max(1, yMax - yMin))) * plotHeight;
  const colors = ["#8fb5ff", "#f2c14e", "#6ed6a0", "#f28c8c", "#b38cff", "#7bdff2", "#f7a072", "#d4e157", "#ff9bd2", "#a0c4ff"];
  return {
    width,
    height,
    margin,
    plotWidth,
    plotHeight,
    trace,
    manifest,
    optionState,
    xValues,
    scaleX,
    scaleY,
    series: groupedRows.map(([key, rows], index) => ({
      key,
      color: colors[index % colors.length],
      rows
    }))
  };
}

function renderLineChartSvg(chart) {
  const { width, height, margin, plotWidth, plotHeight, scaleX, scaleY } = chart;
  const yTicks = [0, 0.25, 0.5, 0.75, 1];
  const xTickRows = representativeXTicks(chart);
  return `
    <svg class="line-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(chart.manifest.heading)}">
      ${yTicks.map(value => `
        <line class="grid-line" x1="${margin.left}" x2="${margin.left + plotWidth}" y1="${scaleY(value)}" y2="${scaleY(value)}"></line>
        <text class="tick-label" x="${margin.left - 10}" y="${scaleY(value) + 4}" text-anchor="end">${Math.round(value * 100)}%</text>
      `).join("")}
      <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${margin.top + plotHeight}"></line>
      <line class="axis-line" x1="${margin.left}" x2="${margin.left + plotWidth}" y1="${margin.top + plotHeight}" y2="${margin.top + plotHeight}"></line>
      ${xTickRows.map(row => `
        <text class="tick-label" x="${scaleX(Number(row.opponent_ordinal))}" y="${margin.top + plotHeight + 22}" text-anchor="middle">${escapeHtml(row.opponent_chii)}</text>
      `).join("")}
      <text class="axis-label" x="${margin.left + plotWidth / 2}" y="${height - 20}" text-anchor="middle">${escapeHtml(chart.manifest.x_axis?.label || "Opponent standing")}</text>
      <text class="axis-label" transform="translate(20 ${margin.top + plotHeight / 2}) rotate(-90)" text-anchor="middle">${escapeHtml(chart.manifest.y_axis?.label || chart.trace.y)}</text>
      ${chart.series.map(series => renderSeries(series, chart)).join("")}
    </svg>
  `;
}

function representativeXTicks(chart) {
  const firstSeries = chart.series[0]?.rows || [];
  const maxTicks = 12;
  const step = Math.max(1, Math.ceil(firstSeries.length / maxTicks));
  return firstSeries.filter((_, index) => index % step === 0 || index === firstSeries.length - 1);
}

function renderSeries(series, chart) {
  const points = series.rows.map(row => {
    const x = chart.scaleX(Number(row[chart.manifest.x_axis?.order_field || "opponent_ordinal"]));
    const y = chart.scaleY(Number(row[chart.trace.y]));
    return { row, x, y };
  }).filter(point => Number.isFinite(point.x) && Number.isFinite(point.y));
  const polyline = points.map(point => `${point.x},${point.y}`).join(" ");
  const errorBars = chart.optionState.error_bars ? points.map(point => renderErrorBar(point, chart)).join("") : "";
  return `
    <g>
      ${errorBars}
      <polyline class="trace-line" points="${polyline}" style="stroke:${series.color}"></polyline>
      ${points.map(point => `<circle class="trace-point" cx="${point.x}" cy="${point.y}" r="3" style="fill:${series.color}"><title>${escapeHtml(series.key)} vs ${escapeHtml(point.row.opponent_chii)}: ${formatPercent(point.row[chart.trace.y])}</title></circle>`).join("")}
    </g>
  `;
}

function renderErrorBar(point, chart) {
  const low = Number(point.row.ci95_lower);
  const high = Number(point.row.ci95_upper);
  if (!Number.isFinite(low) || !Number.isFinite(high)) return "";
  const y1 = chart.scaleY(high);
  const y2 = chart.scaleY(low);
  return `<line class="error-bar" x1="${point.x}" x2="${point.x}" y1="${y1}" y2="${y2}"></line>`;
}

function renderLineLegend(chart) {
  return `
    <div class="chart-legend">
      ${chart.series.map(series => `<span><span class="legend-swatch" style="background:${series.color}"></span>${escapeHtml(series.key)}</span>`).join("")}
    </div>
  `;
}

function displayStandingChii(chii, manifest) {
  const sanyaku = manifest.provenance?.sanyaku_display || [];
  if (!chii) return false;
  if (chii.startsWith("Y")) return sanyaku.includes(chii);
  if (chii.startsWith("O")) return sanyaku.includes(chii);
  if (chii.startsWith("S") && !chii.startsWith("Sd")) return sanyaku.includes(chii);
  if (chii.startsWith("K")) return sanyaku.includes(chii);
  return true;
}

function divisionLabelForChii(chii) {
  if (!chii) return "Other";
  if (chii.startsWith("Ms")) return "Makushita";
  if (chii.startsWith("Sd")) return "Sandanme";
  if (chii.startsWith("Jd")) return "Jonidan";
  if (chii.startsWith("Jk")) return "Jonokuchi";
  if (["Y", "O", "S", "K", "M"].some(prefix => chii.startsWith(prefix))) return "Makuuchi";
  if (chii.startsWith("J")) return "Juryo";
  return "Other";
}

function formatPercent(value) {
  const number = Number(value);
  return Number.isFinite(number) ? `${(number * 100).toFixed(1)}%` : value;
}

function registerRuntimeListeners(taggedManifest, optionState) {
}

function renderOptionControl(option, optionState) {
  const value = optionState[option.id];
  if (option.control === "radio_group") {
    return `
      <div class="control-group">
        <div class="control-label">${escapeHtml(option.label)}</div>
        <div class="radio-group">
          ${(option.values || []).map(item => `
            <label class="radio-option">
              <input type="radio" name="${escapeHtml(option.id)}" data-option-id="${escapeHtml(option.id)}" value="${escapeHtml(item.value)}" ${String(value) === String(item.value) ? "checked" : ""}>
              <span>${escapeHtml(item.label)}</span>
            </label>
          `).join("")}
        </div>
      </div>
    `;
  }
  if (option.kind === "boolean") {
    return `
      <div class="control-group">
        <label class="checkbox-option">
          <input type="checkbox" data-option-id="${escapeHtml(option.id)}" ${value === true || value === "true" ? "checked" : ""}>
          <span>${escapeHtml(option.label)}</span>
        </label>
      </div>
    `;
  }
  return `
    <div class="control-group">
      <label class="control-label" for="option-${escapeHtml(option.id)}">${escapeHtml(option.label)}</label>
      <select id="option-${escapeHtml(option.id)}" data-option-id="${escapeHtml(option.id)}">
        ${(option.values || []).map(item => `
          <option value="${escapeHtml(item.value)}" ${String(value) === String(item.value) ? "selected" : ""}>${escapeHtml(item.label)}</option>
        `).join("")}
      </select>
    </div>
  `;
}

function wireOptionControls(panel, taggedManifest) {
  const optionById = new Map(collectOptions(taggedManifest).map(option => [option.id, option]));
  panel.querySelectorAll("[data-option-id]").forEach(control => {
    control.addEventListener("change", async () => {
      const option = optionById.get(control.dataset.optionId);
      const value = option.kind === "boolean" ? control.checked : control.value;
      runtimeState.optionState[option.id] = coerceOptionValue(option, value);
      runtimeState.sort = defaultSortForManifest(taggedManifest.manifest, runtimeState.optionState);
      normaliseUrlIfNeeded(resolveInitialPageId(), taggedManifest, runtimeState.optionState);
      renderOptionsPanel(taggedManifest, runtimeState.optionState);
      await renderPublishedArtefact(taggedManifest, runtimeState.optionState);
    });
  });
}

async function renderStandingsTable(manifest, optionState, panel) {
  const source = dataSourceForOptions(manifest, optionState);
  if (!source) {
    panel.innerHTML = `<p class="runtime-note">No data source matches the selected options.</p>`;
    return;
  }
  const [rows, metadata] = await Promise.all([
    loadCsvRows(source.path),
    source.metadata_path ? loadJsonFile(source.metadata_path) : Promise.resolve(null)
  ]);
  runtimeState.rows = rows;
  runtimeState.metadata = metadata;
  const visibleColumns = visibleColumnsForTable(manifest, optionState);
  const filteredRows = rows
    .filter(row => includeStandingsRow(row, optionState))
    .sort((a, b) => compareRows(a, b, columnById(manifest, runtimeState.sort.column), runtimeState.sort.descending));
  panel.innerHTML = `
    <div class="table-panel">
      <h2 class="table-title">${escapeHtml(standingsTitle(optionState, metadata, runtimeState.sort.column))}</h2>
      <div class="table-wrap">
        <table>
          ${renderTableHead(manifest, visibleColumns)}
          <tbody>
            ${filteredRows.map((row, index) => renderTableRow(row, index, visibleColumns)).join("")}
          </tbody>
        </table>
      </div>
      ${renderNotes(manifest, optionState)}
    </div>
  `;
  wireTableHeaders(panel, manifest, optionState);
}

async function renderSectionedTable(manifest, optionState, panel) {
  const source = dataSourceForOptions(manifest, optionState);
  if (!source) {
    panel.innerHTML = `<p class="runtime-note">No data source is configured.</p>`;
    return;
  }
  const rows = await loadCsvRows(source.path);
  panel.innerHTML = `
    <div class="table-panel">
      <div class="sectioned-table-grid">
        ${(manifest.sections || []).map(section => renderTableSection(section, rows, manifest.columns || [])).join("")}
      </div>
      ${renderNotes(manifest, optionState)}
    </div>
  `;
}

function renderTableSection(section, rows, columns) {
  const sectionRows = rows
    .filter(row => row[section.source_field] === section.source_value)
    .sort((a, b) => comparePrimitive(Number(a[section.order_by] || 0), Number(b[section.order_by] || 0)));
  return `
    <section class="table-section">
      <h2>${escapeHtml(section.heading)}</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>${columns.map(column => renderPlainHeaderCell(column)).join("")}</tr>
          </thead>
          <tbody>
            ${sectionRows.map((row, index) => renderTableRow(row, index, columns)).join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderPlainHeaderCell(column) {
  const classes = [column.align || ""].filter(Boolean).join(" ");
  return `<th class="${escapeHtml(classes)}">${escapeHtml(column.heading)}</th>`;
}

function dataSourceForOptions(manifest, optionState) {
  return (manifest.data_sources || []).find(source => {
    if (!source.option_id) return source.id === manifest.primary_source || manifest.data_sources.length === 1;
    return String(optionState[source.option_id]) === String(source.option_value);
  });
}

async function loadCsvRows(path) {
  const text = await fetch(path).then(response => {
    if (!response.ok) throw new Error(`Could not load ${path}: ${response.status}`);
    return response.text();
  });
  return parseCsv(text);
}

async function loadJsonFile(path) {
  return fetch(path).then(response => {
    if (!response.ok) throw new Error(`Could not load ${path}: ${response.status}`);
    return response.json();
  });
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = splitCsvLine(lines[0]);
  return lines.slice(1).filter(Boolean).map(line => {
    const values = splitCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
  });
}

function splitCsvLine(line) {
  const values = [];
  let current = "";
  let quoted = false;
  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"' && line[i + 1] === '"') {
      current += '"';
      i += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values;
}

function visibleColumnsForTable(manifest, optionState) {
  const presetId = optionState.metric_group_preset;
  const preset = (manifest.group_visibility_presets || []).find(item => item.id === presetId);
  const visibleGroups = new Set(preset ? preset.visible_groups : (manifest.column_groups || []).map(group => group.id));
  return (manifest.columns || []).filter(column => column.always_visible || visibleGroups.has(column.group));
}

function includeStandingsRow(row, optionState) {
  if ((optionState.current_only === true || optionState.current_only === "true") && String(row.is_current) !== "1") {
    return false;
  }
  if (optionState.division && optionState.division !== "all") {
    return divisionForChii(row.chii) === optionState.division;
  }
  return true;
}

function divisionForChii(chii) {
  if (!chii) return "other";
  if (chii.startsWith("Ms")) return "makushita";
  if (chii.startsWith("Sd")) return "sandanme";
  if (chii.startsWith("Jd")) return "jonidan";
  if (chii.startsWith("Jk")) return "jonokuchi";
  if (["Y", "O", "S", "K", "M"].some(prefix => chii.startsWith(prefix))) return "makuuchi";
  if (chii.startsWith("J")) return "juryo";
  return "other";
}

function renderTableHead(manifest, visibleColumns) {
  const groups = manifest.column_groups || [];
  const groupForColumn = new Map(visibleColumns.map(column => [column.id, groups.find(group => group.id === column.group)]));
  const groupCells = [];
  let index = 0;
  while (index < visibleColumns.length) {
    const group = groupForColumn.get(visibleColumns[index].id);
    const groupColumns = [];
    while (index < visibleColumns.length && groupForColumn.get(visibleColumns[index].id)?.id === group?.id) {
      groupColumns.push(visibleColumns[index]);
      index += 1;
    }
    groupCells.push(`<th colspan="${groupColumns.length}" class="center">${escapeHtml(group?.heading || "")}</th>`);
  }
  return `
    <thead>
      <tr>${groupCells.join("")}</tr>
      <tr>${visibleColumns.map(column => renderHeaderCell(column)).join("")}</tr>
    </thead>
  `;
}

function renderHeaderCell(column) {
  const active = runtimeState.sort?.column === column.id;
  const marker = active ? (runtimeState.sort.descending ? " ▼" : " ▲") : "";
  const classes = [column.align || "", column.sortable ? "sortable" : ""].filter(Boolean).join(" ");
  return `<th class="${escapeHtml(classes)}" data-column-id="${escapeHtml(column.id)}">${escapeHtml(column.heading)}${marker}</th>`;
}

function renderTableRow(row, index, visibleColumns) {
  return `<tr>${visibleColumns.map(column => renderTableCell(row, index, column)).join("")}</tr>`;
}

function renderTableCell(row, index, column) {
  const classes = [column.align || ""].filter(Boolean).join(" ");
  return `<td class="${escapeHtml(classes)}">${formatCell(row, index, column)}</td>`;
}

function formatCell(row, index, column) {
  if (column.formatter === "row_number") return String(index + 1);
  if (column.formatter === "competition_rank") return competitionRank(row, column);
  const raw = column.source_field ? row[column.source_field] : "";
  if (column.formatter === "decimal_2") return formatNumber(raw, 2);
  if (column.formatter === "percent_1") return `${formatNumber(raw, 1)}%`;
  if (column.link === "rikishi" && row.rikishi_id) {
    return `<a href="https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(row.rikishi_id)}">${escapeHtml(raw)}</a>`;
  }
  return escapeHtml(raw);
}

function competitionRank(row, column) {
  const source = column.source_field || column.sort_key;
  const sorted = [...runtimeState.rows]
    .filter(candidate => includeStandingsRow(candidate, runtimeState.optionState))
    .sort((a, b) => comparePrimitive(valueForSort(b, { sort_key: source, source_field: source, sort_kind: "numeric" }), valueForSort(a, { sort_key: source, source_field: source, sort_kind: "numeric" })));
  const target = Number(row[source]);
  const found = sorted.findIndex(candidate => Number(candidate[source]) === target);
  return found >= 0 ? String(found + 1) : "";
}

function formatNumber(value, digits) {
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(digits) : escapeHtml(value);
}

function wireTableHeaders(panel, manifest, optionState) {
  panel.querySelectorAll("th[data-column-id]").forEach(header => {
    const column = columnById(manifest, header.dataset.columnId);
    if (!column?.sortable) return;
    header.addEventListener("click", async () => {
      if (runtimeState.sort?.column === column.id) {
        runtimeState.sort.descending = !runtimeState.sort.descending;
      } else {
        runtimeState.sort = {
          column: column.id,
          descending: defaultSortDescending(column)
        };
      }
      normaliseUrlIfNeeded(resolveInitialPageId(), runtimeState.taggedManifest, runtimeState.optionState);
      await renderPublishedArtefact(runtimeState.taggedManifest, runtimeState.optionState);
    });
  });
}

function compareRows(a, b, column, descending) {
  const result = comparePrimitive(valueForSort(a, column), valueForSort(b, column));
  return descending ? -result : result;
}

function valueForSort(row, column) {
  const key = column.sort_key || column.source_field;
  const value = row[key] ?? "";
  if (column.sort_kind === "numeric" || column.sort_kind === "chii_ordinal") {
    const number = Number(value);
    return Number.isFinite(number) ? number : Number.POSITIVE_INFINITY;
  }
  return String(value).toLocaleLowerCase();
}

function comparePrimitive(a, b) {
  if (a < b) return -1;
  if (a > b) return 1;
  return 0;
}

function columnById(manifest, columnId) {
  return (manifest.columns || []).find(column => column.id === columnId);
}

function defaultSortForManifest(manifest, optionState) {
  if (!manifest) return null;
  const preset = (manifest.group_visibility_presets || []).find(item => item.id === optionState.metric_group_preset);
  const sort = preset?.default_sort || manifest.default_sort;
  if (!sort) return null;
  return { column: sort.column, descending: sort.descending };
}

function defaultSortDescending(column) {
  return !(column.sort_kind === "text" || column.sort_kind === "chii_ordinal");
}

function standingsTitle(optionState, metadata, sortColumn) {
  const division = labelForOption(runtimeState.taggedManifest.manifest, "division", optionState.division) || "All";
  const sortLabel = columnById(runtimeState.taggedManifest.manifest, sortColumn)?.heading || "Selected Column";
  const end = metadata?.effective_end_date || "";
  const monthYear = end ? bashoMonthYear(end) : "";
  return `${division} Standings by ${sortLabel} after ${monthYear} Basho`;
}

function bashoMonthYear(dateToken) {
  const [year, month] = dateToken.split("/");
  const monthName = new Date(Number(year), Number(month) - 1, 1).toLocaleString("en-GB", { month: "long" });
  return `${monthName} ${year}`;
}

function labelForOption(manifest, optionId, value) {
  const option = (manifest.options || []).find(item => item.id === optionId);
  return option?.values?.find(item => String(item.value) === String(value))?.label;
}

function renderNotes(manifest, optionState) {
  const notes = (manifest.notes || []).filter(note => noteApplies(note, optionState));
  if (!notes.length) return "";
  return `<div class="notes-panel">${notes.map(note => `<p>${formatNoteText(note)}</p>`).join("")}</div>`;
}

function formatNoteText(note) {
  return note.format === "html" ? note.text : escapeHtml(note.text);
}

function noteApplies(note, optionState) {
  const applies = note.applies_to || ["all"];
  return applies.includes("all") || applies.includes(optionState.metric_group_preset);
}

function coerceOptionValue(option, value) {
  if (option.kind === "boolean") {
    return value === true || value === "true";
  }
  const matching = (option.values || []).find(item => String(item.value) === String(value));
  return matching ? matching.value : value;
}

function rootRelativeUrl(path) {
  const current = window.location.pathname;
  const marker = "/runtime-skeleton/";
  const index = current.indexOf(marker);
  if (index < 0) return path;
  const tail = current.slice(index + marker.length);
  const depth = Math.max(0, tail.split("/").filter(Boolean).length - 1);
  return "../".repeat(depth) + path;
}

function escapeHtml(value) {
  const span = document.createElement("span");
  span.textContent = value ?? "";
  return span.innerHTML;
}

document.addEventListener("DOMContentLoaded", () => {
  bootSiteRuntime().catch(error => {
    document.getElementById("pa-panel").innerHTML = `<pre>${escapeHtml(error.stack || error.message)}</pre>`;
  });
});
"""

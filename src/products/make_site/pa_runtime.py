"""Experimental PA-manifest runtime skeleton writer."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, is_dataclass
from html import escape
from pathlib import Path
from typing import Any, Mapping

from .classes import NavigationTree, Site, SiteBuildConfig
from .pa_manifest import ACTIVE_PA_MANIFESTS
from .routes import PageRoute, html_href


RUNTIME_DIR = "runtime-skeleton"
RUNTIME_ASSET_VERSION = "20260509-pa-runtime-skeleton"


def write_pa_runtime_skeleton(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
) -> None:
    """Write a parallel shell showing the intended PA-manifest runtime shape."""

    root = config.output_root / RUNTIME_DIR
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    write_manifest_files(root)
    write_runtime_assets(root)
    write_runtime_index(site, config, page_routes, root)
    for page_id, page_route in page_routes.items():
        if page_id in ACTIVE_PA_MANIFESTS:
            write_runtime_page(site, config, page_routes, root, page_id, page_route)


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
) -> None:
    write_runtime_shell_html(
        site=site,
        config=config,
        page_routes=page_routes,
        target_path=root / "index.html",
        selected_page_id="",
        asset_prefix="",
    )


def write_runtime_page(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    root: Path,
    page_id: str,
    page_route: PageRoute,
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
    )


def write_runtime_shell_html(
    *,
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    target_path: Path,
    selected_page_id: str,
    asset_prefix: str,
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
async function bootSiteRuntime() {
  const pageId = resolveInitialPageId();
  const manifestIndex = await loadManifestIndex();
  const taggedManifest = await loadTaggedManifest(pageId, manifestIndex);
  const optionState = resolveOptionState(taggedManifest, readUrlState());
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

function resolveOptionState(taggedManifest, urlState) {
  if (!taggedManifest) return {};
  const options = collectOptions(taggedManifest);
  return Object.fromEntries(options.map(option => [
    option.id,
    urlState[option.url_key || option.id] ?? option.default
  ]));
}

function normaliseUrlIfNeeded(pageId, taggedManifest, optionState) {
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
  panel.innerHTML = options.length
    ? `<pre>${escapeHtml(JSON.stringify({ options, optionState }, null, 2))}</pre>`
    : `<p class="runtime-note">No options.</p>`;
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
  panel.innerHTML = `<pre>${escapeHtml(JSON.stringify({ render: "TablePA", manifest, optionState }, null, 2))}</pre>`;
}

async function renderChartPA(manifest, optionState, panel) {
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

function registerRuntimeListeners(taggedManifest, optionState) {
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

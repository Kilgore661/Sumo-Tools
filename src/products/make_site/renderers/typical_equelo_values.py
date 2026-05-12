"""Typical Equelo Values page renderer."""

from __future__ import annotations

from html import escape
from pathlib import Path

from ..classes import Page


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



// Basho Results recursive table rendering.

import { escapeHtml } from "../../utils/html.js";
import { renderLabelWithHelp } from "../help.js";
import { PRESENTATION } from "./table-spec.js";
import {
  currentBashoResultsSortState,
  isSortableLeaf,
  sortBashoResultsRows,
  sortDefaultDirection,
  toggledSortDirection,
} from "./sorting.js";

// Render the full Basho Results presentation model as a recursive table.
function renderBashoResultsPresentationTable(model) {
  const visiblePaths = new Set(model.projection?.visible_paths || []);
  const leaves = terminalNodes(model.table_spec || [], [], visiblePaths);
  const sortState = currentBashoResultsSortState(model, leaves);
  const sortedValues = sortBashoResultsRows(model.values || [], leaves, sortState);
  return [
    renderBashoResultsHeader(model.header),
    '<table class="artifact-table brb-table brb-redesign-table">',
    renderNestedHead(model.table_spec || [], visiblePaths, leaves, sortState),
    '<tbody>',
    ...sortedValues.map((row, index) => [
      '<tr>',
      ...leaves.map(leaf => `<td ${leafCellAttributes(leaf)}>${renderBashoResultsCell(row, leaf.path, index)}</td>`),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

function renderBashoResultsHeader(header) {
  if (!header) return "";
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(header.heading || "")}</h4>`,
    header.subheading ? `<h5>${escapeHtml(header.subheading)}</h5>` : "",
    '</div>',
  ].join("");
}

// Render multi-row table headings from the recursive table specification.
function renderNestedHead(nodes, visiblePaths, leaves = null, sortState = null) {
  const rows = headerRows(nodes, visiblePaths);
  const leafByPath = new Map((leaves || terminalNodes(nodes, [], visiblePaths)).map(leaf => [leaf.path, leaf]));
  return [
    '<thead>',
    ...rows.map(row => [
      '<tr>',
      ...row.map(cell => renderNestedHeaderCell(cell, leafByPath.get(cell.path), sortState)),
      '</tr>',
    ].join("")),
    '</thead>',
  ].join("");
}

function renderNestedHeaderCell(cell, leaf, sortState) {
  const presentation = leaf?.presentation || PRESENTATION.DEFAULT;
  const alignment = headingAlignment(presentation);
  const attributes = [
    `colspan="${cell.colspan}"`,
    `rowspan="${cell.rowspan}"`,
    `data-column-path="${escapeHtml(cell.path)}"`,
    `style="text-align: ${alignment};"`,
  ];
  if (leaf?.role === "row_number") attributes.push('data-column-id="row_number"');
  if (!isSortableLeaf(leaf)) {
    return `<th ${attributes.join(" ")}>${renderLabelWithHelp(cell.label, cell.help)}</th>`;
  }
  const active = sortState?.path === leaf.path;
  const direction = active ? sortState.direction : "none";
  const indicator = active ? (sortState.direction === "ascending" ? " ▲" : " ▼") : "";
  const escapedLabel = escapeHtml(cell.label);
  const reservedSortText = `${escapedLabel} ▼`;
  const visibleSortText = `${renderLabelWithHelp(cell.label, cell.help)}${indicator}`;
  return [
    `<th ${attributes.join(" ")} aria-sort="${direction}">`,
    `<button type="button" class="table-sort-button" data-basho-results-sort-path="${escapeHtml(leaf.path)}" style="display: inline-grid; place-items: center; ${buttonMarginStyle(alignment)} text-align: ${alignment};">`,
    `<span class="table-sort-width-reserver" aria-hidden="true" style="grid-area: 1 / 1; visibility: hidden; white-space: nowrap;">${reservedSortText}</span>`,
    `<span class="table-sort-visible-content" style="grid-area: 1 / 1; white-space: nowrap;">${visibleSortText}</span>`,
    '</button>',
    '</th>',
  ].join("");
}

// Convert recursive header nodes into concrete table header rows.
function headerRows(nodes, visiblePaths) {
  const depth = maxDepth(nodes, visiblePaths);
  const rows = Array.from({ length: depth }, () => []);
  appendHeaderCells(rows, nodes, [], visiblePaths, depth, 0);
  return rows;
}

function appendHeaderCells(rows, nodes, path, visiblePaths, depth, level) {
  for (const node of nodes || []) {
    const nextPath = [...path, node.key];
    const pathText = nextPath.join(".");
    if (node.children) {
      const childLeaves = terminalNodes(node.children, nextPath, visiblePaths);
      if (!childLeaves.length) continue;
      rows[level].push({
        colspan: childLeaves.length,
        label: node.label ?? node.key,
        help: node.help || "",
        path: pathText,
        rowspan: 1,
      });
      appendHeaderCells(rows, node.children, nextPath, visiblePaths, depth, level + 1);
    } else if (isVisiblePath(pathText, visiblePaths)) {
      rows[level].push({
        colspan: 1,
        label: node.label ?? node.key,
        help: node.help || "",
        path: pathText,
        rowspan: depth - level,
      });
    }
  }
}

function maxDepth(nodes, visiblePaths, path = [], level = 1) {
  const depths = (nodes || []).flatMap(node => {
    const nextPath = [...path, node.key];
    if (node.children) return [maxDepth(node.children, visiblePaths, nextPath, level + 1)];
    return isVisiblePath(nextPath.join("."), visiblePaths) ? [level] : [];
  });
  return Math.max(level, ...depths);
}

// Return visible leaf columns with resolved terminal and sort paths.
function terminalNodes(nodes, path, visiblePaths) {
  return (nodes || []).flatMap(node => {
    const nextPath = [...path, node.key];
    const pathText = nextPath.join(".");
    if (node.children) return terminalNodes(node.children, nextPath, visiblePaths);
    return isVisiblePath(pathText, visiblePaths)
      ? [{ ...node, path: pathText, sort_path: resolveLeafSortPath(node, nextPath) }]
      : [];
  });
}

function resolveLeafSortPath(node, path) {
  if (!node.sort_path) return path.join(".");
  if (node.sort_path.includes(".")) return node.sort_path;
  return [...path.slice(0, -1), node.sort_path].join(".");
}

function isVisiblePath(path, visiblePaths) {
  return !visiblePaths.size || visiblePaths.has(path);
}

function leafCellAttributes(leaf) {
  const attributes = [
    `data-column-path="${escapeHtml(leaf.path)}"`,
    `style="text-align: ${valueAlignment(leaf.presentation)};"`,
  ];
  if (leaf.role === "row_number") attributes.push('data-column-id="row_number"');
  return attributes.join(" ");
}

// Render a terminal-path value, including the special rikishi link cell.
function renderBashoResultsCell(row, path, index) {
  if (path === "reference.row_number") return escapeHtml(String(index + 1));
  if (path === "reference.shikona") {
    return renderRikishiLink(row["reference.shikona"], row["reference.rikishi_id"]);
  }
  return escapeHtml(valueAtPath(row, path));
}

function renderRikishiLink(shikona, rikishiId) {
  if (!rikishiId) return escapeHtml(shikona || "");
  return [
    `<a href="https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(rikishiId)}"`,
    ' target="_blank" rel="noopener">',
    escapeHtml(shikona || ""),
    '</a>',
  ].join("");
}

function valueAtPath(row, path) {
  const value = row?.[path];
  if (value === null || value === undefined) return "";
  return String(value);
}

function headingAlignment(presentation) {
  if (presentation === PRESENTATION.NAME) return "left";
  return "center";
}

function valueAlignment(presentation) {
  if (presentation === PRESENTATION.NAME) return "left";
  if (presentation === PRESENTATION.RATING || presentation === PRESENTATION.NUMERIC_MAGNITUDE) return "right";
  return "center";
}

function buttonMarginStyle(alignment) {
  if (alignment === "left") return "margin-right: auto;";
  if (alignment === "right") return "margin-left: auto;";
  return "margin: 0 auto;";
}

export {
  renderBashoResultsPresentationTable,
  renderBashoResultsHeader,
  renderNestedHead,
  renderNestedHeaderCell,
  headerRows,
  appendHeaderCells,
  maxDepth,
  terminalNodes,
  resolveLeafSortPath,
  isVisiblePath,
  renderBashoResultsCell,
  renderRikishiLink,
  valueAtPath,
  leafCellAttributes,
  headingAlignment,
  valueAlignment,
  buttonMarginStyle,
};
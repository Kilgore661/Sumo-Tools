// Rating Changes grouped table rendering.

import { escapeHtml } from "../../utils/html.js";
import { renderLabelWithHelp } from "../help.js";
import { renderRikishiLink as renderSharedRikishiLink } from "../tables/shared.js";
import { PRESENTATION } from "./table-spec.js";
import {
  currentRatingChangesSortState,
  isSortableLeaf,
  sortDefaultDirection,
  sortRatingChangesRows,
  toggledSortDirection,
} from "./sorting.js";

function renderRatingChangesPresentationTable(model) {
  const visiblePaths = new Set(model.projection?.visible_paths || []);
  const leaves = terminalNodes(model.table_spec || [], [], visiblePaths);
  const boundaries = groupBoundaryMap(model.table_spec || [], visiblePaths, leaves);
  const sortState = currentRatingChangesSortState(model, leaves);
  const sortedValues = sortRatingChangesRows(model.values || [], leaves, sortState);
  return [
    renderRatingChangesHeader(model.header),
    '<table class="artifact-table rating-changes-table">',
    renderNestedHead(model.table_spec || [], visiblePaths, leaves, sortState, boundaries),
    '<tbody>',
    sortedValues.length
      ? sortedValues.map((row, index) => [
        '<tr>',
        ...leaves.map(leaf => `<td ${leafCellAttributes(leaf, boundaries.position(leaf.path))}>${renderRatingChangesCell(row, leaf.path, index)}</td>`),
        '</tr>',
      ].join("")).join("")
      : renderEmptyBodyRow(leaves.length),
    '</tbody>',
    '</table>',
  ].join("");
}

function renderRatingChangesHeader(header) {
  if (!header) return "";
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(header.heading || "")}</h4>`,
    header.subheading ? `<h5>${escapeHtml(header.subheading)}</h5>` : "",
    '</div>',
  ].join("");
}

function renderEmptyBodyRow(colspan) {
  return `<tr><td colspan="${Number(colspan) || 1}" class="artifact-placeholder">Rating Changes producer output is not available yet.</td></tr>`;
}

function renderNestedHead(nodes, visiblePaths, leaves = null, sortState = null, boundaries = null) {
  const rows = headerRows(nodes, visiblePaths);
  const visibleLeaves = leaves || terminalNodes(nodes, [], visiblePaths);
  const leafByPath = new Map(visibleLeaves.map(leaf => [leaf.path, leaf]));
  const boundaryMap = boundaries || groupBoundaryMap(nodes, visiblePaths, visibleLeaves);
  return [
    '<thead>',
    ...rows.map(row => [
      '<tr>',
      ...row.map(cell => renderNestedHeaderCell(cell, leafByPath.get(cell.path), sortState, boundaryMap)),
      '</tr>',
    ].join("")),
    '</thead>',
  ].join("");
}

function renderNestedHeaderCell(cell, leaf, sortState, boundaries = null) {
  const groupPosition = cell.is_group ? "only" : boundaries?.position(cell.path);
  const attributes = [
    `colspan="${cell.colspan}"`,
    `rowspan="${cell.rowspan}"`,
    `data-column-path="${escapeHtml(cell.path)}"`,
    'style="text-align: center;"',
    ...groupBoundaryAttributes(groupPosition),
  ];
  if (cell.is_group) attributes.push('data-heading-group="true"');
  if (leaf?.role === "row_number") attributes.push('data-column-id="row_number"');
  if (!isSortableLeaf(leaf)) {
    return `<th ${attributes.join(" ")}>${renderLabelWithHelp(cell.label, cell.help, { noteId: cell.note_id })}</th>`;
  }
  const active = sortState?.path === leaf.path;
  const direction = active ? sortState.direction : "none";
  const indicator = active ? (sortState.direction === "ascending" ? " ▲" : " ▼") : "";
  const escapedLabel = escapeHtml(cell.label);
  const visibleSortText = `${renderLabelWithHelp(cell.label, cell.help, { noteId: cell.note_id })}${indicator}`;
  return [
    `<th ${attributes.join(" ")} aria-sort="${direction}">`,
    `<button type="button" class="table-sort-button" data-rating-changes-sort-path="${escapeHtml(leaf.path)}" style="display: inline-grid; place-items: center; text-align: center;">`,
    `<span class="table-sort-width-reserver" aria-hidden="true" style="grid-area: 1 / 1; visibility: hidden; white-space: nowrap;">${escapedLabel} ▼</span>`,
    `<span class="table-sort-visible-content" style="grid-area: 1 / 1; white-space: nowrap;">${visibleSortText}</span>`,
    '</button>',
    '</th>',
  ].join("");
}

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
    if (node.hidden) continue;
    if (node.children) {
      const childLeaves = terminalNodes(node.children, nextPath, visiblePaths);
      if (!childLeaves.length) continue;
      rows[level].push({
        colspan: childLeaves.length,
        label: node.label ?? node.key,
        help: node.help || "",
        note_id: node.note_id || "",
        path: pathText,
        rowspan: 1,
        is_group: true,
      });
      appendHeaderCells(rows, node.children, nextPath, visiblePaths, depth, level + 1);
    } else if (isVisiblePath(pathText, visiblePaths)) {
      rows[level].push({
        colspan: 1,
        label: node.label ?? node.key,
        help: node.help || "",
        note_id: node.note_id || "",
        path: pathText,
        rowspan: depth - level,
        is_group: false,
      });
    }
  }
}

function maxDepth(nodes, visiblePaths, path = [], level = 1) {
  const depths = (nodes || []).flatMap(node => {
    if (node.hidden) return [];
    const nextPath = [...path, node.key];
    if (node.children) return [maxDepth(node.children, visiblePaths, nextPath, level + 1)];
    return isVisiblePath(nextPath.join("."), visiblePaths) ? [level] : [];
  });
  return Math.max(level, ...depths);
}

function terminalNodes(nodes, path, visiblePaths) {
  return (nodes || []).flatMap(node => {
    if (node.hidden) return [];
    const nextPath = [...path, node.key];
    const pathText = nextPath.join(".");
    if (node.children) return terminalNodes(node.children, nextPath, visiblePaths);
    return isVisiblePath(pathText, visiblePaths)
      ? [{ ...node, path: pathText, sort_path: resolveLeafSortPath(node, nextPath) }]
      : [];
  });
}

function groupBoundaryMap(nodes, visiblePaths, leaves = null) {
  const visibleLeaves = leaves || terminalNodes(nodes, [], visiblePaths);
  const starts = new Set();
  const ends = new Set();
  collectGroupBoundaries(nodes, [], visiblePaths, starts, ends);
  return {
    starts,
    ends,
    position(path) {
      const start = starts.has(path);
      const end = ends.has(path);
      if (start && end) return "only";
      if (start) return "start";
      if (end) return "end";
      return "";
    },
    leaves: visibleLeaves,
  };
}

function collectGroupBoundaries(nodes, path, visiblePaths, starts, ends) {
  for (const node of nodes || []) {
    if (node.hidden) continue;
    const nextPath = [...path, node.key];
    if (!node.children) continue;
    const childLeaves = terminalNodes(node.children, nextPath, visiblePaths);
    if (!childLeaves.length) continue;
    starts.add(childLeaves[0].path);
    ends.add(childLeaves[childLeaves.length - 1].path);
    collectGroupBoundaries(node.children, nextPath, visiblePaths, starts, ends);
  }
}

function groupBoundaryAttributes(groupPosition = "") {
  if (groupPosition === "only") return ['data-group-start="true"', 'data-group-end="true"'];
  if (groupPosition === "start") return ['data-group-start="true"'];
  if (groupPosition === "end") return ['data-group-end="true"'];
  return [];
}

function resolveLeafSortPath(node, path) {
  if (!node.sort_path) return path.join(".");
  if (node.sort_path.includes(".")) return node.sort_path;
  return [...path.slice(0, -1), node.sort_path].join(".");
}

function isVisiblePath(path, visiblePaths) {
  return !visiblePaths.size || visiblePaths.has(path);
}

function leafCellAttributes(leaf, groupPosition = "") {
  const attributes = [
    `data-column-path="${escapeHtml(leaf.path)}"`,
    `style="text-align: ${valueAlignment(leaf.presentation)};"`,
    ...groupBoundaryAttributes(groupPosition),
  ];
  if (leaf.role === "row_number") attributes.push('data-column-id="row_number"');
  return attributes.join(" ");
}

function renderRatingChangesCell(row, path, index) {
  if (path === "reference.row_number") return escapeHtml(String(index + 1));
  if (path === "reference.shikona") {
    return renderRikishiLink(row["reference.shikona"], row["reference.rikishi_id"]);
  }
  return escapeHtml(valueAtPath(row, path));
}

function renderRikishiLink(shikona, rikishiId) {
  if (!rikishiId) return escapeHtml(shikona || "");
  return renderSharedRikishiLink(shikona || "", rikishiId);
}

function valueAtPath(row, path) {
  const value = row?.[path];
  if (value === null || value === undefined) return "";
  return String(value);
}

function valueAlignment(presentation) {
  if (presentation === PRESENTATION.RATING || presentation === PRESENTATION.NUMERIC) return "right";
  return "left";
}

export {
  renderRatingChangesPresentationTable,
  terminalNodes,
  groupBoundaryMap,
  valueAlignment,
};

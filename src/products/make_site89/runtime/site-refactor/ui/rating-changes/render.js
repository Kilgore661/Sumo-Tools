// Rating Changes grouped table rendering.

import { escapeHtml } from "../../utils/html.js";
import { renderLabelWithHelp } from "../help.js";
import { renderRikishiLink as renderSharedRikishiLink } from "../tables/shared.js";
import {
  groupBoundaryAttributes,
  groupBoundaryMap,
  headerRows,
  terminalNodes,
} from "../tables/header-tree.js";
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

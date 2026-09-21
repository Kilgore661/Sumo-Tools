// Fastest Risers grouped table rendering.

import { escapeHtml } from "../../utils/html.js";
import {
  currentTableSortState,
  renderBashoDateLink,
  renderRikishiLink,
  renderTableHeading,
  sortRows,
  tableCellAttributes,
} from "../tables/shared.js";

function renderFastestRisersTable(artifact, model) {
  const sortState = currentTableSortState(artifact);
  const rows = sortRows(model.values || [], artifact.columns || [], sortState);
  return [
    renderFastestRisersHeader(model.header),
    '<table class="artifact-table fastest-risers-table">',
    renderFastestRisersHead(artifact, sortState),
    '<tbody>',
    rows.length
      ? rows.map(row => renderFastestRisersRow(artifact, row)).join("")
      : `<tr><td colspan="7" class="artifact-placeholder">${escapeHtml(model.empty_message)}</td></tr>`,
    '</tbody>',
    '</table>',
  ].join("");
}

function renderFastestRisersHeader(header) {
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(header?.heading || "")}</h4>`,
    header?.subheading ? `<h5>${escapeHtml(header.subheading)}</h5>` : "",
    '</div>',
  ].join("");
}

function renderFastestRisersHead(artifact, sortState) {
  const columns = new Map((artifact.columns || []).map(column => [column.id, column]));
  return [
    '<thead>',
    '<tr>',
    renderTableHeading(columns.get("position"), sortState, 'rowspan="2" data-group-start="true" data-group-end="true"'),
    renderTableHeading(columns.get("shikona"), sortState, 'rowspan="2" data-group-start="true" data-group-end="true"'),
    '<th colspan="2" data-group-start="true" data-heading-group="true">Start</th>',
    '<th colspan="2" data-group-start="true" data-heading-group="true">Destination</th>',
    renderTableHeading(columns.get("elapsed_basho"), sortState, 'rowspan="2" data-group-start="true" data-group-end="true"'),
    '</tr>',
    '<tr>',
    renderTableHeading(columns.get("start_chii"), sortState, 'data-group-start="true"'),
    renderTableHeading(columns.get("start_date"), sortState, 'data-group-end="true"'),
    renderTableHeading(columns.get("finish_chii"), sortState, 'data-group-start="true"'),
    renderTableHeading(columns.get("finish_date"), sortState, 'data-group-end="true"'),
    '</tr>',
    '</thead>',
  ].join("");
}

function renderFastestRisersRow(artifact, row) {
  return [
    '<tr>',
    ...artifact.columns.map(column => `<td ${tableCellAttributes(column)}>${fastestRisersCell(column, row)}</td>`),
    '</tr>',
  ].join("");
}

function fastestRisersCell(column, row) {
  const value = row[column.source_field || column.id];
  if (column.id === "shikona") return renderRikishiLink(value, row.rik_id);
  if (column.id === "start_date" || column.id === "finish_date") {
    return renderBashoDateLink(value);
  }
  return escapeHtml(value === null || value === undefined ? "" : String(value));
}

export {
  fastestRisersCell,
  renderFastestRisersHead,
  renderFastestRisersHeader,
  renderFastestRisersRow,
  renderFastestRisersTable,
};

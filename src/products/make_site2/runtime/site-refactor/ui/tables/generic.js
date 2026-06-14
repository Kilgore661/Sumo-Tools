// Generic indexed and sectioned table renderers.

import { escapeHtml } from "../../utils/html.js";
import {
  currentTableSortState,
  renderTableHeading,
  renderRikishiLink,
  sortRows,
  tableCellAttributes,
} from "./shared.js";

// Render a table artifact as independent section tables.
function renderSectionedTable(artifact, rows) {
  const sortState = currentTableSortState(artifact);
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    '</div>',
    '<div class="sectioned-table-grid">',
    ...artifact.sections.map(section =>
      renderTableSection(section, rows, artifact.columns || [], sortState)
    ),
    '</div>',
  ].join("");
}

function renderTableSection(section, rows, columns, sortState = null) {
  const sectionRows = sortRows(
    [...rows]
    .filter(row => String(row[section.source_field]) === String(section.source_value))
    .sort((left, right) =>
      compareValues(Number(left[section.order_by]) || 0, Number(right[section.order_by]) || 0)
    ),
    columns,
    sortState
  );
  return [
    '<section class="table-section">',
    `<h5>${escapeHtml(section.heading)}</h5>`,
    '<table class="artifact-table sectioned-table">',
    '<thead><tr>',
    ...columns.map(column => renderTableHeading(column, sortState)),
    '</tr></thead>',
    '<tbody>',
    ...sectionRows.map((row, index) => [
      '<tr>',
      ...columns.map(column =>
        `<td ${tableCellAttributes(column)}>${escapeHtml(cellValue(column, row, index))}</td>`
      ),
      '</tr>'
    ].join("")),
    '</tbody>',
    '</table>',
    '</section>',
  ].join("");
}

// Render a flat indexed-table artifact with filter-controlled column visibility.
function renderIndexedTable(artifact, rows, state) {
  const groups = new Map(artifact.column_groups.map(group => [group.id, group]));
  const visibleColumns = artifact.columns.filter(column => isColumnVisible(column, groups, state));
  const sortState = currentTableSortState(artifact);
  const sortedRows = sortRows(rows, visibleColumns, sortState);
  return [
    '<table class="artifact-table brb-table">',
    '<thead><tr>',
    ...visibleColumns.map(column => renderTableHeading(column, sortState)),
    '</tr></thead>',
    '<tbody>',
    ...sortedRows.map((row, index) => [
      '<tr>',
      ...visibleColumns.map(column => `<td ${tableCellAttributes(column)}>${escapeHtml(cellValue(column, row, index))}</td>`),
      '</tr>'
    ].join("")),
    '</tbody>',
    '</table>'
  ].join("");
}

// Render a flat sortable table artifact.
function renderGenericTable(artifact, rows, state) {
  const sortState = currentTableSortState(artifact);
  const visibleRows = genericRowsForState(rows, state, artifact);
  const sortedRows = sortRows(visibleRows, artifact.columns || [], sortState);
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    '</div>',
    '<table class="artifact-table generic-table">',
    '<thead><tr>',
    ...artifact.columns.map(column => renderTableHeading(column, sortState)),
    '</tr></thead>',
    '<tbody>',
    ...sortedRows.map((row, index) => [
      '<tr>',
      ...artifact.columns.map(column =>
        `<td ${tableCellAttributes(column)}>${genericCellValue(column, row, index)}</td>`
      ),
      '</tr>'
    ].join("")),
    '</tbody>',
    '</table>'
  ].join("");
}

function genericRowsForState(rows, state, artifact = null) {
  if (artifact?.id === "most_career_wins") return careerWinsRowsForState(rows, state);
  if (artifact?.id === "most_career_losses") return careerLossesRowsForState(rows, state);
  if (!state?.clean_only) return rows;
  return rows.filter(row => String(row.clean) === "True");
}

function careerWinsRowsForState(rows, state) {
  const includeRetired = state?.include_retired !== false;
  const suffix = state?.count_fusen_results === false ? "actual" : "all";
  const positionField = includeRetired ? `position_${suffix}` : `active_position_${suffix}`;
  return rows
    .filter(row => includeRetired || String(row.active) === "True")
    .filter(row => String(row[positionField] || "") !== "")
    .map(row => ({
      ...row,
      position: row[positionField],
      wins: row[`wins_${suffix}`],
      losses: row[`losses_${suffix}`],
      bouts: row[`bouts_${suffix}`],
      win_rate: row[`win_rate_${suffix}`],
      start: row[`start_${suffix}`],
      end: row[`end_${suffix}`],
    }));
}

function careerLossesRowsForState(rows, state) {
  const includeRetired = state?.include_retired !== false;
  const suffix = state?.count_fusen_results === false ? "actual" : "all";
  const positionField = includeRetired ? `position_${suffix}` : `active_position_${suffix}`;
  return rows
    .filter(row => includeRetired || String(row.active) === "True")
    .filter(row => String(row[positionField] || "") !== "")
    .map(row => ({
      ...row,
      position: row[positionField],
      losses: row[`losses_${suffix}`],
      wins: row[`wins_${suffix}`],
      bouts: row[`bouts_${suffix}`],
      win_rate: row[`win_rate_${suffix}`],
      start: row[`start_${suffix}`],
      end: row[`end_${suffix}`],
    }));
}

function genericCellValue(column, row, index) {
  if (column.id === "row_number") return escapeHtml(String(index + 1));
  if (column.id === "clean") return String(row[column.source_field || column.id]) === "True" ? "\u2713" : "";
  if (column.id === "win_rate") {
    const value = row[column.source_field || column.id] || "";
    return value ? `${escapeHtml(value)}%` : "";
  }
  if (column.id === "shikona") {
    return renderRikishiLink(row[column.source_field || column.id] || "", row.rikishi_id);
  }
  return escapeHtml(row[column.source_field || column.id] || "");
}

// Apply generic column/group visibility rules from the runtime manifest.
function isColumnVisible(column, groups, state) {
  if (column.always_visible) return true;
  const group = groups.get(column.group);
  if (!group) return false;
  if (group.always_visible) {
    if (column.id === "equelo" || column.id === "delta_equelo") return Boolean(state.rating_context);
    if (column.id === "nu_chii") return Boolean(state.nu_chii);
    return true;
  }
  if (group.controlling_filter_id) return Boolean(state[group.controlling_filter_id]);
  return false;
}

function cellValue(column, row, index) {
  if (column.id === "row_number") return String(index + 1);
  if (column.id === "previous_result") return resultWithMovement(
    row[column.source_field || column.id],
    row.previous_rank_level_movement,
  );
  return row[column.source_field || column.id] || "";
}

function resultWithMovement(result, movement) {
  const marker = rankLevelMovementMarker(movement);
  return [result || "", marker].filter(Boolean).join(" ");
}

function rankLevelMovementMarker(value) {
  if (value === "\u2191" || value === "\u2193") return value;
  return "";
}

function compareValues(left, right) {
  const leftNumber = Number(left);
  const rightNumber = Number(right);
  if (!Number.isNaN(leftNumber) && !Number.isNaN(rightNumber)) {
    return leftNumber - rightNumber;
  }
  return String(left).localeCompare(String(right));
}

export {
  renderSectionedTable,
  renderTableSection,
  renderIndexedTable,
  renderGenericTable,
  genericRowsForState,
  genericCellValue,
  isColumnVisible,
  cellValue,
  resultWithMovement,
  rankLevelMovementMarker,
};

import { escapeHtml } from "../../utils/html.js";
import {
  compareValues,
  currentTableSortState,
  decimal,
  renderRikishiLink,
  renderTableHeading,
  sortRows,
  tableCellAttributes,
} from "./shared.js";
import { cellValue } from "./generic.js";

function renderStandingsTable(artifact, rows, filteredRows, state) {
  const visibleColumns = standingsVisibleColumns(artifact, state);
  const meanPositions = competitionPositions(filteredRows, "selected_average_credited_wins");
  const percentPositions = competitionPositions(filteredRows, "win_percent");
  const sortState = currentTableSortState(artifact, defaultStandingsSortColumn(state));
  const sortedRows = sortRows(rows, visibleColumns, sortState);
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    '</div>',
    '<table class="artifact-table standings-table">',
    renderStandingsTableHead(artifact, visibleColumns, sortState),
    '<tbody>',
    ...sortedRows.map((row, index) => [
      '<tr>',
      ...visibleColumns.map(column =>
        `<td ${tableCellAttributes(column)}>${standingsCellValue(column, row, index, meanPositions, percentPositions)}</td>`
      ),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

function standingsVisibleColumns(artifact, state) {
  const visibleGroups = standingsVisibleGroups(state);
  return artifact.columns.filter(column =>
    column.always_visible || visibleGroups.includes(column.group)
  );
}

function standingsVisibleGroups(state) {
  if (state.metric_group_preset === "percentages") return ["identity", "wins_per_bout"];
  if (state.metric_group_preset === "combined") return ["identity", "wins_per_basho", "wins_per_bout"];
  return ["identity", "wins_per_basho"];
}

function renderStandingsTableHead(artifact, visibleColumns, sortState = null) {
  const groups = artifact.column_groups.filter(group =>
    visibleColumns.some(column => column.group === group.id)
  );
  return [
    '<thead>',
    '<tr>',
    ...groups.map(group => {
      const count = visibleColumns.filter(column => column.group === group.id).length;
      return `<th colspan="${count}">${escapeHtml(group.heading)}</th>`;
    }),
    '</tr>',
    '<tr>',
    ...visibleColumns.map(column => renderTableHeading(column, sortState)),
    '</tr>',
    '</thead>',
  ].join("");
}

function standingsCellValue(column, row, index, meanPositions, percentPositions) {
  if (column.id === "row_number") return String(index + 1);
  if (column.id === "shikona") return renderRikishiLink(row.shikona, row.rikishi_id);
  if (column.id === "selected_average_credited_wins") return decimal(row.selected_average_credited_wins, 2);
  if (column.id === "selected_average_rank") return String(meanPositions.get(String(row.rikishi_id)));
  if (column.id === "win_percent") return decimal(row.win_percent, 1);
  if (column.id === "win_percent_rank") return String(percentPositions.get(String(row.rikishi_id)));
  return escapeHtml(cellValue(column, row, index));
}

function standingsRowsForState(rows, state) {
  return rows.filter(row =>
    (state.division === "all" || standingsDivisionMatches(row.chii_ordinal, state.division)) &&
    (!state.current_only || row.is_current === "1")
  );
}

function standingsDivisionMatches(chiiOrdinal, division) {
  const level = Math.floor(Number(chiiOrdinal) / 100000);
  if (division === "makuuchi") return level >= 0 && level <= 4;
  if (division === "juryo") return level === 5;
  if (division === "makushita") return level === 6;
  if (division === "sandanme") return level === 7;
  if (division === "jonidan") return level === 8;
  if (division === "jonokuchi") return level === 9;
  return true;
}

function sortedStandingsRows(rows, state) {
  const sortField = state.metric_group_preset === "standard"
    ? "selected_average_credited_wins"
    : "win_percent";
  return [...rows].sort((left, right) => compareValues(right[sortField], left[sortField]));
}

function defaultStandingsSortColumn(state) {
  return state.metric_group_preset === "standard"
    ? "selected_average_credited_wins"
    : "win_percent";
}

function competitionPositions(rows, field) {
  const ordered = [...rows].sort((left, right) => compareValues(right[field], left[field]));
  const positions = new Map();
  let previousValue = null;
  let previousPosition = 0;
  for (const [index, row] of ordered.entries()) {
    const value = row[field];
    const position = index > 0 && compareValues(value, previousValue) === 0
      ? previousPosition
      : index + 1;
    previousValue = value;
    previousPosition = position;
    positions.set(String(row.rikishi_id), position);
  }
  return positions;
}

export {
  renderStandingsTable,
  standingsVisibleColumns,
  standingsVisibleGroups,
  renderStandingsTableHead,
  standingsCellValue,
  standingsRowsForState,
  standingsDivisionMatches,
  sortedStandingsRows,
  defaultStandingsSortColumn,
  competitionPositions,
};

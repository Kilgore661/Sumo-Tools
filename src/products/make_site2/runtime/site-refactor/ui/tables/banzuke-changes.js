// Banzuke Changes table renderers and scan-table sort values.

import { escapeHtml } from "../../utils/html.js";
import {
  compareNullableSortValues,
  firstSortableColumn,
  isSortableColumn,
  recordWins,
  renderRikishiLink,
  renderTableHeading,
  sortDefaultDirection,
  tableCellAttributes,
  tableSortStates,
} from "./shared.js";

// Render Banzuke Changes in either banzuke-style or scan-table form.
function renderBanzukeChangesTable(artifact, rows, state, config) {
  const title = config.title || artifact.heading;
  const table = state.banzuke_style
    ? renderBanzukeStyleTable(rows, state)
    : renderBanzukeScanTable(artifact, rows, state);
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(title)}</h4>`,
    '</div>',
    table,
  ].join("");
}

// Render the East/West banzuke-shaped report view.
function renderBanzukeStyleTable(rows, state) {
  const eastColumns = banzukeSideColumns("east", state);
  const westColumns = banzukeSideColumns("west", state);
  return [
    '<table class="artifact-table banzuke-changes-table">',
    '<thead>',
    '<tr>',
    `<th colspan="${eastColumns.length}">East</th>`,
    '<th rowspan="2">Rank</th>',
    `<th colspan="${westColumns.length}">West</th>`,
    '</tr>',
    '<tr>',
    ...eastColumns.map(column => `<th>${escapeHtml(column.heading)}</th>`),
    ...westColumns.map(column => `<th>${escapeHtml(column.heading)}</th>`),
    '</tr>',
    '</thead>',
    '<tbody>',
    ...rows.map(row => [
      '<tr>',
      ...eastColumns.map(column => renderBanzukeSideCell(row, column)),
      `<td scope="row">${escapeHtml(row.bz_chii)}</td>`,
      ...westColumns.map(column => renderBanzukeSideCell(row, column)),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

// Render the sortable row-scan report view.
function renderBanzukeScanTable(artifact, rows, state) {
  const columns = banzukeScanColumns(state);
  const sortState = currentBanzukeScanSortState(artifact, columns);
  const sideRows = sortBanzukeScanRows(
    rows.flatMap(row => ["east", "west"].map(side => ({ row, side })))
      .filter(item => item.row[`${item.side}_rikishi_id`]),
    columns,
    sortState
  );
  return [
    '<table class="artifact-table banzuke-changes-table">',
    '<thead>',
    '<tr>',
    ...columns.map(column => renderTableHeading(column, sortState)),
    '</tr>',
    '</thead>',
    '<tbody>',
    ...sideRows.map(({ row, side }) => [
      '<tr>',
      ...columns.map(column => renderBanzukeScanCell(row, side, column)),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

function banzukeSideColumns(side, state) {
  const identity = { id: "shikona", heading: "Shikona", side };
  const direction = { id: "direction", heading: "â‡…", side };
  const columns = [];

  if (state.equelo) columns.push({ id: "equelo", heading: "Equelo", side });
  if (state.context) {
    columns.push({ id: "old_chii", heading: "Previous Chii", side });
    columns.push({ id: "result", heading: "Result", side });
  }
  columns.push(direction);
  if (state.delta) columns.push({ id: "delta", heading: "Delta", side });

  if (side === "east") return [...columns, identity];
  return [identity, ...columns.reverse()];
}

function banzukeScanColumns(state) {
  const columns = [
    { id: "chii", heading: "Chii", sort_kind: "chii_ordinal" },
    { id: "shikona", heading: "Shikona", sort_kind: "text" },
    { id: "direction", heading: "â‡…", sort_kind: "text" },
  ];
  if (state.delta) columns.push({ id: "delta", heading: "Delta", sort_kind: "numeric" });
  if (state.context) {
    columns.push({ id: "result", heading: "Result", sort_kind: "record" });
    columns.push({ id: "old_chii", heading: "Previous Chii", sort_kind: "chii_ordinal" });
  }
  if (state.equelo) columns.push({ id: "equelo", heading: "Equelo", sort_kind: "numeric" });
  return columns;
}

function renderBanzukeSideCell(row, column) {
  const rikishiId = row[`${column.side}_rikishi_id`];
  const attributes = banzukeCellAttributes(column.id);
  if (!rikishiId) return `<td${attributes}></td>`;
  return `<td${attributes}>${banzukeSideValue(row, column.side, column.id)}</td>`;
}

function renderBanzukeScanCell(row, side, column) {
  return `<td${banzukeCellAttributes(column.id)}>${banzukeSideValue(row, side, column.id)}</td>`;
}

function currentBanzukeScanSortState(artifact, columns) {
  const existing = tableSortStates.get(artifact.id);
  if (existing && columns.some(column => column.id === existing.columnId)) return existing;
  const column = columns.find(item => item.id === "chii") || firstSortableColumn(columns);
  return {
    columnId: column?.id || "",
    direction: sortDefaultDirection(column),
  };
}

// Sort flattened East/West scan rows using Banzuke Changes column semantics.
function sortBanzukeScanRows(rows, columns, sortState) {
  const column = columns.find(item => item.id === sortState?.columnId);
  if (!isSortableColumn(column)) return [...rows];
  const multiplier = sortState.direction === "descending" ? -1 : 1;
  return [...rows].sort((left, right) =>
    compareNullableSortValues(
      banzukeScanSortValue(column, left),
      banzukeScanSortValue(column, right),
      column,
      multiplier
    )
  );
}

function banzukeScanSortValue(column, item) {
  const { row, side } = item;
  if (column.id === "chii") return banzukeChiiOrdinal(row.bz_chii, side);
  if (column.id === "old_chii") return banzukeChiiOrdinal(row[`${side}_old_chii`], side);
  if (column.id === "result") return recordWins(row[`${side}_result`]);
  if (column.id === "direction") return movementDirection(row[`${side}_delta`]);
  if (column.id === "shikona") return row[`${side}_shikona`] || "";
  if (column.id === "delta" || column.id === "equelo") {
    const number = Number(row[`${side}_${column.id}`]);
    return Number.isNaN(number) ? null : number;
  }
  return row[`${side}_${column.id}`] || "";
}

function banzukeChiiOrdinal(chii, side) {
  const match = String(chii || "").match(/^([A-Za-z]+)(\d+)?([ew])?/i);
  if (!match) return null;
  const levelOrder = { Y: 0, O: 1, S: 2, K: 3, M: 4, J: 5, Ms: 6, Sd: 7, Jd: 8, Jk: 9 };
  const level = levelOrder[match[1]];
  if (level === undefined) return null;
  const number = Number(match[2] || 1);
  const explicitSide = String(match[3] || "").toLowerCase();
  const sideOffset = explicitSide ? (explicitSide === "w" ? 1 : 0) : (side === "west" ? 1 : 0);
  return level * 100000 + number * 2 + sideOffset;
}

function banzukeCellAttributes(columnId) {
  return columnId === "shikona" ? ' data-column-id="shikona"' : "";
}

function movementDirection(value) {
  if (String(value).startsWith("+")) return "â†‘";
  if (String(value).startsWith("-")) return "â†“";
  return "";
}

function banzukeSideValue(row, side, columnId) {
  if (columnId === "chii") return escapeHtml(row[`${side}_chii`]);
  if (columnId === "shikona") {
    return renderRikishiLink(
      row[`${side}_shikona`],
      row[`${side}_rikishi_id`],
    );
  }
  if (columnId === "result") {
    const result = row[`${side}_result`];
    const movement = row[`${side}_result_movement`];
    return escapeHtml([result, movement].filter(Boolean).join(" "));
  }
  if (columnId === "direction") {
    return movementDirection(row[`${side}_delta`]);
  }
  return escapeHtml(row[`${side}_${columnId}`]);
}

export {
  renderBanzukeChangesTable,
  renderBanzukeStyleTable,
  renderBanzukeScanTable,
  banzukeSideColumns,
  banzukeScanColumns,
  renderBanzukeSideCell,
  renderBanzukeScanCell,
  currentBanzukeScanSortState,
  sortBanzukeScanRows,
  banzukeScanSortValue,
  banzukeChiiOrdinal,
  banzukeCellAttributes,
  movementDirection,
  banzukeSideValue,
};

// Banzuke Changes table renderers and scan-table sort values.

import { escapeHtml } from "../../utils/html.js";
import { renderLabelWithHelp } from "../help.js";
import {
  compareNullableSortValues,
  firstSortableColumn,
  isSortableColumn,
  recordWins,
  renderRikishiLink,
  renderTableHeading,
  sortDefaultDirection,
  tableSortStates,
} from "./shared.js";

// Render Banzuke Changes in either banzuke-style or scan-table form.
function renderBanzukeChangesTable(artifact, rows, state, config) {
  const title = banzukeTitle(config) || artifact.heading;
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

function banzukeTitle(config) {
  if (!config.current_date) return config.title || "";
  const [yearText, monthText] = String(config.current_date).split("/");
  const year = Number(yearText);
  const month = Number(monthText);
  if (!year || !month) return config.title || "";
  const monthName = new Date(year, month - 1, 1)
    .toLocaleString("en-GB", { month: "long" });
  return `The ${monthName} ${year} Banzuke`;
}

// Render the East/West banzuke-shaped report view.
function renderBanzukeStyleTable(rows, state) {
  const rowNumberColumn = banzukeRowNumberColumn();
  const eastColumns = banzukeSideColumns("east", state);
  const westColumns = banzukeSideColumns("west", state);
  return [
    '<table class="artifact-table banzuke-changes-table">',
    '<thead>',
    '<tr>',
    `<th rowspan="2" ${banzukeGroupAttributes(rowNumberColumn.id, "only")}>${escapeHtml(rowNumberColumn.heading)}</th>`,
    `<th colspan="${eastColumns.length}" ${banzukeGroupAttributes("east", "only")}>East</th>`,
    `<th rowspan="2" ${banzukeGroupAttributes("rank", "only")}>Rank</th>`,
    `<th colspan="${westColumns.length}" ${banzukeGroupAttributes("west", "only")}>West</th>`,
    '</tr>',
    '<tr>',
    ...eastColumns.map(column => `<th>${renderLabelWithHelp(column.heading, column.help, { noteId: column.note_id })}</th>`),
    ...westColumns.map(column => `<th>${renderLabelWithHelp(column.heading, column.help, { noteId: column.note_id })}</th>`),
    '</tr>',
    '</thead>',
    '<tbody>',
    ...rows.map((row, index) => [
      '<tr>',
      renderBanzukeStyleRowNumberCell(index),
      ...eastColumns.map((column, columnIndex) =>
        renderBanzukeSideCell(row, column, banzukeGroupPosition(columnIndex, eastColumns.length))
      ),
      `<td scope="row" ${banzukeGroupAttributes("rank", "only")}>${escapeHtml(row.bz_chii)}</td>`,
      ...westColumns.map((column, columnIndex) =>
        renderBanzukeSideCell(row, column, banzukeGroupPosition(columnIndex, westColumns.length))
      ),
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
    ...sideRows.map(({ row, side }, index) => [
      '<tr>',
      ...columns.map(column => renderBanzukeScanCell(row, side, column, index)),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

function banzukeSideColumns(side, state) {
  const identity = { id: "shikona", heading: "Shikona", help: "Rikishi fighting name.", side };
  const direction = { id: "direction", heading: "⇅", help: "Banzuke movement.", side };
  const columns = [];

  if (state.equelo) columns.push({ id: "equelo", heading: "Equelo", help: "Model rating. See Ratings & Models.", side });
  if (state.context) {
    columns.push({ id: "old_chii", heading: "Previous Chii", side });
    columns.push({ id: "result", heading: "Result", help: "Result movement means rank-group movement. See Notes.", note_id: "note_result", side });
  }
  columns.push(direction);
  if (state.delta) columns.push({ id: "delta", heading: "Delta", help: "Size of movement. See Notes.", note_id: "note_delta", side });

  if (side === "east") return [...columns, identity];
  return [identity, ...columns.reverse()];
}

function banzukeScanColumns(state) {
  const columns = [
    banzukeRowNumberColumn(),
    { id: "chii", heading: "Chii", sort_kind: "chii_ordinal" },
    { id: "shikona", heading: "Shikona", help: "Rikishi fighting name.", sort_kind: "text" },
    { id: "direction", heading: "⇅", help: "Banzuke movement.", sort_kind: "text" },
  ];
  if (state.delta) columns.push({ id: "delta", heading: "Delta", help: "Size of movement. See Notes.", note_id: "note_delta", sort_kind: "numeric" });
  if (state.context) {
    columns.push({ id: "result", heading: "Result", help: "Result movement means rank-group movement. See Notes.", note_id: "note_result", sort_kind: "record" });
    columns.push({ id: "old_chii", heading: "Previous Chii", sort_kind: "chii_ordinal" });
  }
  if (state.equelo) columns.push({ id: "equelo", heading: "Equelo", help: "Model rating. See Ratings & Models.", sort_kind: "numeric" });
  return columns;
}

function banzukeRowNumberColumn() {
  return { id: "row_number", heading: "", sort_kind: "none", align: "right" };
}

function renderBanzukeStyleRowNumberCell(index) {
  return `<td ${banzukeGroupAttributes("row_number", "only")}>${escapeHtml(String(index + 1))}</td>`;
}

function renderBanzukeSideCell(row, column, groupPosition = "") {
  const rikishiId = row[`${column.side}_rikishi_id`];
  const attributes = banzukeCellAttributes(column.id, groupPosition);
  if (!rikishiId) return `<td${attributes}></td>`;
  return `<td${attributes}>${banzukeSideValue(row, column.side, column.id)}</td>`;
}

function renderBanzukeScanCell(row, side, column, index) {
  if (column.id === "row_number") {
    return `<td${banzukeCellAttributes(column.id)}>${escapeHtml(String(index + 1))}</td>`;
  }
  return `<td${banzukeCellAttributes(column.id)}>${banzukeSideValue(row, side, column.id)}</td>`;
}

function currentBanzukeScanSortState(artifact, columns) {
  const existing = tableSortStates.get(artifact.id);
  const existingColumn = columns.find(column => column.id === existing?.columnId);
  if (existingColumn && isSortableColumn(existingColumn)) return existing;
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
  if (column.id === "row_number") return null;
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

function banzukeCellAttributes(columnId, groupPosition = "") {
  const attributes = [];
  if (columnId === "row_number" || columnId === "shikona") {
    attributes.push(`data-column-id="${escapeHtml(columnId)}"`);
  }
  if (groupPosition) attributes.push(...banzukeGroupBoundaryAttributes(groupPosition));
  return attributes.length ? ` ${attributes.join(" ")}` : "";
}

function banzukeGroupAttributes(id, groupPosition) {
  return [
    `data-column-id="${escapeHtml(id)}"`,
    ...banzukeGroupBoundaryAttributes(groupPosition),
  ].join(" ");
}

function banzukeGroupBoundaryAttributes(groupPosition) {
  if (groupPosition === "only") return ['data-group-start="true"', 'data-group-end="true"'];
  if (groupPosition === "start") return ['data-group-start="true"'];
  if (groupPosition === "end") return ['data-group-end="true"'];
  return [];
}

function banzukeGroupPosition(index, count) {
  if (count === 1) return "only";
  if (index === 0) return "start";
  if (index === count - 1) return "end";
  return "";
}

function movementDirection(value) {
  if (String(value).startsWith("+")) return "↑";
  if (String(value).startsWith("-")) return "↓";
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
  banzukeTitle,
  renderBanzukeStyleTable,
  renderBanzukeScanTable,
  banzukeSideColumns,
  banzukeScanColumns,
  banzukeRowNumberColumn,
  renderBanzukeStyleRowNumberCell,
  renderBanzukeSideCell,
  renderBanzukeScanCell,
  currentBanzukeScanSortState,
  sortBanzukeScanRows,
  banzukeScanSortValue,
  banzukeChiiOrdinal,
  banzukeCellAttributes,
  banzukeGroupAttributes,
  banzukeGroupBoundaryAttributes,
  banzukeGroupPosition,
  movementDirection,
  banzukeSideValue,
};

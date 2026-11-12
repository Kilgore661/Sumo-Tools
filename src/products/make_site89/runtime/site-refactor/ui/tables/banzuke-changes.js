// Banzuke Changes table renderers and scan-table sort values.

import { escapeHtml } from "../../utils/html.js";
import { renderLabelWithHelp } from "../help.js";
import {
  groupBoundaryMap,
  headerRows,
  terminalNodes,
} from "./header-tree.js";
import {
  compareNullableSortValues,
  annotatedShikona,
  firstSortableColumn,
  isSortableColumn,
  recordWins,
  renderRikishiLink,
  renderTableHeading,
  sortDefaultDirection,
  tableSortStates,
} from "./shared.js";

const BANZUKE_SCAN_TABLE_SPEC = [
  { key: "row_number", ...banzukeRowNumberColumn() },
  { key: "chii", id: "chii", label: "Chii", heading: "Chii", sort_kind: "chii_ordinal" },
  { key: "shikona", id: "shikona", label: "Shikona", heading: "Shikona", help: "Rikishi fighting name. See Notes.", note_id: "note_annotations", sort_kind: "text" },
  { key: "delta", id: "delta", label: "ΔBz", heading: "ΔBz", help: "Banzuke movement. See Notes.", note_id: "note_delta", sort_kind: "numeric", align: "right" },
  { key: "rating", id: "rating", label: "Elo-89", heading: "Elo-89", help: "Model rating at the start of this basho. See Ratings & Models.", sort_kind: "numeric", align: "right" },
  {
    key: "previous_basho",
    label: "Previous Basho",
    children: [
      { key: "old_chii", id: "old_chii", label: "Chii", heading: "Chii", sort_kind: "chii_ordinal" },
      { key: "result", id: "result", label: "Result", heading: "Result", help: "Result movement means rank-group movement. See Notes.", note_id: "note_result", sort_kind: "record" },
    ],
  },
  {
    key: "ratings_fit",
    label: "Ratings Fit",
    children: [
      { key: "delta_chii", id: "delta_chii", label: "ΔChii", heading: "ΔChii", help: "Difference between official and Elo-89 order. See Notes.", note_id: "note_delta_chii", sort_kind: "numeric", align: "right" },
      { key: "nu_chii", id: "nu_chii", label: "νChii", heading: "νChii", help: "Official slot assigned by Elo-89 order. See Notes.", note_id: "note_nu_chii", sort_kind: "chii_ordinal" },
    ],
  },
];

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
  const ratingsFit = buildBanzukeRatingsFit(rows);
  const hasSubgroups = state.ratings_fit || state.context;
  const headingRowspan = hasSubgroups ? 3 : 2;
  return [
    '<table class="artifact-table banzuke-changes-table">',
    '<thead>',
    '<tr>',
    `<th rowspan="${headingRowspan}" ${banzukeGroupAttributes(rowNumberColumn.id, "only")}>${escapeHtml(rowNumberColumn.heading)}</th>`,
    `<th colspan="${eastColumns.length}" ${banzukeGroupAttributes("east", "only")}>East</th>`,
    `<th rowspan="${headingRowspan}" ${banzukeGroupAttributes("rank", "only")}>Rank</th>`,
    `<th colspan="${westColumns.length}" ${banzukeGroupAttributes("west", "only")}>West</th>`,
    '</tr>',
    '<tr>',
    ...renderBanzukeStyleSecondHeadingRow(eastColumns),
    ...renderBanzukeStyleSecondHeadingRow(westColumns),
    '</tr>',
    ...(hasSubgroups ? [
      '<tr>',
      ...eastColumns.filter(isBanzukeStyleGroupedColumn).map(column => renderBanzukeStyleHeadingCell(column)),
      ...westColumns.filter(isBanzukeStyleGroupedColumn).map(column => renderBanzukeStyleHeadingCell(column)),
      '</tr>',
    ] : []),
    '</thead>',
    '<tbody>',
    ...rows.map((row, index) => [
      '<tr>',
      renderBanzukeStyleRowNumberCell(index),
      ...eastColumns.map((column, columnIndex) =>
        renderBanzukeSideCell(row, column, banzukeGroupPosition(columnIndex, eastColumns.length), ratingsFit)
      ),
      `<td scope="row" ${banzukeGroupAttributes("rank", "only")}>${escapeHtml(row.bz_chii)}</td>`,
      ...westColumns.map((column, columnIndex) =>
        renderBanzukeSideCell(row, column, banzukeGroupPosition(columnIndex, westColumns.length), ratingsFit)
      ),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

// Render the sortable row-scan report view.
function renderBanzukeScanTable(artifact, rows, state) {
  const visiblePaths = banzukeScanVisiblePaths(state);
  const columns = banzukeScanColumns(state);
  const boundaries = groupBoundaryMap(BANZUKE_SCAN_TABLE_SPEC, visiblePaths, columns);
  const sortState = currentBanzukeScanSortState(artifact, columns);
  const ratingsFit = buildBanzukeRatingsFit(rows);
  const sideRows = sortBanzukeScanRows(
    rows.flatMap(row => ["east", "west"].map(side => ({
      row,
      side,
      ratingsFit: ratingsFit.get(row[`${side}_rikishi_id`]),
    })))
      .filter(item => item.row[`${item.side}_rikishi_id`]),
    columns,
    sortState
  );
  return [
    '<table class="artifact-table banzuke-changes-table">',
    renderBanzukeScanHead(visiblePaths, columns, sortState, boundaries),
    '<tbody>',
    ...sideRows.map(({ row, side, ratingsFit: rowRatingsFit }, index) => [
      '<tr>',
      ...columns.map(column => renderBanzukeScanCell(
        row,
        side,
        column,
        index,
        boundaries.position(column.path),
        rowRatingsFit,
      )),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}

function renderBanzukeScanHead(visiblePaths, columns, sortState, boundaries) {
  const columnsByPath = new Map(columns.map(column => [column.path, column]));
  const headingSpec = banzukeScanHeadingSpec(visiblePaths);
  return [
    '<thead>',
    ...headerRows(headingSpec, visiblePaths).map(row => [
      '<tr>',
      ...row.map(cell => renderBanzukeScanHeadingCell(
        cell,
        columnsByPath.get(cell.path),
        sortState,
        boundaries,
      )),
      '</tr>',
    ].join("")),
    '</thead>',
  ].join("");
}

function banzukeScanHeadingSpec(_visiblePaths) {
  return BANZUKE_SCAN_TABLE_SPEC;
}

function renderBanzukeScanHeadingCell(cell, column, sortState, boundaries) {
  const groupPosition = cell.is_group ? "only" : boundaries.position(cell.path);
  const attributes = [
    `colspan="${cell.colspan}"`,
    `rowspan="${cell.rowspan}"`,
    `data-column-path="${escapeHtml(cell.path)}"`,
    ...banzukeGroupBoundaryAttributes(groupPosition),
  ];
  if (cell.is_group) {
    attributes.push('data-heading-group="true"');
    return `<th ${attributes.join(" ")}>${renderLabelWithHelp(cell.label, cell.help, { noteId: cell.note_id })}</th>`;
  }
  return renderTableHeading(column, sortState, attributes.join(" "));
}

function renderBanzukeStyleSecondHeadingRow(columns) {
  if (!columns.some(isBanzukeStyleGroupedColumn)) {
    return columns.map(column => renderBanzukeStyleHeadingCell(column));
  }
  const rendered = [];
  const renderedGroups = new Set();
  for (const column of columns) {
    if (isBanzukeStyleGroupedColumn(column)) {
      if (!renderedGroups.has(column.heading_group)) {
        const groupColumns = columns.filter(
          candidate => candidate.heading_group === column.heading_group
        );
        rendered.push(
          `<th colspan="${groupColumns.length}" data-column-id="${escapeHtml(column.heading_group)}">`
          + escapeHtml(column.heading_group_label)
          + '</th>'
        );
        renderedGroups.add(column.heading_group);
      }
      continue;
    }
    const attributes = banzukeCellAttributeParts(column);
    rendered.push(
      `<th rowspan="2" ${attributes.join(" ")}>`
      + renderLabelWithHelp(column.heading, column.help, { noteId: column.note_id })
      + '</th>'
    );
  }
  return rendered;
}

function isBanzukeStyleGroupedColumn(column) {
  return Boolean(column.heading_group);
}

function banzukeSideColumns(side, state) {
  const identity = { id: "shikona", heading: "Shikona", help: "Rikishi fighting name. See Notes.", note_id: "note_annotations", side };
  const delta = { id: "delta", heading: "ΔBz", help: "Banzuke movement. See Notes.", note_id: "note_delta", side, align: "right" };
  const ratingsFit = [
    { id: "delta_chii", heading: "ΔChii", help: "Difference between official and Elo-89 order. See Notes.", note_id: "note_delta_chii", side, align: "right", heading_group: "ratings_fit", heading_group_label: "Ratings Fit" },
    { id: "nu_chii", heading: "νChii", help: "Official slot assigned by Elo-89 order. See Notes.", note_id: "note_nu_chii", side, heading_group: "ratings_fit", heading_group_label: "Ratings Fit" },
  ];
  const columns = state.ratings_fit ? [...ratingsFit] : [];

  if (state.rating) columns.push({ id: "rating", heading: "Elo-89", help: "Model rating. See Ratings & Models.", side, align: "right" });
  if (state.context) {
    columns.push({ id: "old_chii", heading: "Chii", side, heading_group: "previous_basho", heading_group_label: "Previous Basho" });
    columns.push({ id: "result", heading: "Result", help: "Result movement means rank-group movement. See Notes.", note_id: "note_result", side, heading_group: "previous_basho", heading_group_label: "Previous Basho" });
  }
  if (state.delta_bz) columns.push(delta);
  columns.push(identity);

  return side === "east" ? columns : [...columns].reverse();
}

function banzukeScanColumns(state) {
  return terminalNodes(BANZUKE_SCAN_TABLE_SPEC, [], banzukeScanVisiblePaths(state));
}

function banzukeScanVisiblePaths(state) {
  const paths = new Set(["row_number", "chii", "shikona"]);
  if (state.delta_bz) paths.add("delta");
  if (state.rating) paths.add("rating");
  if (state.context) {
    paths.add("previous_basho.result");
    paths.add("previous_basho.old_chii");
  }
  if (state.ratings_fit) {
    paths.add("ratings_fit.delta_chii");
    paths.add("ratings_fit.nu_chii");
  }
  return paths;
}

function banzukeRowNumberColumn() {
  return { id: "row_number", heading: "", sort_kind: "none", align: "right" };
}

function renderBanzukeStyleRowNumberCell(index) {
  return `<td ${banzukeGroupAttributes("row_number", "only", "right")}>${escapeHtml(String(index + 1))}</td>`;
}

function renderBanzukeSideCell(row, column, groupPosition = "", ratingsFit = new Map()) {
  const rikishiId = row[`${column.side}_rikishi_id`];
  const attributes = banzukeCellAttributes(column, groupPosition);
  if (!rikishiId) return `<td${attributes}></td>`;
  return `<td${attributes}>${banzukeSideValue(row, column.side, column.id, ratingsFit.get(rikishiId))}</td>`;
}

function renderBanzukeScanCell(row, side, column, index, groupPosition = "", ratingsFit = null) {
  if (column.id === "row_number") {
    return `<td${banzukeCellAttributes(column, groupPosition)}>${escapeHtml(String(index + 1))}</td>`;
  }
  return `<td${banzukeCellAttributes(column, groupPosition)}>${banzukeSideValue(row, side, column.id, ratingsFit)}</td>`;
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
  const { row, side, ratingsFit } = item;
  if (column.id === "row_number") return null;
  if (column.id === "chii") return banzukeChiiOrdinal(row.bz_chii, side);
  if (column.id === "old_chii") return banzukeChiiOrdinal(row[`${side}_old_chii`], side);
  if (column.id === "result") return recordWins(row[`${side}_result`]);
  if (column.id === "shikona") return row[`${side}_shikona`] || "";
  if (column.id === "delta_chii") return ratingsFit?.signedError ?? null;
  if (column.id === "nu_chii") return ratingsFit?.nuChiiOrdinal ?? null;
  if (column.id === "delta" || column.id === "rating") {
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

function renderBanzukeStyleHeadingCell(column) {
  const attributes = banzukeCellAttributeParts(column);
  return `<th ${attributes.join(" ")}>${renderLabelWithHelp(column.heading, column.help, { noteId: column.note_id })}</th>`;
}

function banzukeCellAttributes(column, groupPosition = "") {
  const attributes = banzukeCellAttributeParts(column);
  if (groupPosition) attributes.push(...banzukeGroupBoundaryAttributes(groupPosition));
  return attributes.length ? ` ${attributes.join(" ")}` : "";
}

function banzukeCellAttributeParts(column) {
  const columnId = typeof column === "string" ? column : column.id;
  const align = typeof column === "string" ? "" : column.align;
  const attributes = [`data-column-id="${escapeHtml(columnId)}"`];
  if (align) attributes.push(`data-align="${escapeHtml(align)}"`);
  return attributes;
}

function banzukeGroupAttributes(id, groupPosition, align = "") {
  const attributes = [
    `data-column-id="${escapeHtml(id)}"`,
    ...banzukeGroupBoundaryAttributes(groupPosition),
  ];
  if (align) attributes.push(`data-align="${escapeHtml(align)}"`);
  return attributes.join(" ");
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

function banzukeDeltaDisplay(value) {
  const text = String(value ?? "").trim();
  if (text.startsWith("+")) return `↑${text.slice(1)}`;
  if (text.startsWith("-")) return `↓${text.slice(1)}`;
  return text;
}

function banzukeDeltaHtml(value) {
  const display = banzukeDeltaDisplay(value);
  const match = display.match(/^([↑↓])(.*)$/);
  if (!match) return escapeHtml(display);
  return `<span class="banzuke-inline-arrow">${match[1]}</span> ${escapeHtml(match[2])}`;
}

function buildBanzukeRatingsFit(rows) {
  const candidates = rows.flatMap(row => ["east", "west"].map(side => {
    const rikishiId = row[`${side}_rikishi_id`];
    const chii = row[`${side}_chii`];
    const ratingText = String(row[`${side}_rating`] ?? "").trim();
    const rating = Number(ratingText);
    const chiiOrdinal = banzukeChiiOrdinal(chii, side);
    if (!rikishiId || !ratingText || Number.isNaN(rating) || chiiOrdinal === null) {
      return null;
    }
    return { rikishiId, chii, chiiOrdinal, rating };
  })).filter(Boolean);

  const byBanzuke = [...candidates].sort((left, right) =>
    left.chiiOrdinal - right.chiiOrdinal || left.rating - right.rating
  );
  const byRating = [...candidates].sort((left, right) =>
    right.rating - left.rating || left.chiiOrdinal - right.chiiOrdinal
  );
  const banzukePositions = new Map();
  const ratingPositions = new Map();
  byBanzuke.forEach((item, index) => banzukePositions.set(item.rikishiId, index + 1));
  byRating.forEach((item, index) => ratingPositions.set(item.rikishiId, index + 1));

  const values = new Map();
  for (const item of candidates) {
    const banzukePosition = banzukePositions.get(item.rikishiId);
    const ratingPosition = ratingPositions.get(item.rikishiId);
    const nuChiiSlot = byBanzuke[ratingPosition - 1];
    values.set(item.rikishiId, {
      signedError: banzukePosition - ratingPosition,
      nuChii: nuChiiSlot.chii,
      nuChiiOrdinal: nuChiiSlot.chiiOrdinal,
    });
  }
  return values;
}

function ratingsFitErrorHtml(signedError) {
  if (signedError === null || signedError === undefined || signedError === 0) {
    return "";
  }
  const signedText = signedError > 0 ? `+${signedError}` : String(signedError);
  return banzukeDeltaHtml(signedText);
}

function banzukeResultHtml(result, movement) {
  const resultText = String(result ?? "");
  const movementText = String(movement ?? "");
  if (!movementText) return escapeHtml(resultText);
  const separator = resultText ? " " : "";
  return `${escapeHtml(resultText)}${separator}<span class="banzuke-inline-arrow">${escapeHtml(movementText)}</span>`;
}

function banzukeSideValue(row, side, columnId, ratingsFit = null) {
  if (columnId === "chii") return escapeHtml(row[`${side}_chii`]);
  if (columnId === "shikona") {
    return annotatedShikona(
      row[`${side}_shikona`],
      row[`${side}_rikishi_id`],
      {
        highestChii: row[`${side}_highest_chii`],
        promotionKind: row[`${side}_promotion_kind`],
        promotionStatus: row[`${side}_promotion_status`],
        promotionRequired: row[`${side}_promotion_required`],
        promotionPreviousResult: row[`${side}_promotion_previous_result`],
      },
    );
  }
  if (columnId === "result") {
    const result = row[`${side}_result`];
    const movement = row[`${side}_result_movement`];
    return banzukeResultHtml(result, movement);
  }
  if (columnId === "delta") {
    return banzukeDeltaHtml(row[`${side}_delta`]);
  }
  if (columnId === "delta_chii") {
    return ratingsFitErrorHtml(ratingsFit?.signedError);
  }
  if (columnId === "nu_chii") {
    return escapeHtml(ratingsFit?.nuChii || "");
  }
  return escapeHtml(row[`${side}_${columnId}`]);
}

export {
  renderBanzukeChangesTable,
  banzukeTitle,
  renderBanzukeStyleTable,
  renderBanzukeScanTable,
  renderBanzukeScanHead,
  renderBanzukeScanHeadingCell,
  renderBanzukeStyleSecondHeadingRow,
  banzukeSideColumns,
  banzukeScanColumns,
  banzukeScanVisiblePaths,
  BANZUKE_SCAN_TABLE_SPEC,
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
  banzukeDeltaDisplay,
  banzukeDeltaHtml,
  buildBanzukeRatingsFit,
  ratingsFitErrorHtml,
  banzukeResultHtml,
  banzukeSideValue,
};

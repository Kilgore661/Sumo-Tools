import { escapeHtml } from "../utils/html.js";

const tableSortStates = new Map();

function renderSectionedTable(artifact, rows) {
  const sortState = tableSortStates.get(artifact.id) || null;
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
  const direction = { id: "direction", heading: "⇅", side };
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
    { id: "direction", heading: "⇅", sort_kind: "text" },
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
function renderRikishiLink(shikona, rikishiId) {
  if (!rikishiId) return "";
  return [
    `<a href="https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(rikishiId)}"`,
    ' target="_blank" rel="noopener">',
    escapeHtml(shikona),
    '</a>',
  ].join("");
}
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
function decimal(value, places) {
  return Number(value).toFixed(places);
}
function compareValues(left, right) {
  const leftNumber = Number(left);
  const rightNumber = Number(right);
  if (!Number.isNaN(leftNumber) && !Number.isNaN(rightNumber)) {
    return leftNumber - rightNumber;
  }
  return String(left).localeCompare(String(right));
}
function currentTableSortState(artifact, fallbackColumnId = null) {
  const existing = tableSortStates.get(artifact.id);
  if (existing) return existing;
  const columnId = fallbackColumnId || artifact.default_sort_column || firstSortableColumn(artifact.columns || [])?.id || "";
  const column = (artifact.columns || []).find(item => item.id === columnId);
  return {
    columnId,
    direction: !fallbackColumnId && artifact.default_sort_descending ? "descending" : sortDefaultDirection(column),
  };
}
function firstSortableColumn(columns) {
  return columns.find(column => isSortableColumn(column));
}
function isSortableColumn(column) {
  return Boolean(column) && column.sort_kind !== "none";
}
function sortDefaultDirection(column) {
  if (!column) return "ascending";
  if (column.sort_default_direction) return column.sort_default_direction;
  if (column.sort_kind === "text" || column.sort_kind === "chii_ordinal") return "ascending";
  return "descending";
}
function sortRows(rows, columns, sortState) {
  const column = columns.find(item => item.id === sortState?.columnId);
  if (!isSortableColumn(column)) return [...rows];
  const multiplier = sortState.direction === "descending" ? -1 : 1;
  return [...rows].sort((left, right) => compareNullableSortValues(sortValue(column, left), sortValue(column, right), column, multiplier));
}
function compareNullableSortValues(left, right, column, multiplier) {
  if (left === null && right === null) return 0;
  if (left === null) return 1;
  if (right === null) return -1;
  return multiplier * compareSortValues(left, right, column);
}
function compareSortValues(left, right, column) {
  if (column.sort_kind === "text") return String(left).localeCompare(String(right));
  return compareValues(left, right);
}
function sortValue(column, row) {
  const source = column.sort_key || column.source_field || column.id;
  const value = row[source];
  if (column.sort_kind === "record") return recordWins(value);
  if (column.sort_kind === "numeric" || column.sort_kind === "chii_ordinal") {
    const number = Number(value);
    return Number.isNaN(number) ? null : number;
  }
  return value ?? "";
}
function recordWins(value) {
  // Warning! Warning! Dr. Smith! This parses compact result strings because
  // TBD "Producer result-field shape" has not been resolved.
  const match = String(value ?? "").match(/^\s*(\d+)\s*-/);
  return match ? Number(match[1]) : null;
}
function renderTableHeading(column, sortState) {
  const attributes = tableCellAttributes(column);
  if (!isSortableColumn(column)) return `<th ${attributes}>${escapeHtml(column.heading)}</th>`;
  const active = sortState?.columnId === column.id;
  const direction = active ? sortState.direction : "none";
  const indicator = active ? (sortState.direction === "ascending" ? " ▲" : " ▼") : "";
  return [
    `<th ${attributes} aria-sort="${direction}">`,
    `<button type="button" class="table-sort-button" data-sort-column="${escapeHtml(column.id)}">`,
    escapeHtml(column.heading),
    `<span class="table-sort-indicator" aria-hidden="true">${indicator}</span>`,
    '</button>',
    '</th>',
  ].join("");
}
function wireTableSorting(panel, artifact, renderPanel, columns = null) {
  const sortableColumns = columns || artifact.columns || [];
  document.querySelectorAll(".table-sort-button").forEach(button => {
    button.addEventListener("click", () => {
      const columnId = button.dataset.sortColumn;
      const current = tableSortStates.get(artifact.id) || currentTableSortState(artifact);
      const column = sortableColumns.find(item => item.id === columnId);
      tableSortStates.set(artifact.id, {
        columnId,
        direction: current.columnId === columnId
          ? toggledSortDirection(current.direction)
          : sortDefaultDirection(column),
      });
      renderPanel(panel);
    });
  });
}
function toggledSortDirection(direction) {
  return direction === "ascending" ? "descending" : "ascending";
}
function tableCellAttributes(column) {
  return `data-column-id="${escapeHtml(column.id)}"`;
}
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

export { renderSectionedTable, renderTableSection, renderIndexedTable, renderBanzukeChangesTable, renderBanzukeStyleTable, renderBanzukeScanTable, banzukeSideColumns, banzukeScanColumns, renderBanzukeSideCell, renderBanzukeScanCell, banzukeCellAttributes, movementDirection, banzukeSideValue, renderRikishiLink, renderStandingsTable, standingsVisibleColumns, standingsVisibleGroups, renderStandingsTableHead, standingsCellValue, standingsRowsForState, standingsDivisionMatches, sortedStandingsRows, defaultStandingsSortColumn, competitionPositions, decimal, compareValues, currentTableSortState, firstSortableColumn, isSortableColumn, sortDefaultDirection, sortRows, compareNullableSortValues, compareSortValues, sortValue, recordWins, renderTableHeading, wireTableSorting, toggledSortDirection, tableCellAttributes, isColumnVisible, cellValue, resultWithMovement, rankLevelMovementMarker };

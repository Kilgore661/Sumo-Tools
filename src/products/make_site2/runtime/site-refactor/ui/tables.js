import { escapeHtml } from "../utils/html.js";

function renderSectionedTable(artifact, rows) {
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    '</div>',
    '<div class="sectioned-table-grid">',
    ...artifact.sections.map(section =>
      renderTableSection(section, rows, artifact.columns || [])
    ),
    '</div>',
  ].join("");
}
function renderTableSection(section, rows, columns) {
  const sectionRows = [...rows]
    .filter(row => String(row[section.source_field]) === String(section.source_value))
    .sort((left, right) =>
      compareValues(Number(left[section.order_by]) || 0, Number(right[section.order_by]) || 0)
    );
  return [
    '<section class="table-section">',
    `<h5>${escapeHtml(section.heading)}</h5>`,
    '<table class="artifact-table sectioned-table">',
    '<thead><tr>',
    ...columns.map(column => `<th ${tableCellAttributes(column)}>${escapeHtml(column.heading)}</th>`),
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
  return [
    '<table class="artifact-table brb-table">',
    '<thead><tr>',
    ...visibleColumns.map(column => `<th ${tableCellAttributes(column)}>${escapeHtml(column.heading)}</th>`),
    '</tr></thead>',
    '<tbody>',
    ...rows.map((row, index) => [
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
    : renderBanzukeScanTable(rows, state);
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
function renderBanzukeScanTable(rows, state) {
  const columns = banzukeScanColumns(state);
  const sideRows = rows.flatMap(row => ["east", "west"].map(side => ({ row, side })))
    .filter(item => item.row[`${item.side}_rikishi_id`]);
  return [
    '<table class="artifact-table banzuke-changes-table">',
    '<thead>',
    '<tr>',
    ...columns.map(column => `<th>${escapeHtml(column.heading)}</th>`),
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
    { id: "chii", heading: "Chii" },
    { id: "shikona", heading: "Shikona" },
    { id: "direction", heading: "⇅" },
  ];
  if (state.delta) columns.push({ id: "delta", heading: "Delta" });
  if (state.context) {
    columns.push({ id: "result", heading: "Result" });
    columns.push({ id: "old_chii", heading: "Previous Chii" });
  }
  if (state.equelo) columns.push({ id: "equelo", heading: "Equelo" });
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
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    '</div>',
    '<table class="artifact-table standings-table">',
    renderStandingsTableHead(artifact, visibleColumns),
    '<tbody>',
    ...rows.map((row, index) => [
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
function renderStandingsTableHead(artifact, visibleColumns) {
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
    ...visibleColumns.map(column => `<th ${tableCellAttributes(column)}>${escapeHtml(column.heading)}</th>`),
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
  return row[column.source_field || column.id] || "";
}

export { renderSectionedTable, renderTableSection, renderIndexedTable, renderBanzukeChangesTable, renderBanzukeStyleTable, renderBanzukeScanTable, banzukeSideColumns, banzukeScanColumns, renderBanzukeSideCell, renderBanzukeScanCell, banzukeCellAttributes, movementDirection, banzukeSideValue, renderRikishiLink, renderStandingsTable, standingsVisibleColumns, standingsVisibleGroups, renderStandingsTableHead, standingsCellValue, standingsRowsForState, standingsDivisionMatches, sortedStandingsRows, competitionPositions, decimal, compareValues, tableCellAttributes, isColumnVisible, cellValue };

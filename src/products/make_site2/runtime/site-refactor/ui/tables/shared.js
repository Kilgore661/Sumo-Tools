// Shared table sorting, heading and cell-link helpers.

import { escapeHtml } from "../../utils/html.js";
import { dateLikeDisplay } from "../../utils/display.js";
import { renderLabelWithHelp } from "../help.js";

const tableSortStates = new Map();
const SHIKONA_LINK_HELP = "Click for SumoDB; Alt-click for chart.";
const BASHO_DATE_LINK_HELP = "Click for SumoDB; Alt-click for this site.";
const EQUELO_LINK_HELP = "Click for ratings chart.";

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

// Resolve the current sort state for an artifact, creating its default state.
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

// Sort table rows using column metadata and null-last behaviour.
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

// Render a sortable or static table heading cell.
function renderTableHeading(column, sortState, extraAttributes = "") {
  const attributes = [tableCellAttributes(column), extraAttributes].filter(Boolean).join(" ");
  const heading = columnHeading(column);
  if (!isSortableColumn(column)) {
    return `<th ${attributes}>${renderLabelWithHelp(heading, column.help, { noteId: column.note_id })}</th>`;
  }
  const active = sortState?.columnId === column.id;
  const direction = active ? sortState.direction : "none";
  const indicator = active ? (sortState.direction === "ascending" ? " ▲" : " ▼") : "";
  return [
    `<th ${attributes} aria-sort="${direction}">`,
    `<button type="button" class="table-sort-button" data-sort-column="${escapeHtml(column.id)}">`,
    renderLabelWithHelp(heading, column.help, { noteId: column.note_id }),
    `<span class="table-sort-indicator" aria-hidden="true">${indicator}</span>`,
    '</button>',
    '</th>',
  ].join("");
}

function columnHeading(column) {
  if (column.id === "row_number") return "";
  return column.heading;
}

// Attach click handlers for ordinary table heading sort buttons.
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
  const attributes = [`data-column-id="${escapeHtml(column.id)}"`];
  if (column.align) attributes.push(`data-align="${escapeHtml(column.align)}"`);
  return attributes.join(" ");
}

// Render the standard external SumoDB rikishi link.
function renderRikishiLink(shikona, rikishiId) {
  if (!rikishiId) return "";
  const escapedShikona = escapeHtml(shikona);
  const escapedHelp = escapeHtml(SHIKONA_LINK_HELP);
  const altHref = careerComparisonHref(rikishiId);
  return [
    `<a class="shikona-link help-popover" href="https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(rikishiId)}"`,
    ` target="_blank" rel="noopener" data-help="${escapedHelp}"`,
    ` data-alt-href="${escapeHtml(altHref)}" aria-label="${escapedShikona}: ${escapedHelp}">`,
    escapedShikona,
    '</a>',
  ].join("");
}

function careerComparisonHref(rikishiId) {
  return careerComparisonChartHref(rikishiId, {
    skill: "chii",
    log: true,
  });
}

function careerComparisonChartHref(rikishiId, { skill, log }) {
  return [
    "index.html?page=career_comparisons",
    `skill=${encodeURIComponent(skill)}`,
    "x=date",
    `log=${log ? "true" : "false"}`,
    `rikishi=${encodeURIComponent(rikishiId)}`,
  ].join("&");
}

// Render a site link to the Equelo chart for one rikishi.
function renderEqueloChartLink(rating, rikishiId) {
  const label = String(rating || "");
  if (!rikishiId) return escapeHtml(label);
  const escapedLabel = escapeHtml(label);
  const escapedHelp = escapeHtml(EQUELO_LINK_HELP);
  return [
    `<a class="equelo-link help-popover" href="${escapeHtml(careerComparisonChartHref(rikishiId, { skill: "equelo", log: false }))}"`,
    ` data-help="${escapedHelp}" aria-label="${escapedLabel}: ${escapedHelp}">`,
    escapedLabel,
    '</a>',
  ].join("");
}

// Render a basho-date link to SumoDB, with Alt-click opening this site.
function renderBashoDateLink(date) {
  const label = String(date || "");
  const basho = bashoKeyFromDateLabel(label);
  if (!basho) return escapeHtml(label);
  const displayLabel = dateLikeDisplay(label);
  const escapedLabel = escapeHtml(displayLabel);
  const escapedHelp = escapeHtml(BASHO_DATE_LINK_HELP);
  return [
    `<a class="basho-date-link help-popover" href="https://sumodb.sumogames.de/Banzuke.aspx?b=${encodeURIComponent(basho)}"`,
    ` target="_blank" rel="noopener" data-help="${escapedHelp}"`,
    ` data-alt-href="${escapeHtml(bashoResultsHref(basho))}" aria-label="${escapedLabel}: ${escapedHelp}">`,
    escapedLabel,
    '</a>',
  ].join("");
}

function bashoKeyFromDateLabel(label) {
  const match = /^(\d{4})[/-](\d{2})(?:[/-]\d{2})?$/.exec(label);
  return match ? `${match[1]}${match[2]}` : "";
}

function bashoResultsHref(basho) {
  return [
    "index.html?page=basho_results_browser",
    `year=${encodeURIComponent(basho.slice(0, 4))}`,
    `month=${encodeURIComponent(basho.slice(4, 6))}`,
    "division=makuuchi",
    "previous=false",
    "changes=false",
    "ratings=false",
    "analysis=false",
    "nu_chii=false",
  ].join("&");
}

export {
  tableSortStates,
  SHIKONA_LINK_HELP,
  decimal,
  compareValues,
  currentTableSortState,
  firstSortableColumn,
  isSortableColumn,
  sortDefaultDirection,
  sortRows,
  compareNullableSortValues,
  compareSortValues,
  sortValue,
  recordWins,
  renderTableHeading,
  columnHeading,
  wireTableSorting,
  toggledSortDirection,
  tableCellAttributes,
  renderRikishiLink,
  renderBashoDateLink,
  renderEqueloChartLink,
  careerComparisonHref,
  careerComparisonChartHref,
};

import { escapeHtml, compareValues } from '../../utils/dom.js';
import { fetchJson, fetchCsv } from '../../utils/network.js';
import { writePanelUrl } from '../../core/routing.js';
import { 
  resolveFilterState, 
  readFilterUrlState, 
  renderFilterSection, 
  selectedIndexEntry, 
  filterValueLabel 
} from '../filters/filterEngine.js';

/**
 * Isolated logic managing layout grids, structured data logs and indexed dynamic tables.
 */

export async function renderIndexedTableContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter, dispatchRender) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  const index = await fetchJson(artifact.indexed_source.index_path);
  const selectedEntry = selectedIndexEntry(index, state[artifact.selector_filter_id]);
  state[artifact.selector_filter_id] = selectedEntry.basho;
  const payloadPath = selectedEntry[artifact.indexed_source.payload_path_field];
  const dataRoot = artifact.indexed_source.index_path.replace(/[^/]+$/, "");
  const rows = await fetchCsv(`${dataRoot}${payloadPath.replace(/^data\//, "")}`);
  
  const divisions = [...new Set(rows.map(row => row.division_id).filter(Boolean))];
  state.division = divisions.includes(state.division) ? state.division : divisions[0] || state.division;
  
  writePanelUrl(panel.page_id, filters, state, { replace: true });
  const filteredRows = rows.filter(row => row.division_id === state.division);

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body">',
    renderFilterSection(panel.contents.filter_section, state, index),
    '<div class="pa-slot">',
    renderArtifactTitleBlock(artifact, state, selectedEntry, filters),
    window.renderIndexedTable ? window.renderIndexedTable(artifact, filteredRows, state) : "",
    '</div>',
    '</div>',
    window.renderNotes ? window.renderNotes(artifact, state) : "",
    '</section>'
  ].join("");
  runWireFilter(panel, state);
}

export async function renderBanzukeChangesContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  const config = await fetchJson(artifact.config_source.path);
  const rows = await fetchCsv(artifact.rows_source.path);
  
  const divisions = (config.divisions || []).map(div => div.id);
  state.division = divisions.includes(state.division) ? state.division : config.default_division;
  
  writePanelUrl(panel.page_id, filters, state, { replace: true });
  const filteredRows = rows.filter(row => row.division_id === state.division);

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body">',
    renderFilterSection(panel.contents.filter_section, state),
    '<div class="pa-slot">',
    window.renderBanzukeChangesTable ? window.renderBanzukeChangesTable(artifact, filteredRows, state, config) : "",
    '</div>',
    '</div>',
    window.renderNotes ? window.renderNotes(artifact, state) : "",
    '</section>'
  ].join("");
  runWireFilter(panel, state);
}

export async function renderSectionedTableContentPanel(panel, artifact, contentPanel, fetchCsvSet) {
  const rowsBySource = await fetchCsvSet(artifact);
  const rows = rowsBySource[artifact.primary_source] || [];

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body content-body-no-filters">',
    '<div class="pa-slot">',
    renderSectionedTable(artifact, rows),
    '</div>',
    '</div>',
    window.renderNotes ? window.renderNotes(artifact, {}) : "",
    '</section>'
  ].join("");
}

function renderArtifactTitleBlock(artifact, state, entry, filters) {
  if (artifact.id !== "basho_results_browser") return "";
  const division = filterValueLabel(filters, "division", state.division) || state.division || "";
  const label = entry.label || entry.basho || "";
  const title = entry.latest_day && Number(entry.latest_day) < 15
    ? `${division} Results (Day ${entry.latest_day}) for ${label}`
    : `${division} Results for ${label}`;
    
  return `<div class="artifact-title-block"><h4>${escapeHtml(title)}</h4></div>`;
}

function renderSectionedTable(artifact, rows) {
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    '</div>',
    '<div class="sectioned-table-grid">',
    ...artifact.sections.map(section => renderTableSection(section, rows, artifact.columns || [])),
    '</div>',
  ].join("");
}

function renderTableSection(section, rows, columns) {
  const sectionRows = [...rows]
    .filter(row => String(row[section.source_field]) === String(section.source_value))
    .sort((left, right) => compareValues(Number(left[section.order_by]) || 0, Number(right[section.order_by]) || 0));
    
  return [
    '<section class="table-section">',
    `<h5>${escapeHtml(section.heading)}</h5>`,
    '<table class="artifact-table sectioned-table">',
    '<thead><tr>',
    ...columns.map(col => `<th ${window.tableCellAttributes ? window.tableCellAttributes(col) : ""}>${escapeHtml(col.heading)}</th>`),
    '</tr></thead>',
    '<tbody>',
    ...sectionRows.map((row, index) => [
      '<tr>',
      ...columns.map(col => `<td ${window.tableCellAttributes ? window.tableCellAttributes(col) : ""}>${escapeHtml(window.cellValue ? window.cellValue(col, row, index) : "")}</td>`),
      '</tr>'
    ].join("")),
    '</tbody>',
    '</table>',
    '</section>',
  ].join("");
}
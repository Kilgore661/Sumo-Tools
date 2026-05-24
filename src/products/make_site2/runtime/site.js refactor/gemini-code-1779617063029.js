import { escapeHtml } from '../../utils/dom.js';
import { fetchJson, fetchCsv } from '../../utils/network.js';
import { writePanelUrl } from '../../core/routing.js';
import { resolveFilterState, readFilterUrlState, renderFilterSection } from '../filters/filterEngine.js';

/**
 * Analytical metrics engine executing standings and records calculations.
 */

export async function renderStandingsContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  const config = await fetchJson(configSourcePath(artifact));
  
  const windows = (config.supported_num_basho || []).map(String);
  state.current_num_basho = windows.includes(String(state.current_num_basho)) 
    ? String(state.current_num_basho) 
    : String(config.default_num_basho);
    
  const divisions = ["all", "makuuchi", "juryo", "makushita", "sandanme", "jonidan", "jonokuchi"];
  state.division = divisions.includes(state.division) ? state.division : config.default_division;
  
  const source = artifact.data_sources.find(src => String(src.filter_value) === String(state[artifact.selector_filter_id]));
  const rows = await fetchCsv(source.path);
  writePanelUrl(panel.page_id, filters, state, { replace: true });
  
  const filteredRows = window.standingsRowsForState ? window.standingsRowsForState(rows, state) : rows;
  const sortedRows = window.sortedStandingsRows ? window.sortedStandingsRows(filteredRows, state) : filteredRows;

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body">',
    renderFilterSection(panel.contents.filter_section, state),
    '<div class="pa-slot">',
    window.renderStandingsTable ? window.renderStandingsTable(artifact, sortedRows, filteredRows, state) : "",
    '</div>',
    '</div>',
    window.renderNotes ? window.renderNotes(artifact, state) : "",
    '</section>'
  ].join("");
  runWireFilter(panel, state);
}

function configSourcePath(artifact) {
  return artifact.config_source.path;
}
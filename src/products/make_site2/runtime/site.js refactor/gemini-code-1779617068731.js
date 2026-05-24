import { escapeHtml, divisionId } from '../../utils/dom.js';
import { writePanelUrl } from '../../core/routing.js';
import { 
  resolveFilterState, 
  readFilterUrlState, 
  renderFilterSection, 
  resolveSelectedFilterValueFromSource,
  filterValueLabel 
} from '../filters/filterEngine.js';

/**
 * Isolated dynamic charting logic interacting directly with the Plotly.js engine canvas context.
 */

export async function renderChartContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter, fetchCsvSet) {
  const r = artifact.renderer;
  if (r === "finish_by_chii_chart") {
    await renderFinishByChiiContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter, fetchCsvSet);
    return;
  }
  if (r === "standing_win_probability_chart") {
    await renderStandingWinProbabilityContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter, fetchCsvSet);
    return;
  }
  if (r === "career_length") {
    await renderCareerLengthContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter, fetchCsvSet);
    return;
  }

  // Handle standard charts static configuration
  const rowsBySource = await fetchCsvSet(artifact);
  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body content-body-no-filters">',
    '<div class="pa-slot">',
    renderStaticChartSkeleton(artifact, rowsBySource),
    '</div>',
    '</div>',
    window.renderNotes ? window.renderNotes(artifact, {}) : "",
    '</section>'
  ].join("");

  triggerStaticPlotlyHooks(artifact, rowsBySource);
}

async function renderFinishByChiiContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter, fetchCsvSet) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  const rowsBySource = await fetchCsvSet(artifact);
  
  const bindRows = rowsBySource[artifact.data_binding.sources[0]] || [];
  const uniqDivs = [...new Set(bindRows.map(row => String(row.division || "").toLowerCase().replace(/\s+/g, "_")))].filter(Boolean);
  state.division = uniqDivs.includes(state.division) ? state.division : uniqDivs[0] || state.division;
  state.chii = resolveSelectedFilterValueFromSource(filters.find(f => f.id === "chii"), state, rowsBySource);
  
  writePanelUrl(panel.page_id, filters, state, { replace: true });

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body">',
    renderFilterSection(panel.contents.filter_section, state, null, rowsBySource),
    '<div class="pa-slot">',
    renderFinishByChiiChart(artifact, state, filters, rowsBySource),
    '</div>',
    '</div>',
    window.renderNotes ? window.renderNotes(artifact, state) : "",
    '</section>'
  ].join("");
  
  if (window.renderFinishByChiiPlot) window.renderFinishByChiiPlot(artifact, state, rowsBySource);
  runWireFilter(panel, state);
}

async function renderStandingWinProbabilityContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter, fetchCsvSet) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  
  if (window.resolveSelectedDataSourceId) state.source = window.resolveSelectedDataSourceId(artifact, state.source);
  if (window.resolveFilterValue) state.division = window.resolveFilterValue(filters, "division", state.division);
  
  writePanelUrl(panel.page_id, filters, state, { replace: true });
  const rowsBySource = await fetchCsvSet(artifact);

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body">',
    renderFilterSection(panel.contents.filter_section, state),
    '<div class="pa-slot">',
    window.renderStandingWinProbabilityChart ? window.renderStandingWinProbabilityChart(artifact, state, rowsBySource) : "",
    '</div>',
    '</div>',
    window.renderNotes ? window.renderNotes(artifact, state) : "",
    '</section>'
  ].join("");
  
  if (window.renderStandingWinProbabilityPlot) window.renderStandingWinProbabilityPlot(artifact, state, rowsBySource);
  runWireFilter(panel, state);
}

async function renderCareerLengthContentPanel(panel, artifact, overrideState, contentPanel, runWireFilter, fetchCsvSet) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  const rowsBySource = await fetchCsvSet(artifact);
  
  if (window.resolveCareerLengthView) state.view = window.resolveCareerLengthView(artifact, state.view);
  writePanelUrl(panel.page_id, filters, state, { replace: true });

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body">',
    renderFilterSection(panel.contents.filter_section, state),
    '<div class="pa-slot">',
    window.renderCareerLengthArtifact ? window.renderCareerLengthArtifact(artifact, state, rowsBySource) : "",
    '</div>',
    '</div>',
    window.renderNotes ? window.renderNotes(artifact, state) : "",
    '</section>'
  ].join("");
  
  if (window.renderCareerLengthPlot) window.renderCareerLengthPlot(artifact, state, rowsBySource);
  runWireFilter(panel, state);
}

function renderStaticChartSkeleton(artifact, rowsBySource) {
  const sourceId = artifact.data_binding.sources[0];
  const rows = rowsBySource[sourceId] || [];
  if (!rows.length) return `<p>No ${escapeHtml(artifact.heading)} data is available.</p>`;
  
  const elId = artifact.id === "basho_counts_chart" ? "basho-counts-chart" : (window.chartElementId ? window.chartElementId(artifact) : artifact.id);
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    '</div>',
    `<div id="${escapeHtml(elId)}" class="plotly-chart"></div>`,
  ].join("");
}

function triggerStaticPlotlyHooks(artifact, rowsBySource) {
  const r = artifact.renderer;
  if (r === "stacked_bar_chart" && window.renderStackedBarPlot) window.renderStackedBarPlot(artifact, rowsBySource);
  if (r === "grouped_line_chart" && window.renderGroupedLinePlot) window.renderGroupedLinePlot(artifact, rowsBySource);
  if (r === "ordered_bar_chart" && window.renderOrderedBarPlot) window.renderOrderedBarPlot(artifact, rowsBySource);
  if (r === "category_bar_chart" && window.renderCategoryBarPlot) window.renderCategoryBarPlot(artifact, rowsBySource);
}

function renderFinishByChiiChart(artifact, state, filters, rowsBySource) {
  const sourceId = state.direction === "bottom" ? "bottom_thresholds" : "top_thresholds";
  const rows = [...(rowsBySource[sourceId] || [])]
    .filter(row => divisionId(row.division) === state.division && row.chii === state.chii);
    
  if (!rows.length) return '<p>No Finish by Chii data matches the selected options.</p>';
  
  const divisionLabel = filterValueLabel(filters, "division", state.division) || rows[0].division;
  const directionLabel = state.direction === "bottom" ? "Bottom" : "Top";
  const probabilityLabel = state.direction === "bottom" ? "No better than nth-worst" : "No worse than nth";
  
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(divisionLabel)} ${escapeHtml(state.chii)}: ${escapeHtml(directionLabel)} finish</h4>`,
    `<div>${escapeHtml(probabilityLabel)} by wins, sample size ${escapeHtml(rows[0].n || "")}</div>`,
    '</div>',
    '<div id="finish-by-chii-chart" class="plotly-chart"></div>'
  ].join("");
}
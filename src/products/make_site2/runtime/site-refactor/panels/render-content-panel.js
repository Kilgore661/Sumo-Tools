import { contentPanel } from "../core/dom.js";
import { getRuntimeManifest } from "../core/manifest-store.js";
import { readFilterUrlState, writePanelUrl } from "../core/url-state.js";
import { fetchCsv, fetchJson } from "../data/http.js";
import { renderCareerLengthArtifact, renderCareerLengthPlot, renderCategoryBarChart, renderCategoryBarPlot, renderFinishByChiiChart, renderFinishByChiiPlot, renderGroupedLineChart, renderGroupedLinePlot, renderOrderedBarChart, renderOrderedBarPlot, renderStackedBarChart, renderStackedBarPlot, renderStandingWinProbabilityChart, renderStandingWinProbabilityPlot, resolveCareerLengthView, resolveFilterValue, resolveSelectedDataSourceId } from "../ui/charts.js";
import { filterValueLabel, renderFilterSection, resolveBanzukeChangesDivision, resolveFilterState, resolveSelectedDataValue, resolveSelectedDivision, resolveSelectedFilterValueFromSource, resolveStandingsDivision, resolveStandingsWindow, selectedIndexEntry, selectedStandingsSource, wireFilterSection } from "../ui/filters.js";
import { renderNotes } from "../ui/notes.js";
import { renderBanzukeChangesTable, renderIndexedTable, renderSectionedTable, renderStandingsTable, sortedStandingsRows, standingsRowsForState } from "../ui/tables.js";
import { escapeHtml } from "../utils/html.js";

async function renderContentPanel(panel, overrideState = null) {
  if (panel.grammar !== "G1") throw new Error(`Unsupported content grammar: ${panel.grammar}`);
  const artifact = getRuntimeManifest().artifacts[panel.contents.pa.artifact_id];
  if (!artifact) throw new Error(`Unknown artifact: ${panel.contents.pa.artifact_id}`);
  if (artifact.kind === "indexed_table") {
    await renderIndexedTableContentPanel(panel, artifact, overrideState);
    return;
  }
  if (artifact.kind === "sectioned_table") {
    await renderSectionedTableContentPanel(panel, artifact);
    return;
  }
  if (artifact.kind === "banzuke_changes") {
    await renderBanzukeChangesContentPanel(panel, artifact, overrideState);
    return;
  }
  if (artifact.kind === "standings") {
    await renderStandingsContentPanel(panel, artifact, overrideState);
    return;
  }
  if (artifact.kind === "chart") {
    await renderChartContentPanel(panel, artifact, overrideState);
    return;
  }
  throw new Error(`Unsupported artifact kind: ${artifact.kind}`);
}
async function renderIndexedTableContentPanel(panel, artifact, overrideState = null) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  const index = await fetchJson(artifact.indexed_source.index_path);
  const selectedEntry = selectedIndexEntry(index, state[artifact.selector_filter_id]);
  state[artifact.selector_filter_id] = selectedEntry.basho;
  const payloadPath = selectedEntry[artifact.indexed_source.payload_path_field];
  const dataRoot = artifact.indexed_source.index_path.replace(/[^/]+$/, "");
  const rows = await fetchCsv(`${dataRoot}${payloadPath.replace(/^data\//, "")}`);
  state.division = resolveSelectedDivision(rows, state.division);
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
    renderIndexedTable(artifact, filteredRows, state),
    '</div>',
    '</div>',
    renderNotes(artifact, state),
    '</section>'
  ].join("");
  wireFilterSection(panel, state, renderContentPanel);
}
async function renderBanzukeChangesContentPanel(panel, artifact, overrideState = null) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  const config = await fetchJson(artifact.config_source.path);
  const rows = await fetchCsv(artifact.rows_source.path);
  state.division = resolveBanzukeChangesDivision(config, state.division);
  writePanelUrl(panel.page_id, filters, state, { replace: true });
  const filteredRows = rows.filter(row => row.division_id === state.division);

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body">',
    renderFilterSection(panel.contents.filter_section, state),
    '<div class="pa-slot">',
    renderBanzukeChangesTable(artifact, filteredRows, state, config),
    '</div>',
    '</div>',
    renderNotes(artifact, state),
    '</section>'
  ].join("");
  wireFilterSection(panel, state, renderContentPanel);
}
async function renderSectionedTableContentPanel(panel, artifact) {
  const rowsBySource = await fetchArtifactCsvSet(artifact);
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
    renderNotes(artifact, {}),
    '</section>'
  ].join("");
}
async function renderStandingsContentPanel(panel, artifact, overrideState = null) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  const config = await fetchJson(artifact.config_source.path);
  state.current_num_basho = resolveStandingsWindow(config, state.current_num_basho);
  state.division = resolveStandingsDivision(config, state.division);
  const source = selectedStandingsSource(artifact, state);
  const rows = await fetchCsv(source.path);
  writePanelUrl(panel.page_id, filters, state, { replace: true });
  const filteredRows = standingsRowsForState(rows, state);
  const sortedRows = sortedStandingsRows(filteredRows, state);

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body">',
    renderFilterSection(panel.contents.filter_section, state),
    '<div class="pa-slot">',
    renderStandingsTable(artifact, sortedRows, filteredRows, state),
    '</div>',
    '</div>',
    renderNotes(artifact, state),
    '</section>'
  ].join("");
  wireFilterSection(panel, state, renderContentPanel);
}
async function renderChartContentPanel(panel, artifact, overrideState = null) {
  if (artifact.renderer === "stacked_bar_chart") {
    await renderStackedBarChartContentPanel(panel, artifact);
    return;
  }
  if (artifact.renderer === "grouped_line_chart") {
    await renderGroupedLineChartContentPanel(panel, artifact);
    return;
  }
  if (artifact.renderer === "ordered_bar_chart") {
    await renderOrderedBarChartContentPanel(panel, artifact);
    return;
  }
  if (artifact.renderer === "category_bar_chart") {
    await renderCategoryBarChartContentPanel(panel, artifact);
    return;
  }
  if (artifact.renderer === "finish_by_chii_chart") {
    await renderFinishByChiiContentPanel(panel, artifact, overrideState);
    return;
  }
  if (artifact.renderer === "standing_win_probability_chart") {
    await renderStandingWinProbabilityContentPanel(panel, artifact, overrideState);
    return;
  }
  if (artifact.renderer === "career_length") {
    await renderCareerLengthContentPanel(panel, artifact, overrideState);
    return;
  }
  throw new Error(`Unsupported chart renderer: ${artifact.renderer}`);
}
async function renderStandingWinProbabilityContentPanel(panel, artifact, overrideState = null) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  state.source = resolveSelectedDataSourceId(artifact, state.source);
  state.division = resolveFilterValue(filters, "division", state.division);
  writePanelUrl(panel.page_id, filters, state, { replace: true });
  const rowsBySource = await fetchArtifactCsvSet(artifact);

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body">',
    renderFilterSection(panel.contents.filter_section, state),
    '<div class="pa-slot">',
    renderStandingWinProbabilityChart(artifact, state, rowsBySource),
    '</div>',
    '</div>',
    renderNotes(artifact, state),
    '</section>'
  ].join("");
  renderStandingWinProbabilityPlot(artifact, state, rowsBySource);
  wireFilterSection(panel, state, renderContentPanel);
}
async function renderCareerLengthContentPanel(panel, artifact, overrideState = null) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  const rowsBySource = await fetchArtifactCsvSet(artifact);
  state.view = resolveCareerLengthView(artifact, state.view);
  writePanelUrl(panel.page_id, filters, state, { replace: true });

  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body">',
    renderFilterSection(panel.contents.filter_section, state),
    '<div class="pa-slot">',
    renderCareerLengthArtifact(artifact, state, rowsBySource),
    '</div>',
    '</div>',
    renderNotes(artifact, state),
    '</section>'
  ].join("");
  renderCareerLengthPlot(artifact, state, rowsBySource);
  wireFilterSection(panel, state, renderContentPanel);
}
async function renderFinishByChiiContentPanel(panel, artifact, overrideState = null) {
  const filters = panel.contents.filter_section.filters;
  const state = overrideState || resolveFilterState(filters, readFilterUrlState(filters));
  const rowsBySource = await fetchArtifactCsvSet(artifact);
  state.division = resolveSelectedDataValue(
    rowsBySource[artifact.data_binding.sources[0]] || [],
    "division",
    state.division,
    "division_id",
  );
  state.chii = resolveSelectedFilterValueFromSource(
    filters.find(filter => filter.id === "chii"),
    state,
    rowsBySource,
  );
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
    renderNotes(artifact, state),
    '</section>'
  ].join("");
  renderFinishByChiiPlot(artifact, state, rowsBySource);
  wireFilterSection(panel, state, renderContentPanel);
}
async function renderStackedBarChartContentPanel(panel, artifact) {
  const rowsBySource = await fetchArtifactCsvSet(artifact);
  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body content-body-no-filters">',
    '<div class="pa-slot">',
    renderStackedBarChart(artifact, rowsBySource),
    '</div>',
    '</div>',
    renderNotes(artifact, {}),
    '</section>'
  ].join("");
  renderStackedBarPlot(artifact, rowsBySource);
}
async function renderGroupedLineChartContentPanel(panel, artifact) {
  const rowsBySource = await fetchArtifactCsvSet(artifact);
  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body content-body-no-filters">',
    '<div class="pa-slot">',
    renderGroupedLineChart(artifact, rowsBySource),
    '</div>',
    '</div>',
    renderNotes(artifact, {}),
    '</section>'
  ].join("");
  renderGroupedLinePlot(artifact, rowsBySource);
}
async function renderOrderedBarChartContentPanel(panel, artifact) {
  const rowsBySource = await fetchArtifactCsvSet(artifact);
  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body content-body-no-filters">',
    '<div class="pa-slot">',
    renderOrderedBarChart(artifact, rowsBySource),
    '</div>',
    '</div>',
    renderNotes(artifact, {}),
    '</section>'
  ].join("");
  renderOrderedBarPlot(artifact, rowsBySource);
}
async function renderCategoryBarChartContentPanel(panel, artifact) {
  const rowsBySource = await fetchArtifactCsvSet(artifact);
  contentPanel.innerHTML = [
    '<section class="content-panel">',
    `<h2 id="content-title">${escapeHtml(panel.heading.title)}</h2>`,
    `<h3>${escapeHtml(panel.heading.summary)}</h3>`,
    '<div class="content-body content-body-no-filters">',
    '<div class="pa-slot">',
    renderCategoryBarChart(artifact, rowsBySource),
    '</div>',
    '</div>',
    renderNotes(artifact, {}),
    '</section>'
  ].join("");
  renderCategoryBarPlot(artifact, rowsBySource);
}
async function fetchArtifactCsvSet(artifact) {
  const entries = await Promise.all(
    artifact.data_sources.map(async source => [source.id, await fetchCsv(source.path)])
  );
  return Object.fromEntries(entries);
}
function renderArtifactTitleBlock(artifact, state, entry, filters) {
  const title = artifactTitle(artifact, state, entry, filters);
  if (!title) return "";
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(title)}</h4>`,
    '</div>'
  ].join("");
}
function artifactTitle(artifact, state, entry, filters) {
  if (artifact.id !== "basho_results_browser") return "";
  return bashoResultsTitle(state, entry, filters);
}
function bashoResultsTitle(state, entry, filters) {
  const division = filterValueLabel(filters, "division", state.division) || state.division || "";
  const label = entry.label || entry.basho || "";
  if (entry.latest_day && Number(entry.latest_day) < 15) {
    return `${division} Results (Day ${entry.latest_day}) for ${label}`;
  }
  return `${division} Results for ${label}`;
}

export { renderContentPanel, renderIndexedTableContentPanel, renderBanzukeChangesContentPanel, renderSectionedTableContentPanel, renderStandingsContentPanel, renderChartContentPanel, renderStandingWinProbabilityContentPanel, renderCareerLengthContentPanel, renderFinishByChiiContentPanel, renderStackedBarChartContentPanel, renderGroupedLineChartContentPanel, renderOrderedBarChartContentPanel, renderCategoryBarChartContentPanel, fetchArtifactCsvSet, renderArtifactTitleBlock, artifactTitle, bashoResultsTitle };

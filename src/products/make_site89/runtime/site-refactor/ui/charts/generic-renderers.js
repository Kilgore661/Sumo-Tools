// DOM render entry points for generic artifact-driven Plotly chart renderers.

import { escapeHtml } from "../../utils/html.js";
import {
  PLOTLY_CONFIG,
  chartElementId,
  chartRows,
} from "./shared.js";
import {
  categoryBarTrace,
  groupedLineTraces,
  orderedBarTrace,
  stackedBarRows,
  stackedBarTraces,
} from "./generic-traces.js";
import {
  categoryBarLayout,
  groupedChartLayout,
  orderedBarLayout,
  stackedBarLayout,
} from "./generic-layouts.js";

// Render the common title and Plotly host for a stacked bar chart.
function renderStackedBarChart(artifact, rowsBySource) {
  const rows = stackedBarRows(artifact, rowsBySource);
  if (!rows.length) {
    return `<p>No ${escapeHtml(artifact.heading)} data is available.</p>`;
  }
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    renderArtifactSubheading(artifact),
    '</div>',
    `<div id="${escapeHtml(chartElementId(artifact))}" class="plotly-chart"></div>`,
  ].join("");
}

// Render the common title and Plotly host for a grouped line chart.
function renderGroupedLineChart(artifact, rowsBySource) {
  const rows = chartRows(artifact, rowsBySource);
  if (!rows.length) {
    return `<p>No ${escapeHtml(artifact.heading)} data is available.</p>`;
  }
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    renderArtifactSubheading(artifact),
    '</div>',
    `<div id="${escapeHtml(chartElementId(artifact))}" class="plotly-chart"></div>`,
  ].join("");
}

// Render the common title and Plotly host for an ordered bar chart.
function renderOrderedBarChart(artifact, rowsBySource) {
  const rows = chartRows(artifact, rowsBySource);
  if (!rows.length) {
    return `<p>No ${escapeHtml(artifact.heading)} data is available.</p>`;
  }
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    renderArtifactSubheading(artifact),
    '</div>',
    `<div id="${escapeHtml(chartElementId(artifact))}" class="plotly-chart"></div>`,
  ].join("");
}

// Render the common title and Plotly host for a category bar chart.
function renderCategoryBarChart(artifact, rowsBySource) {
  const rows = chartRows(artifact, rowsBySource);
  if (!rows.length) {
    return `<p>No ${escapeHtml(artifact.heading)} data is available.</p>`;
  }
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    renderArtifactSubheading(artifact),
    '</div>',
    `<div id="${escapeHtml(chartElementId(artifact))}" class="plotly-chart"></div>`,
  ].join("");
}

function renderArtifactSubheading(artifact) {
  const subheading = artifact.provenance?.subheading || "";
  return subheading ? `<h5>${escapeHtml(subheading)}</h5>` : "";
}

function renderCategoryBarPlot(artifact, rowsBySource) {
  const host = document.getElementById(chartElementId(artifact));
  if (!host) return;
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  const trace = categoryBarTrace(artifact, rowsBySource);
  Plotly.react(
    host,
    [trace],
    categoryBarLayout(artifact, trace),
    PLOTLY_CONFIG
  );
}

function renderOrderedBarPlot(artifact, rowsBySource) {
  const host = document.getElementById(chartElementId(artifact));
  if (!host) return;
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  const trace = orderedBarTrace(artifact, rowsBySource);
  Plotly.react(
    host,
    [trace],
    orderedBarLayout(artifact, trace),
    PLOTLY_CONFIG
  );
}

function renderGroupedLinePlot(artifact, rowsBySource) {
  const host = document.getElementById(chartElementId(artifact));
  if (!host) return;
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  Plotly.react(
    host,
    groupedLineTraces(artifact, rowsBySource),
    groupedChartLayout(artifact, rowsBySource),
    PLOTLY_CONFIG
  );
}

function renderStackedBarPlot(artifact, rowsBySource) {
  const host = document.getElementById(chartElementId(artifact));
  if (!host) return;
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  Plotly.react(
    host,
    stackedBarTraces(artifact, rowsBySource),
    stackedBarLayout(artifact, rowsBySource),
    PLOTLY_CONFIG
  );
}

export {
  renderStackedBarChart,
  renderGroupedLineChart,
  renderOrderedBarChart,
  renderCategoryBarChart,
  renderArtifactSubheading,
  renderCategoryBarPlot,
  renderOrderedBarPlot,
  renderGroupedLinePlot,
  renderStackedBarPlot,
};

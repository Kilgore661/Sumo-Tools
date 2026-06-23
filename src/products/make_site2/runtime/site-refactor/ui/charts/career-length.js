// Career Length chart runtime view handling.

import { escapeHtml } from "../../utils/html.js";
import { PLOTLY_CONFIG, axisTitle } from "./shared.js";

// Render the selected Career Length view, which may be a table or Plotly host.
function renderCareerLengthArtifact(artifact, state, rowsBySource) {
  const view = careerLengthView(artifact, state.view);
  const rows = rowsBySource[state.view] || [];
  if (!rows.length) {
    return `<p>No ${escapeHtml(view.label)} data is available.</p>`;
  }
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(view.label)}</h4>`,
    '</div>',
    '<div id="career-length-chart" class="plotly-chart"></div>',
  ].join("");
}

// Populate the Career Length chart host when the selected view is graphical.
function renderCareerLengthPlot(artifact, state, rowsBySource) {
  const view = careerLengthView(artifact, state.view);
  const host = document.getElementById("career-length-chart");
  if (!host) return;
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  Plotly.react(
    host,
    careerLengthTraces(view, rowsBySource[state.view] || []),
    careerLengthLayout(view),
    PLOTLY_CONFIG
  );
}

// Convert a Career Length chart view into Plotly traces.
function careerLengthTraces(view, rows) {
  if (view.kind === "stacked_bar") {
    return view.y.map((field, index) => ({
      type: "bar",
      name: view.series_labels[index] || field,
      x: rows.map(row => row[view.x]),
      y: rows.map(row => Number(row[field]) || 0),
      hovertemplate: `${escapeHtml(view.x)}=%{x}<br>${escapeHtml(field)}=%{y}<extra></extra>`,
    }));
  }
  return [{
    type: "scatter",
    mode: "lines+markers",
    name: view.label,
    x: rows.map(row => row[view.x]),
    y: rows.map(row => Number(row[view.y]) || 0),
    hovertemplate: `${escapeHtml(view.x)}=%{x}<br>${escapeHtml(view.y)}=%{y}<extra></extra>`,
  }];
}

function careerLengthLayout(view) {
  return {
    autosize: true,
    barmode: view.kind === "stacked_bar" ? "stack" : undefined,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 76, r: 40, t: 18, b: 70 },
    xaxis: {
      title: axisTitle(view.x_label),
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    yaxis: {
      title: axisTitle(view.y_label),
      rangemode: "tozero",
      tickformat: view.tickformat || undefined,
      automargin: true,
      gridcolor: "rgba(127,149,192,0.22)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    hovermode: "closest",
    legend: {
      orientation: "v",
      yanchor: "top",
      y: 1,
      xanchor: "left",
      x: 1.02,
    },
    font: {
      family: "Arial, Helvetica, sans-serif",
      color: "#ffffff",
    },
  };
}

function resolveCareerLengthView(artifact, selectedView) {
  const views = artifact.provenance.views || {};
  return Object.prototype.hasOwnProperty.call(views, selectedView)
    ? selectedView
    : "distribution";
}

function careerLengthView(artifact, selectedView) {
  return artifact.provenance.views[resolveCareerLengthView(artifact, selectedView)];
}

export {
  renderCareerLengthArtifact,
  renderCareerLengthPlot,
  careerLengthTraces,
  careerLengthLayout,
  resolveCareerLengthView,
  careerLengthView,
};

// Finish by Chii chart rendering and Plotly trace setup.

import { divisionId, filterValueLabel } from "../filters.js";
import { escapeHtml } from "../../utils/html.js";
import { PLOTLY_CONFIG } from "./shared.js";

// Render the static HTML host for the selected Finish by Chii chart.
function renderFinishByChiiChart(artifact, state, filters, rowsBySource) {
  const rows = finishByChiiRows(artifact, state, rowsBySource);
  if (!rows.length) {
    return '<p>No Finish by Chii data matches the selected options.</p>';
  }
  const divisionLabel = filterValueLabel(filters, "division", state.division) || rows[0].division;
  const directionLabel = state.direction === "bottom" ? "Bottom" : "Top";
  const probabilityLabel = state.direction === "bottom"
    ? "No better than nth-worst"
    : "No worse than nth";
  const sampleSize = rows[0].n || "";
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(divisionLabel)} ${escapeHtml(state.chii)}: ${escapeHtml(directionLabel)} finish</h4>`,
    `<div>${escapeHtml(probabilityLabel)} by wins, sample size ${escapeHtml(sampleSize)}</div>`,
    '</div>',
    '<div id="finish-by-chii-chart" class="plotly-chart"></div>'
  ].join("");
}

// Populate the Finish by Chii host with its Plotly bar chart.
function renderFinishByChiiPlot(artifact, state, rowsBySource) {
  const host = document.getElementById("finish-by-chii-chart");
  if (!host) return;
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  const rows = finishByChiiRows(artifact, state, rowsBySource);
  const probabilityField = state.direction === "bottom"
    ? "p_no_better_than_mth_worst"
    : "p_no_worse_than_n";
  const trace = {
    type: "bar",
    x: rows.map(row => Number(row.threshold)),
    y: rows.map(row => 100 * (Number(row[probabilityField]) || 0)),
    marker: {
      color: "rgba(143, 181, 255, 0.88)",
      line: {
        color: "rgba(220, 232, 255, 0.95)",
        width: 1,
      },
    },
    hovertemplate: "Threshold %{x}<br>Probability %{y:.1f}%<extra></extra>",
  };
  const layout = {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 64, r: 26, t: 18, b: 58 },
    xaxis: {
      title: state.direction === "top" ? "No worse than n" : "No better than nth-worst",
      tickmode: "linear",
      dtick: 1,
      gridcolor: "rgba(127,149,192,0.22)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    yaxis: {
      title: "Probability",
      range: [0, 100],
      ticksuffix: "%",
      gridcolor: "rgba(127,149,192,0.22)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    font: {
      family: "Arial, Helvetica, sans-serif",
      color: "#ffffff",
    },
  };
  Plotly.react(host, [trace], layout, PLOTLY_CONFIG);
}

// Select the threshold rows matching the active division, Chii and direction.
function finishByChiiRows(artifact, state, rowsBySource) {
  const sourceId = state.direction === "bottom" ? "bottom_thresholds" : "top_thresholds";
  return [...(rowsBySource[sourceId] || [])]
    .filter(row => divisionId(row.division) === state.division && row.chii === state.chii)
    .sort((left, right) => Number(left.threshold) - Number(right.threshold));
}

export {
  renderFinishByChiiChart,
  renderFinishByChiiPlot,
  finishByChiiRows,
};

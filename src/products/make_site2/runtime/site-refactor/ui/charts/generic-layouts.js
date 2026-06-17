// Plotly layout builders for generic artifact-driven chart renderers.

import { dateLikeDisplay } from "../../utils/display.js";
import {
  axisRange,
  axisTitle,
  chartRows,
  monthIndexTicks,
  sparseTickText,
} from "./shared.js";
import {
  groupedLineTraceSpec,
  stackedBarRows,
  stackedBarTraceSpec,
} from "./generic-traces.js";

function stackedBarLayout(artifact, rowsBySource) {
  const rows = stackedBarRows(artifact, rowsBySource);
  const trace = stackedBarTraceSpec(artifact);
  const xValues = artifact.x_axis.order_values.length
    ? artifact.x_axis.order_values.map(value => dateLikeDisplay(value))
    : [...new Set(rows.map(row => dateLikeDisplay(row[trace.x])))];
  return {
    autosize: true,
    barmode: "stack",
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 76, r: 150, t: 18, b: 90 },
    xaxis: {
      title: axisTitle(artifact.x_axis.label),
      type: "category",
      categoryorder: "array",
      categoryarray: xValues,
      tickangle: artifact.provenance.x_tickangle || 0,
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    yaxis: {
      title: axisTitle(artifact.y_axis.label),
      rangemode: artifact.y_axis.minimum === 0 ? "tozero" : "normal",
      range: axisRange(artifact.y_axis),
      tickformat: artifact.y_axis.tickformat || undefined,
      automargin: true,
      gridcolor: "rgba(127,149,192,0.22)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    hovermode: "closest",
    legend: {
      title: { text: artifact.provenance.legend_title || "" },
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

function groupedChartLayout(artifact, rowsBySource) {
  const rows = chartRows(artifact, rowsBySource);
  const trace = groupedLineTraceSpec(artifact);
  const xValues = artifact.x_axis.order_values.length
    ? artifact.x_axis.order_values.map(value => dateLikeDisplay(value))
    : [...new Set(rows.map(row => dateLikeDisplay(row[trace.x])))];
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 76, r: 150, t: 18, b: 90 },
    xaxis: {
      title: axisTitle(artifact.x_axis.label),
      type: "category",
      categoryorder: "array",
      categoryarray: xValues,
      tickangle: artifact.provenance.x_tickangle || 0,
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    yaxis: {
      title: axisTitle(artifact.y_axis.label),
      rangemode: artifact.y_axis.minimum === 0 ? "tozero" : "normal",
      range: axisRange(artifact.y_axis),
      tickformat: artifact.y_axis.tickformat || undefined,
      automargin: true,
      gridcolor: "rgba(127,149,192,0.22)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    hovermode: "closest",
    legend: {
      title: { text: artifact.provenance.legend_title || "" },
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

function orderedBarLayout(artifact, trace) {
  const maxY = Math.max(...trace.y, 0);
  const yTicks = monthIndexTicks(maxY, artifact);
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 90, r: 30, t: 18, b: 120 },
    xaxis: {
      title: axisTitle(artifact.x_axis.label),
      type: "category",
      categoryorder: "array",
      categoryarray: trace.x,
      tickvals: trace.x,
      ticktext: sparseTickText(trace.x, artifact.provenance.max_x_tick_labels || trace.x.length),
      tickangle: artifact.provenance.x_tickangle || 0,
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    yaxis: {
      title: axisTitle(artifact.y_axis.label),
      range: [0, maxY],
      tickmode: "array",
      tickvals: yTicks.values,
      ticktext: yTicks.labels,
      automargin: true,
      gridcolor: "rgba(127,149,192,0.22)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    hovermode: "closest",
    showlegend: false,
    font: {
      family: "Arial, Helvetica, sans-serif",
      color: "#ffffff",
    },
  };
}

function categoryBarLayout(artifact, trace) {
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 80, r: 30, t: 18, b: 70 },
    xaxis: {
      title: axisTitle(artifact.x_axis.label),
      type: "category",
      categoryorder: "array",
      categoryarray: trace.x,
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    yaxis: {
      title: axisTitle(artifact.y_axis.label),
      rangemode: artifact.y_axis.minimum === 0 ? "tozero" : "normal",
      automargin: true,
      gridcolor: "rgba(127,149,192,0.22)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    hovermode: "closest",
    showlegend: false,
    font: {
      family: "Arial, Helvetica, sans-serif",
      color: "#ffffff",
    },
  };
}

export {
  stackedBarLayout,
  groupedChartLayout,
  orderedBarLayout,
  categoryBarLayout,
};

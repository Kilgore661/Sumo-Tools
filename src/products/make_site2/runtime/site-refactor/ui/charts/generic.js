// Generic artifact-driven Plotly chart renderers.

import { escapeHtml } from "../../utils/html.js";
import {
  PLOTLY_CONFIG,
  axisRange,
  chartElementId,
  chartRows,
  monthIndexTicks,
  sparseTickText,
} from "./shared.js";

// Render the common title and Plotly host for a stacked bar chart.
function renderStackedBarChart(artifact, rowsBySource) {
  const rows = stackedBarRows(artifact, rowsBySource);
  if (!rows.length) {
    return `<p>No ${escapeHtml(artifact.heading)} data is available.</p>`;
  }
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
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
    '</div>',
    `<div id="${escapeHtml(chartElementId(artifact))}" class="plotly-chart"></div>`,
  ].join("");
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

function stackedBarRows(artifact, rowsBySource) {
  return chartRows(artifact, rowsBySource);
}

function stackedBarTraceSpec(artifact) {
  const trace = artifact.traces.find(candidate => candidate.kind === "stacked_bar");
  if (!trace) throw new Error(`No stacked_bar trace for ${artifact.id}`);
  return trace;
}

function groupedLineTraceSpec(artifact) {
  const trace = artifact.traces.find(candidate => candidate.kind === "scatter");
  if (!trace) throw new Error(`No scatter trace for ${artifact.id}`);
  return trace;
}

function orderedBarTraceSpec(artifact) {
  const trace = artifact.traces.find(candidate => candidate.kind === "bar");
  if (!trace) throw new Error(`No bar trace for ${artifact.id}`);
  return trace;
}

// Convert grouped source rows into Plotly stacked-bar traces.
function stackedBarTraces(artifact, rowsBySource) {
  const rows = stackedBarRows(artifact, rowsBySource);
  const trace = stackedBarTraceSpec(artifact);
  const groups = stackedBarGroupOrder(artifact, rows, trace);
  const colours = artifact.provenance.group_colours || {};
  return groups.map(group => {
    const groupRows = rows.filter(row => row[trace.group_by] === group);
    const plotlyTrace = {
      type: "bar",
      name: group,
      x: groupRows.map(row => row[trace.x]),
      y: groupRows.map(row => Number(row[trace.y])),
      hovertemplate: `${escapeHtml(trace.group_by)}=%{fullData.name}<br>${escapeHtml(trace.x)}=%{x}<br>${escapeHtml(trace.y)}=%{y}<extra></extra>`,
    };
    if (colours[group]) {
      plotlyTrace.marker = { color: colours[group] };
    }
    return plotlyTrace;
  });
}

// Convert grouped source rows into Plotly line traces.
function groupedLineTraces(artifact, rowsBySource) {
  const rows = chartRows(artifact, rowsBySource);
  const trace = groupedLineTraceSpec(artifact);
  const groups = chartGroupOrder(artifact, rows, trace);
  const defaultVisible = artifact.provenance.default_visible || [];
  return groups.map(group => {
    const groupRows = rows.filter(row => row[trace.group_by] === group);
    return {
      type: "scatter",
      mode: "lines",
      name: group,
      x: groupRows.map(row => row[trace.x]),
      y: groupRows.map(row => Number(row[trace.y])),
      visible: defaultVisible.length && !defaultVisible.includes(group) ? "legendonly" : true,
      hovertemplate: groupedLineHoverTemplate(trace, artifact.provenance.hover_fields || []),
      customdata: groupRows.map(row =>
        (artifact.provenance.hover_fields || []).map(field => row[field])
      ),
    };
  });
}

function orderedBarTrace(artifact, rowsBySource) {
  const rows = orderedRows(artifact, rowsBySource);
  const trace = orderedBarTraceSpec(artifact);
  const dateFields = artifact.provenance.date_fields || [];
  return {
    type: "bar",
    x: rows.map(row => row[trace.x]),
    y: rows.map(row => Number(row[trace.y])),
    customdata: rows.map(row => [
      row[artifact.provenance.order_field],
      ...dateFields.map(field => row[field]),
    ]),
    hovertemplate: orderedBarHoverTemplate(trace, artifact),
  };
}

function categoryBarTrace(artifact, rowsBySource) {
  const rows = chartRows(artifact, rowsBySource);
  const trace = orderedBarTraceSpec(artifact);
  const rowByCategory = new Map(rows.map(row => [row[trace.x], row]));
  const categories = artifact.x_axis.order_values.length
    ? artifact.x_axis.order_values
    : rows.map(row => row[trace.x]);
  return {
    type: "bar",
    name: trace.label,
    x: categories,
    y: categories.map(category => Number(rowByCategory.get(category)?.[trace.y] || 0)),
    hovertemplate: `${escapeHtml(trace.x)}=%{x}<br>${escapeHtml(trace.y)}=%{y}<extra></extra>`,
  };
}

function orderedRows(artifact, rowsBySource) {
  const rows = chartRows(artifact, rowsBySource);
  const orderField = artifact.provenance.order_field;
  if (!orderField) return rows;
  return [...rows].sort((left, right) => Number(left[orderField]) - Number(right[orderField]));
}

function orderedBarHoverTemplate(trace, artifact) {
  const orderField = artifact.provenance.order_field;
  const dateFields = artifact.provenance.date_fields || [];
  const lines = [
    `${escapeHtml(trace.x)}=%{x}`,
  ];
  if (orderField) {
    lines.push(`${escapeHtml(orderField)}=%{customdata[0]}`);
  }
  if (dateFields.length === 2) {
    lines.push(`${escapeHtml(trace.y)}=%{customdata[1]}/%{customdata[2]}`);
  } else {
    lines.push(`${escapeHtml(trace.y)}=%{y}`);
  }
  lines.push("<extra></extra>");
  return lines.join("<br>");
}

function groupedLineHoverTemplate(trace, hoverFields) {
  return [
    `${escapeHtml(trace.group_by)}=%{fullData.name}`,
    `${escapeHtml(trace.x)}=%{x}`,
    `${escapeHtml(trace.y)}=%{y:.3f}`,
    ...hoverFields.map((field, index) => `${escapeHtml(field)}=%{customdata[${index}]}`),
    "<extra></extra>",
  ].join("<br>");
}

function stackedBarGroupOrder(artifact, rows, trace) {
  const order = artifact.provenance.stack_order || artifact.provenance.group_order || [];
  if (order.length) return order;
  return [...new Set(rows.map(row => row[trace.group_by]))];
}

function chartGroupOrder(artifact, rows, trace) {
  const order = artifact.provenance.group_order || [];
  if (order.length) return order;
  return [...new Set(rows.map(row => row[trace.group_by]))];
}

function stackedBarLayout(artifact, rowsBySource) {
  const rows = stackedBarRows(artifact, rowsBySource);
  const trace = stackedBarTraceSpec(artifact);
  const xValues = artifact.x_axis.order_values.length
    ? artifact.x_axis.order_values
    : [...new Set(rows.map(row => row[trace.x]))];
  return {
    autosize: true,
    barmode: "stack",
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 76, r: 150, t: 18, b: 90 },
    xaxis: {
      title: artifact.x_axis.label,
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
      title: artifact.y_axis.label,
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
    ? artifact.x_axis.order_values
    : [...new Set(rows.map(row => row[trace.x]))];
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 76, r: 150, t: 18, b: 90 },
    xaxis: {
      title: artifact.x_axis.label,
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
      title: artifact.y_axis.label,
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
      title: artifact.x_axis.label,
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
      title: artifact.y_axis.label,
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
      title: artifact.x_axis.label,
      type: "category",
      categoryorder: "array",
      categoryarray: trace.x,
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    yaxis: {
      title: artifact.y_axis.label,
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
  renderStackedBarChart,
  renderGroupedLineChart,
  renderOrderedBarChart,
  renderCategoryBarChart,
  renderCategoryBarPlot,
  renderOrderedBarPlot,
  renderGroupedLinePlot,
  renderStackedBarPlot,
  stackedBarRows,
  stackedBarTraceSpec,
  groupedLineTraceSpec,
  orderedBarTraceSpec,
  stackedBarTraces,
  groupedLineTraces,
  orderedBarTrace,
  categoryBarTrace,
  orderedRows,
  orderedBarHoverTemplate,
  groupedLineHoverTemplate,
  stackedBarGroupOrder,
  chartGroupOrder,
  stackedBarLayout,
  groupedChartLayout,
  orderedBarLayout,
  categoryBarLayout,
};

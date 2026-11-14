// Trace-building helpers for generic artifact-driven Plotly chart renderers.

import { escapeHtml } from "../../utils/html.js";
import { dateLikeDisplay, dateLikeDisplayFromParts } from "../../utils/display.js";
import { chartRows } from "./shared.js";

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

function orderedPointTraceSpec(artifact) {
  const trace = artifact.traces.find(candidate => candidate.kind === "point");
  if (!trace) throw new Error(`No point trace for ${artifact.id}`);
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
      x: groupRows.map(row => dateLikeDisplay(row[trace.x])),
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
function groupedLineTraces(artifact, rowsBySource, state = {}) {
  const rows = chartRows(artifact, rowsBySource);
  const trace = groupedLineTraceSpec(artifact);
  const groups = chartGroupOrder(artifact, rows, trace);
  const defaultVisible = artifact.provenance.default_visible || [];
  return groups.map(group => {
    const groupRows = rows.filter(row => row[trace.group_by] === group);
    const plotlyTrace = {
      type: "scatter",
      mode: "lines",
      name: group,
      x: groupRows.map(row => dateLikeDisplay(row[trace.x])),
      y: groupRows.map(row => numericOrNull(row[trace.y])),
      visible: groupedLineTraceVisibility(group, defaultVisible, state.group_visibility),
      hovertemplate: artifact.provenance.hover_template || groupedLineHoverTemplate(trace, artifact.provenance.hover_fields || []),
      customdata: groupRows.map(row =>
        (artifact.provenance.hover_fields || []).map(field => row[field])
      ),
    };
    const errorFields = trace.error_y || [];
    if (state.error_bars && errorFields.length === 2) {
      const lower = errorFields[0];
      const upper = errorFields[1];
      const array = groupRows.map(row => positiveDifference(row[upper], row[trace.y]));
      const arrayminus = groupRows.map(row => positiveDifference(row[trace.y], row[lower]));
      plotlyTrace.error_y = {
        type: "data",
        symmetric: false,
        array,
        arrayminus,
        visible: true,
        color: "#d7e0ef",
        thickness: 1.5,
        width: 3,
      };
    }
    return plotlyTrace;
  });
}

function positiveDifference(high, low) {
  const highValue = Number(high);
  const lowValue = Number(low);
  return Number.isFinite(highValue) && Number.isFinite(lowValue)
    ? Math.max(0, highValue - lowValue)
    : 0;
}

function numericOrNull(value) {
  if (value === null || value === undefined || String(value).trim() === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function groupedLineTraceVisibility(group, defaultVisible, savedVisibility = null) {
  if (savedVisibility && Object.hasOwn(savedVisibility, group)) {
    return savedVisibility[group] === true ? true : "legendonly";
  }
  return defaultVisible.length && !defaultVisible.includes(group) ? "legendonly" : true;
}

function orderedPointTrace(artifact, rowsBySource) {
  const rows = orderedRows(artifact, rowsBySource);
  const trace = orderedPointTraceSpec(artifact);
  const dateFields = artifact.provenance.date_fields || [];
  return {
    type: "scatter",
    mode: "markers",
    x: rows.map(row => row[trace.x]),
    y: rows.map(row => Number(row[trace.y])),
    customdata: rows.map(row => [
      row[artifact.provenance.order_field],
      dateFields.length === 2 ? dateLikeDisplayFromParts(row[dateFields[0]], row[dateFields[1]]) : "",
    ]),
    hovertemplate: orderedPointHoverTemplate(trace, artifact),
  };
}

function categoryBarTrace(artifact, rowsBySource) {
  const rows = chartRows(artifact, rowsBySource);
  const trace = artifact.traces.find(candidate => candidate.kind === "bar");
  if (!trace) throw new Error(`No bar trace for ${artifact.id}`);
  const rowByCategory = new Map(rows.map(row => [dateLikeDisplay(row[trace.x]), row]));
  const categories = artifact.x_axis.order_values.length
    ? artifact.x_axis.order_values.map(value => dateLikeDisplay(value))
    : rows.map(row => dateLikeDisplay(row[trace.x]));
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

function orderedPointHoverTemplate(trace, artifact) {
  const orderField = artifact.provenance.order_field;
  const dateFields = artifact.provenance.date_fields || [];
  const lines = [
    `${escapeHtml(trace.x)}=%{x}`,
  ];
  if (orderField) {
    lines.push(`${escapeHtml(orderField)}=%{customdata[0]}`);
  }
  if (dateFields.length === 2) {
    lines.push(`${escapeHtml(trace.y)}=%{customdata[1]}`);
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

export {
  stackedBarRows,
  stackedBarTraceSpec,
  groupedLineTraceSpec,
  orderedPointTraceSpec,
  stackedBarTraces,
  groupedLineTraces,
  orderedPointTrace,
  categoryBarTrace,
  orderedRows,
  orderedPointHoverTemplate,
  groupedLineHoverTemplate,
  stackedBarGroupOrder,
  chartGroupOrder,
  positiveDifference,
  numericOrNull,
  groupedLineTraceVisibility,
};

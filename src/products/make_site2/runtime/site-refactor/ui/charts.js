import { divisionId, filterValueLabel } from "./filters.js";
import { compareValues, decimal, renderRikishiLink } from "./tables.js";
import { escapeHtml } from "../utils/html.js";

const PLOTLY_CONFIG = {
  displayModeBar: true,
  displaylogo: false,
  responsive: true,
};

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
function finishByChiiRows(artifact, state, rowsBySource) {
  const sourceId = state.direction === "bottom" ? "bottom_thresholds" : "top_thresholds";
  return [...(rowsBySource[sourceId] || [])]
    .filter(row => divisionId(row.division) === state.division && row.chii === state.chii)
    .sort((left, right) => Number(left.threshold) - Number(right.threshold));
}
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
function renderCareerLengthArtifact(artifact, state, rowsBySource) {
  const view = careerLengthView(artifact, state.view);
  if (view.kind === "table") {
    return renderCareerLengthTable(view, rowsBySource[state.view] || []);
  }
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
function renderStandingWinProbabilityChart(artifact, state, rowsBySource) {
  const source = selectedStandingSource(artifact, state);
  const rows = rowsBySource[source.id] || [];
  if (!rows.length) {
    return `<p>No ${escapeHtml(source.label)} data is available.</p>`;
  }
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(artifact.heading)}</h4>`,
    `<div>${escapeHtml(source.label)} source</div>`,
    '</div>',
    '<div id="standing-win-probability-chart" class="plotly-chart"></div>',
  ].join("");
}
function renderStandingWinProbabilityPlot(artifact, state, rowsBySource) {
  const host = document.getElementById("standing-win-probability-chart");
  if (!host) return;
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  const source = selectedStandingSource(artifact, state);
  const rows = rowsBySource[source.id] || [];
  const traces = standingWinProbabilityTraces(artifact, state, source, rows);
  Plotly.react(
    host,
    traces,
    standingWinProbabilityLayout(artifact, traces),
    PLOTLY_CONFIG
  ).then(() => {
    if (!host.on) return;
    if (host.__standingWinProbabilityHandlersAttached) return;
    host.__standingWinProbabilityHandlersAttached = true;
    host.on("plotly_restyle", () => {
      syncStandingCategoryAxis(host);
    });
    host.on("plotly_legenddoubleclick", event => {
      const target = host.data[event.curveNumber];
      if (!target) return false;
      const visibility = host.data.map((trace, index) => {
        if (trace.meta?.division !== target.meta?.division) return false;
        return index === event.curveNumber ? true : "legendonly";
      });
      Plotly.restyle(host, { visible: visibility }).then(() => {
        syncStandingCategoryAxis(host);
      });
      return false;
    });
  });
}
function standingWinProbabilityTraces(artifact, state, source, rows) {
  const trace = artifact.traces[0];
  const groups = standingWinProbabilityGroups(artifact, state, rows, trace);
  const selectedTraceKey = selectedStandingTraceKey(artifact, groups);
  return groups
    .map(group => standingWinProbabilityTrace(artifact, state, source, group, trace, selectedTraceKey));
}
function standingWinProbabilityGroups(artifact, state, rows, trace) {
  const groups = new Map();
  for (const row of rows) {
    if (!displayStandingChii(artifact, row.selected_chii)) continue;
    if (!displayStandingChii(artifact, row.opponent_chii)) continue;
    const division = divisionForStandingChii(row.selected_chii);
    if (state.division !== "All" && division !== state.division) continue;
    if (!groups.has(row[trace.group_by])) groups.set(row[trace.group_by], []);
    groups.get(row[trace.group_by]).push(row);
  }
  const selectedOrderField = artifact.provenance.selected_order_field;
  const xOrderField = artifact.provenance.x_order_field;
  return [...groups.entries()]
    .map(([key, groupRows]) => ({
      key,
      division: divisionForStandingChii(key),
      order: Number(groupRows[0]?.[selectedOrderField]) || 0,
      rows: groupRows.sort((left, right) =>
        compareValues(Number(left[xOrderField]) || 0, Number(right[xOrderField]) || 0)
      ),
    }))
    .sort((left, right) => left.order - right.order);
}
function standingWinProbabilityTrace(artifact, state, source, group, trace, selectedTraceKey) {
  const errorFields = trace.error_y || [];
  const showErrorBars = Boolean(state.error_bars) && errorFields.length === 2;
  const plotlyTrace = {
    type: "scatter",
    mode: "lines+markers",
    name: group.key,
    x: group.rows.map(row => row[trace.x]),
    y: group.rows.map(row => Number(row[trace.y])),
    visible: standingTraceVisible(group, selectedTraceKey),
    meta: { division: group.division },
    customdata: group.rows.map(row => standingWinProbabilityCustomData(source, row)),
    hovertemplate: standingWinProbabilityHoverTemplate(source),
  };
  if (showErrorBars) {
    const lower = errorFields[0];
    const upper = errorFields[1];
    const array = group.rows.map(row => {
      const high = Number(row[upper]);
      const value = Number(row[trace.y]);
      return Number.isFinite(high) && Number.isFinite(value) ? high - value : 0;
    });
    const arrayminus = group.rows.map(row => {
      const low = Number(row[lower]);
      const value = Number(row[trace.y]);
      return Number.isFinite(low) && Number.isFinite(value) ? value - low : 0;
    });
    if (array.some(value => value > 0) || arrayminus.some(value => value > 0)) {
      plotlyTrace.error_y = {
        type: "data",
        symmetric: false,
        array,
        arrayminus,
        visible: true,
        color: "#d7e0ef",
        thickness: 2,
        width: 4,
      };
    }
  }
  return plotlyTrace;
}
function standingWinProbabilityCustomData(source, row) {
  if (source.id === "observed") {
    return [
      row.selected_chii,
      row.opponent_chii,
      Number(row.opponent_ordinal),
      Number(row.n_obs),
      Number(row.n_selected_wins),
      Number(row.ci95_lower),
      Number(row.ci95_upper),
    ];
  }
  return [
    row.selected_chii,
    row.opponent_chii,
    Number(row.opponent_ordinal),
    Number(row.selected_rating),
    Number(row.opponent_rating),
  ];
}
function standingWinProbabilityHoverTemplate(source) {
  if (source.id === "observed") {
    return [
      "Selected=%{customdata[0]}",
      "Opponent=%{customdata[1]}",
      "P(selected wins)=%{y:.3f}",
      "CI95=[%{customdata[5]:.3f}, %{customdata[6]:.3f}]",
      "Wins=%{customdata[4]:,} / %{customdata[3]:,}",
      "<extra></extra>",
    ].join("<br>");
  }
  return [
    "Selected=%{customdata[0]}",
    "Opponent=%{customdata[1]}",
    "P(selected wins)=%{y:.3f}",
    "Selected rating=%{customdata[3]:.1f}",
    "Opponent rating=%{customdata[4]:.1f}",
    "<extra></extra>",
  ].join("<br>");
}
function selectedStandingTraceKey(artifact, groups) {
  const preferred = artifact.provenance.default_display_trace || "";
  if (groups.some(group => group.key === preferred)) return preferred;
  return groups[0]?.key || "";
}
function standingTraceVisible(group, selectedTraceKey) {
  if (group.key === selectedTraceKey) return true;
  return "legendonly";
}
function renderCareerLengthTable(view, rows) {
  const columns = view.columns || [];
  return [
    '<div class="artifact-title-block">',
    `<h4>${escapeHtml(view.label)}</h4>`,
    '</div>',
    '<table class="artifact-table">',
    '<thead><tr>',
    ...columns.map(column => `<th data-column-id="${escapeHtml(column.id)}">${escapeHtml(column.heading)}</th>`),
    '</tr></thead>',
    '<tbody>',
    ...rows.map((row, index) => [
      '<tr>',
      ...columns.map(column =>
        `<td data-column-id="${escapeHtml(column.id)}">${careerLengthCellValue(column, row, index)}</td>`
      ),
      '</tr>'
    ].join("")),
    '</tbody>',
    '</table>',
  ].join("");
}
function renderCareerLengthPlot(artifact, state, rowsBySource) {
  const view = careerLengthView(artifact, state.view);
  if (view.kind === "table") return;
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
function chartRows(artifact, rowsBySource) {
  const sourceId = artifact.data_binding.sources[0];
  return rowsBySource[sourceId] || [];
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
function careerLengthLayout(view) {
  return {
    autosize: true,
    barmode: view.kind === "stacked_bar" ? "stack" : undefined,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 76, r: 40, t: 18, b: 70 },
    xaxis: {
      title: view.x_label,
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    yaxis: {
      title: view.y_label,
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
function standingWinProbabilityLayout(artifact, traces) {
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 76, r: 36, t: 18, b: 92 },
    xaxis: {
      title: artifact.x_axis.label,
      type: "category",
      categoryorder: "array",
      categoryarray: visibleStandingCategories(traces),
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    yaxis: {
      title: artifact.y_axis.label,
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
      itemclick: "toggle",
      itemdoubleclick: false,
    },
    font: {
      family: "Arial, Helvetica, sans-serif",
      color: "#ffffff",
    },
  };
}
function sparseTickText(labels, maxLabels) {
  const step = Math.max(1, Math.ceil(labels.length / maxLabels));
  return labels.map((label, index) => index % step === 0 ? label : "");
}
function monthIndexTicks(maxMonthIndex, artifact) {
  const tickVals = [];
  const step = 24;
  for (let value = 0; value <= maxMonthIndex; value += step) {
    tickVals.push(value);
  }
  if (!tickVals.includes(maxMonthIndex)) {
    tickVals.push(maxMonthIndex);
  }
  return {
    values: tickVals,
    labels: tickVals.map(value => monthIndexLabel(value, artifact)),
  };
}
function monthIndexLabel(monthIndex, artifact) {
  const totalMonths = artifact.provenance.base_month - 1 + monthIndex;
  const year = artifact.provenance.base_year + Math.floor(totalMonths / 12);
  const month = (totalMonths % 12) + 1;
  return `${String(year).padStart(4, "0")}/${String(month).padStart(2, "0")}`;
}
function axisRange(axis) {
  if (axis.minimum === null || axis.maximum === null) return undefined;
  return [axis.minimum, axis.maximum];
}
function chartElementId(artifact) {
  return `${artifact.id}-chart`;
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
function careerLengthCellValue(column, row, index) {
  if (column.id === "rank") return String(index + 1);
  const value = row[column.source_field || column.id] || "";
  if (column.id === "shikona") return renderRikishiLink(value, row.rikishi_id);
  if (column.formatter === "decimal_2") return decimal(value, 2);
  if (column.id === "active") return value === "True" || value === "true" || value === "1" ? "Yes" : "No";
  return escapeHtml(value);
}
function selectedStandingSource(artifact, state) {
  return artifact.data_sources.find(source => source.id === state.source)
    || artifact.data_sources[0];
}
function resolveSelectedDataSourceId(artifact, selectedSource) {
  return artifact.data_sources.some(source => source.id === selectedSource)
    ? selectedSource
    : artifact.data_sources[0].id;
}
function resolveFilterValue(filters, filterId, selectedValue) {
  const filter = filters.find(candidate => candidate.id === filterId);
  if (!filter) return selectedValue;
  return filter.values.some(value => value.value === selectedValue)
    ? selectedValue
    : filter.default;
}
function displayStandingChii(artifact, chii) {
  const sanyaku = artifact.provenance.sanyaku_display || [];
  if (String(chii).startsWith("Y")) return sanyaku.includes(chii);
  if (String(chii).startsWith("O")) return sanyaku.includes(chii);
  if (String(chii).startsWith("S") && !String(chii).startsWith("Sd")) {
    return sanyaku.includes(chii);
  }
  if (String(chii).startsWith("K")) return sanyaku.includes(chii);
  return true;
}
function divisionForStandingChii(chii) {
  const value = String(chii || "");
  if (value.startsWith("Ms")) return "Makushita";
  if (value.startsWith("Sd")) return "Sandanme";
  if (value.startsWith("Jd")) return "Jonidan";
  if (value.startsWith("Jk")) return "Jonokuchi";
  if (["Y", "O", "S", "K", "M"].some(prefix => value.startsWith(prefix))) return "Makuuchi";
  if (value.startsWith("J")) return "Juryo";
  return "Other";
}
function visibleStandingCategories(traces) {
  const entries = new Map();
  const visibleTraces = traces.filter(trace =>
    trace.visible === true || trace.visible === undefined
  );
  const selectedTraces = visibleTraces.length ? visibleTraces : traces;
  for (const trace of selectedTraces) {
    trace.x.forEach((label, index) => {
      entries.set(label, trace.customdata[index][2]);
    });
  }
  return [...entries.entries()]
    .sort((left, right) => Number(left[1]) - Number(right[1]))
    .map(([label]) => label);
}
function syncStandingCategoryAxis(host) {
  if (!window.Plotly || !host?.data) return;
  Plotly.relayout(host, {
    "xaxis.categoryorder": "array",
    "xaxis.categoryarray": visibleStandingCategories(host.data),
  });
}

export { renderFinishByChiiChart, renderFinishByChiiPlot, finishByChiiRows, renderStackedBarChart, renderGroupedLineChart, renderOrderedBarChart, renderCategoryBarChart, renderCareerLengthArtifact, renderStandingWinProbabilityChart, renderStandingWinProbabilityPlot, standingWinProbabilityTraces, standingWinProbabilityGroups, standingWinProbabilityTrace, standingWinProbabilityCustomData, standingWinProbabilityHoverTemplate, selectedStandingTraceKey, standingTraceVisible, renderCareerLengthTable, renderCareerLengthPlot, careerLengthTraces, renderCategoryBarPlot, renderOrderedBarPlot, renderGroupedLinePlot, renderStackedBarPlot, stackedBarRows, chartRows, stackedBarTraceSpec, groupedLineTraceSpec, orderedBarTraceSpec, stackedBarTraces, groupedLineTraces, orderedBarTrace, categoryBarTrace, orderedRows, orderedBarHoverTemplate, groupedLineHoverTemplate, stackedBarGroupOrder, chartGroupOrder, stackedBarLayout, groupedChartLayout, orderedBarLayout, categoryBarLayout, careerLengthLayout, standingWinProbabilityLayout, sparseTickText, monthIndexTicks, monthIndexLabel, axisRange, chartElementId, resolveCareerLengthView, careerLengthView, careerLengthCellValue, selectedStandingSource, resolveSelectedDataSourceId, resolveFilterValue, displayStandingChii, divisionForStandingChii, visibleStandingCategories, syncStandingCategoryAxis };

// Standing Win Probability chart rendering, trace grouping and legend behaviour.

import { compareValues } from "../tables.js";
import { escapeHtml } from "../../utils/html.js";
import { PLOTLY_CONFIG, axisRange, axisTitle } from "./shared.js";

// Render the title and Plotly host for the selected rank win probability source.
function renderStandingWinProbabilityChart(artifact, state, rowsBySource) {
  const source = selectedStandingSource(artifact, state);
  const rows = rowsBySource[source.id] || [];
  if (!rows.length) {
    return `<p>No ${escapeHtml(source.label)} data is available.</p>`;
  }
  return [
    '<div class="artifact-title-block">',
    `<h4>Win Probability (${escapeHtml(source.label)})</h4>`,
    '</div>',
    '<div id="standing-win-probability-chart" class="plotly-chart"></div>',
  ].join("");
}

// Populate the Standing Win Probability host and attach Plotly legend behaviour.
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

// Build the visible/legendonly Plotly traces for the selected source and division.
function standingWinProbabilityTraces(artifact, state, source, rows) {
  const trace = artifact.traces[0];
  const groups = standingWinProbabilityGroups(artifact, state, rows, trace);
  const selectedTraceKey = selectedStandingTraceKey(artifact, groups);
  return groups
    .map(group => standingWinProbabilityTrace(artifact, state, source, group, trace, selectedTraceKey));
}

// Group source rows by selected Chii and filter them to the active division.
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
      "Selected Rank=%{customdata[0]}",
      "Opponent Rank=%{customdata[1]}",
      "P(selected rikishi wins)=%{y:.3f}",
      "CI95=[%{customdata[5]:.3f}, %{customdata[6]:.3f}]",
      "Wins=%{customdata[4]:,} / %{customdata[3]:,}",
      "<extra></extra>",
    ].join("<br>");
  }
  return [
    "Selected Rank=%{customdata[0]}",
    "Opponent Rank=%{customdata[1]}",
    "P(selected rikishi wins)=%{y:.3f}",
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

function standingWinProbabilityLayout(artifact, traces) {
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 76, r: 36, t: 18, b: 92 },
    xaxis: {
      title: axisTitle(artifact.x_axis.label),
      type: "category",
      categoryorder: "array",
      categoryarray: visibleStandingCategories(traces),
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    yaxis: {
      title: axisTitle(artifact.y_axis.label),
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

function selectedStandingSource(artifact, state) {
  return artifact.data_sources.find(source => source.id === state.source)
    || artifact.data_sources[0];
}

function resolveSelectedDataSourceId(artifact, selectedSource) {
  return artifact.data_sources.some(source => source.id === selectedSource)
    ? selectedSource
    : artifact.data_sources[0].id;
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

// Derive the x-axis category order from currently visible Plotly traces.
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

export {
  renderStandingWinProbabilityChart,
  renderStandingWinProbabilityPlot,
  standingWinProbabilityTraces,
  standingWinProbabilityGroups,
  standingWinProbabilityTrace,
  standingWinProbabilityCustomData,
  standingWinProbabilityHoverTemplate,
  selectedStandingTraceKey,
  standingTraceVisible,
  standingWinProbabilityLayout,
  selectedStandingSource,
  resolveSelectedDataSourceId,
  displayStandingChii,
  divisionForStandingChii,
  visibleStandingCategories,
  syncStandingCategoryAxis,
};

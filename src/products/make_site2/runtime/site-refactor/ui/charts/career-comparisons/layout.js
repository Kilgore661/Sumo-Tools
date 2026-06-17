import { axisTitle } from "../shared.js";
import { buildChiiScale } from "./chii-scale.js";
import { careerComparisonTraces } from "./traces.js";

function careerComparisonLayout(artifact, state, data, traces = null) {
  const resolvedTraces = traces || careerComparisonTraces(artifact, state, data);
  const yAxes = careerComparisonYAxes(artifact, state, data, resolvedTraces);
  return {
    autosize: true,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: usesChiiAxis(state) ? 156 : 116, r: 150, t: 18, b: 70 },
    xaxis: {
      title: axisTitle(state.x_base === "basho" ? "Number of Basho since Hatsu Dohyo" : "Date"),
      ...(state.x_base === "date" ? dateAxisCategoryOrder(traces || []) : {}),
      automargin: true,
      gridcolor: "rgba(127,149,192,0.18)",
      zerolinecolor: "rgba(127,149,192,0.35)",
      color: "#c9d4ee",
    },
    ...yAxes,
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

function careerComparisonYAxes(artifact, state, data, traces) {
  if (state.skill === "both") {
    const chiiTraces = traces.filter(trace => trace.yaxis === "y");
    const equeloTraces = traces.filter(trace => trace.yaxis === "y2");
    return {
      yaxis: chiiAxisLayout(artifact, state, data, chiiTraces),
      yaxis2: {
        ...equeloAxisLayout(state, equeloTraces),
        overlaying: "y",
        side: "right",
      },
    };
  }
  return {
    yaxis: state.skill === "chii"
      ? chiiAxisLayout(artifact, state, data, traces)
      : equeloAxisLayout(state, traces),
  };
}

function usesChiiAxis(state) {
  return state.skill === "chii" || state.skill === "both";
}

function dateAxisCategoryOrder(traces) {
  return {
    type: "category",
    categoryorder: "array",
    categoryarray: sortedTraceDates(traces),
  };
}

function sortedTraceDates(traces) {
  return [...new Set(traces.flatMap(trace => trace.x || []))]
    .sort((left, right) => String(left).localeCompare(String(right)));
}

function chiiAxisLayout(artifact, state, data, traces = null) {
  const scale = buildChiiScale(artifact, state, data);
  const range = numericTraceRange(traces || [], chiiRangePadding(scale));
  return {
    title: axisTitle(state.log ? "Chii (Compressed)" : "Chii"),
    autorange: range ? false : undefined,
    range,
    automargin: true,
    gridcolor: "rgba(127,149,192,0.22)",
    zerolinecolor: "rgba(127,149,192,0.35)",
    color: "#c9d4ee",
    tickmode: "array",
    tickvals: scale.tickValues,
    ticktext: scale.tickLabels,
    ticklabelstandoff: 24,
  };
}

function equeloAxisLayout(state, traces) {
  const range = numericTraceRange(traces, null);
  return {
    title: axisTitle(state.log ? "log(Equelo)" : "Equelo"),
    autorange: range ? false : undefined,
    range,
    tickformat: equeloTickFormat(state, range),
    automargin: true,
    gridcolor: "rgba(127,149,192,0.22)",
    zerolinecolor: "rgba(127,149,192,0.35)",
    color: "#c9d4ee",
  };
}

function equeloTickFormat(state, range) {
  if (!state.log) return ".0f";
  if (!range) return ".2f";
  const span = Math.abs(Number(range[1]) - Number(range[0]));
  if (!Number.isFinite(span)) return ".2f";
  if (span >= 10) return ".0f";
  if (span >= 1) return ".1f";
  if (span >= 0.1) return ".2f";
  return ".3f";
}

function numericTraceRange(traces, fixedPadding = null) {
  const values = traces
    .flatMap(trace => trace.y || [])
    .map(value => Number(value))
    .filter(value => Number.isFinite(value));
  if (!values.length) return undefined;
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  if (minimum === maximum) {
    const padding = fixedPadding ?? Math.max(1, Math.abs(minimum) * 0.02);
    return [minimum - padding, maximum + padding];
  }
  const padding = fixedPadding ?? (maximum - minimum) * 0.05;
  return [minimum - padding, maximum + padding];
}

function chiiRangePadding(scale) {
  if (scale.kind === "compressed") return 0.02;
  return 0.5;
}

export {
  careerComparisonLayout,
  careerComparisonYAxes,
  usesChiiAxis,
  dateAxisCategoryOrder,
  sortedTraceDates,
  chiiAxisLayout,
  equeloAxisLayout,
  equeloTickFormat,
  numericTraceRange,
  chiiRangePadding,
};

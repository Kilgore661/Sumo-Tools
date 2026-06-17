import { dateLikeDisplay } from "../../../utils/display.js";
import {
  CAREER_COMPARISON_TRACE_COLOURS,
  FLOAT_DP,
  POINT_CHII,
  POINT_DATE,
  POINT_EQUELO,
  POINT_SHIKONA,
} from "./constants.js";
import { buildChiiScale, humanChii } from "./chii-scale.js";
import { formatOptionalFloat } from "./format.js";
import { careerComparisonSession, careerComparisonsState } from "./state.js";
import { displayNameForRikishi } from "./options.js";
import { usesChiiAxis } from "./layout.js";

function careerComparisonTraces(artifact, state, data) {
  const chiiScale = usesChiiAxis(state) ? buildChiiScale(artifact, state, data) : null;
  const seriesSpecs = careerComparisonSeriesSpecs(state);
  return careerComparisonsState.selectedRikishiIds
    .flatMap(rikishiId => seriesSpecs
      .map(series => careerComparisonTrace(rikishiId, artifact, state, data, chiiScale, series))
    )
    .filter(Boolean);
}

function careerComparisonSeriesSpecs(state) {
  if (state.skill === "both") {
    return [
      { skill: "chii", suffix: "Chii", yaxis: "y", dash: "solid" },
      { skill: "equelo", suffix: "Equelo", yaxis: "y2", dash: "dot" },
    ];
  }
  return [
    {
      skill: state.skill,
      suffix: null,
      yaxis: "y",
      dash: "solid",
    },
  ];
}

function careerComparisonTrace(rikishiId, artifact, state, data, chiiScale, series = null) {
  const resolvedSeries = series || careerComparisonSeriesSpecs(state)[0];
  const points = data.points_by_rikishi[rikishiId] || [];
  if (!points.length) return null;
  const x = [];
  const y = [];
  const customdata = [];
  points.forEach((point, index) => {
    const yValue = careerComparisonYValue(point, artifact, state, chiiScale, resolvedSeries.skill);
    if (yValue === null || yValue === undefined || Number.isNaN(yValue)) return;
    x.push(state.x_base === "basho" ? index : dateLikeDisplay(point[POINT_DATE]));
    y.push(yValue);
    customdata.push([
      point[POINT_SHIKONA],
      dateLikeDisplay(point[POINT_DATE]),
      point[POINT_CHII],
      formatOptionalFloat(point[POINT_EQUELO]),
    ]);
  });
  if (!x.length) return null;
  return {
    type: "scatter",
    mode: "lines",
    name: careerComparisonTraceName(rikishiId, data, resolvedSeries),
    yaxis: resolvedSeries.yaxis,
    line: { color: careerComparisonTraceColour(rikishiId), dash: resolvedSeries.dash },
    x,
    y,
    customdata,
    hovertemplate: careerComparisonHoverTemplate(state, resolvedSeries.skill),
  };
}

function careerComparisonTraceName(rikishiId, data, series) {
  const displayName = displayNameForRikishi(rikishiId, data);
  return series.suffix ? `${displayName} - ${series.suffix}` : displayName;
}

function careerComparisonTraceColour(rikishiId) {
  if (!careerComparisonSession.traceColoursByRikishiId.has(rikishiId)) {
    const colour = CAREER_COMPARISON_TRACE_COLOURS[
      careerComparisonSession.nextTraceColourIndex % CAREER_COMPARISON_TRACE_COLOURS.length
    ];
    careerComparisonSession.traceColoursByRikishiId.set(rikishiId, colour);
    careerComparisonSession.nextTraceColourIndex += 1;
  }
  return careerComparisonSession.traceColoursByRikishiId.get(rikishiId);
}

function careerComparisonYValue(point, artifact, state, chiiScale, skill = state.skill) {
  if (skill === "equelo") {
    const rating = point[POINT_EQUELO];
    if (rating === null || rating === undefined) return null;
    const value = Number(rating);
    if (!state.log) return value;
    return Math.log(value) / Math.log(Number(artifact.provenance.equelo_log_base));
  }
  const human = humanChii(point[POINT_CHII]);
  return chiiScale.valuesByHuman.get(human);
}

function careerComparisonHoverTemplate(state, skill = state.skill) {
  const yLabel = skill === "equelo"
    ? (state.log ? "log(Equelo)" : "Equelo")
    : (state.log ? "Chii (Compressed)" : "Chii");
  const yFormat = `:.${FLOAT_DP}f`;
  const xLabel = state.x_base === "basho" ? "Number of Basho since Hatsu Dohyo" : "Date";
  const lines = [
    "Shikona=%{customdata[0]}",
    `${xLabel}=%{x}`,
  ];
  if (state.x_base === "basho") {
    lines.push("Date=%{customdata[1]}");
  }
  lines.push(
    "Chii=%{customdata[2]}",
    "Equelo=%{customdata[3]}",
    `${yLabel}=%{y${yFormat}}`,
    "<extra></extra>",
  );
  return lines.join("<br>");
}

export {
  careerComparisonTraces,
  careerComparisonSeriesSpecs,
  careerComparisonTrace,
  careerComparisonTraceName,
  careerComparisonTraceColour,
  careerComparisonYValue,
  careerComparisonHoverTemplate,
};

import { genericXAxisTickAngle } from "./generic-angle-policy.js";
import {
  categoryBarLayout,
  groupedChartLayout as baseGroupedChartLayout,
  orderedBarLayout as baseOrderedBarLayout,
  stackedBarLayout as baseStackedBarLayout,
} from "./generic-layouts.js";

function setXAxisTickAngle(artifact, layout) {
  layout.xaxis.tickangle = genericXAxisTickAngle(artifact);
  return layout;
}

function stackedBarLayout(artifact, rowsBySource) {
  return setXAxisTickAngle(artifact, baseStackedBarLayout(artifact, rowsBySource));
}

function groupedChartLayout(artifact, rowsBySource) {
  return setXAxisTickAngle(artifact, baseGroupedChartLayout(artifact, rowsBySource));
}

function orderedBarLayout(artifact, trace) {
  return setXAxisTickAngle(artifact, baseOrderedBarLayout(artifact, trace));
}

export {
  stackedBarLayout,
  groupedChartLayout,
  orderedBarLayout,
  categoryBarLayout,
};

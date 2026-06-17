// Career Comparisons chart controls, selector and Plotly rendering.
//
// This file intentionally stays thin: it preserves the existing public module
// surface while the implementation lives in focused modules under
// ./career-comparisons/.

export { renderCareerComparisonsPanel } from "./career-comparisons/panel.js";
export {
  renderCareerComparisonsControls,
  wireCareerComparisonsControls,
} from "./career-comparisons/controls.js";
export { renderCareerComparisonsChart } from "./career-comparisons/chart.js";
export { renderCareerComparisonsPlot } from "./career-comparisons/plot.js";
export {
  careerComparisonTraces,
  careerComparisonTrace,
  careerComparisonYValue,
  careerComparisonTraceColour,
} from "./career-comparisons/traces.js";
export {
  careerComparisonLayout,
  dateAxisCategoryOrder,
  sortedTraceDates,
  chiiAxisLayout,
  equeloAxisLayout,
  numericTraceRange,
  chiiRangePadding,
} from "./career-comparisons/layout.js";
export {
  formatFloatLabel,
  formatOptionalFloat,
} from "./career-comparisons/format.js";
export {
  buildChiiScale,
  linearChiiScale,
  compressedChiiScale,
  humanChii,
  humanChiiSortKey,
  spacedChiiTicks,
  parseChii,
} from "./career-comparisons/chii-scale.js";
export { careerComparisonRikishiOptions } from "./career-comparisons/options.js";
export {
  readCareerComparisonSelectionFromUrl,
  writeCareerComparisonSelectionToUrl,
} from "./career-comparisons/selection-url.js";
export { resetCareerComparisonsState } from "./career-comparisons/state.js";

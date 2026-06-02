// Public chart runtime facade.

export {
  renderFinishByChiiChart,
  renderFinishByChiiPlot,
  finishByChiiRows,
} from "./charts/finish-by-chii.js";

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
} from "./charts/generic.js";

export {
  renderCareerLengthArtifact,
  renderCareerLengthTable,
  renderCareerLengthPlot,
  careerLengthTraces,
  careerLengthLayout,
  resolveCareerLengthView,
  careerLengthView,
  careerLengthCellValue,
} from "./charts/career-length.js";

export {
  renderCareerComparisonsPanel,
  renderCareerComparisonsControls,
  renderCareerComparisonsChart,
  wireCareerComparisonsControls,
  renderCareerComparisonsPlot,
  careerComparisonTraces,
  careerComparisonTrace,
  careerComparisonYValue,
  careerComparisonLayout,
  chiiAxisLayout,
  buildChiiScale,
  linearChiiScale,
  compressedChiiScale,
  humanChii,
  humanChiiSortKey,
  parseChii,
  careerComparisonRikishiOptions,
  resetCareerComparisonsState,
} from "./charts/career-comparisons.js";

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
} from "./charts/standing-win-probability.js";

export {
  chartRows,
  sparseTickText,
  monthIndexTicks,
  monthIndexLabel,
  axisRange,
  chartElementId,
  resolveFilterValue,
} from "./charts/shared.js";

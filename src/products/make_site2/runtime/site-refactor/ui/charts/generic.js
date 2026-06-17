// Public facade for generic artifact-driven Plotly chart renderers.

export {
  renderStackedBarChart,
  renderGroupedLineChart,
  renderOrderedBarChart,
  renderCategoryBarChart,
  renderArtifactSubheading,
  renderCategoryBarPlot,
  renderOrderedBarPlot,
  renderGroupedLinePlot,
  renderStackedBarPlot,
} from "./generic-renderers.js";

export {
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
} from "./generic-traces.js";

export {
  stackedBarLayout,
  groupedChartLayout,
  orderedBarLayout,
  categoryBarLayout,
} from "./generic-layouts.js";

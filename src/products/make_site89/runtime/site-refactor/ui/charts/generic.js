// Public facade for generic artifact-driven Plotly chart renderers.

export {
  renderStackedBarChart,
  renderGroupedLineChart,
  renderOrderedPointChart,
  renderCategoryBarChart,
  renderArtifactSubheading,
  renderCategoryBarPlot,
  renderOrderedPointPlot,
  renderGroupedLinePlot,
  groupedLineVisibility,
  renderStackedBarPlot,
} from "./generic-renderers.js";

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
  groupedLineTraceVisibility,
} from "./generic-traces.js";

export {
  stackedBarLayout,
  groupedChartLayout,
  orderedPointLayout,
  categoryBarLayout,
} from "./generic-layouts.js";

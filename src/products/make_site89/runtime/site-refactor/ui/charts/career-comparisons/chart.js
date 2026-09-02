import { escapeHtml } from "../../../utils/html.js";
import { careerComparisonRikishiOptions } from "./options.js";

function renderCareerComparisonsChart(artifact, data, options = null) {
  const resolvedOptions = options || careerComparisonRikishiOptions(data);
  if (!resolvedOptions.length) return "<p>No Rikishi History data is available.</p>";
  return [
    '<div class="artifact-title-block">',
    `<h4 id="career-comparisons-pa-heading">${escapeHtml(artifact.heading)}</h4>`,
    '<h5 id="career-comparisons-pa-subheading" hidden></h5>',
    '</div>',
    '<div id="career-comparisons-chart" class="plotly-chart"></div>',
  ].join("");
}

export { renderCareerComparisonsChart };

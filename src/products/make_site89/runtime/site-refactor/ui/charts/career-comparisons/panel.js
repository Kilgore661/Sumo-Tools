import { renderCareerComparisonsChart } from "./chart.js";
import { renderCareerComparisonsControls } from "./controls.js";
import { careerComparisonRikishiOptions } from "./options.js";

function renderCareerComparisonsPanel(artifact, state, data) {
  const options = careerComparisonRikishiOptions(data);
  return [
    renderCareerComparisonsControls(state),
    '<section class="pa-panel">',
    '<div class="pa-slot">',
    renderCareerComparisonsChart(artifact, data, options),
    '</div>',
    '</section>',
  ].join("");
}

export { renderCareerComparisonsPanel };

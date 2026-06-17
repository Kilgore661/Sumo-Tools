import { PLOTLY_CONFIG } from "../shared.js";
import { careerComparisonsState } from "./state.js";
import { careerComparisonCaption } from "./caption.js";
import { careerComparisonTraces } from "./traces.js";
import { careerComparisonLayout, usesChiiAxis } from "./layout.js";

function renderCareerComparisonsPlot(artifact, state, data) {
  const host = document.getElementById("career-comparisons-chart");
  if (!host) return;
  updateCareerComparisonCaption(artifact, data);
  if (!careerComparisonsState.selectedRikishiIds.length) {
    if (window.Plotly && host.on) Plotly.purge(host);
    host.innerHTML = '<p class="career-comparison-empty">Select one or more rikishi.</p>';
    return;
  }
  if (!window.Plotly) {
    host.innerHTML = "<p>Plotly is not available.</p>";
    return;
  }
  host.classList.toggle("career-comparisons-chii-axis", usesChiiAxis(state));
  const traces = careerComparisonTraces(artifact, state, data);
  if (!traces.length) {
    if (host.on) Plotly.purge(host);
    host.innerHTML = '<p class="career-comparison-empty">No plottable points are available for the selected rikishi and chart options.</p>';
    return;
  }
  if (host.querySelector(".career-comparison-empty")) {
    host.innerHTML = "";
  }
  Plotly.react(host, traces, careerComparisonLayout(artifact, state, data, traces), PLOTLY_CONFIG)
    .then(() => {
      attachCareerComparisonLegendHandler(host);
    });
}

function updateCareerComparisonCaption(artifact, data) {
  const heading = document.getElementById("career-comparisons-pa-heading");
  const subheading = document.getElementById("career-comparisons-pa-subheading");
  if (!heading || !subheading) return;
  const caption = careerComparisonCaption(artifact, data);
  heading.textContent = caption.heading;
  subheading.textContent = caption.subheading;
  subheading.hidden = !caption.subheading;
}

function attachCareerComparisonLegendHandler(host) {
  if (!host.on) return;
  if (host.__careerComparisonHandlersAttached) return;
  host.__careerComparisonHandlersAttached = true;
  host.on("plotly_legenddoubleclick", event => {
    const visibility = host.data.map((_, index) =>
      index === event.curveNumber ? true : "legendonly"
    );
    Plotly.restyle(host, { visible: visibility });
    return false;
  });
}

export {
  renderCareerComparisonsPlot,
  updateCareerComparisonCaption,
  attachCareerComparisonLegendHandler,
};

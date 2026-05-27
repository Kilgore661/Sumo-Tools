import { updateStickyArtifactHeaders } from "./layout.js";
import { escapeHtml } from "../utils/html.js";

function renderNotes(artifact, state) {
  const notes = (artifact.notes || []).filter(note => noteApplies(note, state));
  if (!notes.length) return "";
  return [
    '<aside class="notes-panel" data-notes-panel>',
    '<button class="notes-toggle" type="button" data-notes-toggle aria-expanded="true">Hide notes</button>',
    '<div class="notes-panel-body" data-notes-body>',
    '<h4>Notes</h4>',
    '<ol>',
    ...notes.map(note => `<li>${escapeHtml(note.text)}</li>`),
    '</ol>',
    '</div>',
    '</aside>'
  ].join("");
}
function wireNotesPanel() {
  const panel = document.querySelector("[data-notes-panel]");
  if (!panel) return;
  const toggle = panel.querySelector("[data-notes-toggle]");
  const body = panel.querySelector("[data-notes-body]");
  if (!toggle || !body) return;
  toggle.addEventListener("click", () => {
    const collapsed = panel.classList.toggle("notes-panel-collapsed");
    body.hidden = collapsed;
    toggle.textContent = collapsed ? "Show notes" : "Hide notes";
    toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
    updateStickyArtifactHeaders();
    resizePlotlyCharts();
  });
}
function resizePlotlyCharts() {
  window.requestAnimationFrame(() => {
    if (!window.Plotly?.Plots?.resize) return;
    document.querySelectorAll(".plotly-chart").forEach(chart => {
      window.Plotly.Plots.resize(chart);
    });
  });
}
function noteApplies(note, state) {
  const applies = note.applies_to || ["all"];
  if (applies.includes("all")) return true;
  if (applies.includes("previous_basho")) return Boolean(state.previous_context);
  if (applies.includes("rating_context")) return Boolean(state.rating_context);
  if (applies.includes("nu_chii")) return Boolean(state.nu_chii);
  if (applies.includes("context")) return Boolean(state.context);
  if (applies.includes("delta")) return Boolean(state.delta);
  if (applies.includes("equelo")) return Boolean(state.equelo);
  if (applies.includes("banzuke_style")) return Boolean(state.banzuke_style);
  if (applies.includes(state.metric_group_preset)) return true;
  if (applies.includes(state.view)) return true;
  return false;
}

export { renderNotes, wireNotesPanel, noteApplies };

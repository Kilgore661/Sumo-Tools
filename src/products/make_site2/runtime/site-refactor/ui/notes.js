// PA-local note rendering and collapse behaviour.

import { updateStickyArtifactHeaders } from "./layout.js";
import { escapeHtml } from "../utils/html.js";

const NOTES_COLLAPSED_STORAGE_KEY = "gaspodeSumoLab.makeSite2.notesCollapsed";
const NOTE_HIGHLIGHT_DURATION_MS = 5000;
let noteHighlightTimer = null;
let noteOpenHandlerInstalled = false;

// Render notes that apply to the current artifact and filter state.
function renderNotes(artifact, state) {
  const notes = (artifact.notes || []).filter(note => noteApplies(note, state));
  if (!notes.length) return "";
  return [
    '<aside class="notes-panel" data-notes-panel>',
    '<div class="notes-hider-strip">',
    '<button class="notes-toggle" type="button" data-notes-toggle aria-expanded="true" aria-label="Hide notes" title="Hide notes">˅</button>',
    '</div>',
    '<div class="notes-content" data-notes-body>',
    '<h4>Notes</h4>',
    '<ol>',
    ...notes.map(note => `<li data-note-id="${escapeHtml(note.id)}">${escapeHtml(note.text)}</li>`),
    '</ol>',
    '</div>',
    '</aside>'
  ].join("");
}
// Attach collapse behaviour to the rendered Notes panel.
function wireNotesPanel() {
  installNoteOpenHandler();
  const panel = document.querySelector("[data-notes-panel]");
  if (!panel) return;
  const toggle = panel.querySelector("[data-notes-toggle]");
  const body = panel.querySelector("[data-notes-body]");
  if (!toggle || !body) return;
  const initialCollapsed = window.localStorage.getItem(NOTES_COLLAPSED_STORAGE_KEY) === "true";
  applyNotesCollapsedState(panel, body, toggle, initialCollapsed);
  toggle.addEventListener("click", () => {
    const collapsed = !panel.classList.contains("notes-panel-collapsed");
    applyNotesCollapsedState(panel, body, toggle, collapsed);
    window.localStorage.setItem(NOTES_COLLAPSED_STORAGE_KEY, String(collapsed));
    updateStickyArtifactHeaders();
    resizePlotlyCharts();
  });
}

function installNoteOpenHandler() {
  if (noteOpenHandlerInstalled) return;
  noteOpenHandlerInstalled = true;
  document.addEventListener("sumo:open-note", event => {
    openAndHighlightNote(event.detail?.noteId || "");
  });
}

function openAndHighlightNote(noteId) {
  const panel = document.querySelector("[data-notes-panel]");
  const body = panel?.querySelector("[data-notes-body]");
  const toggle = panel?.querySelector("[data-notes-toggle]");
  const note = noteId && panel ? panel.querySelector(`[data-note-id="${cssEscape(noteId)}"]`) : null;
  if (!panel || !body || !toggle || !note) {
    window.alert("No such note: " + (noteId || "empty"));
    return;
  }
  applyNotesCollapsedState(panel, body, toggle, false);
  window.localStorage.setItem(NOTES_COLLAPSED_STORAGE_KEY, "false");
  updateStickyArtifactHeaders();
  resizePlotlyCharts();
  highlightNote(note);
}

function highlightNote(noteElement) {
  document.querySelectorAll(".note-highlight").forEach(item => item.classList.remove("note-highlight"));
  noteElement.classList.add("note-highlight");
  noteElement.setAttribute("tabindex", "-1");
  noteElement.scrollIntoView({ block: "nearest", behavior: "smooth" });
  noteElement.focus({ preventScroll: true });
  if (noteHighlightTimer) clearTimeout(noteHighlightTimer);
  noteHighlightTimer = window.setTimeout(() => {
    noteElement.classList.remove("note-highlight");
    noteElement.removeAttribute("tabindex");
    noteHighlightTimer = null;
  }, NOTE_HIGHLIGHT_DURATION_MS);
}

function cssEscape(value) {
  if (window.CSS?.escape) return window.CSS.escape(value);
  return String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

function applyNotesCollapsedState(panel, body, toggle, collapsed) {
  panel.classList.toggle("notes-panel-collapsed", collapsed);
  body.hidden = collapsed;
  toggle.textContent = collapsed ? "˄" : "˅";
  toggle.setAttribute("aria-label", collapsed ? "Show notes" : "Hide notes");
  toggle.title = collapsed ? "Show notes" : "Hide notes";
  toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
}

function resizePlotlyCharts() {
  window.requestAnimationFrame(() => {
    if (!window.Plotly?.Plots?.resize) return;
    document.querySelectorAll(".plotly-chart").forEach(chart => {
      window.Plotly.Plots.resize(chart);
    });
  });
}
// Decide whether a note applies under the current filter state.
function noteApplies(note, state) {
  const applies = note.applies_to || ["all"];
  if (applies.includes("all")) return true;
  if (applies.includes("previous_basho")) return Boolean(state.previous_context);
  if (applies.includes("changes_context")) return Boolean(state.changes_context);
  if (applies.includes("rating_context")) return Boolean(state.rating_context);
  if (applies.includes("analysis_context")) return Boolean(state.analysis_context);
  if (applies.includes("nu_chii")) return Boolean(state.nu_chii);
  if (applies.includes("context")) return Boolean(state.context);
  if (applies.includes("delta")) return Boolean(state.delta);
  if (applies.includes("equelo")) return Boolean(state.equelo);
  if (applies.includes("banzuke_style")) return Boolean(state.banzuke_style);
  if (applies.includes(state.metric_group_preset)) return true;
  if (applies.includes(state.view)) return true;
  return false;
}

export {
  renderNotes,
  wireNotesPanel,
  installNoteOpenHandler,
  openAndHighlightNote,
  highlightNote,
  noteApplies,
  applyNotesCollapsedState,
};
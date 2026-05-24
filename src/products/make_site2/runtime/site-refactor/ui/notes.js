import { escapeHtml } from "../utils/html.js";

function renderNotes(artifact, state) {
  const notes = (artifact.notes || []).filter(note => noteApplies(note, state));
  if (!notes.length) return "";
  return [
    '<aside class="notes-panel">',
    '<h4>Notes</h4>',
    '<ol>',
    ...notes.map(note => `<li>${escapeHtml(note.text)}</li>`),
    '</ol>',
    '</aside>'
  ].join("");
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
  if (applies.includes(state.metric_group_preset)) return true;
  if (applies.includes(state.view)) return true;
  return false;
}

export { renderNotes, noteApplies };

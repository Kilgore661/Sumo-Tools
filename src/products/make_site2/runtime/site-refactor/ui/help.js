// Invisible hover help affordance for declared UI gloss.

import { escapeHtml } from "../utils/html.js";

let activeHelpTarget = null;
let helpLayer = null;

function renderLabelWithHelp(label, help, options = {}) {
  if (!help) return escapeHtml(label);
  const resolvedOptions = normalizeHelpOptions(options, label);
  const escapedLabel = escapeHtml(resolvedOptions.helpLabel || label || "Item");
  const escapedHelp = escapeHtml(help);
  const attributes = [
    'class="help-popover"',
    `data-help="${escapedHelp}"`,
    `aria-label="${escapedLabel}: ${escapedHelp}"`,
  ];
  if (containsExactNotes(help)) {
    attributes.push('data-notes-popover="true"');
    attributes.push('role="button"');
    attributes.push('tabindex="0"');
  }
  if (resolvedOptions.noteId) attributes.push(`data-note-id="${escapeHtml(resolvedOptions.noteId)}"`);
  return [
    `<span ${attributes.join(" ")}>`,
    escapeHtml(label),
    '</span>',
    '<span class="help-popover-marker" aria-hidden="true">?</span>',
  ].join("");
}

function normalizeHelpOptions(options, label) {
  if (typeof options === "string") return { helpLabel: options };
  return options || { helpLabel: label };
}

function installHelpPopovers() {
  if (helpLayer) return;
  helpLayer = document.createElement("div");
  helpLayer.className = "help-popover-layer";
  helpLayer.hidden = true;
  document.body.append(helpLayer);

  document.addEventListener("pointerover", event => {
    const target = helpTargetFromEvent(event);
    if (target) showHelpPopover(target);
  });
  document.addEventListener("pointerout", event => {
    if (!activeHelpTarget) return;
    if (event.relatedTarget instanceof Node && activeHelpTarget.contains(event.relatedTarget)) return;
    hideHelpPopover();
  });
  document.addEventListener("focusin", event => {
    const target = helpTargetFromEvent(event);
    if (target) showHelpPopover(target);
  });
  document.addEventListener("focusout", event => {
    if (!activeHelpTarget) return;
    if (event.relatedTarget instanceof Node && activeHelpTarget.contains(event.relatedTarget)) return;
    hideHelpPopover();
  });
  document.addEventListener("click", event => {
    const target = notesHelpTargetFromEvent(event);
    if (!target) return;
    event.preventDefault();
    event.stopPropagation();
    hideHelpPopover();
    dispatchOpenNote(target.dataset.noteId || "");
  }, true);
  document.addEventListener("keydown", event => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const target = notesHelpTargetFromEvent(event);
    if (!target) return;
    event.preventDefault();
    event.stopPropagation();
    hideHelpPopover();
    dispatchOpenNote(target.dataset.noteId || "");
  }, true);
  window.addEventListener("resize", () => positionHelpPopover(), { passive: true });
  document.addEventListener("scroll", () => positionHelpPopover(), { capture: true, passive: true });
}

function helpTargetFromEvent(event) {
  return event.target instanceof Element ? event.target.closest(".help-popover") : null;
}

function notesHelpTargetFromEvent(event) {
  const target = helpTargetFromEvent(event);
  return target?.dataset.notesPopover === "true" ? target : null;
}

function showHelpPopover(target) {
  const help = target.dataset.help;
  if (!help || !helpLayer) return;
  activeHelpTarget = target;
  helpLayer.textContent = help;
  helpLayer.hidden = false;
  positionHelpPopover();
}

function hideHelpPopover() {
  activeHelpTarget = null;
  if (helpLayer) helpLayer.hidden = true;
}

function dispatchOpenNote(noteId) {
  document.dispatchEvent(new CustomEvent("sumo:open-note", { detail: { noteId } }));
}

function containsExactNotes(help) {
  return /(^|[^A-Za-z])Notes([^A-Za-z]|$)/.test(String(help || ""));
}

function positionHelpPopover() {
  if (!activeHelpTarget || !helpLayer || helpLayer.hidden) return;
  const targetRect = activeHelpTarget.getBoundingClientRect();
  const layerRect = helpLayer.getBoundingClientRect();
  const margin = 6;
  const preferredLeft = targetRect.left + targetRect.width * 0.6;
  const top = Math.min(
    targetRect.bottom + margin,
    window.innerHeight - layerRect.height - margin,
  );
  const left = Math.min(
    Math.max(margin, preferredLeft),
    window.innerWidth - layerRect.width - margin,
  );
  helpLayer.style.left = `${left}px`;
  helpLayer.style.top = `${Math.max(margin, top)}px`;
}

export { installHelpPopovers, renderLabelWithHelp, containsExactNotes, hideHelpPopover };
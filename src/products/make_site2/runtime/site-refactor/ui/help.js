// Invisible hover help affordance for declared UI gloss.

import { escapeHtml } from "../utils/html.js";

const HELP_POPOVER_LIFETIME_MS = 2000;

let activeHelpTarget = null;
let helpLayer = null;
let hideTimer = null;
let hideStartedAt = 0;
let hideRemainingMs = HELP_POPOVER_LIFETIME_MS;

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
  if (containsExactNotes(help)) attributes.push('data-notes-popover="true"');
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
  document.addEventListener("focusin", event => {
    const target = helpTargetFromEvent(event);
    if (target) showHelpPopover(target);
  });
  helpLayer.addEventListener("pointerover", () => {
    if (helpLayer.dataset.notesPopover === "true") pauseHideCountdown();
  });
  helpLayer.addEventListener("pointerout", event => {
    if (event.relatedTarget instanceof Node && helpLayer.contains(event.relatedTarget)) return;
    if (helpLayer.dataset.notesPopover === "true") startHideCountdown();
  });
  helpLayer.addEventListener("focusin", () => {
    if (helpLayer.dataset.notesPopover === "true") pauseHideCountdown();
  });
  helpLayer.addEventListener("focusout", event => {
    if (event.relatedTarget instanceof Node && helpLayer.contains(event.relatedTarget)) return;
    if (helpLayer.dataset.notesPopover === "true") startHideCountdown();
  });
  helpLayer.addEventListener("click", event => {
    if (helpLayer.dataset.notesPopover !== "true") return;
    event.preventDefault();
    event.stopPropagation();
    const noteId = helpLayer.dataset.noteId || "";
    hideHelpPopover();
    dispatchOpenNote(noteId);
  });
  helpLayer.addEventListener("keydown", event => {
    if (event.key !== "Enter" && event.key !== " ") return;
    if (helpLayer.dataset.notesPopover !== "true") return;
    event.preventDefault();
    event.stopPropagation();
    const noteId = helpLayer.dataset.noteId || "";
    hideHelpPopover();
    dispatchOpenNote(noteId);
  });
  window.addEventListener("resize", () => positionHelpPopover(), { passive: true });
  document.addEventListener("scroll", () => positionHelpPopover(), { capture: true, passive: true });
}

function helpTargetFromEvent(event) {
  return event.target instanceof Element ? event.target.closest(".help-popover") : null;
}

function showHelpPopover(target) {
  const help = target.dataset.help;
  if (!help || !helpLayer) return;
  activeHelpTarget = target;
  helpLayer.innerHTML = target.dataset.notesPopover === "true"
    ? renderNotesHelpText(help)
    : escapeHtml(help);
  helpLayer.dataset.notesPopover = target.dataset.notesPopover === "true" ? "true" : "false";
  helpLayer.dataset.noteId = target.dataset.noteId || "";
  helpLayer.tabIndex = helpLayer.dataset.notesPopover === "true" ? 0 : -1;
  helpLayer.setAttribute("role", helpLayer.dataset.notesPopover === "true" ? "button" : "tooltip");
  helpLayer.style.pointerEvents = helpLayer.dataset.notesPopover === "true" ? "auto" : "none";
  helpLayer.style.cursor = helpLayer.dataset.notesPopover === "true" ? "pointer" : "default";
  helpLayer.hidden = false;
  positionHelpPopover();
  hideRemainingMs = HELP_POPOVER_LIFETIME_MS;
  startHideCountdown(hideRemainingMs);
}

function renderNotesHelpText(help) {
  const escapedHelp = escapeHtml(help);
  return escapedHelp.replace(
    /(^|[^A-Za-z])(Notes)([^A-Za-z]|$)/,
    '$1<span class="help-popover-notes-link" style="cursor:pointer;text-decoration:underline;">$2</span>$3',
  );
}

function hideHelpPopover() {
  clearHideTimer();
  activeHelpTarget = null;
  if (!helpLayer) return;
  helpLayer.hidden = true;
  helpLayer.dataset.notesPopover = "false";
  helpLayer.dataset.noteId = "";
  helpLayer.tabIndex = -1;
  helpLayer.style.pointerEvents = "none";
  helpLayer.style.cursor = "default";
  hideRemainingMs = HELP_POPOVER_LIFETIME_MS;
}

function startHideCountdown(duration = hideRemainingMs) {
  clearHideTimer();
  hideRemainingMs = Math.max(0, duration);
  hideStartedAt = performance.now();
  hideTimer = window.setTimeout(() => {
    hideHelpPopover();
  }, hideRemainingMs);
}

function pauseHideCountdown() {
  if (!hideTimer) return;
  window.clearTimeout(hideTimer);
  hideTimer = null;
  hideRemainingMs = Math.max(0, hideRemainingMs - (performance.now() - hideStartedAt));
}

function clearHideTimer() {
  if (!hideTimer) return;
  window.clearTimeout(hideTimer);
  hideTimer = null;
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

export { installHelpPopovers, renderLabelWithHelp, containsExactNotes, hideHelpPopover, renderNotesHelpText };
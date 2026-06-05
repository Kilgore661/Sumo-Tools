// Invisible hover help affordance for declared UI gloss.

import { escapeHtml } from "../utils/html.js";

let activeHelpTarget = null;
let helpLayer = null;

function renderLabelWithHelp(label, help, helpLabel = label) {
  if (!help) return escapeHtml(label);
  const escapedLabel = escapeHtml(helpLabel || label || "Item");
  const escapedHelp = escapeHtml(help);
  return [
    `<span class="help-popover" data-help="${escapedHelp}" aria-label="${escapedLabel}: ${escapedHelp}">`,
    escapeHtml(label),
    '</span>',
    '<span class="help-popover-marker" aria-hidden="true">?</span>',
  ].join("");
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
  helpLayer.textContent = help;
  helpLayer.hidden = false;
  positionHelpPopover();
}

function hideHelpPopover() {
  activeHelpTarget = null;
  if (helpLayer) helpLayer.hidden = true;
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

export { installHelpPopovers, renderLabelWithHelp };

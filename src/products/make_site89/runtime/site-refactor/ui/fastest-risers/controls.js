// Purpose-built Fastest Risers Options panel.

import { escapeHtml } from "../../utils/html.js";
import { renderLabelWithHelp } from "../help.js";
import { groupLabel } from "./model.js";

function renderFastestRisersControls(model) {
  const { state, available_starts: starts, available_finishes: finishes } = model;
  return [
    '<form class="filter-section fastest-risers-controls" aria-label="Filters">',
    '<h4>Options</h4>',
    '<ul class="filter-list">',
    `<li>${renderRadioGroup("start", "Starting Division", starts.map(value => ({ value, label: groupLabel(value) })), state.start)}</li>`,
    `<li>${renderDropdown("finish", "Division of Interest", finishes.map(value => ({ value, label: groupLabel(value) })), state.finish)}</li>`,
    `<li>${renderRadioGroup("direction", "Direction", [{ value: "fastest", label: "Fastest" }, { value: "slowest", label: "Slowest" }], state.direction)}</li>`,
    `<li>${renderDropdown("ranking_range", "Ranking Range", [{ value: "10", label: "Top 10" }, { value: "20", label: "Top 20" }, { value: "50", label: "Top 50" }, { value: "all", label: "All" }], state.ranking_range)}</li>`,
    `<li>${renderHideRetired(state.hide_retired)}</li>`,
    '</ul>',
    '</form>',
  ].join("");
}

function renderRadioGroup(name, label, values, selected) {
  return [
    `<div class="choice-control" role="group" aria-label="${escapeHtml(label)}">`,
    `<span class="choice-label">${escapeHtml(label)}</span>`,
    '<ul class="choice-list">',
    ...values.map(value => [
      '<li><label class="radio-control">',
      `<input type="radio" name="${escapeHtml(name)}" value="${escapeHtml(value.value)}"${value.value === selected ? " checked" : ""}>`,
      `<span>${escapeHtml(value.label)}</span>`,
      '</label></li>',
    ].join("")),
    '</ul>',
    '</div>',
  ].join("");
}

function renderDropdown(name, label, values, selected) {
  return [
    '<label class="filter-control">',
    `<span>${escapeHtml(label)}</span>`,
    `<select name="${escapeHtml(name)}">`,
    ...values.map(value => `<option value="${escapeHtml(value.value)}"${value.value === selected ? " selected" : ""}>${escapeHtml(value.label)}</option>`),
    '</select>',
    '</label>',
  ].join("");
}

function renderHideRetired(checked) {
  const help = "Filters the selected ranking range. Positions are not recalculated and the table is not refilled.";
  return [
    '<label class="checkbox-control">',
    `<input type="checkbox" name="hide_retired"${checked ? " checked" : ""}>`,
    `<span>${renderLabelWithHelp("Hide retired rikishi", help)}</span>`,
    '</label>',
  ].join("");
}

export { renderFastestRisersControls, renderDropdown, renderRadioGroup };

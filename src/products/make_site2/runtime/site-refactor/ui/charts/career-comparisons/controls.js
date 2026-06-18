import { escapeHtml } from "../../../utils/html.js";
import { renderLabelWithHelp } from "../../help.js";
import { careerComparisonsState } from "./state.js";
import { modeLabel, skillHelp, skillLabel } from "./labels.js";
import { careerComparisonRikishiOptions } from "./options.js";
import {
  readCareerComparisonSelectionFromUrl,
  writeCareerComparisonSelectionToUrl,
} from "./selection-url.js";
import { renderCareerComparisonsPlot } from "./plot.js";
import {
  removeStoredRikishiVisibility,
  setRikishiTraceVisibility,
  syncRikishiVisibilityControls,
} from "./visibility.js";

const TRASH_ICON_PATH = "assets/trash.svg";

function renderCareerComparisonsControls(state) {
  return [
    '<form class="filter-section career-comparisons-controls" aria-label="Career comparison options">',
    '<h4>Options</h4>',
    '<fieldset class="career-comparison-mode-fieldset">',
    '<legend class="visually-hidden">Chart</legend>',
    '<table class="career-comparison-mode-table">',
    `<thead><tr><th></th><th scope="col">${renderLabelWithHelp("Date", "Use calendar date on the x-axis.")}</th><th scope="col">${renderLabelWithHelp("Hatsu", "Use basho since first appearance on the x-axis.")}</th></tr></thead>`,
    '<tbody>',
    ...["chii", "equelo", "both"].map(skill => [
      '<tr>',
      `<th scope="row">${renderLabelWithHelp(skillLabel(skill), skillHelp(skill))}</th>`,
      ...["date", "basho"].map(xBase => `<td>${renderModeChoice(skill, xBase, state)}</td>`),
      '</tr>',
    ].join("")),
    '</tbody>',
    '</table>',
    '</fieldset>',
    '<label class="checkbox-control career-comparison-log-control">',
    `<input type="checkbox" name="log"${state.log ? " checked" : ""}>`,
    `<span>${renderLabelWithHelp("Compress", "Compress lower banzuke divisions.")}</span>`,
    '</label>',
    '<div class="career-comparison-selector">',
    '<label class="filter-control career-comparison-search">',
    '<span>Rikishi</span>',
    '<input type="text" name="rikishi_search" autocomplete="off" list="career-comparison-candidates" autofocus tabindex="0">',
    '</label>',
    '<datalist id="career-comparison-candidates"></datalist>',
    '<ul class="career-comparison-selected" aria-label="Selected rikishi"></ul>',
    '</div>',
    '</form>',
  ].join("");
}

function renderModeChoice(skill, xBase, state) {
  const id = `career-comparison-${skill}-${xBase}`;
  const checked = state.skill === skill && state.x_base === xBase ? " checked" : "";
  return [
    '<label class="radio-control career-comparison-mode">',
    `<input id="${id}" type="radio" name="career_comparison_mode" value="${skill}:${xBase}"${checked}>`,
    `<span class="visually-hidden">${escapeHtml(modeLabel(skill, xBase))}</span>`,
    '</label>',
  ].join("");
}

function wireCareerComparisonsControls(panel, artifact, state, data, writeState) {
  const form = document.querySelector(".career-comparisons-controls");
  if (!form) return;
  readCareerComparisonSelectionFromUrl(data);
  const options = careerComparisonRikishiOptions(data);
  const optionsByLabel = new Map(options.map(option => [option.label, option]));
  const optionsById = new Map(options.map(option => [option.id, option]));
  const input = form.elements.rikishi_search;
  const datalist = form.querySelector("#career-comparison-candidates");
  const selectedList = form.querySelector(".career-comparison-selected");
  const applyState = () => {
    const nextState = careerComparisonControlState(form, state);
    Object.assign(state, nextState);
    writeState(panel, nextState);
    writeCareerComparisonSelectionToUrl();
    renderCareerComparisonsPlot(artifact, nextState, data);
  };

  updateCareerComparisonCandidates(input, datalist, options);
  renderSelectedRikishiList(selectedList, optionsById);
  renderCareerComparisonsPlot(artifact, state, data);
  focusCareerComparisonSearch(input);

  input.addEventListener("input", () => {
    enableCareerComparisonDatalist(input);
    if (consumeExactRikishiSelection(input, optionsByLabel, datalist, selectedList, options, optionsById)) {
      applyState();
      return;
    }
    updateCareerComparisonCandidates(input, datalist, options);
  });
  input.addEventListener("change", () => {
    enableCareerComparisonDatalist(input);
    if (consumeExactRikishiSelection(input, optionsByLabel, datalist, selectedList, options, optionsById)) {
      applyState();
    }
  });
  selectedList.addEventListener("click", event => {
    const button = event.target.closest("button[data-rikishi-id]");
    if (!button) return;
    careerComparisonsState.selectedRikishiIds = careerComparisonsState.selectedRikishiIds
      .filter(id => id !== button.dataset.rikishiId);
    removeStoredRikishiVisibility(button.dataset.rikishiId);
    renderSelectedRikishiList(selectedList, optionsById);
    applyState();
  });
  selectedList.addEventListener("change", event => {
    const control = event.target.closest("input[data-rikishi-visible-id]");
    if (!control) return;
    const host = document.getElementById("career-comparisons-chart");
    setRikishiTraceVisibility(host, control.dataset.rikishiVisibleId, control.checked)
      .then(() => syncRikishiVisibilityControls(host, selectedList));
  });
  form.addEventListener("change", event => {
    const control = event.target;
    if (control.name === "career_comparison_mode" || control.name === "log") {
      applyState();
    }
  });
  form.addEventListener("submit", event => {
    event.preventDefault();
    applyState();
  });
}

function focusCareerComparisonSearch(input) {
  const focus = () => {
    if (document.activeElement === input) return;
    input.focus();
    try {
      input.setSelectionRange(input.value.length, input.value.length);
    } catch {
      // Search inputs can reject selection APIs in some browser states.
    }
  };
  requestAnimationFrame(focus);
  for (const delay of [50, 150, 400]) {
    setTimeout(focus, delay);
  }
}

function careerComparisonControlState(form, state) {
  const checkedMode = form.querySelector("input[name='career_comparison_mode']:checked");
  const [skill, xBase] = String(checkedMode?.value || "chii:date").split(":");
  return {
    ...state,
    skill,
    x_base: xBase,
    log: Boolean(form.elements.log?.checked),
  };
}

function updateCareerComparisonCandidates(input, datalist, options) {
  const query = input.value.trim().toLowerCase();
  const selected = new Set(careerComparisonsState.selectedRikishiIds);
  const matches = options
    .filter(option => !selected.has(option.id))
    .filter(option => !query || option.prefixes.some(prefix => prefix.startsWith(query)))
    .slice(0, careerComparisonsState.candidateLimit);
  datalist.innerHTML = matches
    .map(option => `<option value="${escapeHtml(option.label)}"></option>`)
    .join("");
}

function consumeExactRikishiSelection(input, optionsByLabel, datalist, selectedList, options, optionsById) {
  const label = input.value.trim();
  if (!optionsByLabel.has(label)) return false;
  addSelectedRikishi(label, optionsByLabel);
  input.value = "";
  input.removeAttribute("list");
  datalist.innerHTML = "";
  updateCareerComparisonCandidates(input, datalist, options);
  renderSelectedRikishiList(selectedList, optionsById);
  return true;
}

function enableCareerComparisonDatalist(input) {
  if (!input.hasAttribute("list")) {
    input.setAttribute("list", "career-comparison-candidates");
  }
}

function addSelectedRikishi(label, optionsByLabel) {
  const option = optionsByLabel.get(label);
  if (!option) return;
  if (careerComparisonsState.selectedRikishiIds.includes(option.id)) return;
  removeStoredRikishiVisibility(option.id);
  careerComparisonsState.selectedRikishiIds = [
    ...careerComparisonsState.selectedRikishiIds,
    option.id,
  ];
}

function renderSelectedRikishiList(selectedList, optionsById) {
  selectedList.innerHTML = careerComparisonsState.selectedRikishiIds
    .map(id => {
      const option = optionsById.get(id);
      if (!option) return "";
      return [
        '<li>',
        `<span>${escapeHtml(option.label)}</span>`,
        `<button type="button" class="career-comparison-remove-control" data-rikishi-id="${escapeHtml(id)}" aria-label="Remove ${escapeHtml(option.label)}" title="Remove ${escapeHtml(option.label)}"><img class="career-comparison-remove-icon" src="${TRASH_ICON_PATH}" alt="" aria-hidden="true" draggable="false"></button>`,
        `<input type="checkbox" data-rikishi-visible-id="${escapeHtml(id)}" checked aria-label="Show ${escapeHtml(option.label)} traces" title="Show/hide ${escapeHtml(option.label)} traces">`,
        '</li>',
      ].join("");
    })
    .join("");
}

export {
  renderCareerComparisonsControls,
  renderModeChoice,
  wireCareerComparisonsControls,
  focusCareerComparisonSearch,
  careerComparisonControlState,
  updateCareerComparisonCandidates,
  consumeExactRikishiSelection,
  enableCareerComparisonDatalist,
  addSelectedRikishi,
  renderSelectedRikishiList,
};

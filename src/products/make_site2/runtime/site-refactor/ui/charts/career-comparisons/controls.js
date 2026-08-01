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
const EYE_ICON_PATH = "assets/eye.svg";
const EYE_CLOSED_ICON_PATH = "assets/eye-closed.svg";
const INVALID_RIKISHI_SELECTION_MESSAGE = (
  "The rikishi name is incomplete or ambiguous. Choose a rikishi from the dropdown."
);

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
    '<span class="career-comparison-selector-caption">Selected Rikishi</span>',
    '<ul class="career-comparison-selected" aria-label="Selected rikishi"></ul>',
    '<div class="filter-control career-comparison-search">',
    '<label for="career-comparison-search-input">Add</label>',
    '<div class="career-comparison-combobox">',
    '<input id="career-comparison-search-input" type="text" name="rikishi_search" autocomplete="off" role="combobox" aria-autocomplete="list" aria-haspopup="listbox" aria-expanded="false" aria-controls="career-comparison-candidates" autofocus tabindex="0">',
    '<ul id="career-comparison-candidates" class="career-comparison-candidates" role="listbox" hidden></ul>',
    '</div>',
    '</div>',
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
  const optionsByLabel = groupCareerComparisonOptionsByLabel(options);
  const optionsById = new Map(options.map(option => [option.id, option]));
  const input = form.elements.rikishi_search;
  const candidateList = form.querySelector("#career-comparison-candidates");
  const selectedList = form.querySelector(".career-comparison-selected");
  let highlightedRikishiId = null;
  const applyState = () => {
    const nextState = careerComparisonControlState(form, state);
    Object.assign(state, nextState);
    writeState(panel, nextState);
    writeCareerComparisonSelectionToUrl();
    renderCareerComparisonsPlot(artifact, nextState, data);
  };
  const refreshCandidates = open => {
    const matches = updateCareerComparisonCandidates(
      input,
      candidateList,
      options,
      optionsByLabel,
      open,
    );
    if (!matches.some(option => option.id === highlightedRikishiId)) {
      highlightedRikishiId = null;
    }
    setCareerComparisonCandidateHighlight(candidateList, input, highlightedRikishiId);
    return matches;
  };
  const closeCandidates = () => {
    highlightedRikishiId = null;
    closeCareerComparisonCandidates(input, candidateList);
  };
  const commitOption = option => {
    if (!addSelectedRikishi(option)) return;
    input.value = "";
    closeCandidates();
    renderSelectedRikishiList(selectedList, optionsById);
    applyState();
    input.focus();
  };

  refreshCandidates(false);
  renderSelectedRikishiList(selectedList, optionsById);
  renderCareerComparisonsPlot(artifact, state, data);
  focusCareerComparisonSearch(input);

  input.addEventListener("input", () => {
    highlightedRikishiId = null;
    refreshCandidates(true);
  });
  input.addEventListener("focus", () => {
    refreshCandidates(true);
  });
  input.addEventListener("click", () => {
    refreshCandidates(true);
  });
  input.addEventListener("keydown", event => {
    if (event.isComposing) return;
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const matches = refreshCandidates(true);
      highlightedRikishiId = moveCareerComparisonCandidateHighlight(
        matches,
        highlightedRikishiId,
        event.key === "ArrowDown" ? 1 : -1,
      );
      setCareerComparisonCandidateHighlight(candidateList, input, highlightedRikishiId);
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      closeCandidates();
      return;
    }
    if (event.key !== "Enter") return;
    event.preventDefault();
    const option = resolveCareerComparisonCandidate(
      input.value,
      highlightedRikishiId,
      optionsByLabel,
      optionsById,
      careerComparisonsState.selectedRikishiIds,
    );
    if (!option) {
      window.alert(INVALID_RIKISHI_SELECTION_MESSAGE);
      input.focus();
      return;
    }
    commitOption(option);
  });
  input.addEventListener("blur", closeCandidates);
  candidateList.addEventListener("pointerdown", event => {
    if (event.target.closest("[role='option']")) event.preventDefault();
  });
  candidateList.addEventListener("click", event => {
    const candidate = event.target.closest("[data-rikishi-id]");
    if (!candidate) return;
    commitOption(optionsById.get(candidate.dataset.rikishiId));
  });
  selectedList.addEventListener("click", event => {
    const button = event.target.closest("button[data-rikishi-id]");
    if (!button) return;
    careerComparisonsState.selectedRikishiIds = careerComparisonsState.selectedRikishiIds
      .filter(id => id !== button.dataset.rikishiId);
    removeStoredRikishiVisibility(button.dataset.rikishiId);
    renderSelectedRikishiList(selectedList, optionsById);
    refreshCandidates(document.activeElement === input);
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

function updateCareerComparisonCandidates(
  input,
  candidateList,
  options,
  optionsByLabel = groupCareerComparisonOptionsByLabel(options),
  open = true,
) {
  const query = input.value.trim().toLowerCase();
  const selected = new Set(careerComparisonsState.selectedRikishiIds);
  const matches = options
    .filter(option => !selected.has(option.id))
    .filter(option => !query || option.prefixes.some(prefix => prefix.startsWith(query)))
    .slice(0, careerComparisonsState.candidateLimit);
  candidateList.innerHTML = matches
    .map(option => [
      `<li id="${careerComparisonCandidateDomId(option.id)}" role="option"`,
      ` data-rikishi-id="${escapeHtml(option.id)}" aria-selected="false">`,
      escapeHtml(careerComparisonCandidateLabel(option, optionsByLabel)),
      '</li>',
    ].join(""))
    .join("");
  const expanded = open && matches.length > 0;
  candidateList.hidden = !expanded;
  input.setAttribute("aria-expanded", String(expanded));
  return matches;
}

function groupCareerComparisonOptionsByLabel(options) {
  const optionsByLabel = new Map();
  for (const option of options) {
    const label = canonicalRikishiLabel(option.label);
    const matchingOptions = optionsByLabel.get(label) || [];
    optionsByLabel.set(label, [...matchingOptions, option]);
  }
  return optionsByLabel;
}

function canonicalRikishiLabel(value) {
  return String(value).trim().toLowerCase();
}

function careerComparisonCandidateLabel(option, optionsByLabel) {
  const matches = optionsByLabel.get(canonicalRikishiLabel(option.label));
  return matches.length === 1 ? option.label : `${option.label} (${option.id})`;
}

function careerComparisonCandidateDomId(rikishiId) {
  return `career-comparison-candidate-${encodeURIComponent(rikishiId)}`;
}

function closeCareerComparisonCandidates(input, candidateList) {
  candidateList.hidden = true;
  input.setAttribute("aria-expanded", "false");
  input.removeAttribute("aria-activedescendant");
}

function setCareerComparisonCandidateHighlight(candidateList, input, rikishiId) {
  candidateList.querySelectorAll("[role='option']").forEach(candidate => {
    const active = candidate.dataset.rikishiId === rikishiId;
    candidate.setAttribute("aria-selected", String(active));
    candidate.classList.toggle("career-comparison-candidate-active", active);
    if (active) candidate.scrollIntoView({ block: "nearest" });
  });
  if (rikishiId === null) {
    input.removeAttribute("aria-activedescendant");
    return;
  }
  input.setAttribute("aria-activedescendant", careerComparisonCandidateDomId(rikishiId));
}

function moveCareerComparisonCandidateHighlight(options, currentId, direction) {
  if (!options.length) return null;
  const currentIndex = options.findIndex(option => option.id === currentId);
  if (currentIndex === -1) return direction > 0 ? options[0].id : options[options.length - 1].id;
  const nextIndex = (currentIndex + direction + options.length) % options.length;
  return options[nextIndex].id;
}

function resolveCareerComparisonCandidate(
  query,
  highlightedRikishiId,
  optionsByLabel,
  optionsById,
  selectedRikishiIds,
) {
  const selected = new Set(selectedRikishiIds);
  if (highlightedRikishiId !== null && !selected.has(highlightedRikishiId)) {
    return optionsById.get(highlightedRikishiId);
  }
  const canonicalQuery = canonicalRikishiLabel(query);
  const exactMatches = [...optionsById.values()]
    .filter(option => !selected.has(option.id))
    .filter(option => (
      canonicalRikishiLabel(careerComparisonCandidateLabel(option, optionsByLabel))
      === canonicalQuery
    ));
  return exactMatches.length === 1 ? exactMatches[0] : null;
}

function addSelectedRikishi(option) {
  if (careerComparisonsState.selectedRikishiIds.includes(option.id)) return false;
  removeStoredRikishiVisibility(option.id);
  careerComparisonsState.selectedRikishiIds = [
    ...careerComparisonsState.selectedRikishiIds,
    option.id,
  ];
  return true;
}

function renderSelectedRikishiList(selectedList, optionsById) {
  if (!careerComparisonsState.selectedRikishiIds.length) {
    selectedList.innerHTML = '<li class="career-comparison-selected-empty">(None.)</li>';
    return;
  }
  selectedList.innerHTML = careerComparisonsState.selectedRikishiIds
    .map(id => {
      const option = optionsById.get(id);
      if (!option) return "";
      const escapedId = escapeHtml(id);
      const escapedLabel = escapeHtml(option.label);
      return [
        '<li>',
        '<span class="career-comparison-selected-row">',
        renderSelectedRikishiLink(option.label, id),
        `<button type="button" class="career-comparison-remove-control" data-rikishi-id="${escapedId}" aria-label="Remove ${escapedLabel}" title="Remove ${escapedLabel}"><img class="career-comparison-remove-icon" src="${TRASH_ICON_PATH}" alt="" aria-hidden="true" draggable="false"></button>`,
        `<label class="career-comparison-visibility-control" title="Show/hide ${escapedLabel} traces"><input type="checkbox" data-rikishi-visible-id="${escapedId}" checked aria-label="Show ${escapedLabel} traces"><img class="career-comparison-visibility-icon career-comparison-visibility-icon-on" src="${EYE_ICON_PATH}" alt="" aria-hidden="true" draggable="false"><img class="career-comparison-visibility-icon career-comparison-visibility-icon-off" src="${EYE_CLOSED_ICON_PATH}" alt="" aria-hidden="true" draggable="false"></label>`,
        '</span>',
        '</li>',
      ].join("");
    })
    .join("");
}

function renderSelectedRikishiLink(label, rikishiId) {
  return [
    `<a class="shikona-link" href="https://sumodb.sumogames.de/Rikishi.aspx?r=${encodeURIComponent(rikishiId)}"`,
    ' target="_blank" rel="noopener">',
    escapeHtml(label),
    '</a>',
  ].join("");
}

export {
  renderCareerComparisonsControls,
  renderModeChoice,
  wireCareerComparisonsControls,
  focusCareerComparisonSearch,
  careerComparisonControlState,
  updateCareerComparisonCandidates,
  groupCareerComparisonOptionsByLabel,
  canonicalRikishiLabel,
  careerComparisonCandidateLabel,
  careerComparisonCandidateDomId,
  closeCareerComparisonCandidates,
  setCareerComparisonCandidateHighlight,
  moveCareerComparisonCandidateHighlight,
  resolveCareerComparisonCandidate,
  addSelectedRikishi,
  renderSelectedRikishiList,
  renderSelectedRikishiLink,
};

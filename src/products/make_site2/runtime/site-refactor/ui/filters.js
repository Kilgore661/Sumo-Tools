// Filter state, rendering and event wiring.

import { contentPanel } from "../core/dom.js";
import { writePanelUrl } from "../core/url-state.js";
import { escapeHtml } from "../utils/html.js";

function filterValueLabel(filters, filterId, value) {
  const filter = filters.find(candidate => candidate.id === filterId);
  const option = (filter?.values || []).find(candidate => candidate.value === value);
  return option?.label || "";
}
// Resolve URL filter values into a complete state object with defaults.
function resolveFilterState(filters, urlState) {
  return Object.fromEntries(filters.map(filter => [
    filter.id,
    coerceFilterValue(filter, urlState[filter.id] ?? filter.default)
  ]));
}
// Coerce string URL values according to filter value types.
function coerceFilterValue(filter, value) {
  if (filter.control === "checkbox") return value === true || value === "true";
  if (value === null || value === undefined || value === "") return filter.default;
  if (
    filter.values &&
    filter.values.length &&
    !filter.values.some(candidate => String(candidate.value) === String(value))
  ) {
    return filter.default;
  }
  return value;
}
function resolveSelectedDivision(rows, selectedDivision) {
  const divisions = [...new Set(rows.map(row => row.division_id).filter(Boolean))];
  return divisions.includes(selectedDivision) ? selectedDivision : divisions[0] || selectedDivision;
}
function resolveBanzukeChangesDivision(config, selectedDivision) {
  const divisions = (config.divisions || []).map(division => division.id);
  return divisions.includes(selectedDivision) ? selectedDivision : config.default_division;
}
function resolveStandingsWindow(config, selectedWindow) {
  const windows = (config.supported_num_basho || []).map(String);
  return windows.includes(String(selectedWindow)) ? String(selectedWindow) : String(config.default_num_basho);
}
function resolveStandingsDivision(config, selectedDivision) {
  const divisions = ["all", "makuuchi", "juryo", "makushita", "sandanme", "jonidan", "jonokuchi"];
  return divisions.includes(selectedDivision) ? selectedDivision : config.default_division;
}
function selectedStandingsSource(artifact, state) {
  return artifact.data_sources.find(source =>
    String(source.filter_value) === String(state[artifact.selector_filter_id])
  );
}
// Attach filter controls and rerender the panel on change.
function wireFilterSection(panel, state, renderPanel) {
  const form = contentPanel.querySelector(".filter-section");
  if (!form) return;
  form.addEventListener("change", event => {
    const control = event.target;
    if (!(control instanceof HTMLInputElement || control instanceof HTMLSelectElement)) return;
    const filters = panel.contents.filter_section.filters;
    const nextState = { ...state };
    for (const filter of filters) {
      const input = form.elements[filter.id];
      if (!input) continue;
      nextState[filter.id] = filter.control === "checkbox" ? input.checked : input.value;
    }
    writePanelUrl(panel.page_id, filters, nextState, { replace: false });
    renderPanel(panel, nextState).catch(error => {
      contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
    });
  });
}
// Select the requested indexed payload entry, resolving "latest" if needed.
function selectedIndexEntry(index, selected) {
  const entries = index.entries || [];
  if (selected && selected !== "latest") {
    const match = entries.find(entry => entry.basho === selected);
    if (match) return match;
  }
  return entries.find(entry => entry.basho === index.default_basho) || latestIndexEntry(entries);
}
function latestIndexEntry(entries) {
  return [...entries].sort((left, right) => String(right.basho).localeCompare(String(left.basho)))[0];
}
function bashoSelectorValues(index) {
  return [...(index.entries || [])]
    .sort((left, right) => String(right.basho).localeCompare(String(left.basho)))
    .map(entry => ({ value: entry.basho, label: entry.label || entry.basho }));
}
// Render all controls for a panel FilterSection.
function renderFilterSection(filterSection, state, index, rowsBySource = {}) {
  if (!filterSection.filters.length) return "";
  return [
    '<form class="filter-section" aria-label="Filters">',
    '<h4>Options</h4>',
    '<ul class="filter-list">',
    ...filterSection.filters.map(filter => `<li>${renderFilter(filter, state, index, rowsBySource)}</li>`),
    '</ul>',
    '</form>'
  ].join("");
}
function renderFilter(filter, state, index, rowsBySource = {}) {
  if (filter.control === "checkbox") {
    return [
      '<label class="checkbox-control">',
      `<input type="checkbox" name="${escapeHtml(filter.id)}"${state[filter.id] ? " checked" : ""}>`,
      `<span>${escapeHtml(filter.label)}</span>`,
      '</label>'
    ].join("");
  }
  const values = filterValues(filter, state, index, rowsBySource);
  const selected = selectedFilterValue(filter, state, index);
  if (values.length <= 7) {
    return renderRadioChoice(filter, values, selected);
  }
  return renderDropdownChoice(filter, values, selected);
}
function filterValues(filter, state, index, rowsBySource) {
  if (filter.id === "basho_date" && index) return bashoSelectorValues(index);
  if (filter.values_source) return dataSelectorValues(filter, state, rowsBySource);
  return filter.values;
}
function selectedFilterValue(filter, state, index) {
  if (filter.id === "basho_date" && index) {
    return selectedIndexEntry(index, state[filter.id]).basho;
  }
  return state[filter.id];
}
function renderRadioChoice(filter, values, selected) {
  return [
    `<div class="choice-control" role="group" aria-label="${escapeHtml(filter.label)}">`,
    `<span class="choice-label">${escapeHtml(filter.label)}</span>`,
    '<ul class="choice-list">',
    ...values.map(value => [
      '<li>',
      '<label class="radio-control">',
      `<input type="radio" name="${escapeHtml(filter.id)}" value="${escapeHtml(value.value)}"${value.value === selected ? " checked" : ""}>`,
      `<span>${escapeHtml(value.label)}</span>`,
      '</label>',
      '</li>',
    ].join("")),
    '</ul>',
    '</div>'
  ].join("");
}
function renderDropdownChoice(filter, values, selected) {
  return [
    '<label class="filter-control">',
    `<span>${escapeHtml(filter.label)}</span>`,
    `<select name="${escapeHtml(filter.id)}">`,
    ...values.map(value => {
      const selectedAttr = value.value === selected ? " selected" : "";
      return `<option value="${escapeHtml(value.value)}"${selectedAttr}>${escapeHtml(value.label)}</option>`;
    }),
    '</select>',
    '</label>'
  ].join("");
}
// Derive selector values from a loaded data source field.
function dataSelectorValues(filter, state, rowsBySource) {
  const source = filter.values_source;
  const rows = rowsBySource[source.source] || [];
  const partitionValue = source.partition_filter ? state[source.partition_filter] : null;
  const entries = new Map();
  for (const row of rows) {
    if (source.partition_filter) {
      const actual = normalizedSourceValue(row[source.partition_field], source.partition_normalizer);
      if (actual !== partitionValue) continue;
    }
    entries.set(row[source.field], {
      value: row[source.field],
      label: row[source.label_field],
      order: Number(row[source.order_field]),
    });
  }
  return [...entries.values()]
    .sort((left, right) => left.order - right.order)
    .map(({ value, label }) => ({ value, label }));
}
function resolveSelectedFilterValueFromSource(filter, state, rowsBySource) {
  const values = filter ? dataSelectorValues(filter, state, rowsBySource) : [];
  return values.some(value => value.value === state[filter.id])
    ? state[filter.id]
    : values[0]?.value || state[filter.id];
}
function resolveSelectedDataValue(rows, field, selectedValue, normalizer = null) {
  const values = [...new Set(rows.map(row => normalizedSourceValue(row[field], normalizer)))].filter(Boolean);
  return values.includes(selectedValue) ? selectedValue : values[0] || selectedValue;
}
function normalizedSourceValue(value, normalizer) {
  if (normalizer === "division_id") return divisionId(value);
  return value;
}
function divisionId(value) {
  return String(value || "").toLowerCase().replace(/\s+/g, "_");
}

export { filterValueLabel, resolveFilterState, coerceFilterValue, resolveSelectedDivision, resolveBanzukeChangesDivision, resolveStandingsWindow, resolveStandingsDivision, selectedStandingsSource, wireFilterSection, selectedIndexEntry, latestIndexEntry, bashoSelectorValues, renderFilterSection, renderFilter, filterValues, selectedFilterValue, renderRadioChoice, renderDropdownChoice, dataSelectorValues, resolveSelectedFilterValueFromSource, resolveSelectedDataValue, normalizedSourceValue, divisionId };

// Filter state, rendering and event wiring.

import { contentPanel } from "../core/dom.js";
import { writePanelUrl } from "../core/url-state.js";
import { escapeHtml } from "../utils/html.js";
import { renderLabelWithHelp } from "./help.js";

const SUMO_MONTHS = [
  { value: "01", label: "January" },
  { value: "03", label: "March" },
  { value: "05", label: "May" },
  { value: "07", label: "July" },
  { value: "09", label: "September" },
  { value: "11", label: "November" },
];

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
function wireFilterSection(panel, state, renderPanel, index = null) {
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
  form.addEventListener("click", event => {
    const button = event.target.closest("button[data-basho-nav]");
    if (!button || !index) return;
    const nextState = bashoNavigationState(button.dataset.bashoNav, index, state);
    if (!nextState) return;
    const filters = panel.contents.filter_section.filters;
    writePanelUrl(panel.page_id, filters, nextState, { replace: false });
    renderPanel(panel, nextState).catch(error => {
      contentPanel.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
    });
  });
}
// Select the requested indexed payload entry, resolving "latest" if needed.
function selectedIndexEntry(index, selected) {
  const entries = validBashoEntries(index);
  if (selected && selected !== "latest") {
    const selectedKey = safeBashoKey(selected);
    if (selectedKey) {
      const match = entries.find(entry => bashoKey(entry.basho) === selectedKey);
      if (match) return match;
    }
  }
  const defaultKey = safeBashoKey(index.default_basho);
  if (defaultKey) {
    const defaultEntry = entries.find(entry => bashoKey(entry.basho) === defaultKey);
    if (defaultEntry) return defaultEntry;
  }
  return latestIndexEntry(entries);
}
function latestIndexEntry(entries) {
  return [...entries].sort((left, right) => bashoKey(right.basho).localeCompare(bashoKey(left.basho)))[0];
}
function bashoSelectorValues(index) {
  return validBashoEntries(index)
    .sort((left, right) => bashoKey(right.basho).localeCompare(bashoKey(left.basho)))
    .map(entry => ({ value: entry.basho, label: entry.label || entry.basho }));
}
function resolveBashoCalendarState(index, state) {
  const defaultEntry = selectedIndexEntry(index, "latest");
  if (!defaultEntry) throw new Error("Bad URL");
  const defaultParts = parseBashoId(defaultEntry.basho);
  const year = state.basho_year === "latest" ? defaultParts.year : String(state.basho_year || "");
  const month = state.basho_month === "latest" ? defaultParts.month : normalizeBashoMonth(state.basho_month);
  validateBashoCalendarSlot(index, year, month);
  const basho = `${year}${month}`;
  const entry = validBashoEntries(index).find(candidate => bashoKey(candidate.basho) === basho) || null;
  return { year, month, basho, entry };
}
function validateBashoCalendarSlot(index, year, month) {
  if (!/^\d{4}$/.test(year)) throw new Error("Bad URL");
  if (!SUMO_MONTHS.some(candidate => candidate.value === month)) throw new Error("Bad URL");
  const years = supportedBashoYears(index);
  if (!years.some(candidate => candidate.value === year)) throw new Error("Bad URL");
}
function normalizeBashoMonth(month) {
  if (/^\d$/.test(String(month))) return `0${month}`;
  return String(month || "");
}
function parseBashoId(basho) {
  const value = String(basho || "");
  const match = /^(\d{4})\D?(\d{1,2})$/.exec(value);
  if (!match) throw new Error("Bad URL");
  return { year: match[1], month: match[2].padStart(2, "0") };
}
function bashoKey(basho) {
  const { year, month } = parseBashoId(basho);
  return `${year}${month}`;
}
function safeBashoKey(basho) {
  try {
    return bashoKey(basho);
  } catch {
    return null;
  }
}
function validBashoEntries(index) {
  return (index.entries || []).filter(entry => safeBashoKey(entry.basho));
}
function supportedBashoYears(index) {
  const yearNumbers = validBashoEntries(index)
    .map(entry => Number(parseBashoId(entry.basho).year));
  const minYear = Math.min(...yearNumbers);
  const maxYear = Math.max(...yearNumbers);
  if (!Number.isFinite(minYear) || !Number.isFinite(maxYear)) return [];
  return Array.from({ length: maxYear - minYear + 1 }, (_, offset) => String(maxYear - offset))
    .map(year => ({ value: year, label: year }));
}
function monthLabel(month) {
  return SUMO_MONTHS.find(candidate => candidate.value === month)?.label || month;
}
function bashoNavigationState(direction, index, state) {
  const entries = validBashoEntries(index)
    .sort((left, right) => bashoKey(left.basho).localeCompare(bashoKey(right.basho)));
  if (!entries.length) return null;
  const current = `${state.basho_year}${state.basho_month}`;
  const currentIndex = entries.findIndex(entry => bashoKey(entry.basho) === current);
  if (currentIndex < 0) return null;
  let nextIndex = currentIndex;
  if (direction === "first") nextIndex = 0;
  if (direction === "previous") nextIndex = Math.max(0, currentIndex - 1);
  if (direction === "next") nextIndex = Math.min(entries.length - 1, currentIndex + 1);
  if (direction === "last") nextIndex = entries.length - 1;
  if (nextIndex === currentIndex) return null;
  const { year, month } = parseBashoId(entries[nextIndex].basho);
  return { ...state, basho_year: year, basho_month: month };
}
// Render all controls for a panel FilterSection.
function renderFilterSection(filterSection, state, index, rowsBySource = {}) {
  if (!filterSection.filters.length) return "";
  const filters = filterSection.filters;
  const bashoCalendar = filters.some(filter => filter.id === "basho_year") &&
    filters.some(filter => filter.id === "basho_month") && index;
  const visibleFilters = filters.filter(filter => isFilterVisible(filter, state, bashoCalendar));
  return [
    '<form class="filter-section" aria-label="Filters">',
    '<h4>Options</h4>',
    '<ul class="filter-list">',
    bashoCalendar ? `<li>${renderBashoCalendarControl(state, index)}</li>` : "",
    ...visibleFilters.map(filter => renderFilterListItem(filter, state, index, rowsBySource)),
    '</ul>',
    '</form>'
  ].join("");
}
function isFilterVisible(filter, state, bashoCalendar) {
  if (bashoCalendar && (filter.id === "basho_year" || filter.id === "basho_month")) return false;
  if (filter.id === "show_active") return state.view === "longest";
  return true;
}
function renderFilterListItem(filter, state, index, rowsBySource) {
  const classes = ["filter-list-item"];
  if (filter.id === "show_active") classes.push("filter-list-item-dependent", "filter-list-item-longest");
  return `<li class="${classes.join(" ")}">${renderFilter(filter, state, index, rowsBySource)}</li>`;
}
function renderBashoCalendarControl(state, index) {
  return [
    '<div class="basho-calendar-control" role="group" aria-label="Basho">',
    '<span class="choice-label">Basho</span>',
    '<label class="filter-control basho-year-control">',
    '<span>Year</span>',
    '<select name="basho_year">',
    ...supportedBashoYears(index).map(value => optionHtml(value, state.basho_year)),
    '</select>',
    '</label>',
    '<label class="filter-control basho-month-control">',
    '<span>Month</span>',
    '<select name="basho_month">',
    ...SUMO_MONTHS.map(value => optionHtml(value, state.basho_month)),
    '</select>',
    '</label>',
    '<div class="basho-navigation-buttons" aria-label="Basho navigation">',
    '<button type="button" data-basho-nav="first">&lt;&lt;</button>',
    '<button type="button" data-basho-nav="previous">&lt;</button>',
    '<button type="button" data-basho-nav="next">&gt;</button>',
    '<button type="button" data-basho-nav="last">&gt;&gt;</button>',
    '</div>',
    '</div>'
  ].join("");
}
function optionHtml(value, selected) {
  const selectedAttr = value.value === selected ? " selected" : "";
  return `<option value="${escapeHtml(value.value)}"${selectedAttr}>${escapeHtml(value.label)}</option>`;
}
function renderFilter(filter, state, index, rowsBySource = {}) {
  if (filter.control === "checkbox") {
    return [
      '<label class="checkbox-control">',
      `<input type="checkbox" name="${escapeHtml(filter.id)}"${state[filter.id] ? " checked" : ""}>`,
      `<span>${renderLabelWithHelp(filter.label, filter.help)}</span>`,
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
  if (filter.id === "basho_year" && index) return supportedBashoYears(index);
  if (filter.id === "basho_month" && index) return SUMO_MONTHS;
  if (filter.values_source) return dataSelectorValues(filter, state, rowsBySource);
  return filter.values || [];
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
    `<span class="choice-label">${renderLabelWithHelp(filter.label, filter.help)}</span>`,
    '<ul class="choice-list">',
    ...values.map(value => [
      '<li>',
      '<label class="radio-control">',
      `<input type="radio" name="${escapeHtml(filter.id)}" value="${escapeHtml(value.value)}"${value.value === selected ? " checked" : ""}>`,
      `<span>${renderLabelWithHelp(value.label, value.help, `${filter.label} ${value.label}`)}</span>`,
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
    `<span>${renderLabelWithHelp(filter.label, filter.help)}</span>`,
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

export { filterValueLabel, resolveFilterState, coerceFilterValue, resolveSelectedDivision, resolveBanzukeChangesDivision, resolveStandingsWindow, resolveStandingsDivision, selectedStandingsSource, wireFilterSection, selectedIndexEntry, latestIndexEntry, bashoSelectorValues, resolveBashoCalendarState, monthLabel, renderFilterSection, renderFilter, filterValues, selectedFilterValue, renderRadioChoice, renderDropdownChoice, dataSelectorValues, resolveSelectedFilterValueFromSource, resolveSelectedDataValue, normalizedSourceValue, divisionId };
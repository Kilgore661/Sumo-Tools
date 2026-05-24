import { escapeHtml, normalizedSourceValue } from '../../utils/dom.js';

/**
 * Filter Evaluation engine constructing interactive visual dashboard widgets.
 */

export function resolveFilterState(filters, urlState) {
  return Object.fromEntries(filters.map(filter => [
    filter.id,
    coerceFilterValue(filter, urlState[filter.id] ?? filter.default)
  ]));
}

export function coerceFilterValue(filter, value) {
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

export function filterValueLabel(filters, filterId, value) {
  const filter = filters.find(candidate => candidate.id === filterId);
  const option = (filter?.values || []).find(candidate => candidate.value === value);
  return option?.label || "";
}

export function renderFilterSection(filterSection, state, index, rowsBySource = {}) {
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

export function selectedIndexEntry(index, selected) {
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

export function dataSelectorValues(filter, state, rowsBySource) {
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

export function resolveSelectedFilterValueFromSource(filter, state, rowsBySource) {
  const values = filter ? dataSelectorValues(filter, state, rowsBySource) : [];
  return values.some(value => value.value === state[filter.id])
    ? state[filter.id]
    : values[0]?.value || state[filter.id];
}
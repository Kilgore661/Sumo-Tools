// Shared chart runtime helpers used by the chart-family modules.

import { dateLikeDisplayFromParts } from "../../utils/display.js";

const PLOTLY_CONFIG = {
  displayModeBar: true,
  displaylogo: false,
  responsive: true,
};

function chartRows(artifact, rowsBySource) {
  const sourceId = artifact.data_binding.sources[0];
  return rowsBySource[sourceId] || [];
}

function sparseTickText(labels, maxLabels) {
  const step = Math.max(1, Math.ceil(labels.length / maxLabels));
  return labels.map((label, index) => index % step === 0 ? label : "");
}

function monthIndexTicks(maxMonthIndex, artifact) {
  const tickVals = [];
  const step = 24;
  for (let value = 0; value <= maxMonthIndex; value += step) {
    tickVals.push(value);
  }
  if (!tickVals.includes(maxMonthIndex)) {
    tickVals.push(maxMonthIndex);
  }
  return {
    values: tickVals,
    labels: tickVals.map(value => monthIndexLabel(value, artifact)),
  };
}

function monthIndexLabel(monthIndex, artifact) {
  const totalMonths = artifact.provenance.base_month - 1 + monthIndex;
  const year = artifact.provenance.base_year + Math.floor(totalMonths / 12);
  const month = (totalMonths % 12) + 1;
  return dateLikeDisplayFromParts(year, month);
}

function axisRange(axis) {
  if (axis.minimum === null || axis.maximum === null) return undefined;
  return [axis.minimum, axis.maximum];
}

function chartElementId(artifact) {
  return `${artifact.id}-chart`;
}

function resolveFilterValue(filters, filterId, selectedValue) {
  const filter = filters.find(candidate => candidate.id === filterId);
  if (!filter) return selectedValue;
  return filter.values.some(value => value.value === selectedValue)
    ? selectedValue
    : filter.default;
}

export {
  PLOTLY_CONFIG,
  chartRows,
  sparseTickText,
  monthIndexTicks,
  monthIndexLabel,
  axisRange,
  chartElementId,
  resolveFilterValue,
};

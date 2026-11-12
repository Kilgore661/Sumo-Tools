// Basho Results presentation model construction.

import { BASHO_RESULTS_TABLE_ID } from "./shared.js";
import { TRANSITIONAL_TABLE_SPEC } from "./table-spec.js";
import { transitionalRowValues } from "./values.js";

// Build the complete UI model consumed by the Basho Results recursive renderer.
function buildBashoResultsPresentationModel({ rows, state, entry, title }) {
  const visiblePaths = bashoResultsVisiblePaths(state);
  return {
    id: BASHO_RESULTS_TABLE_ID,
    header: bashoResultsHeader(title, entry),
    table_spec: resolveSelectedHeading(TRANSITIONAL_TABLE_SPEC, entry),
    values: (rows || []).map((row, index) => transitionalRowValues(row, index)),
    projection: { visible_paths: visiblePaths },
  };
}

function bashoResultsHeader(title, entry) {
  return {
    heading: title || "Basho Results",
    subheading: bashoResultsSubheading(entry),
  };
}

function bashoResultsSubheading(entry) {
  const latestDay = Number(entry?.latest_day);
  if (latestDay && latestDay < 15) return `After Day ${latestDay}`;
  return "";
}

// Adjust the selected-context heading for in-progress versus final basho output.
function resolveSelectedHeading(spec, entry) {
  const selectedHeading = Number(entry?.latest_day) && Number(entry.latest_day) < 15
    ? "Current"
    : "After Basho";
  return spec.map(node => node.key === "selected" ? { ...node, label: selectedHeading } : node);
}

// Project filter state into the terminal table paths that should be visible.
function bashoResultsVisiblePaths(state) {
  const visible = [
    "reference.row_number",
    "reference.shikona",
    "selected.context.skill.bp",
    "selected.result.wins",
    "selected.result.wins_losses_separator",
    "selected.result.losses",
    "selected.result.losses_absences_separator",
    "selected.result.absences",
    "selected.result.prizes",
  ];
  if (state.previous_context) {
    visible.push(
      "before.context.skill.bp",
      "before.result.wins",
      "before.result.wins_losses_separator",
      "before.result.losses",
      "before.result.losses_absences_separator",
      "before.result.absences",
      "before.result.prizes",
    );
  }
  if (state.rating_context) {
    if (state.previous_context) visible.push("before.context.skill.rating");
    visible.push(
      "selected.context.skill.rating",
      "selected.context.skill.rating_delta",
    );
  }
  return visible;
}

export {
  buildBashoResultsPresentationModel,
  bashoResultsHeader,
  bashoResultsSubheading,
  resolveSelectedHeading,
  bashoResultsVisiblePaths,
};

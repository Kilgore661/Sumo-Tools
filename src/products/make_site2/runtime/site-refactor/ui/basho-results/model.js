import { BASHO_RESULTS_TABLE_ID } from "./shared.js";
import { TRANSITIONAL_TABLE_SPEC } from "./table-spec.js";
import {
  buildRecordAnalyses,
  transitionalRowValues,
} from "./values.js";

function buildBashoResultsPresentationModel({ rows, state, entry, title }) {
  const visiblePaths = bashoResultsVisiblePaths(state);
  const analyses = buildRecordAnalyses(rows || []);
  return {
    id: BASHO_RESULTS_TABLE_ID,
    header: bashoResultsHeader(title, entry),
    table_spec: resolveSelectedHeading(TRANSITIONAL_TABLE_SPEC, entry),
    values: (rows || []).map((row, index) => transitionalRowValues(row, index, analyses)),
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
  return "Final";
}

function resolveSelectedHeading(spec, entry) {
  const selectedHeading = Number(entry?.latest_day) && Number(entry.latest_day) < 15
    ? "Current"
    : "After Basho";
  return spec.map(node => node.key === "selected" ? { ...node, label: selectedHeading } : node);
}

function bashoResultsVisiblePaths(state) {
  const visible = [
    "reference.row_number",
    "reference.shikona",
    "selected.context.skill.bp",
    "selected.result.wins",
    "selected.result.losses",
    "selected.result.absences",
    "selected.result.prizes",
  ];
  if (state.changes_context) {
    visible.push(
      "changes.movement.bp",
      "changes.movement.division",
    );
  }
  if (state.previous_context) {
    visible.push(
      "before.context.skill.bp",
      "before.result.wins",
      "before.result.losses",
      "before.result.absences",
      "before.result.prizes",
    );
  }
  if (state.rating_context) {
    if (state.previous_context) visible.push("before.context.skill.equelo");
    visible.push("selected.context.skill.equelo");
    if (state.changes_context) visible.push("changes.delta_equelo");
  }
  if (state.analysis_context) {
    if (state.previous_context) {
      visible.push(
        "before.context.analysis.banzuke_error.direction",
        "before.context.analysis.banzuke_error.magnitude",
        "before.context.analysis.rbbp",
      );
    }
    visible.push(
      "selected.context.analysis.banzuke_error.direction",
      "selected.context.analysis.banzuke_error.magnitude",
      "selected.context.analysis.rbbp",
    );
  }
  if (state.nu_chii) {
    visible.push("selected.next_bp");
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

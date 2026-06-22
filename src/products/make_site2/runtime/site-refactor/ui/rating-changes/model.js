// Rating Changes presentation model boundary.

import { RATING_CHANGES_TABLE_SPEC } from "./table-spec.js";

function selectedRatingChangesEntry(index, selectedN) {
  const entries = validRatingChangeEntries(index);
  if (!entries.length) return null;
  const requested = String(selectedN || "");
  const requestedEntry = entries.find(entry => String(entry.n) === requested);
  if (requestedEntry) return requestedEntry;
  const defaultN = String(index.default_n || "");
  const defaultEntry = entries.find(entry => String(entry.n) === defaultN);
  return defaultEntry || entries[0];
}

function validRatingChangeEntries(index) {
  return (index.entries || []).filter(entry => entry.n !== undefined && entry.payload_path);
}

function buildRatingChangesPresentationModel({ artifact, rows, state, entry, title }) {
  return {
    id: "rating_changes",
    artifact,
    title,
    state,
    entry,
    header: ratingChangesHeader(title, state, entry),
    table_spec: RATING_CHANGES_TABLE_SPEC,
    projection: { visible_paths: ratingChangesVisiblePaths(state) },
    values: (rows || []).map(ratingChangesPresentationRow),
    raw_rows: rows || [],
  };
}

function ratingChangesHeader(title, state, entry) {
  const n = entry?.n || state?.n || "";
  return {
    heading: title || "Rating Changes",
    subheading: n ? `Latest ${n}-basho change` : "Latest rating change",
  };
}

function ratingChangesVisiblePaths(state) {
  const visible = [
    "reference.row_number",
    "reference.shikona",
    "context.start.chii",
    "context.start.equelo",
    "context.end.chii",
    "context.end.equelo",
    "context.delta",
  ];

  const basis = state?.basis || "expected";
  const showExpected = basis === "expected" || basis === "both";
  const showActual = basis === "actual" || basis === "both";
  const measurePath = state?.normalised ? "normalised_per_bout" : "delta_per_bout";

  if (showExpected) {
    visible.push("expected.bouts", `expected.${measurePath}`);
  }
  if (showActual) {
    visible.push("actual.bouts", `actual.${measurePath}`);
  }

  return visible;
}

function ratingChangesPresentationRow(row) {
  return {
    "reference.rikishi_id": row.rikishi_id,
    "reference.shikona": row.shikona,
    "context.start.chii": row.chii_at_start,
    "context.start.chii_ordinal": row.chii_ordinal_at_start,
    "context.start.equelo": row.rating_at_start,
    "context.end.chii": row.chii_at_end,
    "context.end.chii_ordinal": row.chii_ordinal_at_end,
    "context.end.equelo": row.rating_at_end,
    "context.delta": row.delta,
    "expected.bouts": row.expected_bouts,
    "expected.delta_per_bout": row.delta_per_expected_bout,
    "expected.normalised_per_bout": row.normalised_delta_per_expected_bout,
    "actual.bouts": row.actual_bouts,
    "actual.delta_per_bout": row.delta_per_actual_bout,
    "actual.normalised_per_bout": row.normalised_delta_per_actual_bout,
  };
}

export {
  buildRatingChangesPresentationModel,
  ratingChangesHeader,
  ratingChangesPresentationRow,
  ratingChangesVisiblePaths,
  selectedRatingChangesEntry,
};

// Recursive Basho Results table specification and presentation vocabulary.

const PRESENTATION = {
  DEFAULT: "default",
  NAME: "name",
  RANK: "rank",
  RATING: "rating",
  COMPACT_COUNT: "compact_count",
  RECORD_SEPARATOR: "record_separator",
  SPECIAL_NON_NUMERIC: "special_non_numeric",
  NUMERIC_MAGNITUDE: "numeric_magnitude",
  COMPACT_TEXT: "compact_text",
  };

const PRIZE_DISPLAY_ORDER = ["Y", "D", "J", "K", "S", "G"];

const TRANSITIONAL_TABLE_SPEC = [
  group("reference", "", [
    column("row_number", "", { sort_kind: "none", presentation: PRESENTATION.NUMERIC_MAGNITUDE, role: "row_number" }),
    column("shikona", "Shikona", { sort_kind: "text", presentation: PRESENTATION.NAME }),
  ]),
  group("before", "Before Basho", recordSpec()),
  group("selected", "Current/After", recordSpec()),
];

function recordSpec() {
  return [
    group("context", "Context", [
      group("skill", "Skill", [
        column("bp", "Chii", {
          sort_kind: "chii_ordinal",
          sort_path: "bp_ordinal",
          presentation: PRESENTATION.RANK,
        }),
        column("rating", "Elo", { help: "Elo-89 rating.", sort_kind: "numeric", presentation: PRESENTATION.RATING }),
        column("rating_delta", "ΔElo", {
          help: "Difference in rating.",
          sort_kind: "numeric",
          presentation: PRESENTATION.RATING,
        }),
      ]),
    ]),
    group("result", "Result", [
      column("wins", "W", { sort_kind: "numeric", presentation: PRESENTATION.COMPACT_COUNT }),
      column("wins_losses_separator", "-", { sort_kind: "none", presentation: PRESENTATION.RECORD_SEPARATOR }),
      column("losses", "L", { sort_kind: "numeric", presentation: PRESENTATION.COMPACT_COUNT }),
      column("losses_absences_separator", "-", { sort_kind: "none", presentation: PRESENTATION.RECORD_SEPARATOR }),
      column("absences", "A", { sort_kind: "numeric", presentation: PRESENTATION.COMPACT_COUNT }),
      column("prizes", "📦", {
        sort_kind: "prize_set",
        sort_default_direction: "descending",
        presentation: PRESENTATION.SPECIAL_NON_NUMERIC,
      }),
    ], { help: "See Notes.", note_id: "note_result" }),
  ];
}

function group(key, label, children, options = {}) {
  return { key, label, children, ...options };
}

function column(key, label, options = {}) {
  return { key, label, presentation: PRESENTATION.DEFAULT, ...options };
}

export {
  PRESENTATION,
  PRIZE_DISPLAY_ORDER,
  TRANSITIONAL_TABLE_SPEC,
  recordSpec,
  group,
  column,
};

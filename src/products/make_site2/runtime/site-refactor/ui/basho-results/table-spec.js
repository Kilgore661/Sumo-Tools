// Recursive Basho Results table specification and presentation vocabulary.

const PRESENTATION = {
  DEFAULT: "default",
  NAME: "name",
  RANK_CODE: "rank_code",
  RATING: "rating",
  COMPACT_COUNT: "compact_count",
  MOVEMENT_SYMBOL: "movement_symbol",
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
  group("selected", "Current/After", [
    ...recordSpec(),
    column("next_bp", "nuChii", {
      sort_kind: "chii_ordinal",
      sort_path: "next_bp_ordinal",
      presentation: PRESENTATION.RANK_CODE,
    }),
  ]),
  group("changes", "Next Basho", [
    column("delta_equelo", "ΔEq", {
      help: "Difference in rating.",
      sort_kind: "numeric",
      presentation: PRESENTATION.RATING,
    }),
    group("movement", "⇅", [
      column("bp", "Chii", {
        help: "See Notes.",
        sort_kind: "movement_symbol",
        sort_default_direction: "descending",
        presentation: PRESENTATION.MOVEMENT_SYMBOL,
      }),
      column("division", "Div", {
        help: "See Notes.",
        sort_kind: "movement_symbol",
        sort_default_direction: "descending",
        presentation: PRESENTATION.MOVEMENT_SYMBOL,
      }),
    ], { help: "See Notes." }),
  ]),
];

function recordSpec() {
  return [
    group("context", "Context", [
      group("skill", "Skill", [
        column("bp", "Chii", {
          sort_kind: "chii_ordinal",
          sort_path: "bp_ordinal",
          presentation: PRESENTATION.RANK_CODE,
        }),
        column("equelo", "Eq", { help: "Equelo rating.", sort_kind: "numeric", presentation: PRESENTATION.RATING }),
      ]),
      group("analysis", "Ratings Fit", [
        group("banzuke_error", "ΔBZ", [
          column("direction", "Dir", {
            sort_kind: "movement_symbol",
            sort_default_direction: "descending",
            presentation: PRESENTATION.MOVEMENT_SYMBOL,
          }),
          column("magnitude", "Mag", { sort_kind: "numeric", presentation: PRESENTATION.NUMERIC_MAGNITUDE }),
        ]),
        column("rbbp", "Eq Chii", {
          sort_kind: "chii_ordinal",
          sort_path: "rbbp_ordinal",
          presentation: PRESENTATION.RANK_CODE,
        }),
      ], { help: "See TBD" }),
    ]),
    group("result", "Result", [
      column("wins", "W", { sort_kind: "numeric", presentation: PRESENTATION.COMPACT_COUNT }),
      column("losses", "L", { sort_kind: "numeric", presentation: PRESENTATION.COMPACT_COUNT }),
      column("absences", "A", { sort_kind: "numeric", presentation: PRESENTATION.COMPACT_COUNT }),
      column("prizes", "📦", {
        sort_kind: "prize_set",
        sort_default_direction: "descending",
        presentation: PRESENTATION.COMPACT_TEXT,
      }),
    ], { help: "See Notes." }),
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
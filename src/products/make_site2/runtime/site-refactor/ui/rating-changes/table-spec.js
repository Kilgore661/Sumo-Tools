// Rating Changes grouped table specification.

const PRESENTATION = Object.freeze({
  DEFAULT: "default",
  NUMERIC: "numeric",
  RATING: "rating",
});

const RATING_CHANGES_TABLE_SPEC = [
  {
    key: "reference",
    label: "",
    children: [
      { key: "row_number", label: "#", role: "row_number", presentation: PRESENTATION.NUMERIC, sort_kind: "none" },
      { key: "shikona", label: "Shikona", presentation: PRESENTATION.DEFAULT, sort_kind: "text" },
    ],
  },
  {
    key: "context",
    label: "Context",
    children: [
      {
        key: "start",
        label: "Start",
        children: [
          { key: "chii", label: "Chii", presentation: PRESENTATION.DEFAULT, sort_kind: "chii_ordinal", sort_path: "chii_ordinal" },
          { key: "equelo", label: "Equelo", presentation: PRESENTATION.RATING, sort_kind: "numeric" },
          { key: "chii_ordinal", label: "Start Chii Ordinal", presentation: PRESENTATION.NUMERIC, sort_kind: "numeric", hidden: true },
        ],
      },
      {
        key: "end",
        label: "End",
        children: [
          { key: "chii", label: "Chii", presentation: PRESENTATION.DEFAULT, sort_kind: "chii_ordinal", sort_path: "chii_ordinal" },
          { key: "equelo", label: "Equelo", presentation: PRESENTATION.RATING, sort_kind: "numeric" },
          { key: "chii_ordinal", label: "End Chii Ordinal", presentation: PRESENTATION.NUMERIC, sort_kind: "numeric", hidden: true },
        ],
      },
      { key: "delta", label: "Δ", presentation: PRESENTATION.RATING, sort_kind: "numeric", sort_default_direction: "descending", note_id: "note_delta" },
    ],
  },
  {
    key: "expected",
    label: "Expected",
    children: [
      { key: "bouts", label: "Bouts", presentation: PRESENTATION.NUMERIC, sort_kind: "numeric", note_id: "note_basis" },
      { key: "delta_per_bout", label: "Δ / bout", presentation: PRESENTATION.RATING, sort_kind: "numeric" },
      { key: "normalised_per_bout", label: "ND / bout", presentation: PRESENTATION.NUMERIC, sort_kind: "numeric", note_id: "note_normalised" },
    ],
  },
  {
    key: "actual",
    label: "Actual",
    children: [
      { key: "bouts", label: "Bouts", presentation: PRESENTATION.NUMERIC, sort_kind: "numeric", note_id: "note_basis" },
      { key: "delta_per_bout", label: "Δ / bout", presentation: PRESENTATION.RATING, sort_kind: "numeric" },
      { key: "normalised_per_bout", label: "ND / bout", presentation: PRESENTATION.NUMERIC, sort_kind: "numeric", note_id: "note_normalised" },
    ],
  },
];

const DEFAULT_RATING_CHANGES_SORT_PATH = "context.delta";

export {
  DEFAULT_RATING_CHANGES_SORT_PATH,
  PRESENTATION,
  RATING_CHANGES_TABLE_SPEC,
};

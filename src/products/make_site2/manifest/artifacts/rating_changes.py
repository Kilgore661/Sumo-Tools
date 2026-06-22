"""Rating Changes artifact declaration."""

from ...artifact_model import (
    ColumnGroup,
    IndexedDataSource,
    IndexedTableArtifact,
    Note,
    TableColumn,
)


RATING_CHANGES_ARTIFACT = IndexedTableArtifact(
    id="rating_changes",
    heading="Rating Changes",
    kind="indexed_table",
    renderer="rating_changes_table",
    indexed_source=IndexedDataSource(
        id="rating_changes",
        label="Rating Changes",
        index_path="current-sumo/rating-changes/data/rating_changes_index.json",
        payload_path_field="payload_path",
        payload_media_type="text/csv",
    ),
    selector_filter_id="n",
    column_groups=(
        ColumnGroup(
            id="context",
            heading="Context",
            always_visible=True,
            columns=(
                "row_number",
                "shikona",
                "chii_at_start",
                "chii_at_end",
                "rating_at_start",
                "rating_at_end",
                "delta",
            ),
        ),
        ColumnGroup(
            id="expected",
            heading="Expected",
            columns=(
                "expected_bouts",
                "delta_per_expected_bout",
                "normalised_delta_per_expected_bout",
            ),
        ),
        ColumnGroup(
            id="actual",
            heading="Actual",
            columns=(
                "actual_bouts",
                "delta_per_actual_bout",
                "normalised_delta_per_actual_bout",
            ),
        ),
    ),
    columns=(
        TableColumn(id="row_number", heading="#", group="context", always_visible=True, sort_kind="none", align="right"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", group="context", always_visible=True, sort_kind="text"),
        TableColumn(id="chii_at_start", heading="Start", source_field="chii_at_start", group="context", always_visible=True, sort_key="chii_ordinal_at_start", sort_kind="chii_ordinal"),
        TableColumn(id="chii_at_end", heading="End", source_field="chii_at_end", group="context", always_visible=True, sort_key="chii_ordinal_at_end", sort_kind="chii_ordinal"),
        TableColumn(id="rating_at_start", heading="Start Eq", source_field="rating_at_start", group="context", always_visible=True, sort_kind="numeric", align="right"),
        TableColumn(id="rating_at_end", heading="End Eq", source_field="rating_at_end", group="context", always_visible=True, sort_kind="numeric", align="right"),
        TableColumn(id="delta", heading="Δ", source_field="delta", group="context", always_visible=True, sort_kind="numeric", sort_default_direction="descending", align="right", note_id="note_delta"),
        TableColumn(id="expected_bouts", heading="Bouts", source_field="expected_bouts", group="expected", sort_kind="numeric", align="right", note_id="note_basis"),
        TableColumn(id="delta_per_expected_bout", heading="Δ / bout", source_field="delta_per_expected_bout", group="expected", sort_kind="numeric", align="right"),
        TableColumn(id="normalised_delta_per_expected_bout", heading="ND / bout", source_field="normalised_delta_per_expected_bout", group="expected", sort_kind="numeric", align="right", note_id="note_normalised"),
        TableColumn(id="actual_bouts", heading="Bouts", source_field="actual_bouts", group="actual", sort_kind="numeric", align="right", note_id="note_basis"),
        TableColumn(id="delta_per_actual_bout", heading="Δ / bout", source_field="delta_per_actual_bout", group="actual", sort_kind="numeric", align="right"),
        TableColumn(id="normalised_delta_per_actual_bout", heading="ND / bout", source_field="normalised_delta_per_actual_bout", group="actual", sort_kind="numeric", align="right", note_id="note_normalised"),
    ),
    default_sort_column="delta",
    default_sort_descending=True,
    notes=(
        Note(id="note_delta", applies_to=("all",), text="Δ is the Equelo rating-point change over the selected window."),
        Note(id="note_basis", applies_to=("all",), text="Expected basis counts possible scheduled bouts in the window; actual basis counts bouts actually fought."),
        Note(id="note_normalised", applies_to=("normalised",), text="Normalised values divide each bout's rating movement by the K-factor used for that bout."),
    ),
)

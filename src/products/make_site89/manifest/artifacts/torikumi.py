"""Historical and current rating-annotated Torikumi artifact declaration."""

from ...artifact_model import (
    ColumnGroup,
    IndexedDataSource,
    IndexedTableArtifact,
    Note,
    TableColumn,
)


TORIKUMI_ARTIFACT = IndexedTableArtifact(
    id="torikumi",
    heading="Torikumi",
    kind="indexed_table",
    renderer="torikumi_table",
    indexed_source=IndexedDataSource(
        id="torikumi",
        label="Torikumi",
        index_path="current-sumo/torikumi/data/torikumi_index.json",
        payload_path_field="payload_path",
        payload_media_type="text/csv",
    ),
    selector_filter_id="torikumi_day",
    column_groups=(
        ColumnGroup(
            id="east",
            heading="East",
            columns=("east_shikona", "east_elo89", "east_odds"),
            always_visible=True,
        ),
        ColumnGroup(
            id="west",
            heading="West",
            columns=("west_odds", "west_elo89", "west_shikona"),
            always_visible=True,
        ),
    ),
    columns=(
        TableColumn(id="east_shikona", heading="Shikona", source_field="east_shikona", group="east", always_visible=True),
        TableColumn(id="east_elo89", heading="Elo89", source_field="east_elo89", group="east", always_visible=True, align="right"),
        TableColumn(id="east_odds", heading="Odds", source_field="east_odds", group="east", always_visible=True, align="right"),
        TableColumn(id="prediction", heading="Elo89 prediction", source_field="prediction_side", always_visible=True),
        TableColumn(id="west_odds", heading="Odds", source_field="west_odds", group="west", always_visible=True, align="right"),
        TableColumn(id="west_elo89", heading="Elo89", source_field="west_elo89", group="west", always_visible=True, align="right"),
        TableColumn(id="west_shikona", heading="Shikona", source_field="west_shikona", group="west", always_visible=True),
    ),
    default_sort_column="order",
    notes=(
        Note(
            id="rating_cutoff",
            applies_to=("all",),
            text="Odds are fair decimal odds derived from the Elo89 ratings available before the selected day. The £1 figures assume a separate £1 stake on each applicable bout. Fusen, draws, pending results and unavailable odds are excluded from all totals. Exactly equal Elo89 ratings are also excluded from the prediction tally, favourite total and winner benchmark. The higher-chii total additionally requires both rikishi to have a comparable published banzuke rank.",
        ),
    ),
)

"""Rating-annotated future Torikumi artifact declaration."""

from ...artifact_model import (
    ColumnGroup,
    IndexedDataSource,
    IndexedTableArtifact,
    Note,
    TableColumn,
)


TORIKUMI_ARTIFACT = IndexedTableArtifact(
    id="torikumi",
    heading="Torikumi for Future Days",
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
            columns=("east_shikona", "east_elo89", "east_probability"),
            always_visible=True,
        ),
        ColumnGroup(
            id="west",
            heading="West",
            columns=("west_probability", "west_elo89", "west_shikona"),
            always_visible=True,
        ),
    ),
    columns=(
        TableColumn(id="east_shikona", heading="Shikona", source_field="east_shikona", group="east", always_visible=True),
        TableColumn(id="east_elo89", heading="Elo89", source_field="east_elo89", group="east", always_visible=True, align="right"),
        TableColumn(id="east_probability", heading="P(win)", source_field="east_probability", group="east", always_visible=True, align="right"),
        TableColumn(id="west_probability", heading="P(win)", source_field="west_probability", group="west", always_visible=True, align="left"),
        TableColumn(id="west_elo89", heading="Elo89", source_field="west_elo89", group="west", always_visible=True, align="right"),
        TableColumn(id="west_shikona", heading="Shikona", source_field="west_shikona", group="west", always_visible=True),
    ),
    default_sort_column="order",
    notes=(
        Note(
            id="rating_cutoff",
            applies_to=("all",),
            text="Forecasts use the latest Elo89 ratings available in the site-data bundle.",
        ),
    ),
)

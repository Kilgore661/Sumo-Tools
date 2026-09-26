"""Rikishi biographical table artifact."""

from ...artifact_model import DataSource, Note, TableArtifact, TableColumn


RIKISHI_BIO_DATA_ARTIFACT = TableArtifact(
    id="rikishi_bio_data",
    heading="Rikishi bio data",
    kind="table",
    renderer="generic_table",
    rows_source=DataSource(
        id="rikishi_bio_data",
        label="Latest-banzuke rikishi bio data",
        path="rikishi/bio-data/data/rikishi_bio_data.csv",
        media_type="text/csv",
    ),
    columns=(
        TableColumn(id="row_number", heading="", sort_kind="none", align="right"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", sort_kind="text", align="left"),
        TableColumn(id="chii", heading="Chii", source_field="chii", sort_key="chii_ordinal", sort_kind="chii_ordinal", align="left"),
        TableColumn(id="age", heading="Age", source_field="age", sort_kind="numeric", align="right", note_id="bio_snapshot"),
        TableColumn(id="height_cm", heading="Height", source_field="height_cm", sort_kind="numeric", align="right", note_id="bio_measurements"),
        TableColumn(id="weight_kg", heading="Weight", source_field="weight_kg", sort_kind="numeric", align="right", note_id="bio_measurements"),
        TableColumn(id="bmi", heading="BMI", source_field="bmi", sort_kind="numeric", align="right", note_id="bio_measurements"),
    ),
    default_sort_column="row_number",
    notes=(
        Note(id="bio_snapshot", applies_to=("all",), text="Age is the number of completed years on the first day of the latest represented banzuke month."),
        Note(id="bio_measurements", applies_to=("all",), text="Height and weight are the latest available values on the cached SumoDB rikishi page. BMI is weight in kilograms divided by height in metres squared."),
    ),
)

from src.products.make_site2.manifest.artifacts import (
    BANZUKE_CHANGES_ARTIFACT,
    BASHO_RESULTS_ARTIFACT,
    STANDINGS_BY_WINS_ARTIFACT,
)
from src.products.make_site2.publication_model import build_publication_plan
from src.products.make_site2.site_definition import SITE
from src.products.make_site2.site_manifest import build_runtime_manifest


def column_by_id(columns: list[dict], column_id: str) -> dict:
    return next(column for column in columns if column["id"] == column_id)


def test_runtime_manifest_exposes_table_sort_metadata() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    brb_artifact = manifest["artifacts"][BASHO_RESULTS_ARTIFACT.id]
    columns = brb_artifact["columns"]

    assert brb_artifact["default_sort_column"] == "chii"
    assert brb_artifact["default_sort_descending"] is False
    assert column_by_id(columns, "row_number")["sort_kind"] == "none"
    assert column_by_id(columns, "chii")["sort_key"] == "chii_ordinal"
    assert column_by_id(columns, "chii")["sort_kind"] == "chii_ordinal"
    assert column_by_id(columns, "score")["sort_kind"] == "record"


def test_standings_columns_declare_sort_values_for_visible_metrics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    artifact = manifest["artifacts"][STANDINGS_BY_WINS_ARTIFACT.id]
    columns = artifact["columns"]

    assert column_by_id(columns, "row_number")["sort_kind"] == "none"
    assert column_by_id(columns, "shikona")["sort_kind"] == "text"
    assert column_by_id(columns, "chii")["sort_key"] == "chii_ordinal"
    assert column_by_id(columns, "credited_wins")["sort_kind"] == "numeric"
    assert column_by_id(columns, "selected_average_credited_wins")["sort_kind"] == "numeric"
    assert column_by_id(columns, "win_percent")["sort_kind"] == "numeric"


def test_banzuke_changes_declares_banzuke_style_sorting_note() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    artifact = manifest["artifacts"][BANZUKE_CHANGES_ARTIFACT.id]
    notes = {note["id"]: note for note in artifact["notes"]}

    assert notes["note_banzuke_style_sorting"]["applies_to"] == ["banzuke_style"]

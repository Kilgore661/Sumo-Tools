from src.products.make_site2.manifest.artifacts import (
    BANZUKE_CHANGES_ARTIFACT,
    BASHO_RESULTS_ARTIFACT,
    LONGEST_CAREERS_ARTIFACT,
    STANDINGS_BY_WINS_ARTIFACT,
)
from src.products.make_site2.publication_model import build_publication_plan
from src.products.make_site2.site_definition import SITE
from src.products.make_site2.site_manifest import build_runtime_manifest


# Basho Results (7.1) now uses a specialized recursive presentation-table
# renderer. Its terminal-path sorting is tested in
# test_make_site2_basho_results_redesign.py; this file keeps ordinary flat-table
# sort metadata checks that still live in the runtime manifest.


def column_by_id(columns: list[dict], column_id: str) -> dict:
    return next(column for column in columns if column["id"] == column_id)


def test_runtime_manifest_declares_basho_results_as_specialized_indexed_table() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    artifact = manifest["artifacts"][BASHO_RESULTS_ARTIFACT.id]

    assert artifact["kind"] == "indexed_table"
    assert artifact["selector_filter_id"] == "basho_date"
    assert artifact["indexed_source"]["index_path"] == (
        "sumo-history/basho-results/data/basho_results_index.json"
    )


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


def test_longest_careers_columns_declare_ranked_table_sort_values() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    artifact = manifest["artifacts"][LONGEST_CAREERS_ARTIFACT.id]
    columns = artifact["columns"]

    assert column_by_id(columns, "row_number")["sort_kind"] == "none"
    assert column_by_id(columns, "rank")["sort_kind"] == "numeric"
    assert column_by_id(columns, "rank")["sort_default_direction"] == "ascending"
    assert column_by_id(columns, "shikona")["sort_kind"] == "text"
    assert column_by_id(columns, "participation_years")["sort_kind"] == "numeric"
    assert column_by_id(columns, "gap_basho_count")["sort_kind"] == "numeric"

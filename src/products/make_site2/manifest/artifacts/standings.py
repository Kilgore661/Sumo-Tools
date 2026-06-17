from ..artifact_model import StandingsArtifact, IndexedTableArtifact, IndexedDataSource, DataSource, ColumnGroup, TableColumn, Note, SelectedTableDataSource
from .filters import STANDINGS_WINDOW_VALUES

def standings_source(window: str) -> SelectedTableDataSource:
    filename = f"multiple basho standings view (2026_03, BACKWARDS, {window})"
    return SelectedTableDataSource(
        id=f"window_{window}",
        label=f"{window} basho",
        filter_value=window,
        path=f"current-sumo/standings-by-wins/data/{filename}.csv",
        metadata_path=f"current-sumo/standings-by-wins/data/{filename}.json",
        media_type="text/csv",
    )

STANDINGS_BY_WINS_ARTIFACT = StandingsArtifact(
    id="standings_by_wins",
    heading="Rolling Wins-Based Ranking",
    kind="standings",
    renderer="standings_table",
    selector_filter_id="current_num_basho",
    config_source=DataSource(id="site_config", label="Site Config", path="current-sumo/standings-by-wins/data/site_config.json", media_type="application/json"),
    data_sources=tuple(standings_source(value.value) for value in STANDINGS_WINDOW_VALUES),
    column_groups=(
        ColumnGroup(id="row_number", heading="", always_visible=True, columns=("row_number",)),
        ColumnGroup(id="context", heading="Context", always_visible=True, columns=("shikona", "chii", "credited_wins")),
        ColumnGroup(id="wins_per_basho", heading="Wins per Basho", columns=("selected_average_credited_wins", "selected_average_rank")),
        ColumnGroup(id="wins_per_bout", heading="Wins per Bout", columns=("selected_expected_bout_count", "win_percent", "win_percent_rank")),
    ),
    # ... (columns definition remains long, but broken into lines for readability)
)

BASHO_RESULTS_ARTIFACT = IndexedTableArtifact(
    id="basho_results_browser",
    heading="Basho Results",
    kind="indexed_table",
    renderer="indexed_table",
    indexed_source=IndexedDataSource(id="basho_results", label="Basho Results", index_path="sumo-history/basho-results/data/basho_results_index.json", payload_path_field="payload_path", payload_media_type="text/csv"),
    selector_filter_id="basho_date",
    # ... (column groups and columns definitions)
)

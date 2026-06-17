"""Standings and indexed-basho artifact declarations for the public site."""

from ...artifact_model import (
    ColumnGroup,
    DataSource,
    IndexedDataSource,
    IndexedTableArtifact,
    Note,
    SelectedTableDataSource,
    StandingsArtifact,
    TableColumn,
)
from ..filters import STANDINGS_WINDOW_VALUES


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
    id="standings_by_wins", heading="Rolling Wins-Based Ranking", kind="standings", renderer="standings_table", selector_filter_id="current_num_basho",
    config_source=DataSource(id="site_config", label="Site Config", path="current-sumo/standings-by-wins/data/site_config.json", media_type="application/json"),
    data_sources=tuple(standings_source(value.value) for value in STANDINGS_WINDOW_VALUES),
    column_groups=(
        ColumnGroup(id="row_number", heading="", always_visible=True, columns=("row_number",)),
        ColumnGroup(id="context", heading="Context", always_visible=True, columns=("shikona", "chii", "credited_wins")),
        ColumnGroup(id="wins_per_basho", heading="Wins per Basho", columns=("selected_average_credited_wins", "selected_average_rank")),
        ColumnGroup(id="wins_per_bout", heading="Wins per Bout", columns=("selected_expected_bout_count", "win_percent", "win_percent_rank")),
    ),
    columns=(
        TableColumn(id="row_number", heading="#", group="row_number", always_visible=True, sort_kind="none", align="center"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", group="context", help="Name disambiguation. See Notes.", always_visible=True, sort_key="shikona", sort_kind="text", note_id="note_identity"),
        TableColumn(id="chii", heading="Chii", source_field="chii", group="context", always_visible=True, sort_key="chii_ordinal", sort_kind="chii_ordinal"),
        TableColumn(id="credited_wins", heading="Wins", source_field="credited_wins", group="context", always_visible=True, sort_key="credited_wins", sort_kind="numeric", align="right", note_id="note_wins"),
        TableColumn(id="selected_average_credited_wins", heading="Average", source_field="selected_average_credited_wins", group="wins_per_basho", sort_key="selected_average_credited_wins", sort_kind="numeric", align="right"),
        TableColumn(id="selected_average_rank", heading="#", source_field="selected_average_credited_wins", group="wins_per_basho", sort_key="selected_average_credited_wins", sort_kind="numeric", align="right"),
        TableColumn(id="selected_expected_bout_count", heading="Bouts", source_field="selected_expected_bout_count", group="wins_per_bout", sort_key="selected_expected_bout_count", sort_kind="numeric", align="right", note_id="note_bouts"),
        TableColumn(id="win_percent", heading="Win %", source_field="win_percent", group="wins_per_bout", sort_key="win_percent", sort_kind="numeric", align="right"),
        TableColumn(id="win_percent_rank", heading="#", source_field="win_percent", group="wins_per_bout", sort_key="win_percent", sort_kind="numeric", align="right"),
    ),
    notes=(
        Note(id="note_identity", applies_to=("all",), text="Shikona values followed by a number identify rikishi who have shared the same fighting name."),
        Note(id="note_wins", applies_to=("all",), text="Wins include fusensho."),
        Note(id="note_bouts", applies_to=("percentages", "combined"), text="Bouts means the expected number of scheduled bouts in the selected window."),
    ),
)

BASHO_RESULTS_ARTIFACT = IndexedTableArtifact(
    id="basho_results_browser", heading="Basho Results", kind="indexed_table", renderer="indexed_table",
    indexed_source=IndexedDataSource(id="basho_results", label="Basho Results", index_path="sumo-history/basho-results/data/basho_results_index.json", payload_path_field="payload_path", payload_media_type="text/csv"),
    selector_filter_id="basho_date",
    column_groups=(
        ColumnGroup(id="identity", heading="", always_visible=True, columns=("row_number", "shikona", "chii")),
        ColumnGroup(id="previous_basho", heading="Previous Basho", controlling_filter_id="previous_context", columns=("previous_chii", "previous_result")),
        ColumnGroup(id="result_state", heading="After/During", always_visible=True, columns=("score", "equelo", "delta_equelo", "nu_chii")),
    ),
    columns=(
        TableColumn(id="row_number", heading="#", group="identity", always_visible=True, sort_kind="none", align="center"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", group="identity", always_visible=True, sort_kind="text"),
        TableColumn(id="chii", heading="Chii", source_field="chii", group="identity", always_visible=True, sort_key="chii_ordinal", sort_kind="chii_ordinal"),
        TableColumn(id="previous_result", heading="Result", source_field="previous_result", group="previous_basho", sort_kind="record", align="center"),
        TableColumn(id="previous_chii", heading="Chii", source_field="previous_chii", group="previous_basho", sort_key="previous_chii_ordinal", sort_kind="chii_ordinal", align="center"),
        TableColumn(id="score", heading="Score", source_field="score", group="result_state", always_visible=True, sort_kind="record", align="center"),
        TableColumn(id="equelo", heading="Equelo", source_field="equelo", group="result_state", sort_kind="numeric", align="center"),
        TableColumn(id="delta_equelo", heading="Delta Equelo", source_field="delta_equelo", group="result_state", sort_kind="numeric", align="right"),
        TableColumn(id="nu_chii", heading="nuChii", source_field="nu_chii", group="result_state", sort_key="nu_chii_ordinal", sort_kind="chii_ordinal"),
    ),
    default_sort_column="chii",
    notes=(
        Note(id="note_result", applies_to=("all",), text="Result shows the number of wins, losses, absences and prizes."),
        Note(id="note_movement", applies_to=("changes_context",), text="Movement notes placeholder. Replace with meaningful movement documentation."),
        Note(id="note_chii_movement", applies_to=("changes_context",), text="Chii movement notes placeholder. Replace with meaningful chii movement documentation."),
        Note(id="note_division_movement", applies_to=("changes_context",), text="Division movement notes placeholder. Replace with meaningful division movement documentation."),
    ),
)

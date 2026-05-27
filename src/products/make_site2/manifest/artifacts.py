"""Published Artifact declarations used by the current public site."""

from __future__ import annotations

from ..artifact_model import (
    BanzukeChangesArtifact,
    ChartAxis,
    ChartArtifact,
    ChartTrace,
    ColumnGroup,
    DataBinding,
    DataSource,
    IndexedDataSource,
    IndexedTableArtifact,
    Note,
    SectionedTableArtifact,
    SelectedTableDataSource,
    StandingsArtifact,
    TableColumn,
    TableSection,
)
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


BANZUKE_CHANGES_ARTIFACT = BanzukeChangesArtifact(
    id="banzuke_changes", heading="Banzuke Changes", kind="banzuke_changes", renderer="banzuke_changes_table",
    config_source=DataSource(id="site_config", label="Site Config", path="current-sumo/banzuke-changes/site_config.json", media_type="application/json"),
    rows_source=DataSource(id="banzuke_change_report", label="Banzuke Change Report", path="current-sumo/banzuke-changes/data/banzuke_change_report.csv", media_type="text/csv"),
    notes=(
        Note(id="note_result", applies_to=("context",), text="Result gives wins, losses and absences followed by prizes if any. A trailing up/down marker indicates promotion or demotion into the current broad rank level."),
        Note(id="note_delta", applies_to=("delta",), text="Delta indicates the size of movement from the previous basho's position, measured in banzuke rows."),
        Note(id="note_banzuke_style_sorting", applies_to=("banzuke_style",), text="Sorting is not available in banzuke-style view because the layout preserves the East/West banzuke structure. Disable banzuke-style view to sort."),
    ),
)

STANDINGS_BY_WINS_ARTIFACT = StandingsArtifact(
    id="standings_by_wins", heading="Standings by Wins", kind="standings", renderer="standings_table", selector_filter_id="current_num_basho",
    config_source=DataSource(id="site_config", label="Site Config", path="current-sumo/standings-by-wins/data/site_config.json", media_type="application/json"),
    data_sources=tuple(standings_source(value.value) for value in STANDINGS_WINDOW_VALUES),
    column_groups=(
        ColumnGroup(id="identity", heading="", always_visible=True, columns=("row_number", "shikona", "chii", "credited_wins")),
        ColumnGroup(id="wins_per_basho", heading="Wins per Basho", columns=("selected_average_credited_wins", "selected_average_rank")),
        ColumnGroup(id="wins_per_bout", heading="Wins per Bout", columns=("selected_expected_bout_count", "win_percent", "win_percent_rank")),
    ),
    columns=(
        TableColumn(id="row_number", heading="#", group="identity", always_visible=True, sort_kind="none", align="center"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", group="identity", always_visible=True, sort_key="shikona", sort_kind="text", note_id="note_identity"),
        TableColumn(id="chii", heading="Chii", source_field="chii", group="identity", always_visible=True, sort_key="chii_ordinal", sort_kind="chii_ordinal", note_id="note_identity"),
        TableColumn(id="credited_wins", heading="Wins", source_field="credited_wins", group="identity", always_visible=True, sort_key="credited_wins", sort_kind="numeric", align="right", note_id="note_wins"),
        TableColumn(id="selected_average_credited_wins", heading="Average", source_field="selected_average_credited_wins", group="wins_per_basho", sort_key="selected_average_credited_wins", sort_kind="numeric", align="right"),
        TableColumn(id="selected_average_rank", heading="#", source_field="selected_average_credited_wins", group="wins_per_basho", sort_key="selected_average_credited_wins", sort_kind="numeric", align="right"),
        TableColumn(id="selected_expected_bout_count", heading="Bouts", source_field="selected_expected_bout_count", group="wins_per_bout", sort_key="selected_expected_bout_count", sort_kind="numeric", align="right", note_id="note_bouts"),
        TableColumn(id="win_percent", heading="Win %", source_field="win_percent", group="wins_per_bout", sort_key="win_percent", sort_kind="numeric", align="right"),
        TableColumn(id="win_percent_rank", heading="#", source_field="win_percent", group="wins_per_bout", sort_key="win_percent", sort_kind="numeric", align="right"),
    ),
    notes=(
        Note(id="note_identity", applies_to=("all",), text="The reported Shikona and Chii are those that pertain to the rikishi in the latest basho."),
        Note(id="note_wins", applies_to=("all",), text="Wins include fusensho."),
        Note(id="note_active", applies_to=("all",), text="An Active rikishi is one that is listed on the banzuke for the latest basho."),
        Note(id="note_bouts", applies_to=("percentages", "combined"), text="Bouts is the expected number of scheduled bouts in the selected window."),
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
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", group="identity", always_visible=True, sort_kind="text", note_id="note_shikona"),
        TableColumn(id="chii", heading="Chii", source_field="chii", group="identity", always_visible=True, sort_key="chii_ordinal", sort_kind="chii_ordinal", note_id="note_chii"),
        TableColumn(id="previous_result", heading="Result", source_field="previous_result", group="previous_basho", sort_kind="record", align="center", note_id="note_previous_result"),
        TableColumn(id="previous_chii", heading="Chii", source_field="previous_chii", group="previous_basho", sort_key="previous_chii_ordinal", sort_kind="chii_ordinal", align="center"),
        TableColumn(id="score", heading="Score", source_field="score", group="result_state", always_visible=True, sort_kind="record", align="center", note_id="note_score"),
        TableColumn(id="equelo", heading="Equelo", source_field="equelo", group="result_state", sort_kind="numeric", align="center", note_id="note_equelo"),
        TableColumn(id="delta_equelo", heading="Delta Equelo", source_field="delta_equelo", group="result_state", sort_kind="numeric", align="right", note_id="note_delta_equelo"),
        TableColumn(id="nu_chii", heading="nuChii", source_field="nu_chii", group="result_state", sort_key="nu_chii_ordinal", sort_kind="chii_ordinal", note_id="note_nu_chii"),
    ),
    default_sort_column="chii",
    notes=(
        Note(id="note_shikona", applies_to=("all",), text="Shikona is the name used by the rikishi for the selected basho."),
        Note(id="note_chii", applies_to=("all",), text="Chii is the official rank slot at the start of the selected basho."),
        Note(id="note_previous_result", applies_to=("previous_basho",), text="Previous Result gives wins, losses and absences followed by prizes if any. A trailing up/down marker indicates promotion or demotion into the selected basho's broad rank level."),
        Note(id="note_score", applies_to=("all",), text="Score gives wins, losses and absences for the selected basho. For an in-progress basho it is the score through the latest published day."),
        Note(id="note_equelo", applies_to=("rating_context",), text="Equelo is the fixed_v2 process rating at the represented point."),
        Note(id="note_delta_equelo", applies_to=("rating_context",), text="Delta Equelo is the rating change from the start of the selected basho."),
        Note(id="note_nu_chii", applies_to=("nu_chii",), text="nuChii is the after/during chii value for the selected state. It may be actual, estimated, or unavailable depending on what is known when the page data is produced."),
    ),
)

FINISH_BY_CHII_ARTIFACT = ChartArtifact(
    id="finish_by_chii", heading="Finish by Chii", kind="chart", renderer="finish_by_chii_chart",
    data_binding=DataBinding(kind="csv_set", sources=("top_thresholds", "bottom_thresholds")),
    data_sources=(
        DataSource(id="top_thresholds", label="Top finish thresholds", path="performance/finish-by-chii/data/top_thresholds.csv", media_type="text/csv"),
        DataSource(id="bottom_thresholds", label="Bottom finish thresholds", path="performance/finish-by-chii/data/bottom_thresholds.csv", media_type="text/csv"),
    ),
)

BANZUKE_DIVISION_BY_ERA_ARTIFACT = ChartArtifact(
    id="banzuke_division_by_era", heading="Banzuke Division by Era", kind="chart", renderer="stacked_bar_chart",
    data_binding=DataBinding(kind="csv", sources=("divisions",)),
    data_sources=(DataSource(id="divisions", label="Average banzuke composition by era", path="banzuke-rank/banzuke-structure-over-time/banzuke-division-by-era/data/divisions.csv", media_type="text/csv"),),
    traces=(ChartTrace(id="division_average", label="Division average", kind="stacked_bar", x="era", y="average_rikishi", group_by="division"),),
    x_axis=ChartAxis(id="x", source_field="era", label="Era", order_values=("1958-1967", "1968-1977", "1978-1987", "1988-1997", "1998-2007", "2008-2017", "2018-2026")),
    y_axis=ChartAxis(id="y", source_field="average_rikishi", label="Average rikishi per basho", minimum=0),
    provenance={"legend_title": "Division", "stack_order": ("Jonokuchi", "Jonidan", "Sandanme", "Makushita", "Juryo", "Makuuchi"), "x_tickangle": -45, "group_colours": {"Makuuchi": "#6D597A", "Juryo": "#355C7D", "Makushita": "#457B9D", "Sandanme": "#2A9D8F", "Jonidan": "#8D6A9F", "Jonokuchi": "#BC6C25"}},
)

MAKUUCHI_RANK_BY_ERA_ARTIFACT = ChartArtifact(
    id="makuuchi_rank_by_era", heading="Makuuchi Rank by Era", kind="chart", renderer="stacked_bar_chart",
    data_binding=DataBinding(kind="csv", sources=("ranks",)),
    data_sources=(DataSource(id="ranks", label="Rank appearances by era", path="banzuke-rank/banzuke-structure-over-time/makuuchi-rank-by-era/data/ranks.csv", media_type="text/csv"),),
    traces=(ChartTrace(id="era_counts", label="Era counts", kind="stacked_bar", x="rank", y="count", group_by="era"),),
    x_axis=ChartAxis(id="x", source_field="rank", label="Rank"),
    y_axis=ChartAxis(id="y", source_field="count", label="Appearances", minimum=0),
    provenance={"legend_title": "Era", "group_order": ("1958-1967", "1968-1977", "1978-1987", "1988-1997", "1998-2007", "2008-2017", "2018-2026"), "x_tickangle": -45},
)

DIVISION_STABILITY_ARTIFACT = ChartArtifact(
    id="division_stability", heading="Division Stability", kind="chart", renderer="grouped_line_chart",
    data_binding=DataBinding(kind="csv", sources=("persistence",)),
    data_sources=(DataSource(id="persistence", label="Division persistence", path="banzuke-rank/division-stability/data/persistence.csv", media_type="text/csv"),),
    traces=(ChartTrace(id="mean_persistence", label="Mean persistence", kind="scatter", x="date", y="mean_persistence", group_by="division"),),
    x_axis=ChartAxis(id="x", source_field="date", label="Basho"),
    y_axis=ChartAxis(id="y", source_field="mean_persistence", label="Mean persistence", minimum=0, maximum=1, tickformat=".0%"),
    provenance={"legend_title": "Division", "default_visible": ("Makuuchi",), "group_order": ("Makuuchi", "Juryo", "Makushita", "Sandanme", "Jonidan", "Jonokuchi"), "hover_fields": ("num_basho", "frequency", "stdev_persistence"), "x_tickangle": -45},
)

FIRST_CHII_APPEARANCE_ARTIFACT = ChartArtifact(
    id="first_chii_appearance", heading="First Chii Appearance", kind="chart", renderer="ordered_bar_chart",
    data_binding=DataBinding(kind="csv", sources=("appearances",)),
    data_sources=(DataSource(id="appearances", label="First observed appearance", path="banzuke-rank/rank-history/first-chii-appearance/data/appearances.csv", media_type="text/csv"),),
    traces=(ChartTrace(id="first_appearance", label="First appearance", kind="bar", x="chii", y="first_appearance_month_index"),),
    x_axis=ChartAxis(id="x", source_field="chii", label="Chii"),
    y_axis=ChartAxis(id="y", source_field="first_appearance_month_index", label="First appearance"),
    provenance={"order_field": "ordinal", "x_tickangle": -45, "max_x_tick_labels": 40, "base_year": 1958, "base_month": 1, "date_fields": ("year", "month")},
)

RANK_AT_RETIREMENT_ARTIFACT = ChartArtifact(
    id="rank_at_retirement", heading="Rank at Retirement", kind="chart", renderer="category_bar_chart",
    data_binding=DataBinding(kind="csv", sources=("distribution",)),
    data_sources=(DataSource(id="distribution", label="Distribution", path="sumo-history/career-lifecycle/rank-at-retirement/data/distribution.csv", media_type="text/csv"),),
    traces=(ChartTrace(id="retired_rikishi", label="Retired rikishi", kind="bar", x="rank_group", y="count"),),
    x_axis=ChartAxis(id="x", source_field="rank_group", label="Final observed rank group", order_values=("Y", "O", "S", "K", "M", "J", "Ms", "Sd", "Jd", "Jk")),
    y_axis=ChartAxis(id="y", source_field="count", label="Retired rikishi count", minimum=0),
    notes=(Note(id="rank_at_retirement", applies_to=("all",), text="Rank at Retirement. This is the final observed banzuke rank group for retired rikishi according to SumoDB-derived banzuke history. Rikishi listed on the latest available banzuke are treated as active and excluded."),),
)

CAREER_LENGTH_ARTIFACT = ChartArtifact(
    id="career_length", heading="Career Length", kind="chart", renderer="career_length",
    data_binding=DataBinding(kind="csv_set", sources=("distribution", "pmf", "cdf", "survival", "longest")),
    data_sources=(
        DataSource(id="distribution", label="Distribution", path="sumo-history/career-lifecycle/career-length/data/distribution.csv", media_type="text/csv"),
        DataSource(id="pmf", label="PMF", path="sumo-history/career-lifecycle/career-length/data/pmf.csv", media_type="text/csv"),
        DataSource(id="cdf", label="CDF", path="sumo-history/career-lifecycle/career-length/data/cdf.csv", media_type="text/csv"),
        DataSource(id="survival", label="Survival", path="sumo-history/career-lifecycle/career-length/data/survival.csv", media_type="text/csv"),
        DataSource(id="longest", label="Longest", path="sumo-history/career-lifecycle/career-length/data/longest.csv", media_type="text/csv"),
    ),
    provenance={"views": {
        "distribution": {"kind": "stacked_bar", "label": "Distribution", "x": "nearest_years", "y": ("retired_count", "active_count"), "series_labels": ("Retired", "Active"), "x_label": "Nearest integer years", "y_label": "Rikishi count"},
        "pmf": {"kind": "line", "label": "PMF", "x": "nearest_years", "y": "probability", "x_label": "Nearest integer years", "y_label": "Probability", "tickformat": ".0%"},
        "cdf": {"kind": "line", "label": "CDF", "x": "nearest_years", "y": "cumulative_probability", "x_label": "Nearest integer years", "y_label": "Cumulative probability", "tickformat": ".0%"},
        "survival": {"kind": "line", "label": "Survival", "x": "nearest_years", "y": "survival_probability", "x_label": "Nearest integer years", "y_label": "Survival probability", "tickformat": ".0%"},
        "longest": {"kind": "table", "label": "Longest Careers", "columns": [{"id": "rank", "heading": "#", "source_field": "rank", "align": "right"}, {"id": "shikona", "heading": "Shikona", "source_field": "shikona", "align": "left", "link": "rikishi"}, {"id": "first_appearance", "heading": "First", "source_field": "first_appearance", "align": "left"}, {"id": "last_appearance", "heading": "Last", "source_field": "last_appearance", "align": "left"}, {"id": "participation_years", "heading": "Years", "source_field": "participation_years", "align": "right", "formatter": "decimal_2"}, {"id": "gap_basho_count", "heading": "Bg", "source_field": "gap_basho_count", "align": "right"}, {"id": "active", "heading": "Active", "source_field": "active", "align": "center"}]},
    }},
    notes=(
        Note(id="observed_career_length", applies_to=("all",), text="Years is the observed career length: the elapsed time between the first and last banzuke appearances in the prepared history."),
        Note(id="bg_count", applies_to=("longest",), text="Bg is the number of basho for which the rikishi was absent."),
    ),
)

TYPICAL_EQUELO_VALUES_ARTIFACT = SectionedTableArtifact(
    id="typical_equelo_values", heading="Typical Equelo Ratings", kind="sectioned_table", renderer="sectioned_table", primary_source="typical_equelo_values",
    data_sources=(DataSource(id="typical_equelo_values", label="Typical Equelo Ratings", path="ratings-models/rating-and-rank/typical-equelo-values/data/typical_equelo_values.csv", media_type="text/csv"),),
    sections=(
        TableSection(id="sanyaku", heading="Sanyaku", source_field="table", source_value="Sanyaku", order_by="row_order"),
        TableSection(id="maegashira", heading="Maegashira", source_field="table", source_value="Maegashira", order_by="row_order"),
        TableSection(id="other", heading="Other", source_field="table", source_value="Other", order_by="row_order"),
    ),
    columns=(
        TableColumn(id="label", heading="Rank", source_field="label", sort_kind="none", align="left"),
        TableColumn(id="rating", heading="Equelo", source_field="rating", sort_kind="numeric", align="right"),
    ),
    notes=(
        Note(id="typical_equelo_values", applies_to=("all",), text="Equelo Ratings are typical rating landmarks, not promises about every rikishi at a rank. Sideless labels such as M3 use the average of the east and west rank slots."),
        Note(id="jd100", applies_to=("all",), text="Below Jd100 the support is low and Jonokuchi has too much churn for Elo-like ratings such as Equelo to produce stable public landmarks."),
    ),
)

WIN_PROBABILITY_BY_STANDING_ARTIFACT = ChartArtifact(
    id="win_probability_by_standing", heading="Win Probability by Standing", kind="chart", renderer="standing_win_probability_chart",
    data_binding=DataBinding(kind="selected_csv", sources=("observed", "equelo")),
    data_sources=(
        DataSource(id="observed", label="Observed", path="ratings-models/observed-vs-modelled/win-probability-by-standing/data/observed_trace_points.csv", media_type="text/csv"),
        DataSource(id="equelo", label="Equelo", path="ratings-models/observed-vs-modelled/win-probability-by-standing/data/equelo_trace_points.csv", media_type="text/csv"),
    ),
    traces=(ChartTrace(id="standing_trace", label="Standing", kind="scatter", x="opponent_chii", y="p_selected_wins", group_by="selected_chii", error_y=("ci95_lower", "ci95_upper")),),
    x_axis=ChartAxis(id="x", source_field="opponent_chii", label="Opponent sideless chii"),
    y_axis=ChartAxis(id="y", source_field="p_selected_wins", label="P(selected standing wins)", minimum=0, maximum=1, tickformat=".0%"),
    provenance={"default_display_trace": "Y1", "sanyaku_display": ("Y1", "O1", "S1", "K1"), "x_order_field": "opponent_ordinal", "selected_order_field": "selected_ordinal", "legend_title": "Selected chii"},
)

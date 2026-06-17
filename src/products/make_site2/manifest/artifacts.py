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
    TableArtifact,
    TableColumn,
    TableSection,
)
from ..perf_chart.config import EQUELO_LOG_BASE, TOP_CHART_PROP
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
    id="banzuke_changes", heading="Most Recent Banzuke", kind="banzuke_changes", renderer="banzuke_changes_table",
    config_source=DataSource(id="site_config", label="Site Config", path="current-sumo/banzuke-changes/site_config.json", media_type="application/json"),
    rows_source=DataSource(id="banzuke_change_report", label="Banzuke Change Report", path="current-sumo/banzuke-changes/data/banzuke_change_report.csv", media_type="text/csv"),
    notes=(
        Note(id="note_result", applies_to=("context",), text="In Result, arrows show movement between rank groups such as Maegashira, Komusubi, Sekiwake, Ozeki, Yokozuna or the lower divisions. This differs from the movement column, which shows movement up or down in banzuke slot order."),
        Note(id="note_delta", applies_to=("delta",), text="Delta measures how many east/west banzuke slots a rikishi moved. A full numbered rank change, such as M2e to M3e, counts as two slots."),
        Note(id="note_banzuke_style_sorting", applies_to=("banzuke_style",), text="Sorting is not available in banzuke-style view because the layout preserves the East/West banzuke structure. Disable banzuke-style view to sort."),
    ),
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

FINISH_BY_CHII_ARTIFACT = ChartArtifact(
    id="finish_by_chii", heading="Finish Chances by Wins", kind="chart", renderer="finish_by_chii_chart",
    data_binding=DataBinding(kind="csv_set", sources=("top_thresholds", "bottom_thresholds")),
    data_sources=(
        DataSource(id="top_thresholds", label="Top finish thresholds", path="performance/finish-by-chii/data/top_thresholds.csv", media_type="text/csv"),
        DataSource(id="bottom_thresholds", label="Bottom finish thresholds", path="performance/finish-by-chii/data/bottom_thresholds.csv", media_type="text/csv"),
    ),
)

BANZUKE_DIVISION_BY_ERA_ARTIFACT = ChartArtifact(
    id="banzuke_division_by_era", heading="Average Banzuke Composition by Era", kind="chart", renderer="stacked_bar_chart",
    data_binding=DataBinding(kind="csv", sources=("divisions",)),
    data_sources=(DataSource(id="divisions", label="Average banzuke composition by era", path="banzuke-rank/banzuke-structure-over-time/banzuke-division-by-era/data/divisions.csv", media_type="text/csv"),),
    traces=(ChartTrace(id="division_average", label="Division average", kind="stacked_bar", x="era", y="average_rikishi", group_by="division"),),
    x_axis=ChartAxis(id="x", source_field="era", label="Era", order_values=("1958-1967", "1968-1977", "1978-1987", "1988-1997", "1998-2007", "2008-2017", "2018-2026")),
    y_axis=ChartAxis(id="y", source_field="average_rikishi", label="Average rikishi per basho", minimum=0),
    provenance={"subheading": "Average rikishi per basho, grouped by division.", "legend_title": "Division", "stack_order": ("Jonokuchi", "Jonidan", "Sandanme", "Makushita", "Juryo", "Makuuchi"), "x_tickangle": "auto", "group_colours": {"Makuuchi": "#6D597A", "Juryo": "#355C7D", "Makushita": "#457B9D", "Sandanme": "#2A9D8F", "Jonidan": "#8D6A9F", "Jonokuchi": "#BC6C25"}},
)

MAKUUCHI_RANK_BY_ERA_ARTIFACT = ChartArtifact(
    id="makuuchi_rank_by_era", heading="Makuuchi Rank Appearances by Era", kind="chart", renderer="stacked_bar_chart",
    data_binding=DataBinding(kind="csv", sources=("ranks",)),
    data_sources=(DataSource(id="ranks", label="Rank appearances by era", path="banzuke-rank/banzuke-structure-over-time/makuuchi-rank-by-era/data/ranks.csv", media_type="text/csv"),),
    traces=(ChartTrace(id="era_counts", label="Era counts", kind="stacked_bar", x="rank", y="count", group_by="era"),),
    x_axis=ChartAxis(id="x", source_field="rank", label="Rank"),
    y_axis=ChartAxis(id="y", source_field="count", label="Appearances", minimum=0),
    provenance={"subheading": "Count of banzuke appearances at each Makuuchi rank.", "legend_title": "Era", "group_order": ("1958-1967", "1968-1977", "1978-1987", "1988-1997", "1998-2007", "2008-2017", "2018-2026"), "x_tickangle": -45},
)

DIVISION_STABILITY_ARTIFACT = ChartArtifact(
    id="division_stability", heading="Division Persistence", kind="chart", renderer="grouped_line_chart",
    data_binding=DataBinding(kind="csv", sources=("persistence",)),
    data_sources=(DataSource(id="persistence", label="Division persistence", path="banzuke-rank/division-stability/data/persistence.csv", media_type="text/csv"),),
    traces=(ChartTrace(id="mean_persistence", label="Mean persistence", kind="scatter", x="date", y="mean_persistence", group_by="division"),),
    x_axis=ChartAxis(id="x", source_field="date", label="Basho"),
    y_axis=ChartAxis(id="y", source_field="mean_persistence", label="Mean persistence", minimum=0, maximum=1, tickformat=".0%"),
    provenance={"subheading": "How consistently each basho's division members stayed in the same division across that basho and the previous 10.", "legend_title": "Division", "default_visible": ("Makuuchi",), "group_order": ("Makuuchi", "Juryo", "Makushita", "Sandanme", "Jonidan", "Jonokuchi"), "hover_fields": ("num_basho", "frequency", "stdev_persistence"), "x_tickangle": -45},
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

MOST_CONSECUTIVE_BOUTS_ARTIFACT = TableArtifact(
    id="most_consecutive_bouts", heading="Most Consecutive Bouts", kind="table", renderer="generic_table",
    rows_source=DataSource(id="longest_streak_candidates", label="Longest streak candidates", path="sumo-history/records/most-consecutive-bouts/data/longest_streak_candidates.csv", media_type="text/csv"),
    columns=(
        TableColumn(id="row_number", heading="", sort_kind="none", align="right"),
        TableColumn(id="position", heading="#", source_field="position", sort_key="position", sort_kind="numeric", sort_default_direction="ascending", align="right"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", sort_kind="text", align="left"),
        TableColumn(id="bouts", heading="Bouts", source_field="bouts", sort_kind="numeric", align="right"),
        TableColumn(id="start", heading="Start", source_field="start", help="year/month/day of basho", sort_kind="text", align="left"),
        TableColumn(id="end", heading="End", source_field="end", help="year/month/day of basho", sort_kind="text", align="left"),
        TableColumn(id="clean", heading="Clean", source_field="clean", help="See Notes", sort_kind="none", align="center", note_id="clean_record"),
    ),
    default_sort_column="position",
    notes=(
        Note(id="clean_record", applies_to=("all",), text='A "clean" record is one where the rikishi has never missed a day in his entire career.'),
    ),
)

MOST_CAREER_WINS_ARTIFACT = TableArtifact(
    id="most_career_wins", heading="Most Career Wins", kind="table", renderer="generic_table",
    rows_source=DataSource(id="career_wins", label="Career wins", path="sumo-history/records/most-career-wins/data/career_wins.csv", media_type="text/csv"),
    columns=(
        TableColumn(id="row_number", heading="", sort_kind="none", align="right"),
        TableColumn(id="position", heading="#", source_field="position", sort_key="position", sort_kind="numeric", sort_default_direction="ascending", align="right"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", sort_kind="text", align="left"),
        TableColumn(id="wins", heading="Wins", source_field="wins", sort_kind="numeric", align="right"),
        TableColumn(id="losses", heading="Losses", source_field="losses", sort_kind="numeric", align="right"),
        TableColumn(id="bouts", heading="Bouts", source_field="bouts", sort_kind="numeric", align="right"),
        TableColumn(id="win_rate", heading="Win rate", source_field="win_rate", sort_kind="numeric", align="right"),
        TableColumn(id="start", heading="Start", source_field="start", help="year/month/day of basho", sort_kind="text", align="left"),
        TableColumn(id="end", heading="End", source_field="end", help="year/month/day of basho", sort_kind="text", align="left"),
    ),
    default_sort_column="position",
)

MOST_CAREER_LOSSES_ARTIFACT = TableArtifact(
    id="most_career_losses", heading="Most Career Losses", kind="table", renderer="generic_table",
    rows_source=DataSource(id="career_losses", label="Career losses", path="sumo-history/records/most-career-losses/data/career_losses.csv", media_type="text/csv"),
    columns=(
        TableColumn(id="row_number", heading="", sort_kind="none", align="right"),
        TableColumn(id="position", heading="#", source_field="position", sort_key="position", sort_kind="numeric", sort_default_direction="ascending", align="right"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", sort_kind="text", align="left"),
        TableColumn(id="losses", heading="Losses", source_field="losses", sort_kind="numeric", align="right"),
        TableColumn(id="wins", heading="Wins", source_field="wins", sort_kind="numeric", align="right"),
        TableColumn(id="bouts", heading="Bouts", source_field="bouts", sort_kind="numeric", align="right"),
        TableColumn(id="win_rate", heading="Win rate", source_field="win_rate", sort_kind="numeric", align="right"),
        TableColumn(id="start", heading="Start", source_field="start", help="year/month/day of basho", sort_kind="text", align="left"),
        TableColumn(id="end", heading="End", source_field="end", help="year/month/day of basho", sort_kind="text", align="left"),
    ),
    default_sort_column="position",
)

CAREER_COMPARISONS_ARTIFACT = ChartArtifact(
    id="career_comparisons", heading="Rikishi History", kind="chart", renderer="career_comparisons",
    data_binding=DataBinding(kind="json", sources=("trajectory_master",)),
    data_sources=(
        DataSource(id="trajectory_master", label="Trajectory Master", path="rikishi/career-comparisons/data/trajectory_master.json", media_type="application/json"),
    ),
    provenance={
        "equelo_log_base": EQUELO_LOG_BASE,
        "top_chart_prop": TOP_CHART_PROP,
        "default_skill": "chii",
        "default_x_base": "date",
        "default_log": True,
        "legend_title": "Rikishi",
    },
    notes=(
        Note(id="missing_equelo", applies_to=("all",), text="Some obscure pre-1989 lower-division chii are outside the Equelo bout-data rating domain; Equelo traces omit points without a rating."),
    )
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
        TableColumn(id="rating", heading="Equelo", source_field="rating", sort_kind="none", align="right"),
    ),
    notes=(
        Note(id="typical_equelo_values", applies_to=("all",), text="Equelo Ratings are typical rating landmarks, not promises about every rikishi at a rank. Sideless labels such as M3 use the average of the east and west rank slots."),
        Note(id="jd100", applies_to=("all",), text="Below Jd100 the support is low and Jonokuchi has too much churn for Elo-like ratings such as Equelo to produce stable public landmarks."),
    ),
)

WIN_PROBABILITY_BY_STANDING_ARTIFACT = ChartArtifact(
    id="win_probability_by_standing", heading="Win Probability by Ranks", kind="chart", renderer="standing_win_probability_chart",
    data_binding=DataBinding(kind="selected_csv", sources=("observed", "equelo")),
    data_sources=(
        DataSource(id="observed", label="Observed", path="ratings-models/observed-vs-modelled/win-probability-by-standing/data/observed_trace_points.csv", media_type="text/csv"),
        DataSource(id="equelo", label="Predicted", path="ratings-models/observed-vs-modelled/win-probability-by-standing/data/equelo_trace_points.csv", media_type="text/csv"),
    ),
    traces=(ChartTrace(id="standing_trace", label="Rank", kind="scatter", x="opponent_chii", y="p_selected_wins", group_by="selected_chii", error_y=("ci95_lower", "ci95_upper")),),
    x_axis=ChartAxis(id="x", source_field="opponent_chii", label="Opponent Rank"),
    y_axis=ChartAxis(id="y", source_field="p_selected_wins", label="P(selected rikishi wins)", minimum=0, maximum=1, tickformat=".0%"),
    provenance={"default_display_trace": "Y1", "sanyaku_display": ("Y1", "O1", "S1", "K1"), "x_order_field": "opponent_ordinal", "selected_order_field": "selected_ordinal", "legend_title": "Selected Rank"},
)

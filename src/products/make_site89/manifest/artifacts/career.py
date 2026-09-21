"""Career lifecycle, career records, and rank-history artifact declarations."""

from ...artifact_model import (
    ChartArtifact,
    ChartAxis,
    ChartTrace,
    DataBinding,
    DataSource,
    Note,
    TableArtifact,
    TableColumn,
)


DIVISION_STABILITY_ARTIFACT = ChartArtifact(
    id="division_stability", heading="Division Persistence", kind="chart", renderer="grouped_line_chart",
    data_binding=DataBinding(kind="csv", sources=("persistence",)),
    data_sources=(DataSource(id="persistence", label="Division persistence", path="banzuke-rank/division-stability/data/persistence.csv", media_type="text/csv"),),
    traces=(ChartTrace(id="mean_persistence", label="Mean persistence", kind="scatter", x="date", y="mean_persistence", group_by="division"),),
    x_axis=ChartAxis(id="x", source_field="date", label="Basho"),
    y_axis=ChartAxis(id="y", source_field="mean_persistence", label="Mean persistence", minimum=0, maximum=1, tickformat=".0%"),
    provenance={"subheading": "How consistently each basho's division members stayed in the same division across that basho and the previous 10.", "legend_title": "Division", "default_visible": ("Makuuchi",), "group_order": ("Makuuchi", "Juryo", "Makushita", "Sandanme", "Jonidan", "Jonokuchi"), "hover_fields": ("num_basho", "frequency", "stdev_persistence"), "nticks": 20, "x_tickangle": "auto"},
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
    data_binding=DataBinding(kind="csv_set", sources=("distribution", "pmf", "cdf", "survival")),
    data_sources=(
        DataSource(id="distribution", label="Distribution", path="sumo-history/career-lifecycle/career-length/data/distribution.csv", media_type="text/csv"),
        DataSource(id="pmf", label="PMF", path="sumo-history/career-lifecycle/career-length/data/pmf.csv", media_type="text/csv"),
        DataSource(id="cdf", label="CDF", path="sumo-history/career-lifecycle/career-length/data/cdf.csv", media_type="text/csv"),
        DataSource(id="survival", label="Survival", path="sumo-history/career-lifecycle/career-length/data/survival.csv", media_type="text/csv"),
    ),
    provenance={"views": {
        "distribution": {"kind": "stacked_bar", "label": "Distribution", "x": "nearest_years", "y": ("retired_count", "active_count"), "series_labels": ("Retired", "Active"), "x_label": "Nearest integer years", "y_label": "Rikishi count"},
        "pmf": {"kind": "line", "label": "PMF", "x": "nearest_years", "y": "probability", "x_label": "Nearest integer years", "y_label": "Probability", "tickformat": ".0%"},
        "cdf": {"kind": "line", "label": "CDF", "x": "nearest_years", "y": "cumulative_probability", "x_label": "Nearest integer years", "y_label": "Cumulative probability", "tickformat": ".0%"},
        "survival": {"kind": "line", "label": "Survival", "x": "nearest_years", "y": "survival_probability", "x_label": "Nearest integer years", "y_label": "Survival probability", "tickformat": ".0%"},
    }},
)

LONGEST_CAREERS_ARTIFACT = TableArtifact(
    id="longest_careers", heading="Longest Careers", kind="table", renderer="generic_table",
    rows_source=DataSource(id="longest", label="Longest careers", path="sumo-history/records/longest-careers/data/longest.csv", media_type="text/csv"),
    columns=(
        TableColumn(id="row_number", heading="", sort_kind="none", align="right"),
        TableColumn(id="rank", heading="#", source_field="rank", sort_key="rank", sort_kind="numeric", sort_default_direction="ascending", align="right"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", sort_kind="text", align="left"),
        TableColumn(id="first_appearance", heading="First", source_field="first_appearance", sort_kind="text", align="left"),
        TableColumn(id="last_appearance", heading="Last", source_field="last_appearance", sort_kind="text", align="left"),
        TableColumn(id="participation_years", heading="Years", source_field="participation_years", help="See Notes", sort_kind="numeric", align="right", note_id="observed_career_length"),
        TableColumn(id="gap_basho_count", heading="Bg", source_field="gap_basho_count", help="See Notes", sort_kind="numeric", align="right", note_id="bg_count"),
    ),
    default_sort_column="rank",
    notes=(
        Note(id="observed_career_length", applies_to=("all",), text="Years is the observed career length: the elapsed time between the first and last banzuke appearances in the prepared history."),
        Note(id="bg_count", applies_to=("all",), text="Bg is the number of basho for which the rikishi was absent."),
    ),
)

FASTEST_RISERS_ARTIFACT = TableArtifact(
    id="fastest_risers",
    heading="Fastest Risers",
    kind="table",
    renderer="fastest_risers_table",
    rows_source=DataSource(
        id="rankings",
        label="Fastest and slowest progression rankings",
        path="sumo-history/records/fastest-risers/data/rankings.json",
        media_type="application/json",
    ),
    columns=(
        TableColumn(id="position", heading="#", source_field="position", sort_kind="numeric", sort_default_direction="ascending", align="right"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", sort_kind="text", align="left"),
        TableColumn(id="start_chii", heading="Chii", source_field="start_chii", sort_key="start_chii_ordinal", sort_kind="chii_ordinal", align="left"),
        TableColumn(id="start_date", heading="Basho", source_field="start_date", sort_kind="text", align="left"),
        TableColumn(id="finish_chii", heading="Chii", source_field="finish_chii", sort_key="finish_chii_ordinal", sort_kind="chii_ordinal", align="left"),
        TableColumn(id="finish_date", heading="Basho", source_field="finish_date", sort_kind="text", align="left"),
        TableColumn(id="elapsed_basho", heading="Elapsed Basho", source_field="elapsed_basho", sort_kind="numeric", align="right", note_id="fastest_elapsed"),
    ),
    default_sort_column="position",
    notes=(
        Note(id="fastest_elapsed", applies_to=("all",), text="Elapsed Basho is the difference between the represented banzuke ordinals of the first destination appearance and the starting appearance. The starting basho is not counted; the immediately following represented banzuke is one basho later."),
        Note(id="fastest_cohort", applies_to=("all",), text="A rikishi's starting cohort is the rank group of his first appearance after the supporting boundary. Exact starting rank is retained but does not create a separate cohort."),
        Note(id="fastest_scope", applies_to=("all",), text="This proof of concept uses 1989/01 as supporting boundary data, excludes rikishi already present there, and admits first appearances from 1989/03. This is a temporary make_site89 production constraint, not a ratings requirement."),
        Note(id="fastest_groups", applies_to=("all",), text="M means Maegashira only. KS is the first appearance at either Komusubi or Sekiwake. Exact chii and annotations remain visible in the table."),
        Note(id="fastest_ties", applies_to=("all",), text="Equal elapsed values receive consecutive positions using the producer's deterministic secondary ordering; positions are not shared."),
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
        TableColumn(id="start", heading="Start", source_field="start", help="year-month-day of basho", sort_kind="text", align="left"),
        TableColumn(id="end", heading="End", source_field="end", help="year-month-day of basho", sort_kind="text", align="left"),
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
        TableColumn(id="start", heading="Start", source_field="start", help="year-month-day of basho", sort_kind="text", align="left"),
        TableColumn(id="end", heading="End", source_field="end", help="year-month-day of basho", sort_kind="text", align="left"),
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
        TableColumn(id="start", heading="Start", source_field="start", help="year-month-day of basho", sort_kind="text", align="left"),
        TableColumn(id="end", heading="End", source_field="end", help="year-month-day of basho", sort_kind="text", align="left"),
    ),
    default_sort_column="position",
)

HIGHEST_RATING_ARTIFACT = TableArtifact(
    id="highest_rating", heading="Highest Elo-89", kind="table", renderer="generic_table",
    rows_source=DataSource(id="highest_rating", label="Highest Elo-89", path="sumo-history/records/highest-rating/data/highest_rating.csv", media_type="text/csv"),
    columns=(
        TableColumn(id="row_number", heading="", sort_kind="none", align="right"),
        TableColumn(id="position", heading="#", source_field="position", sort_key="position", sort_kind="numeric", sort_default_direction="ascending", align="right"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", sort_kind="text", align="left"),
        TableColumn(id="chii", heading="Chii", source_field="chii", sort_key="chii_ordinal", sort_kind="chii_ordinal", align="left"),
        TableColumn(id="rating", heading="Elo-89", source_field="rating", sort_kind="numeric", align="right"),
        TableColumn(id="date", heading="Date", source_field="date", help="year-month-day of basho", sort_kind="text", align="left"),
    ),
    default_sort_column="position",
)

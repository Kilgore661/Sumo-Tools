"""Concrete chart and multi-view PA manifest instances."""

from __future__ import annotations

from .chart_pa import AxisSpec, ChartPA, EssayPA, ExcludedPA, MultiViewItem, MultiViewPA, TraceSpec
from .table_pa import DataSource, Note, Option, OptionValue, SortSpec, TableColumn, TablePA


rank_at_retirement = ChartPA(
    id="rank_at_retirement",
    heading="Rank at Retirement",
    renderer="rank_group_bar_chart",
    primary_source="distribution",
    data_sources=(
        DataSource(
            id="distribution",
            label="Distribution",
            path="data/distribution.csv",
            media_type="text/csv",
        ),
    ),
    traces=(
        TraceSpec(
            id="retired_rikishi",
            label="Retired rikishi",
            kind="bar",
            x="rank_group",
            y="count",
        ),
    ),
    x_axis=AxisSpec(
        id="x",
        source_field="rank_group",
        label="Final observed rank group",
        order_values=("Y", "O", "S", "K", "M", "J", "Ms", "Sd", "Jd", "Jk"),
    ),
    y_axis=AxisSpec(
        id="y",
        source_field="count",
        label="Retired rikishi count",
        minimum=0,
    ),
    notes=(
        Note(
            id="rank_at_retirement",
            placement="below_chart",
            format="html",
            text=(
                "<strong>Rank at Retirement.</strong> This is the final observed "
                "banzuke rank group for retired rikishi according to "
                '<a href="https://sumodb.sumogames.de/">SumoDB</a>-derived '
                "banzuke history. Rikishi listed on the latest available "
                "banzuke are treated as active and excluded."
            ),
        ),
    ),
)


win_probability_by_standing = ChartPA(
    id="win_probability_by_standing",
    heading="Win Probability by Standing",
    renderer="standing_win_probability_chart",
    options=(
        Option(
            id="source",
            label="Source",
            kind="enum",
            control="select",
            default="observed",
            url_key="source",
            values=(
                OptionValue(value="observed", label="Observed"),
                OptionValue(value="equelo", label="Equelo"),
            ),
        ),
        Option(
            id="division",
            label="Division",
            kind="enum",
            control="select",
            default="Makuuchi",
            url_key="division",
            values=(
                OptionValue(value="Makuuchi", label="Makuuchi"),
                OptionValue(value="Juryo", label="Juryo"),
                OptionValue(value="Makushita", label="Makushita"),
                OptionValue(value="Sandanme", label="Sandanme"),
                OptionValue(value="Jonidan", label="Jonidan"),
                OptionValue(value="Jonokuchi", label="Jonokuchi"),
                OptionValue(value="All", label="All"),
            ),
        ),
        Option(
            id="error_bars",
            label="Error bars",
            kind="boolean",
            control="checkbox",
            default=True,
            url_key="error_bars",
        ),
    ),
    data_sources=(
        DataSource(
            id="observed",
            label="Observed",
            path="data/observed_trace_points.csv",
            media_type="text/csv",
            option_id="source",
            option_value="observed",
        ),
        DataSource(
            id="equelo",
            label="Equelo",
            path="data/equelo_trace_points.csv",
            media_type="text/csv",
            option_id="source",
            option_value="equelo",
        ),
    ),
    traces=(
        TraceSpec(
            id="standing_trace",
            label="Standing",
            kind="scatter",
            x="opponent_chii",
            y="p_selected_wins",
            group_by="selected_chii",
            error_y=("ci95_lower", "ci95_upper"),
        ),
    ),
    x_axis=AxisSpec(
        id="x",
        source_field="opponent_chii",
        order_field="opponent_ordinal",
    ),
    y_axis=AxisSpec(
        id="y",
        source_field="p_selected_wins",
        label="P(selected standing wins)",
        minimum=0,
        maximum=1,
        tickformat=".0%",
    ),
    default_trace="standing_trace",
    consumes_options=("source", "division", "error_bars"),
    provenance={
        "default_display_trace": "Y1",
        "sanyaku_display": ("Y1", "O1", "S1", "K1"),
    },
)


career_length_distribution = ChartPA(
    id="career_length_distribution",
    heading="Distribution",
    renderer="career_length_distribution_chart",
    primary_source="distribution",
    data_sources=(
        DataSource(id="distribution", path="data/distribution.csv", media_type="text/csv"),
    ),
    traces=(
        TraceSpec(
            id="retired",
            label="Retired",
            kind="stacked_bar",
            x="nearest_years",
            y="retired_count",
        ),
        TraceSpec(
            id="active",
            label="Active",
            kind="stacked_bar",
            x="nearest_years",
            y="active_count",
        ),
    ),
    x_axis=AxisSpec(id="x", source_field="nearest_years", label="Nearest integer years", minimum=0),
    y_axis=AxisSpec(id="y", label="Rikishi count", minimum=0),
)


career_length_pmf = ChartPA(
    id="career_length_pmf",
    heading="PMF",
    renderer="career_length_line_chart",
    primary_source="pmf",
    data_sources=(DataSource(id="pmf", path="data/pmf.csv", media_type="text/csv"),),
    traces=(
        TraceSpec(id="pmf", label="PMF", kind="line", x="nearest_years", y="probability"),
    ),
    x_axis=AxisSpec(id="x", source_field="nearest_years", label="Nearest integer years", minimum=0),
    y_axis=AxisSpec(id="y", source_field="probability", label="Probability", minimum=0),
)


career_length_cdf = ChartPA(
    id="career_length_cdf",
    heading="CDF",
    renderer="career_length_line_chart",
    primary_source="cdf",
    data_sources=(DataSource(id="cdf", path="data/cdf.csv", media_type="text/csv"),),
    traces=(
        TraceSpec(id="cdf", label="CDF", kind="line", x="nearest_years", y="probability"),
    ),
    x_axis=AxisSpec(id="x", source_field="nearest_years", label="Nearest integer years", minimum=0),
    y_axis=AxisSpec(id="y", source_field="probability", label="Cumulative probability", minimum=0),
)


career_length_survival = ChartPA(
    id="career_length_survival",
    heading="Survival",
    renderer="career_length_line_chart",
    primary_source="survival",
    data_sources=(DataSource(id="survival", path="data/survival.csv", media_type="text/csv"),),
    traces=(
        TraceSpec(id="survival", label="Survival", kind="line", x="nearest_years", y="probability"),
    ),
    x_axis=AxisSpec(id="x", source_field="nearest_years", label="Nearest integer years", minimum=0),
    y_axis=AxisSpec(id="y", source_field="probability", label="Survival probability", minimum=0),
)


career_length_longest = TablePA(
    id="career_length_longest",
    heading="Longest",
    renderer="career_length_longest_table",
    primary_source="longest",
    data_sources=(DataSource(id="longest", path="data/longest.csv", media_type="text/csv"),),
    columns=(
        TableColumn(id="rank", heading="#", source_field="rank", sortable=False, align="right"),
        TableColumn(id="shikona", heading="Shikona", source_field="shikona", link="rikishi"),
        TableColumn(id="first_basho", heading="First Basho", source_field="first_basho"),
        TableColumn(id="last_basho", heading="Last Basho", source_field="last_basho"),
        TableColumn(
            id="nearest_years",
            heading="Years",
            source_field="nearest_years",
            sort_kind="numeric",
            align="right",
        ),
        TableColumn(
            id="missing_basho",
            heading="Bg",
            source_field="missing_basho",
            sort_kind="numeric",
            align="right",
            note="bg_count",
        ),
    ),
    default_sort=SortSpec(column="nearest_years", descending=True),
    notes=(
        Note(
            id="bg_count",
            placement="below_table",
            format="html",
            text="<strong>Bg.</strong> The number of basho for which the rikishi was absent.",
        ),
    ),
)


career_length = MultiViewPA(
    id="career_length",
    heading="Career Length",
    view_option=Option(
        id="view",
        label="View",
        kind="enum",
        control="radio_group",
        default="distribution",
        url_key="view",
        values=(
            OptionValue(value="distribution", label="Distribution"),
            OptionValue(value="pmf", label="PMF"),
            OptionValue(value="cdf", label="CDF"),
            OptionValue(value="survival", label="Survival"),
            OptionValue(value="longest", label="Longest"),
        ),
    ),
    views=(
        MultiViewItem(id="distribution", label="Distribution", pa=career_length_distribution),
        MultiViewItem(id="pmf", label="PMF", pa=career_length_pmf),
        MultiViewItem(id="cdf", label="CDF", pa=career_length_cdf),
        MultiViewItem(id="survival", label="Survival", pa=career_length_survival),
        MultiViewItem(id="longest", label="Longest", pa=career_length_longest),
    ),
    notes=(
        Note(
            id="observed_career_length",
            placement="below_chart",
            format="html",
            text=(
                "<strong>Years.</strong> This is the observed Career Length; "
                "i.e. the difference in years between the first and last basho "
                "dates in which the rikishi appeared on the banzuke."
            ),
        ),
        Note(
            id="bg_count",
            placement="below_chart",
            applies_to=("longest",),
            format="html",
            text="<strong>Bg.</strong> The number of basho for which the rikishi was absent.",
        ),
    ),
)


v5_landmark_policy = EssayPA(
    id="v5_landmark_policy",
    heading="V5 Landmark Policy",
    body_html="<p>Placeholder for the v5 rating landmark policy.</p>",
)


lower_rank_rating_stability = EssayPA(
    id="lower_rank_rating_stability",
    heading="Lower-Rank Rating Stability",
    body_html="<p>Placeholder for lower-rank Equelo stability notes.</p>",
)


finish_by_chii = ExcludedPA(
    id="finish_by_chii",
    heading="Finish by Chii",
    previous_view_kind="StandaloneHtmlView",
    reason="Static HTML is outside the target PA architecture until migrated.",
)


banzuke_division_by_era = ExcludedPA(
    id="banzuke_division_by_era",
    heading="Banzuke Division by Era",
    previous_view_kind="StandaloneHtmlView",
    reason="Static HTML is outside the target PA architecture until migrated.",
)


makuuchi_rank_by_era = ExcludedPA(
    id="makuuchi_rank_by_era",
    heading="Makuuchi Rank by Era",
    previous_view_kind="StandaloneHtmlView",
    reason="Static HTML is outside the target PA architecture until migrated.",
)


division_stability = ChartPA(
    id="division_stability",
    heading="Division Stability",
    renderer="division_stability_chart",
    primary_source="persistence",
    data_sources=(
        DataSource(
            id="persistence",
            label="Division persistence",
            path="data/persistence.csv",
            media_type="text/csv",
        ),
    ),
    traces=(
        TraceSpec(
            id="mean_persistence",
            label="Mean persistence",
            kind="scatter",
            x="date",
            y="mean_persistence",
            group_by="division",
        ),
    ),
    x_axis=AxisSpec(
        id="x",
        source_field="date",
        label="Basho",
    ),
    y_axis=AxisSpec(
        id="y",
        source_field="mean_persistence",
        label="Mean persistence",
        minimum=0,
        maximum=1,
        tickformat=".0%",
    ),
    default_trace="mean_persistence",
    provenance={
        "default_visible": ("Makuuchi",),
        "group_field": "division",
        "hover_fields": ("num_basho", "frequency", "stdev_persistence"),
        "x_tickangle": -45,
    },
)


for pa in (
    rank_at_retirement,
    win_probability_by_standing,
    career_length,
    v5_landmark_policy,
    lower_rank_rating_stability,
    finish_by_chii,
    banzuke_division_by_era,
    makuuchi_rank_by_era,
    division_stability,
):
    pa.validate()

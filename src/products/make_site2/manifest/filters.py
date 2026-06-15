"""Declared reader-visible Filters used by current Published Artifacts."""

from __future__ import annotations

from ..ui_model import Filter, FilterValue, FilterValuesSource


DIVISION_FILTER_VALUES = (
    FilterValue(value="makuuchi", label="Makuuchi"),
    FilterValue(value="juryo", label="Juryo"),
    FilterValue(value="makushita", label="Makushita"),
    FilterValue(value="sandanme", label="Sandanme"),
    FilterValue(value="jonidan", label="Jonidan"),
    FilterValue(value="jonokuchi", label="Jonokuchi"),
)

STANDINGS_DIVISION_FILTER_VALUES = (
    FilterValue(value="all", label="All"),
    *DIVISION_FILTER_VALUES,
)

STANDINGS_WINDOW_VALUES = tuple(
    FilterValue(value=str(value), label=str(value))
    for value in (1, 2, 3, 4, 5, 6, 12, 18, 24, 36, 60)
)

BRB_FILTERS = (
    Filter(id="basho_year", label="Year", control="select", default="latest", url_key="year"),
    Filter(id="basho_month", label="Month", control="select", default="latest", url_key="month"),
    Filter(
        id="division",
        label="Division",
        control="select",
        default="makuuchi",
        url_key="division",
        values=DIVISION_FILTER_VALUES,
    ),
    Filter(id="previous_context", label="Previous Basho", control="checkbox", default=False, url_key="previous"),
    Filter(id="changes_context", label="Next Basho", control="checkbox", default=True, url_key="changes"),
    Filter(id="rating_context", label="Equelo Ratings", control="checkbox", default=False, url_key="ratings"),
    Filter(id="analysis_context", label="Ratings Fit", control="checkbox", default=False, url_key="analysis", help="See TBD"),
    Filter(id="nu_chii", label="nuChii", control="checkbox", default=False, url_key="nu_chii"),
)

STANDINGS_FILTERS = (
    Filter(
        id="metric_group_preset",
        label="View",
        control="select",
        default="standard",
        url_key="view",
        values=(
            FilterValue(value="standard", label="Wins per Basho"),
            FilterValue(value="percentages", label="Wins per Bout"),
            FilterValue(value="combined", label="Both"),
        ),
    ),
    Filter(
        id="current_num_basho",
        label="Number of Basho",
        control="select",
        default="6",
        url_key="num_basho",
        values=STANDINGS_WINDOW_VALUES,
    ),
    Filter(
        id="current_only",
        label="Active Rikishi Only",
        control="checkbox",
        default=True,
        url_key="current_only",
        help="When off, longer windows may include retired rikishi.",
    ),
    Filter(
        id="division",
        label="Division",
        control="select",
        default="makuuchi",
        url_key="division",
        values=STANDINGS_DIVISION_FILTER_VALUES,
    ),
)

BANZUKE_CHANGES_FILTERS = (
    Filter(
        id="division",
        label="Division",
        control="select",
        default="makuuchi",
        url_key="division",
        values=DIVISION_FILTER_VALUES,
    ),
    Filter(id="context", label="Previous Basho", control="checkbox", default=False, url_key="context"),
    Filter(id="banzuke_style", label="Banzuke Style", control="checkbox", default=True, url_key="banzuke_style"),
    Filter(id="delta", label="Delta", control="checkbox", default=False, url_key="delta", help="Size of movement. See Notes."),
    Filter(
        id="equelo",
        label="Equelo Ratings",
        control="checkbox",
        default=False,
        url_key="equelo",
        help="Model ratings. See Ratings & Models.",
    ),
)

FINISH_BY_CHII_FILTERS = (
    Filter(
        id="division",
        label="Division",
        control="select",
        default="makuuchi",
        url_key="division",
        values=(
            FilterValue(value="makuuchi", label="Makuuchi"),
            FilterValue(value="juryo", label="Juryo"),
        ),
    ),
    Filter(
        id="direction",
        label="Direction",
        control="select",
        default="top",
        url_key="direction",
        values=(
            FilterValue(value="top", label="Top"),
            FilterValue(value="bottom", label="Bottom"),
        ),
    ),
    Filter(
        id="chii",
        label="Chii",
        control="select",
        default="Y1e",
        url_key="chii",
        values_source=FilterValuesSource(
            source="top_thresholds",
            field="chii",
            label_field="chii",
            order_field="chii_ordinal",
            partition_filter="division",
            partition_field="division",
            partition_normalizer="division_id",
        ),
    ),
)

CAREER_LENGTH_FILTERS = (
    Filter(
        id="view",
        label="View",
        control="select",
        default="distribution",
        url_key="view",
        values=(
            FilterValue(value="distribution", label="Distribution"),
            FilterValue(value="pmf", label="PMF"),
            FilterValue(value="cdf", label="CDF"),
            FilterValue(value="survival", label="Survival"),
            FilterValue(value="longest", label="Longest"),
        ),
    ),
)

MOST_CONSECUTIVE_BOUTS_FILTERS = (
    Filter(
        id="clean_only",
        label="Clean only?",
        control="checkbox",
        default=False,
        url_key="clean_only",
    ),
)

MOST_CAREER_WINS_FILTERS = (
    Filter(
        id="include_retired",
        label="Include retired?",
        control="checkbox",
        default=True,
        url_key="include_retired",
    ),
    Filter(
        id="count_fusen_results",
        label="Count fusen results?",
        control="checkbox",
        default=True,
        url_key="count_fusen",
    ),
)

MOST_CAREER_LOSSES_FILTERS = (
    Filter(
        id="include_retired",
        label="Include retired?",
        control="checkbox",
        default=True,
        url_key="include_retired",
    ),
    Filter(
        id="count_fusen_results",
        label="Count fusen results?",
        control="checkbox",
        default=True,
        url_key="count_fusen",
    ),
)

CAREER_COMPARISONS_FILTERS = (
    Filter(
        id="skill",
        label="Skill",
        control="select",
        default="chii",
        url_key="skill",
        values=(
            FilterValue(value="chii", label="Chii", help="Show chii achieved."),
            FilterValue(value="equelo", label="Equelo", help="Show rating achieved."),
            FilterValue(value="both", label="Both", help="Show chii and rating together."),
        ),
    ),
    Filter(
        id="x_base",
        label="X",
        control="select",
        default="date",
        url_key="x",
        values=(
            FilterValue(value="date", label="Date", help="Use calendar date on the x-axis."),
            FilterValue(value="basho", label="Hatsu", help="Use basho since first appearance on the x-axis."),
        ),
    ),
    Filter(id="log", label="Compress", control="checkbox", default=True, url_key="log", help="Compress lower banzuke divisions."),
)

WIN_PROBABILITY_BY_STANDING_FILTERS = (
    Filter(
        id="source",
        label="Source",
        control="select",
        default="observed",
        url_key="source",
        values=(
            FilterValue(value="observed", label="Observed"),
            FilterValue(value="equelo", label="Predicted", help="Prediction based on Equelo rating."),
        ),
    ),
    Filter(
        id="division",
        label="Division",
        control="select",
        default="Makuuchi",
        url_key="division",
        values=(
            FilterValue(value="Makuuchi", label="Makuuchi"),
            FilterValue(value="Juryo", label="Juryo"),
            FilterValue(value="Makushita", label="Makushita"),
            FilterValue(value="Sandanme", label="Sandanme"),
            FilterValue(value="Jonidan", label="Jonidan"),
            FilterValue(value="Jonokuchi", label="Jonokuchi"),
            FilterValue(value="All", label="All"),
        ),
    ),
)

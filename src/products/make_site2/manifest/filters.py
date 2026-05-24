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
    Filter(id="basho_date", label="Basho", control="select", default="latest", url_key="basho"),
    Filter(
        id="division",
        label="Division",
        control="select",
        default="makuuchi",
        url_key="division",
        values=DIVISION_FILTER_VALUES,
    ),
    Filter(id="previous_context", label="Previous Basho", control="checkbox", default=False, url_key="previous"),
    Filter(id="rating_context", label="Equelo Ratings", control="checkbox", default=False, url_key="ratings"),
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
            FilterValue(value="combined", label="Combined"),
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
    Filter(id="current_only", label="Active Rikishi Only", control="checkbox", default=True, url_key="current_only"),
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
    Filter(id="delta", label="Delta", control="checkbox", default=False, url_key="delta"),
    Filter(id="equelo", label="Equelo Ratings", control="checkbox", default=False, url_key="equelo"),
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

WIN_PROBABILITY_BY_STANDING_FILTERS = (
    Filter(
        id="source",
        label="Source",
        control="select",
        default="observed",
        url_key="source",
        values=(
            FilterValue(value="observed", label="Observed"),
            FilterValue(value="equelo", label="Equelo"),
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
    Filter(id="error_bars", label="Error bars", control="checkbox", default=True, url_key="error_bars"),
)

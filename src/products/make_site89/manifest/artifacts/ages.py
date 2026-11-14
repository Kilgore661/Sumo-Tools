"""Age-analysis artifact declarations."""

from ...artifact_model import ChartArtifact, ChartAxis, ChartTrace, DataBinding, DataSource, Note


AVERAGE_AGE_BY_DIVISION_ARTIFACT = ChartArtifact(
    id="average_age_by_division",
    heading="Average Age by Division",
    kind="chart",
    renderer="grouped_line_chart",
    data_binding=DataBinding(kind="csv", sources=("average_ages",)),
    data_sources=(
        DataSource(
            id="average_ages",
            label="Average ages",
            path="age/average-age-by-division/data/average_age_by_division.csv",
            media_type="text/csv",
        ),
    ),
    traces=(
        ChartTrace(
            id="mean_age",
            label="Mean age",
            kind="scatter",
            x="basho",
            y="mean_age_years",
            group_by="division",
            error_y=("min_age_years", "max_age_years"),
        ),
    ),
    x_axis=ChartAxis(id="x", source_field="basho", label="Basho"),
    y_axis=ChartAxis(id="y", source_field="mean_age_years", label="Age (years)"),
    provenance={
        "subheading": "Mean age on exact Day 1 of each basho; optional bars show the observed youngest-to-oldest range.",
        "legend_title": "Division",
        "default_visible": ("Makuuchi",),
        "group_order": ("Makuuchi", "Juryo", "Makushita", "Sandanme", "Jonidan", "Jonokuchi"),
        "hover_fields": (
            "start_date",
            "min_age_years",
            "max_age_years",
            "exact_birth_date",
            "banzuke_rikishi",
            "missing_exact_birth_date",
        ),
        "hover_template": (
            "Division=%{fullData.name}<br>"
            "Basho=%{x}<br>"
            "Day 1=%{customdata[0]}<br>"
            "Mean age=%{y:.2f}<br>"
            "Youngest=%{customdata[1]:.2f}<br>"
            "Oldest=%{customdata[2]:.2f}<br>"
            "Exact birth dates=%{customdata[3]:,} / %{customdata[4]:,}<br>"
            "Missing exact birth dates=%{customdata[5]:,}<extra></extra>"
        ),
        "nticks": 20,
        "x_tickangle": "auto",
        "error_bar_label": "Observed range",
    },
    notes=(
        Note(id="average_age_population", applies_to=("all",), text="The mean, youngest and oldest ages include only rikishi with exact birth dates. Contributor and missing-date counts are shown in the hover text; missing birth dates may vary systematically by period or division."),
        Note(id="average_age_range", applies_to=("all",), text="Min & Max shows the observed youngest-to-oldest range, not uncertainty around the mean."),
        Note(id="average_age_day_one", applies_to=("all",), text="Age is continuous age in years on the exact civil date of Day 1. Maezumo is excluded because it is not a formal banzuke division."),
    ),
)

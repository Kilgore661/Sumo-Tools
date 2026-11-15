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
        Note(id="average_age_jonokuchi_may", applies_to=("all",), text="The saw-toothed nature of the Jonokuchi trace is due to the influx of newcomers each May."),
    ),
)


PROSPECTS_ARTIFACT = ChartArtifact(
    id="prospects",
    heading="San'yaku Prospects",
    kind="chart",
    renderer="prospects",
    data_binding=DataBinding(kind="json", sources=("trajectory_master",)),
    data_sources=(
        DataSource(
            id="trajectory_master",
            label="Prospect trajectories",
            path="age/prospects/data/trajectory_master.json",
            media_type="application/json",
        ),
    ),
    provenance={"default_x": "age", "legend_title": "Rikishi"},
    notes=(
        Note(id="prospects_meaning", applies_to=("all",), text="Each ordinary point is the historical proportion of resolved rikishi who eventually reached san'yaku, matched by division, rank number and completed age. It is not a personalised forecast of ability."),
        Note(id="prospects_support", applies_to=("all",), text="Marker colour describes unique resolved-rikishi support: green 20 or more, amber 10–19, and red 1–9. Unresolved careers remain in audit counts but not the displayed proportion."),
        Note(id="prospects_endpoint", applies_to=("all",), text="The gold star marks first attainment of Komusubi, Sekiwake, Ozeki or Yokozuna. A career without san'yaku simply ends; no artificial zero is added."),
        Note(id="prospects_scope", applies_to=("all",), text="The calculation uses complete represented careers beginning after the January 1989 boundary and exact age on Day 1 of each basho."),
    ),
)

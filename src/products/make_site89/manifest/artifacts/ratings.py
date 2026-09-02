"""Rating, probability, and comparison artifact declarations for the public site."""

from ...artifact_model import (
    ChartArtifact,
    ChartAxis,
    ChartTrace,
    DataBinding,
    DataSource,
    Note,
    SectionedTableArtifact,
    TableColumn,
    TableSection,
)
from ...perf_chart.config import RATING_LOG_BASE, TOP_CHART_PROP


FINISH_BY_CHII_ARTIFACT = ChartArtifact(
    id="finish_by_chii", heading="Finish Chances by Wins", kind="chart", renderer="finish_by_chii_chart",
    data_binding=DataBinding(kind="csv_set", sources=("top_thresholds", "bottom_thresholds")),
    data_sources=(
        DataSource(id="top_thresholds", label="Top finish thresholds", path="performance/finish-by-chii/data/top_thresholds.csv", media_type="text/csv"),
        DataSource(id="bottom_thresholds", label="Bottom finish thresholds", path="performance/finish-by-chii/data/bottom_thresholds.csv", media_type="text/csv"),
    ),
)

CAREER_COMPARISONS_ARTIFACT = ChartArtifact(
    id="career_comparisons", heading="Rikishi History", kind="chart", renderer="career_comparisons",
    data_binding=DataBinding(kind="json", sources=("trajectory_master",)),
    data_sources=(
        DataSource(id="trajectory_master", label="Trajectory Master", path="rikishi/career-comparisons/data/trajectory_master.json", media_type="application/json"),
    ),
    provenance={
        "rating_log_base": RATING_LOG_BASE,
        "top_chart_prop": TOP_CHART_PROP,
        "default_skill": "chii",
        "default_x_base": "date",
        "default_log": True,
        "legend_title": "Rikishi",
    },
    notes=(),
)

TYPICAL_RATING_VALUES_ARTIFACT = SectionedTableArtifact(
    id="typical_rating_values", heading="Typical Elo-89 Ratings", kind="sectioned_table", renderer="sectioned_table", primary_source="typical_rating_values",
    data_sources=(DataSource(id="typical_rating_values", label="Typical Elo-89 Ratings", path="ratings-models/rating-and-rank/typical-rating-values/data/typical_rating_values.csv", media_type="text/csv"),),
    sections=(
        TableSection(id="sanyaku", heading="Sanyaku", source_field="table", source_value="Sanyaku", order_by="row_order"),
        TableSection(id="maegashira", heading="Maegashira", source_field="table", source_value="Maegashira", order_by="row_order"),
        TableSection(id="other", heading="Other", source_field="table", source_value="Other", order_by="row_order"),
    ),
    columns=(
        TableColumn(id="label", heading="Rank", source_field="label", sort_kind="none", align="left"),
        TableColumn(id="rating", heading="Elo-89", source_field="rating", sort_kind="none", align="right"),
    ),
    notes=(
        Note(id="typical_rating_values", applies_to=("all",), text="Elo-89 ratings are typical rating landmarks, not promises about every rikishi at a rank. Sideless labels such as M3 use the average of the east and west rank slots."),
        Note(id="jd100", applies_to=("all",), text="Below Jd100 the support is low and Jonokuchi has too much churn for Elo-like ratings such as Elo-89 to produce stable public landmarks."),
    ),
)

WIN_PROBABILITY_BY_STANDING_ARTIFACT = ChartArtifact(
    id="win_probability_by_standing", heading="Win Probability by Ranks", kind="chart", renderer="standing_win_probability_chart",
    data_binding=DataBinding(kind="selected_csv", sources=("observed", "rating")),
    data_sources=(
        DataSource(id="observed", label="Observed", path="ratings-models/observed-vs-modelled/win-probability-by-standing/data/observed_trace_points.csv", media_type="text/csv"),
        DataSource(id="rating", label="Predicted", path="ratings-models/observed-vs-modelled/win-probability-by-standing/data/rating_trace_points.csv", media_type="text/csv"),
    ),
    traces=(ChartTrace(id="standing_trace", label="Rank", kind="scatter", x="opponent_chii", y="p_selected_wins", group_by="selected_chii", error_y=("ci95_lower", "ci95_upper")),),
    x_axis=ChartAxis(id="x", source_field="opponent_chii", label="Opponent Rank"),
    y_axis=ChartAxis(id="y", source_field="p_selected_wins", label="P(selected rikishi wins)", minimum=0, maximum=1, tickformat=".0%"),
    provenance={"default_display_trace": "Y1", "sanyaku_display": ("Y1", "O1", "S1", "K1"), "x_order_field": "opponent_ordinal", "selected_order_field": "selected_ordinal", "legend_title": "Selected Rank"},
)

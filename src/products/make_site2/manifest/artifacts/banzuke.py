"""Banzuke and rank-structure artifact declarations for the public site."""

from ...artifact_model import (
    BanzukeChangesArtifact,
    ChartArtifact,
    ChartAxis,
    ChartTrace,
    DataBinding,
    DataSource,
    Note,
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
    provenance={"subheading": "Count of banzuke appearances at each Makuuchi rank.", "legend_title": "Era", "group_order": ("1958-1967", "1968-1977", "1978-1987", "1988-1997", "1998-2007", "2008-2017", "2018-2026"), "x_tickangle": "auto"},
)

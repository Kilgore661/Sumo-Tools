"""make_site2 semantic manifests assembled from site and artifact declarations."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from .artifact_model import (
    BanzukeChangesArtifact,
    ChartArtifact,
    ColumnGroup,
    DataBinding,
    DataSource,
    IndexedDataSource,
    IndexedTableArtifact,
    Note,
    TableColumn,
)
from .publication_model import NavigationItem, PublicationPlan
from .ui_model import (
    ContentPanel,
    Filter,
    FilterSection,
    FilterValuesSource,
    FilterValue,
    G1Contents,
    Heading,
    NavigationBar,
    NavigationCollapseControl,
    PA,
    PublicSiteShell,
)


DIVISION_FILTER_VALUES = (
    FilterValue(value="makuuchi", label="Makuuchi"),
    FilterValue(value="juryo", label="Juryo"),
    FilterValue(value="makushita", label="Makushita"),
    FilterValue(value="sandanme", label="Sandanme"),
    FilterValue(value="jonidan", label="Jonidan"),
    FilterValue(value="jonokuchi", label="Jonokuchi"),
)


BRB_FILTERS = (
    Filter(
        id="basho_date",
        label="Basho",
        control="basho_date_selector",
        default="latest",
        url_key="basho",
    ),
    Filter(
        id="division",
        label="Division",
        control="select",
        default="makuuchi",
        url_key="division",
        values=DIVISION_FILTER_VALUES,
    ),
    Filter(
        id="previous_context",
        label="Previous Basho",
        control="checkbox",
        default=False,
        url_key="previous",
    ),
    Filter(
        id="rating_context",
        label="Equelo Ratings",
        control="checkbox",
        default=False,
        url_key="ratings",
    ),
    Filter(
        id="nu_chii",
        label="nuChii",
        control="checkbox",
        default=False,
        url_key="nu_chii",
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
    Filter(
        id="context",
        label="Previous Basho",
        control="checkbox",
        default=False,
        url_key="context",
    ),
    Filter(
        id="banzuke_style",
        label="Banzuke Style",
        control="checkbox",
        default=True,
        url_key="banzuke_style",
    ),
    Filter(
        id="delta",
        label="Delta",
        control="checkbox",
        default=False,
        url_key="delta",
    ),
    Filter(
        id="equelo",
        label="Equelo Ratings",
        control="checkbox",
        default=False,
        url_key="equelo",
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
        control="data_selector",
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


BANZUKE_CHANGES_ARTIFACT = BanzukeChangesArtifact(
    id="banzuke_changes",
    heading="Banzuke Changes",
    kind="banzuke_changes",
    renderer="banzuke_changes_table",
    config_source=DataSource(
        id="site_config",
        label="Site Config",
        path="current-sumo/banzuke-changes/site_config.json",
        media_type="application/json",
    ),
    rows_source=DataSource(
        id="banzuke_change_report",
        label="Banzuke Change Report",
        path="current-sumo/banzuke-changes/data/banzuke_change_report.csv",
        media_type="text/csv",
    ),
    notes=(
        Note(
            id="note_result",
            applies_to=("context",),
            text=(
                "Result gives wins, losses and absences followed by prizes if "
                "any. A trailing up/down marker indicates promotion or demotion "
                "into the current broad rank level."
            ),
        ),
        Note(
            id="note_delta",
            applies_to=("delta",),
            text=(
                "Delta indicates the size of movement from the previous "
                "basho's position, measured in banzuke rows."
            ),
        ),
    ),
)


BASHO_RESULTS_ARTIFACT = IndexedTableArtifact(
    id="basho_results_browser",
    heading="Basho Results",
    kind="indexed_table",
    renderer="indexed_table",
    indexed_source=IndexedDataSource(
        id="basho_results",
        label="Basho Results",
        index_path="sumo-history/basho-results/data/basho_results_index.json",
        payload_path_field="payload_path",
        payload_media_type="text/csv",
    ),
    selector_filter_id="basho_date",
    column_groups=(
        ColumnGroup(
            id="identity",
            heading="",
            always_visible=True,
            columns=("row_number", "shikona", "chii"),
        ),
        ColumnGroup(
            id="previous_basho",
            heading="Previous Basho",
            controlling_filter_id="previous_context",
            columns=("previous_chii", "previous_result", "previous_delta_direction"),
        ),
        ColumnGroup(
            id="result_state",
            heading="After/During",
            always_visible=True,
            columns=("score", "equelo", "delta_equelo", "nu_chii"),
        ),
    ),
    columns=(
        TableColumn(
            id="row_number",
            heading="#",
            group="identity",
            always_visible=True,
            sort_kind="none",
            align="center",
        ),
        TableColumn(
            id="shikona",
            heading="Shikona",
            source_field="shikona",
            group="identity",
            always_visible=True,
            sort_kind="text",
            note_id="note_shikona",
        ),
        TableColumn(
            id="chii",
            heading="Chii",
            source_field="chii",
            group="identity",
            always_visible=True,
            sort_key="chii_ordinal",
            sort_kind="chii_ordinal",
            note_id="note_chii",
        ),
        TableColumn(
            id="previous_delta_direction",
            heading="Direction",
            source_field="previous_delta_direction",
            group="previous_basho",
            align="center",
            note_id="note_previous_direction",
        ),
        TableColumn(
            id="previous_result",
            heading="Result",
            source_field="previous_result",
            group="previous_basho",
            sort_kind="record",
            align="center",
            note_id="note_previous_result",
        ),
        TableColumn(
            id="previous_chii",
            heading="Chii",
            source_field="previous_chii",
            group="previous_basho",
            sort_key="previous_chii_ordinal",
            sort_kind="chii_ordinal",
            align="center",
        ),
        TableColumn(
            id="score",
            heading="Score",
            source_field="score",
            group="result_state",
            always_visible=True,
            sort_kind="record",
            align="center",
            note_id="note_score",
        ),
        TableColumn(
            id="equelo",
            heading="Equelo",
            source_field="equelo",
            group="result_state",
            sort_kind="numeric",
            align="center",
            note_id="note_equelo",
        ),
        TableColumn(
            id="delta_equelo",
            heading="Delta Equelo",
            source_field="delta_equelo",
            group="result_state",
            sort_kind="numeric",
            align="right",
            note_id="note_delta_equelo",
        ),
        TableColumn(
            id="nu_chii",
            heading="nuChii",
            source_field="nu_chii",
            group="result_state",
            sort_key="nu_chii_ordinal",
            sort_kind="chii_ordinal",
            note_id="note_nu_chii",
        ),
    ),
    default_sort_column="chii",
    notes=(
        Note(
            id="note_shikona",
            applies_to=("all",),
            text="Shikona is the name used by the rikishi for the selected basho.",
        ),
        Note(
            id="note_chii",
            applies_to=("all",),
            text="Chii is the official rank slot at the start of the selected basho.",
        ),
        Note(
            id="note_previous_direction",
            applies_to=("previous_basho",),
            text="Direction indicates a better or worse position than in the previous basho.",
        ),
        Note(
            id="note_score",
            applies_to=("all",),
            text=(
                "Score gives wins, losses and absences for the selected basho. "
                "For an in-progress basho it is the score through the latest "
                "published day."
            ),
        ),
        Note(
            id="note_equelo",
            applies_to=("rating_context",),
            text="Equelo is the fixed_v2 process rating at the represented point.",
        ),
        Note(
            id="note_delta_equelo",
            applies_to=("rating_context",),
            text=(
                "Delta Equelo is the rating change from the start of the "
                "selected basho."
            ),
        ),
        Note(
            id="note_nu_chii",
            applies_to=("nu_chii",),
            text=(
                "nuChii is the after/during chii value for the selected state. "
                "It may be actual, estimated, or unavailable depending on what "
                "is known when the page data is produced."
            ),
        ),
    ),
)


FINISH_BY_CHII_ARTIFACT = ChartArtifact(
    id="finish_by_chii",
    heading="Finish by Chii",
    kind="chart",
    renderer="finish_by_chii_chart",
    data_binding=DataBinding(
        kind="csv_set",
        sources=("top_thresholds", "bottom_thresholds"),
    ),
    data_sources=(
        DataSource(
            id="top_thresholds",
            label="Top finish thresholds",
            path="performance/finish-by-chii/data/top_thresholds.csv",
            media_type="text/csv",
        ),
        DataSource(
            id="bottom_thresholds",
            label="Bottom finish thresholds",
            path="performance/finish-by-chii/data/bottom_thresholds.csv",
            media_type="text/csv",
        ),
    ),
)


def build_public_site_shell(plan: PublicationPlan) -> PublicSiteShell:
    banzuke_changes_page = plan.pages["banzuke_changes"].page
    brb_page = plan.pages["basho_results_browser"].page
    finish_by_chii_page = plan.pages["finish_by_chii"].page
    content_panels = (
        ContentPanel(
            page_id=banzuke_changes_page.id,
            heading=Heading(
                title=banzuke_changes_page.title,
                summary=banzuke_changes_page.summary,
            ),
            grammar="G1",
            contents=G1Contents(
                filter_section=FilterSection(filters=BANZUKE_CHANGES_FILTERS),
                pa=PA(artifact_id=BANZUKE_CHANGES_ARTIFACT.id),
                note_ids=tuple(note.id for note in BANZUKE_CHANGES_ARTIFACT.notes),
            ),
        ),
        ContentPanel(
            page_id=finish_by_chii_page.id,
            heading=Heading(
                title=finish_by_chii_page.title,
                summary=finish_by_chii_page.summary,
            ),
            grammar="G1",
            contents=G1Contents(
                filter_section=FilterSection(filters=FINISH_BY_CHII_FILTERS),
                pa=PA(artifact_id=FINISH_BY_CHII_ARTIFACT.id),
            ),
        ),
        ContentPanel(
            page_id=brb_page.id,
            heading=Heading(title=brb_page.title, summary=brb_page.summary),
            grammar="G1",
            contents=G1Contents(
                filter_section=FilterSection(filters=BRB_FILTERS),
                pa=PA(artifact_id=BASHO_RESULTS_ARTIFACT.id),
                note_ids=tuple(note.id for note in BASHO_RESULTS_ARTIFACT.notes),
            ),
        ),
    )
    renderable_page_ids = frozenset(panel.page_id for panel in content_panels)
    return PublicSiteShell(
        navigation_bar=NavigationBar(
            heading=plan.site.title,
            navigation_tree=renderable_navigation_tree(
                plan.navigation_tree,
                renderable_page_ids,
            ),
            collapse_control=NavigationCollapseControl(
                enabled=True,
                storage_key="gaspodeSumoLab.makeSite2.navCollapsed",
            ),
        ),
        content_panels=content_panels,
    )


def renderable_navigation_tree(
    items: tuple[NavigationItem, ...],
    renderable_page_ids: frozenset[str],
) -> tuple[NavigationItem, ...]:
    return tuple(
        renderable_navigation_item(item, renderable_page_ids)
        for item in items
    )


def renderable_navigation_item(
    item: NavigationItem,
    renderable_page_ids: frozenset[str],
) -> NavigationItem:
    included = item.page_id in renderable_page_ids if item.page_id is not None else False
    return NavigationItem(
        id=item.id,
        label=item.label,
        slug=item.slug,
        page_id=item.page_id,
        href=item.href if included else None,
        included=included,
        children=renderable_navigation_tree(item.children, renderable_page_ids),
    )


def build_runtime_manifest(plan: PublicationPlan) -> dict[str, Any]:
    return {
        "site": {
            "id": plan.site.id,
            "title": plan.site.title,
        },
        "ui": to_plain(build_public_site_shell(plan)),
        "artifacts": {
            BANZUKE_CHANGES_ARTIFACT.id: to_plain(BANZUKE_CHANGES_ARTIFACT),
            BASHO_RESULTS_ARTIFACT.id: to_plain(BASHO_RESULTS_ARTIFACT),
            FINISH_BY_CHII_ARTIFACT.id: to_plain(FINISH_BY_CHII_ARTIFACT),
        },
    }


def to_plain(value: Any) -> Any:
    if is_dataclass(value):
        return {key: to_plain(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple):
        return [to_plain(item) for item in value]
    if isinstance(value, list):
        return [to_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: to_plain(item) for key, item in value.items()}
    return value

"""make_site2 semantic manifests assembled from site and artifact declarations."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from .artifact_model import (
    ColumnGroup,
    IndexedDataSource,
    IndexedTableArtifact,
    Note,
    TableColumn,
)
from .publication_model import PublicationPlan
from .ui_model import (
    ContentPanel,
    Filter,
    FilterSection,
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
            text="Score gives wins, losses and absences for the selected basho.",
        ),
    ),
)


def build_public_site_shell(plan: PublicationPlan) -> PublicSiteShell:
    brb_page = plan.pages["basho_results_browser"].page
    return PublicSiteShell(
        navigation_bar=NavigationBar(
            heading=plan.site.title,
            navigation_tree=plan.navigation_tree,
            collapse_control=NavigationCollapseControl(
                enabled=True,
                storage_key="gaspodeSumoLab.makeSite2.navCollapsed",
            ),
        ),
        content_panels=(
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
        ),
    )


def build_runtime_manifest(plan: PublicationPlan) -> dict[str, Any]:
    return {
        "site": {
            "id": plan.site.id,
            "title": plan.site.title,
        },
        "ui": to_plain(build_public_site_shell(plan)),
        "artifacts": {
            BASHO_RESULTS_ARTIFACT.id: to_plain(BASHO_RESULTS_ARTIFACT),
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

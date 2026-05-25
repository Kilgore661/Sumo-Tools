"""Resolve planned Pages into the public UI and runtime manifest."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from typing import Any

from ..publication_model import NavigationItem, PublicationPlan
from ..ui_model import (
    ContentPanel,
    Contents,
    Filter,
    FilterSection,
    Heading,
    NavigationBar,
    NavigationCollapseControl,
    Notes,
    PA,
    PAPanel,
    PublicSiteShell,
)
from . import artifacts as a
from . import filters as f


@dataclass(frozen=True, kw_only=True)
class PanelDeclaration:
    """Site-facing material required to render one declared public Page."""

    filters: tuple[Filter, ...]
    artifact: object


PANEL_DECLARATIONS: dict[str, PanelDeclaration] = {
    "banzuke_changes": PanelDeclaration(
        filters=f.BANZUKE_CHANGES_FILTERS,
        artifact=a.BANZUKE_CHANGES_ARTIFACT,
    ),
    "standings_by_wins": PanelDeclaration(
        filters=f.STANDINGS_FILTERS,
        artifact=a.STANDINGS_BY_WINS_ARTIFACT,
    ),
    "finish_by_chii": PanelDeclaration(
        filters=f.FINISH_BY_CHII_FILTERS,
        artifact=a.FINISH_BY_CHII_ARTIFACT,
    ),
    "banzuke_division_by_era": PanelDeclaration(
        filters=(),
        artifact=a.BANZUKE_DIVISION_BY_ERA_ARTIFACT,
    ),
    "makuuchi_rank_by_era": PanelDeclaration(
        filters=(),
        artifact=a.MAKUUCHI_RANK_BY_ERA_ARTIFACT,
    ),
    "division_stability": PanelDeclaration(
        filters=(),
        artifact=a.DIVISION_STABILITY_ARTIFACT,
    ),
    "first_chii_appearance": PanelDeclaration(
        filters=(),
        artifact=a.FIRST_CHII_APPEARANCE_ARTIFACT,
    ),
    "basho_results_browser": PanelDeclaration(
        filters=f.BRB_FILTERS,
        artifact=a.BASHO_RESULTS_ARTIFACT,
    ),
    "rank_at_retirement": PanelDeclaration(
        filters=(),
        artifact=a.RANK_AT_RETIREMENT_ARTIFACT,
    ),
    "career_length": PanelDeclaration(
        filters=f.CAREER_LENGTH_FILTERS,
        artifact=a.CAREER_LENGTH_ARTIFACT,
    ),
    "typical_equelo_values": PanelDeclaration(
        filters=(),
        artifact=a.TYPICAL_EQUELO_VALUES_ARTIFACT,
    ),
    "win_probability_by_standing": PanelDeclaration(
        filters=f.WIN_PROBABILITY_BY_STANDING_FILTERS,
        artifact=a.WIN_PROBABILITY_BY_STANDING_ARTIFACT,
    ),
}


def build_public_site_shell(plan: PublicationPlan) -> PublicSiteShell:
    declarations = planned_panel_declarations(plan)
    content_panels = tuple(
        build_content_panel(plan.pages[page_id].page, declaration)
        for page_id, declaration in declarations
    )
    renderable_page_ids = frozenset(panel.page_id for panel in content_panels)
    return PublicSiteShell(
        navigation_bar=NavigationBar(
            heading=plan.site.title,
            navigation_tree=renderable_navigation_tree(
                plan.navigation_tree, renderable_page_ids
            ),
            collapse_control=NavigationCollapseControl(
                enabled=True,
                storage_key="gaspodeSumoLab.makeSite2.navCollapsed",
            ),
        ),
        content_panels=content_panels,
    )


def build_content_panel(page: object, declaration: PanelDeclaration) -> ContentPanel:
    artifact = declaration.artifact
    note_ids = tuple(note.id for note in getattr(artifact, "notes", ()))
    return ContentPanel(
        page_id=page.id,
        heading=Heading(title=page.title, summary=page.summary),
        contents=Contents(
            filter_section=(
                FilterSection(filters=declaration.filters)
                if declaration.filters
                else None
            ),
            pa_panel=PAPanel(
                pa=PA(artifact_id=artifact.id),
                notes=Notes(note_ids=note_ids),
            ),
        ),
    )


def planned_panel_declarations(
    plan: PublicationPlan,
) -> tuple[tuple[str, PanelDeclaration], ...]:
    missing = tuple(page_id for page_id in plan.pages if page_id not in PANEL_DECLARATIONS)
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"No public panel declaration for planned Page(s): {joined}")
    return tuple((page_id, PANEL_DECLARATIONS[page_id]) for page_id in plan.pages)


def renderable_navigation_tree(
    items: tuple[NavigationItem, ...], renderable_page_ids: frozenset[str]
) -> tuple[NavigationItem, ...]:
    return tuple(renderable_navigation_item(item, renderable_page_ids) for item in items)


def renderable_navigation_item(
    item: NavigationItem, renderable_page_ids: frozenset[str]
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
    declarations = planned_panel_declarations(plan)
    return {
        "site": {"id": plan.site.id, "title": plan.site.title},
        "ui": to_plain(build_public_site_shell(plan)),
        "artifacts": {
            declaration.artifact.id: to_plain(declaration.artifact)
            for _, declaration in declarations
        },
    }


def to_plain(value: Any) -> Any:
    if is_dataclass(value):
        return {key: to_plain(item) for key, item in asdict(value).items()}
    if isinstance(value, (tuple, list)):
        return [to_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: to_plain(item) for key, item in value.items()}
    return value

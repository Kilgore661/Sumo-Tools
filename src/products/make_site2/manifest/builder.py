"""Resolve planned Pages into the public UI and runtime manifest."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from typing import Any
from urllib.parse import urlencode

from ..publication_model import NavigationItem, PublicationPlan
from ..ui_model import (
    ContentPanel,
    Contents,
    Filter,
    FilterSection,
    Heading,
    NavigationBar,
    NavigationCollapseControl,
    NavigationQuickLink,
    Notes,
    PA,
    PAPanel,
    PublicSiteShell,
)
from . import artifacts as a
from . import filters as f


@dataclass(frozen=True, kw_only=True)
class QuickLinkDeclaration:
    """Builder-facing declaration for a curated NavigationBar quick link."""

    label: str
    page_id: str | None = None
    href: str | None = None


GOATS_HREF = "?page=career_comparisons&skill=equelo&x=date&log=true&rikishi=1123%2C3987%2C1354%2C2%2C3%2C4080"

QUICK_LINKS: tuple[QuickLinkDeclaration, ...] = (
    QuickLinkDeclaration(page_id="basho_results_browser", label="Basho Results"),
    QuickLinkDeclaration(page_id="banzuke_changes", label="Most Recent Banzuke"),
    QuickLinkDeclaration(label="GOATs", href=GOATS_HREF),
)

LANDING_NAVIGATION_NODE_ID = "home"
LANDING_NAVIGATION_HREF = "index.html"


@dataclass(frozen=True, kw_only=True)
class PanelDeclaration:
    """Site-facing material required to render one declared public Page."""

    filters: tuple[Filter, ...]
    artifact: object
    public_url_keys: tuple[str, ...] = ()


PANEL_DECLARATIONS: dict[str, PanelDeclaration] = {
    "banzuke_changes": PanelDeclaration(
        filters=f.BANZUKE_CHANGES_FILTERS,
        artifact=a.BANZUKE_CHANGES_ARTIFACT,
    ),
    "standings_by_wins": PanelDeclaration(
        filters=f.STANDINGS_FILTERS,
        artifact=a.STANDINGS_BY_WINS_ARTIFACT,
    ),
    "rating_changes": PanelDeclaration(
        filters=f.RATING_CHANGES_FILTERS,
        artifact=a.RATING_CHANGES_ARTIFACT,
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
    "most_consecutive_bouts": PanelDeclaration(
        filters=f.MOST_CONSECUTIVE_BOUTS_FILTERS,
        artifact=a.MOST_CONSECUTIVE_BOUTS_ARTIFACT,
    ),
    "most_career_wins": PanelDeclaration(
        filters=f.MOST_CAREER_WINS_FILTERS,
        artifact=a.MOST_CAREER_WINS_ARTIFACT,
    ),
    "most_career_losses": PanelDeclaration(
        filters=f.MOST_CAREER_LOSSES_FILTERS,
        artifact=a.MOST_CAREER_LOSSES_ARTIFACT,
    ),
    "highest_equelo": PanelDeclaration(
        filters=f.HIGHEST_EQUELO_FILTERS,
        artifact=a.HIGHEST_EQUELO_ARTIFACT,
    ),
    "career_comparisons": PanelDeclaration(
        filters=f.CAREER_COMPARISONS_FILTERS,
        artifact=a.CAREER_COMPARISONS_ARTIFACT,
        public_url_keys=("rikishi",),
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


def build_public_site_shell(
    plan: PublicationPlan, *, full_navigation: bool = False
) -> PublicSiteShell:
    declarations = planned_panel_declarations(plan)
    declaration_by_page_id = dict(declarations)
    content_panels = tuple(
        build_content_panel(plan.pages[page_id].page, declaration)
        for page_id, declaration in declarations
    )
    renderable_page_ids = frozenset(panel.page_id for panel in content_panels)
    return PublicSiteShell(
        navigation_bar=NavigationBar(
            heading=plan.site.title,
            quick_links=renderable_quick_links(
                QUICK_LINKS, renderable_page_ids, declaration_by_page_id
            ),
            navigation_tree=renderable_navigation_tree(
                plan.navigation_tree,
                renderable_page_ids,
                declaration_by_page_id,
                full_navigation=full_navigation,
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
        public_url_keys=declaration.public_url_keys,
    )


def planned_panel_declarations(
    plan: PublicationPlan,
) -> tuple[tuple[str, PanelDeclaration], ...]:
    missing = tuple(page_id for page_id in plan.pages if page_id not in PANEL_DECLARATIONS)
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"No public panel declaration for planned Page(s): {joined}")
    return tuple((page_id, PANEL_DECLARATIONS[page_id]) for page_id in plan.pages)


def canonical_default_view_href(page_id: str, filters: tuple[Filter, ...]) -> str:
    """Return the single-shell public link requesting a Page's default view."""

    state: list[tuple[str, str]] = [("page", page_id)]
    state.extend(
        (filter.url_key or filter.id, serialize_filter_value(filter.default))
        for filter in filters
    )
    return f"?{urlencode(state)}"


def serialize_filter_value(value: str | bool) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def renderable_quick_links(
    quick_links: tuple[QuickLinkDeclaration, ...],
    renderable_page_ids: frozenset[str],
    declaration_by_page_id: dict[str, PanelDeclaration],
) -> tuple[NavigationQuickLink, ...]:
    resolved = []
    for quick_link in quick_links:
        if quick_link.href is not None:
            resolved.append(
                NavigationQuickLink(
                    page_id=quick_link.page_id,
                    label=quick_link.label,
                    href=quick_link.href,
                )
            )
            continue
        page_id = quick_link.page_id
        if page_id is None:
            continue
        declaration = declaration_by_page_id.get(page_id)
        if page_id not in renderable_page_ids or declaration is None:
            continue
        resolved.append(
            NavigationQuickLink(
                page_id=page_id,
                label=quick_link.label,
                href=canonical_default_view_href(page_id, declaration.filters),
            )
        )
    return tuple(resolved)


def renderable_navigation_tree(
    items: tuple[NavigationItem, ...],
    renderable_page_ids: frozenset[str],
    declaration_by_page_id: dict[str, PanelDeclaration],
    *,
    full_navigation: bool,
) -> tuple[NavigationItem, ...]:
    resolved_items = tuple(
        renderable_navigation_item(
            item,
            renderable_page_ids,
            declaration_by_page_id,
            full_navigation=full_navigation,
        )
        for item in items
    )
    if full_navigation:
        return resolved_items
    return tuple(item for item in resolved_items if item.href is not None or item.children)


def renderable_navigation_item(
    item: NavigationItem,
    renderable_page_ids: frozenset[str],
    declaration_by_page_id: dict[str, PanelDeclaration],
    *,
    full_navigation: bool,
) -> NavigationItem:
    included = item.page_id in renderable_page_ids if item.page_id is not None else False
    declaration = declaration_by_page_id.get(item.page_id or "")
    href = (
        canonical_default_view_href(item.page_id, declaration.filters)
        if included and item.page_id is not None and declaration is not None
        else item.href
    )
    if item.id == LANDING_NAVIGATION_NODE_ID and item.page_id is None:
        href = LANDING_NAVIGATION_HREF
    return NavigationItem(
        id=item.id,
        label=item.label,
        slug=item.slug,
        page_id=item.page_id,
        href=href,
        included=included,
        children=renderable_navigation_tree(
            item.children,
            renderable_page_ids,
            declaration_by_page_id,
            full_navigation=full_navigation,
        ),
    )


def build_runtime_manifest(
    plan: PublicationPlan, *, full_navigation: bool = False
) -> dict[str, Any]:
    declarations = planned_panel_declarations(plan)
    return {
        "site": {"id": plan.site.id, "title": plan.site.title},
        "ui": to_plain(build_public_site_shell(plan, full_navigation=full_navigation)),
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

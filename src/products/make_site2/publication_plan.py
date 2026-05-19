"""Resolve a SiteDefinition into the first make_site2 publication plan."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .models import ArtifactRef, NavigationTree, PageDefinition, PageStatus, SiteDefinition
from .routes import PageRoute, derive_page_routes, route_href


@dataclass(frozen=True, kw_only=True)
class PlannedPage:
    """A page selected for a particular build."""

    page: PageDefinition
    route: PageRoute


@dataclass(frozen=True, kw_only=True)
class NavigationItem:
    """Navigation entry after route resolution."""

    id: str
    label: str
    slug: str
    page_id: str | None
    href: str | None
    included: bool
    children: tuple["NavigationItem", ...] = ()


@dataclass(frozen=True, kw_only=True)
class NavigationBar:
    """Publication UI Model input for the shared site navigation."""

    title: str
    collapse_control: "NavigationCollapseControl"
    items: tuple[NavigationItem, ...]


@dataclass(frozen=True, kw_only=True)
class NavigationCollapseControl:
    """Configuration for hiding and recovering the navigation panel."""

    enabled: bool
    storage_key: str


@dataclass(frozen=True, kw_only=True)
class PublicationPlan:
    """Resolved publication model for a build."""

    site: SiteDefinition
    routes: Mapping[str, PageRoute]
    pages: Mapping[str, PlannedPage]
    navigation_bar: NavigationBar


DEFAULT_INCLUDED_STATUSES = frozenset({PageStatus.PROMOTED})


def build_publication_plan(
    site: SiteDefinition,
    *,
    included_statuses: frozenset[PageStatus] = DEFAULT_INCLUDED_STATUSES,
) -> PublicationPlan:
    """Resolve routes and navigation for the currently included pages."""

    routes = derive_page_routes(site)
    planned_pages = {
        page_id: PlannedPage(page=route.page, route=route)
        for page_id, route in routes.items()
        if route.page.status in included_statuses
    }
    navigation_bar = NavigationBar(
        title=site.title,
        collapse_control=NavigationCollapseControl(
            enabled=True,
            storage_key="gaspodeSumoLab.makeSite2.navCollapsed",
        ),
        items=tuple(
            _navigation_item(child, routes, planned_pages)
            for child in site.navigation.children
        ),
    )
    return PublicationPlan(
        site=site,
        routes=routes,
        pages=planned_pages,
        navigation_bar=navigation_bar,
    )


def artifact_refs(plan: PublicationPlan) -> Mapping[str, ArtifactRef]:
    """Return the artifact/data-reference side of the key seam."""

    return {
        page_id: planned_page.page.artifact
        for page_id, planned_page in plan.pages.items()
    }


def _navigation_item(
    node: NavigationTree,
    routes: Mapping[str, PageRoute],
    planned_pages: Mapping[str, PlannedPage],
) -> NavigationItem:
    included = node.page_id in planned_pages if node.page_id is not None else False
    href = route_href(routes[node.page_id].parts) if included and node.page_id is not None else None
    return NavigationItem(
        id=node.id,
        label=node.label,
        slug=node.slug,
        page_id=node.page_id,
        href=href,
        included=included,
        children=tuple(
            _navigation_item(child, routes, planned_pages)
            for child in node.children
        ),
    )

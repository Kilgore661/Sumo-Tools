"""Resolved publication model before UI rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .models import NavigationTree, PageDefinition, PageStatus, SiteDefinition
from .routes import PageRoute, derive_page_routes, route_href


@dataclass(frozen=True, kw_only=True)
class PlannedPage:
    page: PageDefinition
    route: PageRoute


@dataclass(frozen=True, kw_only=True)
class NavigationItem:
    id: str
    label: str
    slug: str
    page_id: str | None
    href: str | None
    included: bool
    children: tuple["NavigationItem", ...] = ()


@dataclass(frozen=True, kw_only=True)
class PublicationPlan:
    site: SiteDefinition
    routes: Mapping[str, PageRoute]
    pages: Mapping[str, PlannedPage]
    navigation_tree: tuple[NavigationItem, ...]


DEFAULT_INCLUDED_STATUSES = frozenset({PageStatus.PROMOTED})


def build_publication_plan(
    site: SiteDefinition,
    *,
    included_statuses: frozenset[PageStatus] = DEFAULT_INCLUDED_STATUSES,
) -> PublicationPlan:
    routes = derive_page_routes(site)
    planned_pages = {
        page_id: PlannedPage(page=route.page, route=route)
        for page_id, route in routes.items()
        if route.page.status in included_statuses
    }
    navigation_tree = tuple(
        _navigation_item(child, routes, planned_pages)
        for child in site.navigation.children
    )
    return PublicationPlan(
        site=site,
        routes=routes,
        pages=planned_pages,
        navigation_tree=navigation_tree,
    )


def artifact_refs(plan: PublicationPlan):
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
    href = (
        route_href(routes[node.page_id].parts)
        if included and node.page_id is not None
        else node.href
    )
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

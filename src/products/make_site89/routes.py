"""Route derivation from the declared navigation tree."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Mapping

from .models import NavigationTree, PageDefinition, SiteDefinition


@dataclass(frozen=True, kw_only=True)
class PageRoute:
    """Route derived from a page node in the navigation tree."""

    page: PageDefinition
    parts: tuple[str, ...]


def derive_page_routes(site: SiteDefinition) -> Mapping[str, PageRoute]:
    """Return canonical routes for every navigation node with a page id."""

    routes: dict[str, PageRoute] = {}

    def walk(node: NavigationTree, parent_parts: tuple[str, ...]) -> None:
        parts = parent_parts + ((node.slug,) if node.slug else ())
        if node.page_id is not None:
            if node.page_id not in site.pages.pages:
                raise KeyError(f"Navigation node {node.id!r} references unknown page {node.page_id!r}")
            if node.page_id in routes:
                raise ValueError(f"Page {node.page_id!r} has more than one canonical route")
            routes[node.page_id] = PageRoute(
                page=site.pages.pages[node.page_id],
                parts=parts,
            )
        for child in node.children:
            walk(child, parts)

    walk(site.navigation, ())
    walk(site.research_navigation, ())
    return routes


def route_href(parts: tuple[str, ...]) -> str:
    """Return the relative static HTML path for route parts."""

    return PurePosixPath(*parts, "index.html").as_posix()


def html_href(base_route: str, parts: tuple[str, ...]) -> str:
    """Return a browser href for route parts under a configured base route."""

    return f"{base_route.rstrip('/')}/{route_href(parts)}"

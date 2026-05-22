"""Route derivation from the navigation tree."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Mapping

from .classes import NavigationTree, Page, Site


@dataclass(frozen=True, kw_only=True)
class PageRoute:
    """Route derived from a page node in the navigation tree."""

    page: Page
    parts: tuple[str, ...]


def derive_page_routes(site: Site) -> Mapping[str, PageRoute]:
    routes: dict[str, PageRoute] = {}

    def walk(node: NavigationTree, parent_parts: tuple[str, ...]) -> None:
        parts = parent_parts + ((node.slug,) if node.slug else ())
        if node.page_id is not None:
            routes[node.page_id] = PageRoute(
                page=site.pages.pages[node.page_id],
                parts=parts,
            )
        for child in node.children:
            walk(child, parts)

    walk(site.navigation, ())
    return routes


def html_href(base_route: str, parts: tuple[str, ...]) -> str:
    route = PurePosixPath(*parts, "index.html").as_posix()
    return f"{base_route.rstrip('/')}/{route}"


def route_href(parts: tuple[str, ...]) -> str:
    return PurePosixPath(*parts, "index.html").as_posix()

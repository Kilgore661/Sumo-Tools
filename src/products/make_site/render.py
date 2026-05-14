"""HTML rendering helpers for the static site builder."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Mapping

from .classes import DataRef, NavigationTree, Page, Site, SiteBuildConfig
from .classes.page_parts import CustomView
from .renderers.career_length import write_career_length_page
from .renderers.rank_at_retirement import write_rank_at_retirement_page
from .renderers.standing_win_probability import write_standing_win_probability_page
from .renderers.tbd import write_tbd_page
from .renderers.typical_equelo_values import write_typical_equelo_values_page
from .routes import PageRoute, html_href, route_href


SHELL_ASSET_VERSION = "20260514-nav-toggle"



def write_site_index(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    build_stamp: str,
) -> None:
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<link rel="icon" type="image/x-icon" href="../Sumo/meep.png">',
            '<link rel="stylesheet" href="common/files/site-wide.css">',
            f'<link rel="stylesheet" href="site-shell.css?v={SHELL_ASSET_VERSION}">',
            f"<title>{escape(site.title)}</title>",
            "</head>",
            "<body>",
            '<div class="site-shell" data-nav-shell>',
            (
                '<button type="button" class="nav-toggle" data-nav-toggle '
                'aria-controls="site-nav" aria-expanded="true" '
                'aria-label="Hide navigation" title="Hide navigation">&lt;</button>'
            ),
            '<aside id="site-nav" class="site-nav" data-nav-panel aria-label="Site navigation">',
            '<header class="site-brand">',
            f'<div class="site-name">{escape(site.title)}</div>',
            f'<div class="site-status">{escape(build_stamp)}</div>',
            "</header>",
            render_navigation(site.navigation, config.base_route, page_routes),
            "</aside>",
            '<main class="site-main">',
            '<section id="welcome-panel" class="welcome-panel"><p>Hello World!</p></section>',
            '<section id="frame-panel" class="frame-panel" hidden>',
            '<iframe id="content-frame" title="Selected site page"></iframe>',
            "</section>",
            "</main>",
            "</div>",
            f'<script src="nav-toggle.js?v={SHELL_ASSET_VERSION}"></script>',
            f'<script src="site-shell.js?v={SHELL_ASSET_VERSION}"></script>',
            "</body>",
            "</html>",
            "",
        )
    )
    target_path = config.output_root / "index.html"
    target_path.write_text(html, encoding="utf-8")


def render_navigation(
    node: NavigationTree,
    base_route: str,
    page_routes: Mapping[str, PageRoute],
) -> str:
    children = "".join(
        render_navigation_node(child, base_route, page_routes) for child in node.children
    )
    return f'<ol class="nav-tree">{children}</ol>'


def render_navigation_node(
    node: NavigationTree,
    base_route: str,
    page_routes: Mapping[str, PageRoute],
) -> str:
    label = escape(node.label)
    if node.page_id is None:
        heading = f"<span>{label}</span>"
    else:
        route = page_routes[node.page_id]
        href = html_href(base_route, route.parts)
        frame_href = route_href(route.parts)
        title = escape(route.page.title)
        summary = escape(route.page.summary)
        nav_class = "nav-link"
        if isinstance(route.page.view, CustomView) and route.page.view.kind == "tbd_page":
            nav_class = "nav-link nav-link-tbd"
        heading = (
            f'<a class="{nav_class}" href="{escape(href)}" '
            f'data-frame-src="{escape(frame_href)}" '
            f'data-title="{title}" data-summary="{summary}">{label}</a>'
        )

    if node.children:
        children = "".join(
            render_navigation_node(child, base_route, page_routes)
            for child in node.children
        )
        return f"<li>{heading}<ol>{children}</ol></li>"
    return f"<li>{heading}</li>"


def write_plotly_json_page(
    page: Page,
    data: DataRef,
    template: str,
    config: DataRef,
    target_path: Path,
) -> None:
    html = template.format(
        title=escape(page.title),
        data_path=data.output_path.as_posix(),
        config_path=config.output_path.as_posix(),
    )
    target_path.write_text(html, encoding="utf-8")


def write_custom_page(
    page: Page,
    kind: str,
    target_path: Path,
    asset_prefix: str = "",
) -> None:
    if kind == "standing_win_probability":
        write_standing_win_probability_page(page, target_path, asset_prefix)
        return
    if kind == "career_length":
        write_career_length_page(page, target_path, asset_prefix)
        return
    if kind == "rank_at_retirement":
        write_rank_at_retirement_page(page, target_path, asset_prefix)
        return
    if kind == "typical_equelo_values":
        write_typical_equelo_values_page(page, target_path, asset_prefix)
        return
    if kind == "tbd_page":
        write_tbd_page(page, target_path, asset_prefix)
        return

    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<link rel="icon" type="image/x-icon" href="../Sumo/meep.png">',
            f"<title>{escape(page.title)}</title>",
            "</head>",
            "<body>",
            f"<h1>{escape(page.title)}</h1>",
            f"<p>{escape(page.summary)}</p>",
            f"<p>Custom view: {escape(kind)}</p>",
            render_options(page),
            render_data_refs(page.data),
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")




def render_options(page: Page) -> str:
    if page.options is None:
        return ""
    items = "".join(
        f"<li>{escape(option.label)}: {escape(str(option.default))}</li>"
        for option in page.options.options
    )
    return f"<h2>Options</h2><ol>{items}</ol>"


def render_data_refs(data_refs: tuple[DataRef, ...]) -> str:
    items = "".join(
        (
            f'<li><a href="{escape(data_ref.output_path.as_posix())}">'
            f"{escape(data_ref.id)}</a></li>"
        )
        for data_ref in data_refs
    )
    return f"<h2>Data</h2><ol>{items}</ol>"

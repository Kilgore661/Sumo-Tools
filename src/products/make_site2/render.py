"""HTML rendering for make_site2.

This module renders the site shell from a semantic PublicSiteShell. It should
not invent page structure or artifact details.
"""

from __future__ import annotations

from html import escape
from urllib.parse import urlencode

from .publication_model import NavigationItem
from .ui_model import NavigationBar, NavigationQuickLink, PublicSiteShell



def render_site_shell(
    shell: PublicSiteShell,
    *,
    cache_mode: str = "prod",
    cache_bust_token: str = "",
    cache_bust_param: str = "cb",
) -> str:
    cache_attrs = render_cache_attrs(
        cache_mode=cache_mode,
        cache_bust_token=cache_bust_token,
        cache_bust_param=cache_bust_param,
    )
    return "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            (
                '<link rel="stylesheet" '
                f'href="{escape(cache_busted_url("runtime/site.css", cache_mode=cache_mode, cache_bust_token=cache_bust_token, cache_bust_param=cache_bust_param))}">'
            ),
            '<link rel="icon" href="/Sumo/meepinvert.png" type="image/png">',
            f"<title>{escape(render_document_title(shell.navigation_bar.heading))}</title>",
            '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>',
            "</head>",
            f"<body{cache_attrs}>",
            '<div class="site-shell" data-nav-shell>',
            render_navigation_bar(shell.navigation_bar),
            '<main class="site-main" aria-label="Page content">',
            '<div id="content-panel"></div>',
            "</main>",
            "</div>",
            (
                '<script type="module" '
                f'src="{escape(cache_busted_url("runtime/site.js", cache_mode=cache_mode, cache_bust_token=cache_bust_token, cache_bust_param=cache_bust_param))}"></script>'
            ),
            "</body>",
            "</html>",
            "",
        )
    )


def render_cache_attrs(
    *,
    cache_mode: str,
    cache_bust_token: str,
    cache_bust_param: str,
) -> str:
    if cache_mode != "dev" or not cache_bust_token:
        return ""
    return (
        f' data-cache-mode="{escape(cache_mode)}"'
        f' data-cache-bust="{escape(cache_bust_token)}"'
        f' data-cache-bust-param="{escape(cache_bust_param)}"'
    )


def render_document_title(heading: str) -> str:
    return " ".join(heading.split())


def render_visible_title(heading: str) -> str:
    lines = heading.splitlines() or [heading]
    return "<br>".join(escape(line) for line in lines)


def cache_busted_url(
    path: str,
    *,
    cache_mode: str,
    cache_bust_token: str,
    cache_bust_param: str,
) -> str:
    if cache_mode != "dev" or not cache_bust_token:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}{urlencode({cache_bust_param: cache_bust_token})}"


def render_navigation_bar(navigation_bar: NavigationBar) -> str:
    return "\n".join(
        (
            '<nav id="site-nav" class="site-nav" data-nav-panel aria-label="Site navigation">',
            '<div class="nav-hider-strip">',
            render_navigation_toggle(navigation_bar),
            "</div>",
            '<div id="site-nav-content" class="nav-content" data-nav-content>',
            f'<h1 class="site-title">{render_visible_title(navigation_bar.heading)}</h1>',
            render_quick_links(navigation_bar),
            '<div class="nav-tree-panels">',
            render_navigation_panel(
                panel_id="public-nav-tree",
                heading="Contents",
                items=navigation_bar.navigation_tree,
                modifier="public-nav-tree-panel",
                collapsed=False,
            ),
            render_navigation_panel(
                panel_id="research-nav-tree",
                heading="Research",
                items=navigation_bar.research_navigation_tree,
                modifier="research-nav-tree-panel",
                collapsed=True,
            ),
            "</div>",
            "</div>",
            "</nav>",
        )
    )


def render_navigation_panel(
    *,
    panel_id: str,
    heading: str,
    items: tuple[NavigationItem, ...],
    modifier: str,
    collapsed: bool,
) -> str:
    escaped_panel_id = escape(panel_id)
    escaped_heading = escape(heading)
    body_id = f"{escaped_panel_id}-body"
    expanded = "false" if collapsed else "true"
    toggle_label = f"Show {heading}" if collapsed else f"Hide {heading}"
    hidden = " hidden" if collapsed else ""
    chevron = "˅" if collapsed else "˄"
    return "\n".join(
        (
            f'<section id="{escaped_panel_id}" class="nav-tree-panel {escape(modifier)}" aria-labelledby="{escaped_panel_id}-heading" data-nav-tree-panel>',
            f'<h2 id="{escaped_panel_id}-heading" class="nav-tree-heading"><span>{escaped_heading}</span><button class="nav-tree-toggle" type="button" data-nav-tree-toggle aria-controls="{body_id}" aria-expanded="{expanded}" aria-label="{escape(toggle_label)}" title="{escape(toggle_label)}">{chevron}</button></h2>',
            f'<ul id="{body_id}" class="nav-list" data-nav-tree-body{hidden}>',
            *[render_navigation_item(item) for item in items],
            "</ul>",
            "</section>",
        )
    )


def render_quick_links(navigation_bar: NavigationBar) -> str:
    if not navigation_bar.quick_links:
        return ""
    return "\n".join(
        (
            '<section class="quick-links" aria-labelledby="quick-links-heading">',
            '<h2 id="quick-links-heading">Quick Links</h2>',
            '<ul class="quick-links-list">',
            *[render_quick_link(link) for link in navigation_bar.quick_links],
            "</ul>",
            "</section>",
        )
    )


def render_quick_link(link: NavigationQuickLink) -> str:
    page_attr = (
        f' data-page-id="{escape(link.page_id)}"'
        if getattr(link, "page_id", None) is not None
        else ""
    )
    return (
        f'<li><a class="quick-link nav-link" href="{escape(link.href)}"'
        f'{page_attr}>{escape(link.label)}</a></li>'
    )


def render_navigation_toggle(navigation_bar: NavigationBar) -> str:
    control = navigation_bar.collapse_control
    if not control.enabled:
        return ""
    return (
        '<button type="button" class="nav-toggle" data-nav-toggle '
        'aria-controls="site-nav-content" aria-expanded="true" '
        'aria-label="Hide navigation" title="Hide navigation" '
        f'data-storage-key="{escape(control.storage_key)}">&lt;</button>'
    )


def render_navigation_item(item: NavigationItem) -> str:
    children = "\n".join(render_navigation_item(child) for child in item.children)
    child_list = f'\n<ul class="nav-list">\n{children}\n</ul>' if children else ""
    return "\n".join(
        (
            "<li>",
            render_navigation_label(item),
            child_list,
            "</li>",
        )
    )


def render_navigation_label(item: NavigationItem) -> str:
    label = escape(item.label)
    if item.href is None:
        return f'<span class="nav-label">{label}</span>'
    if item.page_id is None:
        return f'<a class="nav-link" href="{escape(item.href)}">{label}</a>'
    page_id = escape(item.page_id or "")
    return (
        f'<a class="nav-link" href="{escape(item.href)}" '
        f'data-page-id="{page_id}">{label}</a>'
    )

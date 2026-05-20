"""HTML rendering for make_site2.

This module renders the site shell from a semantic PublicSiteShell. It should
not invent page structure or artifact details.
"""

from __future__ import annotations

from html import escape
from urllib.parse import urlencode

from .publication_model import NavigationItem
from .ui_model import NavigationBar, PublicSiteShell


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
            f"<title>{escape(render_document_title(shell.navigation_bar.heading))}</title>",
            "</head>",
            f"<body{cache_attrs}>",
            '<div class="site-shell" data-nav-shell>',
            render_navigation_toggle(shell.navigation_bar),
            render_navigation_bar(shell.navigation_bar),
            '<main class="site-main" aria-label="Page content">',
            '<div id="content-panel"></div>',
            "</main>",
            "</div>",
            (
                '<script '
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
            '<nav class="site-nav" data-nav-panel aria-label="Site navigation">',
            f'<h1 class="site-title">{render_visible_title(navigation_bar.heading)}</h1>',
            '<ol class="nav-list">',
            *[render_navigation_item(item) for item in navigation_bar.navigation_tree],
            "</ol>",
            "</nav>",
        )
    )


def render_navigation_toggle(navigation_bar: NavigationBar) -> str:
    control = navigation_bar.collapse_control
    if not control.enabled:
        return ""
    return (
        '<button type="button" class="nav-toggle" data-nav-toggle '
        'aria-controls="site-nav" aria-expanded="true" '
        'aria-label="Hide navigation" title="Hide navigation" '
        f'data-storage-key="{escape(control.storage_key)}">&lt;</button>'
    )


def render_navigation_item(item: NavigationItem) -> str:
    children = "\n".join(render_navigation_item(child) for child in item.children)
    child_list = f'\n<ol class="nav-list">\n{children}\n</ol>' if children else ""
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
    page_id = escape(item.page_id or "")
    return (
        f'<a class="nav-link" href="{escape(item.href)}" '
        f'data-page-id="{page_id}">{label}</a>'
    )

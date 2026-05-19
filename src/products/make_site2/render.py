"""HTML rendering for make_site2.

This module renders the site shell from a semantic PublicSiteShell. It should
not invent page structure or artifact details.
"""

from __future__ import annotations

from html import escape

from .publication_model import NavigationItem
from .ui_model import NavigationBar, PublicSiteShell


def render_site_shell(shell: PublicSiteShell) -> str:
    return "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<link rel="stylesheet" href="runtime/site.css">',
            f"<title>{escape(shell.navigation_bar.heading)}</title>",
            "</head>",
            "<body>",
            '<div class="site-shell" data-nav-shell>',
            render_navigation_toggle(shell.navigation_bar),
            render_navigation_bar(shell.navigation_bar),
            '<main class="site-main" aria-label="Page content">',
            '<div id="content-panel"></div>',
            "</main>",
            "</div>",
            '<script src="runtime/site.js"></script>',
            "</body>",
            "</html>",
            "",
        )
    )


def render_navigation_bar(navigation_bar: NavigationBar) -> str:
    return "\n".join(
        (
            '<nav class="site-nav" data-nav-panel aria-label="Site navigation">',
            f'<h1 class="site-title">{escape(navigation_bar.heading)}</h1>',
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

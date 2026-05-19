"""Minimal HTML rendering for the first make_site2 navigation slice."""

from __future__ import annotations

from html import escape

from .publication_plan import NavigationBar, NavigationItem, PublicationPlan


def render_navigation_page(plan: PublicationPlan, content_html: str = "") -> str:
    """Render one static page with the left navigation bar and content panel."""

    return "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<link rel="stylesheet" href="runtime/site.css">',
            f"<title>{escape(plan.site.title)}</title>",
            "</head>",
            "<body>",
            '<div class="site-shell" data-nav-shell>',
            render_navigation_toggle(plan.navigation_bar),
            render_navigation_bar(plan.navigation_bar),
            '<main class="site-main" aria-label="Page content">',
            '<div id="content-panel"></div>',
            content_html,
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
            f'<h1 class="site-title">{escape(navigation_bar.title)}</h1>',
            '<ol class="nav-list">',
            *[render_navigation_item(item) for item in navigation_bar.items],
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

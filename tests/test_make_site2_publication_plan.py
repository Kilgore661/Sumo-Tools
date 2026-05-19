from src.products.make_site2.publication_plan import (
    artifact_refs,
    build_publication_plan,
)
from src.products.make_site2.render import render_navigation_page
from src.products.make_site2.site_definition import SITE


def test_publication_plan_resolves_copied_navigation_routes() -> None:
    plan = build_publication_plan(SITE)

    assert "basho_results_browser" in plan.pages
    assert plan.pages["basho_results_browser"].route.parts == (
        "sumo-history",
        "basho-results",
    )


def test_navigation_bar_uses_resolved_hrefs_without_rendering_pages() -> None:
    plan = build_publication_plan(SITE)
    sumo_history = next(
        item for item in plan.navigation_bar.items if item.id == "sumo_history"
    )
    basho_results = next(
        item for item in sumo_history.children if item.id == "basho_results_browser"
    )

    assert basho_results.included
    assert basho_results.href == "sumo-history/basho-results/index.html"
    assert artifact_refs(plan)["basho_results_browser"].kind == "table"


def test_navigation_page_contains_left_nav_without_page_content() -> None:
    html = render_navigation_page(build_publication_plan(SITE))

    assert '<div class="site-shell" data-nav-shell>' in html
    assert 'data-nav-shell' in html
    assert 'data-nav-toggle' in html
    assert 'gaspodeSumoLab.makeSite2.navCollapsed' in html
    assert '<nav class="site-nav" data-nav-panel aria-label="Site navigation">' in html
    assert '<script src="runtime/site.js"></script>' in html
    assert 'data-page-id="basho_results_browser"' in html
    assert '<main class="site-main" aria-label="Page content">' in html
    assert "Basho Results" in html
    assert '<table class="brb-table">' not in html

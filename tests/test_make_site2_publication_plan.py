from src.products.make_site2.publication_model import (
    artifact_refs,
    build_publication_plan,
)
from src.products.make_site2.render import render_site_shell
from src.products.make_site2.site_manifest import (
    BASHO_RESULTS_ARTIFACT,
    build_public_site_shell,
    build_runtime_manifest,
)
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
    shell = build_public_site_shell(plan)
    sumo_history = next(
        item for item in shell.navigation_bar.navigation_tree if item.id == "sumo_history"
    )
    basho_results = next(
        item for item in sumo_history.children if item.id == "basho_results_browser"
    )

    assert basho_results.included
    assert basho_results.href == "sumo-history/basho-results/index.html"
    assert artifact_refs(plan)["basho_results_browser"].kind == "table"


def test_site_shell_is_rendered_from_ui_manifest() -> None:
    shell = build_public_site_shell(build_publication_plan(SITE))
    html = render_site_shell(shell)

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


def test_runtime_manifest_declares_brb_ui_and_artifact_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    brb_panel = manifest["ui"]["content_panels"][0]
    brb_artifact = manifest["artifacts"]["basho_results_browser"]

    assert brb_panel["grammar"] == "G1"
    assert brb_panel["contents"]["pa"]["artifact_id"] == BASHO_RESULTS_ARTIFACT.id
    assert [item["id"] for item in brb_panel["contents"]["filter_section"]["filters"]] == [
        "basho_date",
        "division",
        "previous_context",
        "rating_context",
        "nu_chii",
    ]
    assert brb_artifact["kind"] == "indexed_table"
    assert brb_artifact["indexed_source"]["index_path"] == (
        "sumo-history/basho-results/data/basho_results_index.json"
    )

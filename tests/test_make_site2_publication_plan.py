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


def content_panel_by_artifact(manifest: dict, artifact_id: str) -> dict:
    return next(
        panel
        for panel in manifest["ui"]["content_panels"]
        if panel["contents"]["pa"]["artifact_id"] == artifact_id
    )


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


def test_site_shell_cache_busts_runtime_assets_in_dev_mode() -> None:
    shell = build_public_site_shell(build_publication_plan(SITE))
    html = render_site_shell(shell, cache_mode="dev", cache_bust_token="test-token")

    assert 'data-cache-mode="dev"' in html
    assert 'data-cache-bust="test-token"' in html
    assert 'data-cache-bust-param="cb"' in html
    assert '<link rel="stylesheet" href="runtime/site.css?cb=test-token">' in html
    assert '<script src="runtime/site.js?cb=test-token"></script>' in html


def test_site_shell_uses_stable_runtime_assets_in_prod_mode() -> None:
    shell = build_public_site_shell(build_publication_plan(SITE))
    html = render_site_shell(shell, cache_mode="prod", cache_bust_token="test-token")

    assert "data-cache-bust" not in html
    assert '<link rel="stylesheet" href="runtime/site.css">' in html
    assert '<script src="runtime/site.js"></script>' in html


def test_runtime_manifest_declares_brb_ui_and_artifact_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    brb_panel = content_panel_by_artifact(manifest, BASHO_RESULTS_ARTIFACT.id)
    brb_artifact = manifest["artifacts"]["basho_results_browser"]
    filters = brb_panel["contents"]["filter_section"]["filters"]

    assert brb_panel["grammar"] == "G1"
    assert brb_panel["contents"]["pa"]["artifact_id"] == BASHO_RESULTS_ARTIFACT.id
    assert [item["id"] for item in filters] == [
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


def test_brb_filter_defaults_and_url_keys_match_current_public_site() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    brb_panel = content_panel_by_artifact(manifest, BASHO_RESULTS_ARTIFACT.id)
    filters = {
        item["id"]: item for item in brb_panel["contents"]["filter_section"]["filters"]
    }

    assert filters["basho_date"]["default"] == "latest"
    assert filters["basho_date"]["url_key"] == "basho"
    assert filters["division"]["default"] == "makuuchi"
    assert filters["division"]["url_key"] == "division"
    assert filters["previous_context"]["default"] is False
    assert filters["previous_context"]["url_key"] == "previous"
    assert filters["rating_context"]["default"] is False
    assert filters["rating_context"]["url_key"] == "ratings"
    assert filters["nu_chii"]["default"] is False
    assert filters["nu_chii"]["url_key"] == "nu_chii"


def test_brb_notes_cover_context_columns() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    brb_artifact = manifest["artifacts"]["basho_results_browser"]

    assert {item["id"] for item in brb_artifact["notes"]} >= {
        "note_equelo",
        "note_delta_equelo",
        "note_nu_chii",
        "note_previous_direction",
    }

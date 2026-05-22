from src.products.make_site2.publication_model import (
    artifact_refs,
    build_publication_plan,
)
from src.products.make_site2.render import render_site_shell
from src.products.make_site2.site_manifest import (
    BANZUKE_CHANGES_ARTIFACT,
    BANZUKE_DIVISION_BY_ERA_ARTIFACT,
    BASHO_RESULTS_ARTIFACT,
    CAREER_LENGTH_ARTIFACT,
    DIVISION_STABILITY_ARTIFACT,
    FIRST_CHII_APPEARANCE_ARTIFACT,
    MAKUUCHI_RANK_BY_ERA_ARTIFACT,
    RANK_AT_RETIREMENT_ARTIFACT,
    STANDINGS_BY_WINS_ARTIFACT,
    TYPICAL_EQUELO_VALUES_ARTIFACT,
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
    assert plan.pages["banzuke_changes"].route.parts == (
        "current-sumo",
        "banzuke-changes",
    )
    assert plan.pages["standings_by_wins"].route.parts == (
        "current-sumo",
        "standings-by-wins",
    )
    assert plan.pages["banzuke_division_by_era"].route.parts == (
        "banzuke-rank",
        "banzuke-structure-over-time",
        "banzuke-division-by-era",
    )
    assert plan.pages["makuuchi_rank_by_era"].route.parts == (
        "banzuke-rank",
        "banzuke-structure-over-time",
        "makuuchi-rank-by-era",
    )
    assert plan.pages["division_stability"].route.parts == (
        "banzuke-rank",
        "division-stability",
    )
    assert plan.pages["first_chii_appearance"].route.parts == (
        "banzuke-rank",
        "rank-history",
        "first-chii-appearance",
    )
    assert plan.pages["rank_at_retirement"].route.parts == (
        "sumo-history",
        "career-lifecycle",
        "rank-at-retirement",
    )
    assert plan.pages["career_length"].route.parts == (
        "sumo-history",
        "career-lifecycle",
        "career-length",
    )
    assert plan.pages["typical_equelo_values"].route.parts == (
        "ratings-models",
        "rating-and-rank",
        "typical-equelo-values",
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
    career_lifecycle = next(
        item for item in sumo_history.children if item.id == "career_lifecycle"
    )
    rank_at_retirement = next(
        item for item in career_lifecycle.children if item.id == "rank_at_retirement"
    )
    career_length = next(
        item for item in career_lifecycle.children if item.id == "history_career_length"
    )
    current_sumo = next(
        item for item in shell.navigation_bar.navigation_tree if item.id == "current_sumo"
    )
    banzuke_changes = next(
        item for item in current_sumo.children if item.id == "banzuke_changes"
    )
    standings = next(
        item for item in current_sumo.children if item.id == "standings_by_wins"
    )
    banzuke_rank = next(
        item for item in shell.navigation_bar.navigation_tree if item.id == "banzuke_rank"
    )
    banzuke_structure = next(
        item
        for item in banzuke_rank.children
        if item.id == "banzuke_structure_over_time"
    )
    banzuke_division_by_era = next(
        item
        for item in banzuke_structure.children
        if item.id == "banzuke_division_by_era"
    )
    makuuchi_rank_by_era = next(
        item
        for item in banzuke_structure.children
        if item.id == "makuuchi_rank_by_era"
    )
    division_stability = next(
        item for item in banzuke_rank.children if item.id == "division_stability"
    )
    rank_history = next(
        item for item in banzuke_rank.children if item.id == "rank_history"
    )
    first_chii_appearance = next(
        item for item in rank_history.children if item.id == "first_chii_appearance"
    )
    ratings_models = next(
        item for item in shell.navigation_bar.navigation_tree if item.id == "ratings_models"
    )
    rating_and_rank = next(
        item for item in ratings_models.children if item.id == "rating_and_rank"
    )
    typical_equelo_values = next(
        item for item in rating_and_rank.children if item.id == "typical_equelo_values"
    )

    assert basho_results.included
    assert basho_results.href == "sumo-history/basho-results/index.html"
    assert rank_at_retirement.included
    assert rank_at_retirement.href == (
        "sumo-history/career-lifecycle/rank-at-retirement/index.html"
    )
    assert career_length.included
    assert career_length.href == (
        "sumo-history/career-lifecycle/career-length/index.html"
    )
    assert banzuke_changes.included
    assert banzuke_changes.href == "current-sumo/banzuke-changes/index.html"
    assert standings.included
    assert standings.href == "current-sumo/standings-by-wins/index.html"
    assert banzuke_division_by_era.included
    assert banzuke_division_by_era.href == (
        "banzuke-rank/banzuke-structure-over-time/"
        "banzuke-division-by-era/index.html"
    )
    assert makuuchi_rank_by_era.included
    assert makuuchi_rank_by_era.href == (
        "banzuke-rank/banzuke-structure-over-time/"
        "makuuchi-rank-by-era/index.html"
    )
    assert division_stability.included
    assert division_stability.href == "banzuke-rank/division-stability/index.html"
    assert first_chii_appearance.included
    assert first_chii_appearance.href == (
        "banzuke-rank/rank-history/first-chii-appearance/index.html"
    )
    assert typical_equelo_values.included
    assert typical_equelo_values.href == (
        "ratings-models/rating-and-rank/typical-equelo-values/index.html"
    )
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
    assert 'data-page-id="banzuke_changes"' in html
    assert 'data-page-id="standings_by_wins"' in html
    assert 'data-page-id="banzuke_division_by_era"' in html
    assert 'data-page-id="makuuchi_rank_by_era"' in html
    assert 'data-page-id="division_stability"' in html
    assert 'data-page-id="first_chii_appearance"' in html
    assert 'data-page-id="rank_at_retirement"' in html
    assert 'data-page-id="career_length"' in html
    assert 'data-page-id="typical_equelo_values"' in html
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
    assert filters[0]["control"] == "select"
    assert filters[1]["control"] == "select"
    assert filters[2]["control"] == "checkbox"
    assert brb_artifact["kind"] == "indexed_table"
    assert brb_artifact["indexed_source"]["index_path"] == (
        "sumo-history/basho-results/data/basho_results_index.json"
    )


def test_runtime_manifest_declares_banzuke_changes_ui_and_artifact_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, BANZUKE_CHANGES_ARTIFACT.id)
    artifact = manifest["artifacts"]["banzuke_changes"]
    filters = panel["contents"]["filter_section"]["filters"]

    assert panel["grammar"] == "G1"
    assert panel["contents"]["pa"]["artifact_id"] == BANZUKE_CHANGES_ARTIFACT.id
    assert [item["id"] for item in filters] == [
        "division",
        "context",
        "banzuke_style",
        "delta",
        "equelo",
    ]
    assert artifact["kind"] == "banzuke_changes"
    assert artifact["renderer"] == "banzuke_changes_table"
    assert artifact["config_source"]["path"] == (
        "current-sumo/banzuke-changes/site_config.json"
    )
    assert artifact["rows_source"]["path"] == (
        "current-sumo/banzuke-changes/data/banzuke_change_report.csv"
    )


def test_runtime_manifest_declares_standings_ui_and_artifact_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, STANDINGS_BY_WINS_ARTIFACT.id)
    artifact = manifest["artifacts"]["standings_by_wins"]
    filters = panel["contents"]["filter_section"]["filters"]

    assert panel["grammar"] == "G1"
    assert panel["contents"]["pa"]["artifact_id"] == STANDINGS_BY_WINS_ARTIFACT.id
    assert [item["id"] for item in filters] == [
        "metric_group_preset",
        "current_num_basho",
        "current_only",
        "division",
    ]
    assert artifact["kind"] == "standings"
    assert artifact["renderer"] == "standings_table"
    assert artifact["selector_filter_id"] == "current_num_basho"
    assert artifact["config_source"]["path"] == (
        "current-sumo/standings-by-wins/data/site_config.json"
    )
    assert artifact["data_sources"][5]["option_value"] == "6"
    assert artifact["data_sources"][5]["path"] == (
        "current-sumo/standings-by-wins/data/"
        "multiple basho standings view (2026_03, BACKWARDS, 6).csv"
    )


def test_runtime_manifest_declares_banzuke_era_chart_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, BANZUKE_DIVISION_BY_ERA_ARTIFACT.id)
    artifact = manifest["artifacts"]["banzuke_division_by_era"]

    assert panel["grammar"] == "G1"
    assert panel["contents"]["filter_section"]["filters"] == []
    assert artifact["kind"] == "chart"
    assert artifact["renderer"] == "stacked_bar_chart"
    assert artifact["data_binding"] == {"kind": "csv", "sources": ["divisions"]}
    assert artifact["data_sources"][0]["path"] == (
        "banzuke-rank/banzuke-structure-over-time/"
        "banzuke-division-by-era/data/divisions.csv"
    )
    assert artifact["traces"][0]["kind"] == "stacked_bar"
    assert artifact["traces"][0]["x"] == "era"
    assert artifact["traces"][0]["y"] == "average_rikishi"
    assert artifact["traces"][0]["group_by"] == "division"


def test_runtime_manifest_declares_makuuchi_rank_era_chart_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, MAKUUCHI_RANK_BY_ERA_ARTIFACT.id)
    artifact = manifest["artifacts"]["makuuchi_rank_by_era"]

    assert panel["grammar"] == "G1"
    assert panel["contents"]["filter_section"]["filters"] == []
    assert artifact["kind"] == "chart"
    assert artifact["renderer"] == "stacked_bar_chart"
    assert artifact["data_binding"] == {"kind": "csv", "sources": ["ranks"]}
    assert artifact["data_sources"][0]["path"] == (
        "banzuke-rank/banzuke-structure-over-time/"
        "makuuchi-rank-by-era/data/ranks.csv"
    )
    assert artifact["traces"][0]["kind"] == "stacked_bar"
    assert artifact["traces"][0]["x"] == "rank"
    assert artifact["traces"][0]["y"] == "count"
    assert artifact["traces"][0]["group_by"] == "era"


def test_runtime_manifest_declares_division_stability_chart_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, DIVISION_STABILITY_ARTIFACT.id)
    artifact = manifest["artifacts"]["division_stability"]

    assert panel["grammar"] == "G1"
    assert panel["contents"]["filter_section"]["filters"] == []
    assert artifact["kind"] == "chart"
    assert artifact["renderer"] == "grouped_line_chart"
    assert artifact["data_binding"] == {"kind": "csv", "sources": ["persistence"]}
    assert artifact["data_sources"][0]["path"] == (
        "banzuke-rank/division-stability/data/persistence.csv"
    )
    assert artifact["traces"][0]["kind"] == "scatter"
    assert artifact["traces"][0]["x"] == "date"
    assert artifact["traces"][0]["y"] == "mean_persistence"
    assert artifact["traces"][0]["group_by"] == "division"
    assert artifact["y_axis"]["maximum"] == 1
    assert artifact["y_axis"]["tickformat"] == ".0%"


def test_runtime_manifest_declares_first_chii_appearance_chart_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, FIRST_CHII_APPEARANCE_ARTIFACT.id)
    artifact = manifest["artifacts"]["first_chii_appearance"]

    assert panel["grammar"] == "G1"
    assert panel["contents"]["filter_section"]["filters"] == []
    assert artifact["kind"] == "chart"
    assert artifact["renderer"] == "ordered_bar_chart"
    assert artifact["data_binding"] == {"kind": "csv", "sources": ["appearances"]}
    assert artifact["data_sources"][0]["path"] == (
        "banzuke-rank/rank-history/first-chii-appearance/data/appearances.csv"
    )
    assert artifact["traces"][0]["kind"] == "bar"
    assert artifact["traces"][0]["x"] == "chii"
    assert artifact["traces"][0]["y"] == "first_appearance_month_index"
    assert artifact["provenance"]["order_field"] == "ordinal"
    assert artifact["provenance"]["base_year"] == 1958
    assert artifact["provenance"]["base_month"] == 1


def test_runtime_manifest_declares_rank_at_retirement_chart_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, RANK_AT_RETIREMENT_ARTIFACT.id)
    artifact = manifest["artifacts"]["rank_at_retirement"]

    assert panel["grammar"] == "G1"
    assert panel["contents"]["filter_section"]["filters"] == []
    assert panel["contents"]["note_ids"] == ["rank_at_retirement"]
    assert artifact["kind"] == "chart"
    assert artifact["renderer"] == "category_bar_chart"
    assert artifact["data_binding"] == {"kind": "csv", "sources": ["distribution"]}
    assert artifact["data_sources"][0]["path"] == (
        "sumo-history/career-lifecycle/rank-at-retirement/data/distribution.csv"
    )
    assert artifact["traces"][0]["kind"] == "bar"
    assert artifact["traces"][0]["x"] == "rank_group"
    assert artifact["traces"][0]["y"] == "count"
    assert artifact["x_axis"]["order_values"] == [
        "Y",
        "O",
        "S",
        "K",
        "M",
        "J",
        "Ms",
        "Sd",
        "Jd",
        "Jk",
    ]


def test_runtime_manifest_declares_career_length_as_flat_g1_view_selector() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, CAREER_LENGTH_ARTIFACT.id)
    artifact = manifest["artifacts"]["career_length"]
    filters = panel["contents"]["filter_section"]["filters"]

    assert panel["grammar"] == "G1"
    assert [item["id"] for item in filters] == ["view"]
    assert filters[0]["control"] == "select"
    assert [item["value"] for item in filters[0]["values"]] == [
        "distribution",
        "pmf",
        "cdf",
        "survival",
        "longest",
    ]
    assert artifact["kind"] == "chart"
    assert artifact["renderer"] == "career_length"
    assert artifact["data_binding"] == {
        "kind": "csv_set",
        "sources": ["distribution", "pmf", "cdf", "survival", "longest"],
    }
    assert artifact["data_sources"][0]["path"] == (
        "sumo-history/career-lifecycle/career-length/data/distribution.csv"
    )
    assert artifact["data_sources"][4]["path"] == (
        "sumo-history/career-lifecycle/career-length/data/longest.csv"
    )
    assert artifact["provenance"]["views"]["distribution"]["kind"] == "stacked_bar"
    assert artifact["provenance"]["views"]["longest"]["kind"] == "table"
    assert artifact["provenance"]["views"]["longest"]["columns"][1]["id"] == "shikona"


def test_runtime_manifest_declares_typical_equelo_values_sectioned_table() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, TYPICAL_EQUELO_VALUES_ARTIFACT.id)
    artifact = manifest["artifacts"]["typical_equelo_values"]

    assert panel["grammar"] == "G1"
    assert panel["contents"]["filter_section"]["filters"] == []
    assert panel["contents"]["note_ids"] == ["typical_equelo_values", "jd100"]
    assert artifact["kind"] == "sectioned_table"
    assert artifact["renderer"] == "sectioned_table"
    assert artifact["primary_source"] == "typical_equelo_values"
    assert artifact["data_sources"][0]["path"] == (
        "ratings-models/rating-and-rank/"
        "typical-equelo-values/data/typical_equelo_values.csv"
    )
    assert [section["id"] for section in artifact["sections"]] == [
        "sanyaku",
        "maegashira",
        "other",
    ]
    assert [column["id"] for column in artifact["columns"]] == ["label", "rating"]


def test_brb_filter_defaults_and_url_keys_match_current_public_site() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    brb_panel = content_panel_by_artifact(manifest, BASHO_RESULTS_ARTIFACT.id)
    filters = {
        item["id"]: item for item in brb_panel["contents"]["filter_section"]["filters"]
    }

    assert filters["basho_date"]["default"] == "latest"
    assert filters["basho_date"]["control"] == "select"
    assert filters["basho_date"]["url_key"] == "basho"
    assert filters["division"]["default"] == "makuuchi"
    assert filters["division"]["control"] == "select"
    assert filters["division"]["url_key"] == "division"
    assert filters["previous_context"]["default"] is False
    assert filters["previous_context"]["control"] == "checkbox"
    assert filters["previous_context"]["url_key"] == "previous"
    assert filters["rating_context"]["default"] is False
    assert filters["rating_context"]["control"] == "checkbox"
    assert filters["rating_context"]["url_key"] == "ratings"
    assert filters["nu_chii"]["default"] is False
    assert filters["nu_chii"]["control"] == "checkbox"
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

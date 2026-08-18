from src.products.make_site2.manifest.artifacts import (
    BANZUKE_CHANGES_ARTIFACT,
    BANZUKE_DIVISION_BY_ERA_ARTIFACT,
    BASHO_RESULTS_ARTIFACT,
    CAREER_LENGTH_ARTIFACT,
    DIVISION_STABILITY_ARTIFACT,
    FIRST_CHII_APPEARANCE_ARTIFACT,
    HIGHEST_EQUELO_ARTIFACT,
    LONGEST_CAREERS_ARTIFACT,
    MAKUUCHI_RANK_BY_ERA_ARTIFACT,
    RANK_AT_RETIREMENT_ARTIFACT,
    STANDINGS_BY_WINS_ARTIFACT,
    EQUELO_VS_CHII_ARTIFACT,
)
from src.products.make_site2.publication_model import (
    artifact_refs,
    build_publication_plan,
)
from src.products.make_site2.render import render_site_shell
from src.products.make_site2.models import PageStatus
from src.products.make_site2.site_definition import SITE
from src.products.make_site2.site_manifest import (
    build_public_site_shell,
    build_runtime_manifest,
)


def content_panel_by_artifact(manifest: dict, artifact_id: str) -> dict:
    return next(
        panel
        for panel in manifest["ui"]["content_panels"]
        if panel["contents"]["pa_panel"]["pa"]["artifact_id"] == artifact_id
    )


def filter_section(panel: dict) -> dict:
    return panel["contents"]["filter_section"]


def note_ids(panel: dict) -> list[str]:
    return panel["contents"]["pa_panel"]["notes"]["note_ids"]


def test_publication_plan_resolves_copied_navigation_routes() -> None:
    plan = build_publication_plan(SITE)

    assert "basho_results_browser" in plan.pages
    assert plan.pages["basho_results_browser"].route.parts == (
        "home",
        "basho-results",
    )
    assert plan.pages["banzuke_changes"].route.parts == (
        "home",
        "banzuke-changes",
    )
    assert plan.pages["standings_by_wins"].route.parts == (
        "lab-archive",
        "standings-by-wins",
    )
    assert plan.pages["banzuke_division_by_era"].route.parts == (
        "miscellaneous-stats",
        "banzuke-division-by-era",
    )
    assert plan.pages["makuuchi_rank_by_era"].route.parts == (
        "miscellaneous-stats",
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
        "miscellaneous-stats",
        "rank-at-retirement",
    )
    assert plan.pages["career_length"].route.parts == (
        "miscellaneous-stats",
        "career-length",
    )
    assert plan.pages["equelo_vs_chii"].route.parts == (
        "equelo-ratings",
        "equelo-vs-chii",
    )
    assert "typical_equelo_values" not in plan.pages
    assert SITE.pages.pages["typical_equelo_values"].status == PageStatus.LEGACY
    assert plan.pages["highest_equelo"].route.parts == (
        "records",
        "highest-equelo",
    )
    assert plan.pages["longest_careers"].route.parts == (
        "records",
        "longest-careers",
    )


def test_navigation_bar_uses_canonical_default_view_links_without_rendering_pages() -> None:
    plan = build_publication_plan(SITE)
    shell = build_public_site_shell(plan)
    home = next(
        item for item in shell.navigation_bar.navigation_tree if item.id == "home"
    )
    basho_results = next(
        item for item in home.children if item.id == "quick_basho_results_browser"
    )
    banzuke_changes = next(
        item for item in home.children if item.id == "quick_banzuke_changes"
    )
    miscellaneous_stats = next(
        item
        for item in shell.navigation_bar.navigation_tree
        if item.id == "miscellaneous_stats"
    )
    career_length = next(
        item for item in miscellaneous_stats.children if item.id == "history_career_length"
    )
    rank_at_retirement = next(
        item for item in miscellaneous_stats.children if item.id == "rank_at_retirement"
    )
    banzuke_division_by_era = next(
        item for item in miscellaneous_stats.children if item.id == "banzuke_division_by_era"
    )
    makuuchi_rank_by_era = next(
        item for item in miscellaneous_stats.children if item.id == "makuuchi_rank_by_era"
    )
    banzuke_rank = next(
        item
        for item in shell.navigation_bar.research_navigation_tree
        if item.id == "banzuke_rank"
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
        item for item in shell.navigation_bar.navigation_tree if item.id == "equelo_ratings"
    )
    equelo_vs_chii = next(
        item for item in ratings_models.children if item.id == "equelo_vs_chii"
    )
    records = next(
        item for item in shell.navigation_bar.navigation_tree if item.id == "records"
    )
    highest_equelo = next(
        item for item in records.children if item.id == "highest_equelo"
    )
    longest_careers = next(
        item for item in records.children if item.id == "longest_careers"
    )
    lab_archive = next(
        item
        for item in shell.navigation_bar.research_navigation_tree
        if item.id == "research_lab_archive"
    )
    standings = next(
        item for item in lab_archive.children if item.id == "standings_by_wins"
    )

    assert basho_results.included
    assert basho_results.href == (
        "index.html?page=basho_results_browser&year=latest&month=latest"
        "&division=makuuchi&previous=false&changes=false&ratings=false"
        "&analysis=false&nu_chii=false"
    )
    assert rank_at_retirement.included
    assert rank_at_retirement.href == "index.html?page=rank_at_retirement"
    assert career_length.included
    assert career_length.href == "index.html?page=career_length&view=distribution"
    assert banzuke_changes.included
    assert banzuke_changes.href == (
        "index.html?page=banzuke_changes&division=makuuchi&context=false"
        "&banzuke_style=true&delta=false&equelo=false"
    )
    assert standings.included
    assert standings.href == (
        "index.html?page=standings_by_wins&view=standard&num_basho=6"
        "&current_only=true&division=makuuchi"
    )
    assert banzuke_division_by_era.included
    assert banzuke_division_by_era.href == "index.html?page=banzuke_division_by_era"
    assert makuuchi_rank_by_era.included
    assert makuuchi_rank_by_era.href == "index.html?page=makuuchi_rank_by_era"
    assert division_stability.included
    assert division_stability.href == "index.html?page=division_stability"
    assert first_chii_appearance.included
    assert first_chii_appearance.href == "index.html?page=first_chii_appearance"
    assert equelo_vs_chii.included
    assert equelo_vs_chii.href == "index.html?page=equelo_vs_chii"
    assert highest_equelo.included
    assert highest_equelo.href == "index.html?page=highest_equelo&current_only=false"
    assert longest_careers.included
    assert longest_careers.href == "index.html?page=longest_careers&active=true"
    assert [item.id for item in records.children][-1] == "longest_careers"
    assert artifact_refs(plan)["basho_results_browser"].kind == "table"


def test_site_shell_is_rendered_from_ui_manifest() -> None:
    shell = build_public_site_shell(build_publication_plan(SITE))
    html = render_site_shell(shell)

    assert '<div class="site-shell" data-nav-shell>' in html
    assert 'data-nav-shell' in html
    assert 'data-nav-toggle' in html
    assert 'gaspodeSumoLab.makeSite2.navCollapsed' in html
    assert '<nav id="site-nav" class="site-nav" data-nav-panel aria-label="Site navigation">' in html
    assert '<script type="module" src="runtime/site.js"></script>' in html
    assert 'data-page-id="basho_results_browser"' in html
    assert 'data-page-id="banzuke_changes"' in html
    assert 'data-page-id="standings_by_wins"' in html
    assert 'data-page-id="banzuke_division_by_era"' in html
    assert 'data-page-id="makuuchi_rank_by_era"' in html
    assert 'data-page-id="division_stability"' in html
    assert 'data-page-id="first_chii_appearance"' in html
    assert 'data-page-id="rank_at_retirement"' in html
    assert 'data-page-id="career_length"' in html
    assert 'data-page-id="typical_equelo_values"' not in html
    assert 'data-page-id="equelo_vs_chii"' in html
    assert 'data-page-id="highest_equelo"' in html
    assert 'data-page-id="longest_careers"' in html
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
    assert '<script type="module" src="runtime/site.js?cb=test-token"></script>' in html


def test_site_shell_uses_stable_runtime_assets_in_prod_mode() -> None:
    shell = build_public_site_shell(build_publication_plan(SITE))
    html = render_site_shell(shell, cache_mode="prod", cache_bust_token="test-token")

    assert "data-cache-bust" not in html
    assert '<link rel="stylesheet" href="runtime/site.css">' in html
    assert '<script type="module" src="runtime/site.js"></script>' in html


def test_runtime_manifest_declares_brb_ui_and_artifact_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    brb_panel = content_panel_by_artifact(manifest, BASHO_RESULTS_ARTIFACT.id)
    brb_artifact = manifest["artifacts"]["basho_results_browser"]
    filters = filter_section(brb_panel)["filters"]

    assert brb_panel["contents"]["pa_panel"]["pa"]["artifact_id"] == BASHO_RESULTS_ARTIFACT.id
    assert [item["id"] for item in filters] == [
        "basho_year",
        "basho_month",
        "division",
        "previous_context",
        "changes_context",
        "rating_context",
        "analysis_context",
        "nu_chii",
    ]
    assert filters[0]["control"] == "select"
    assert filters[1]["control"] == "select"
    assert filters[2]["control"] == "select"
    assert filters[3]["control"] == "checkbox"
    assert brb_artifact["kind"] == "indexed_table"
    assert brb_artifact["indexed_source"]["index_path"] == (
        "sumo-history/basho-results/data/basho_results_index.json"
    )


def test_runtime_manifest_declares_banzuke_changes_ui_and_artifact_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, BANZUKE_CHANGES_ARTIFACT.id)
    artifact = manifest["artifacts"]["banzuke_changes"]
    filters = filter_section(panel)["filters"]

    assert panel["contents"]["pa_panel"]["pa"]["artifact_id"] == BANZUKE_CHANGES_ARTIFACT.id
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
    filters = filter_section(panel)["filters"]

    assert panel["contents"]["pa_panel"]["pa"]["artifact_id"] == STANDINGS_BY_WINS_ARTIFACT.id
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
    assert artifact["data_sources"][5]["filter_value"] == "6"
    assert artifact["data_sources"][5]["path"].startswith(
        "current-sumo/standings-by-wins/data/multiple basho standings view "
    )
    assert artifact["data_sources"][5]["path"].endswith(", BACKWARDS, 6).csv")


def test_runtime_manifest_declares_banzuke_era_chart_semantics() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, BANZUKE_DIVISION_BY_ERA_ARTIFACT.id)
    artifact = manifest["artifacts"]["banzuke_division_by_era"]

    assert filter_section(panel) is None
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

    assert filter_section(panel) is None
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

    assert filter_section(panel) is None
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

    assert filter_section(panel) is None
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

    assert filter_section(panel) is None
    assert note_ids(panel) == ["rank_at_retirement"]
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


def test_runtime_manifest_declares_career_length_as_chart_view_selector() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, CAREER_LENGTH_ARTIFACT.id)
    artifact = manifest["artifacts"]["career_length"]
    filters = filter_section(panel)["filters"]

    assert [item["id"] for item in filters] == ["view"]
    assert filters[0]["control"] == "select"
    assert [item["value"] for item in filters[0]["values"]] == [
        "distribution",
        "pmf",
        "cdf",
        "survival",
    ]
    assert artifact["kind"] == "chart"
    assert artifact["renderer"] == "career_length"
    assert artifact["data_binding"] == {
        "kind": "csv_set",
        "sources": ["distribution", "pmf", "cdf", "survival"],
    }
    assert artifact["data_sources"][0]["path"] == (
        "sumo-history/career-lifecycle/career-length/data/distribution.csv"
    )
    assert artifact["provenance"]["views"]["distribution"]["kind"] == "stacked_bar"
    assert "longest" not in artifact["provenance"]["views"]


def test_runtime_manifest_declares_longest_careers_records_table() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, LONGEST_CAREERS_ARTIFACT.id)
    artifact = manifest["artifacts"]["longest_careers"]
    filters = filter_section(panel)["filters"]

    assert [item["id"] for item in filters] == ["show_active"]
    assert filters[0]["label"] == "Show Active?"
    assert filters[0]["control"] == "checkbox"
    assert filters[0]["default"] is True
    assert artifact["kind"] == "table"
    assert artifact["renderer"] == "generic_table"
    assert artifact["rows_source"]["path"] == (
        "sumo-history/records/longest-careers/data/longest.csv"
    )
    assert [column["id"] for column in artifact["columns"]] == [
        "row_number",
        "rank",
        "shikona",
        "first_appearance",
        "last_appearance",
        "participation_years",
        "gap_basho_count",
    ]
    assert artifact["columns"][1]["heading"] == "#"
    assert artifact["columns"][1]["sort_default_direction"] == "ascending"
    assert artifact["default_sort_column"] == "rank"
    assert note_ids(panel) == ["observed_career_length", "bg_count"]


def test_runtime_manifest_declares_equelo_vs_chii_prose() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, EQUELO_VS_CHII_ARTIFACT.id)
    artifact = manifest["artifacts"]["equelo_vs_chii"]

    assert filter_section(panel) is None
    assert note_ids(panel) == []
    assert artifact["kind"] == "prose"
    assert artifact["renderer"] == "prose"
    assert artifact["path"] == "prose/Equelo vs Chii.html"
    assert "typical_equelo_values" not in manifest["artifacts"]


def test_runtime_manifest_declares_highest_equelo_table() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    panel = content_panel_by_artifact(manifest, HIGHEST_EQUELO_ARTIFACT.id)
    artifact = manifest["artifacts"]["highest_equelo"]
    filters = filter_section(panel)["filters"]

    assert [item["id"] for item in filters] == ["current_only"]
    assert filters[0]["label"] == "Current only?"
    assert filters[0]["control"] == "checkbox"
    assert filters[0]["default"] is False
    assert artifact["kind"] == "table"
    assert artifact["renderer"] == "generic_table"
    assert artifact["rows_source"]["path"] == (
        "sumo-history/records/highest-equelo/data/highest_equelo.csv"
    )
    assert [column["id"] for column in artifact["columns"]] == [
        "row_number",
        "position",
        "shikona",
        "chii",
        "rating",
        "date",
    ]
    assert artifact["columns"][3]["sort_key"] == "chii_ordinal"
    assert artifact["columns"][3]["sort_kind"] == "chii_ordinal"
    assert artifact["default_sort_column"] == "position"


def test_brb_filter_defaults_and_url_keys_match_current_public_site() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    brb_panel = content_panel_by_artifact(manifest, BASHO_RESULTS_ARTIFACT.id)
    filters = {
        item["id"]: item for item in filter_section(brb_panel)["filters"]
    }

    assert filters["basho_year"]["default"] == "latest"
    assert filters["basho_year"]["control"] == "select"
    assert filters["basho_year"]["url_key"] == "year"
    assert filters["basho_month"]["default"] == "latest"
    assert filters["basho_month"]["control"] == "select"
    assert filters["basho_month"]["url_key"] == "month"
    assert filters["division"]["default"] == "makuuchi"
    assert filters["division"]["control"] == "select"
    assert filters["division"]["url_key"] == "division"
    assert filters["previous_context"]["default"] is False
    assert filters["previous_context"]["control"] == "checkbox"
    assert filters["previous_context"]["url_key"] == "previous"
    assert filters["changes_context"]["default"] is False
    assert filters["changes_context"]["control"] == "checkbox"
    assert filters["changes_context"]["url_key"] == "changes"
    assert filters["rating_context"]["default"] is False
    assert filters["rating_context"]["control"] == "checkbox"
    assert filters["rating_context"]["url_key"] == "ratings"
    assert filters["analysis_context"]["default"] is False
    assert filters["analysis_context"]["control"] == "checkbox"
    assert filters["analysis_context"]["url_key"] == "analysis"
    assert filters["analysis_context"]["label"] == "Ratings Fit"
    assert filters["analysis_context"]["help"] == "See TBD"
    assert filters["nu_chii"]["default"] is False
    assert filters["nu_chii"]["control"] == "checkbox"
    assert filters["nu_chii"]["url_key"] == "nu_chii"


def test_brb_notes_cover_current_context_columns() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))
    brb_artifact = manifest["artifacts"]["basho_results_browser"]

    assert {item["id"] for item in brb_artifact["notes"]} >= {
        "note_result",
        "note_movement",
    }

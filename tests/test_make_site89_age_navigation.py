from src.products.make_site89.manifest.builder import build_public_site_shell, build_runtime_manifest
from src.products.make_site89.publication_model import build_publication_plan
from src.products.make_site89.render import render_site_shell
from src.products.make_site89.site_definition import SITE


def test_age_contains_average_age_by_division_in_research_navigation() -> None:
    shell = build_public_site_shell(build_publication_plan(SITE))
    public_items = shell.navigation_bar.navigation_tree
    items = shell.navigation_bar.research_navigation_tree
    age = next(item for item in items if item.id == "age")

    assert "age" not in {item.id for item in public_items}
    assert age.label == "Age"
    assert age.href is None
    assert len(age.children) == 2
    artifact = age.children[0]
    assert artifact.id == "average_age_by_division"
    assert artifact.included
    assert artifact.href == "index.html?page=average_age_by_division&error_bars=false"
    prospects = age.children[1]
    assert prospects.id == "prospects"
    assert prospects.included
    assert prospects.href == "index.html?page=prospects"
    assert [item.id for item in items].index("age") == [item.id for item in items].index("rikishi") + 1
    assert '<span class="nav-label">Age</span>' in render_site_shell(shell)

    manifest = build_runtime_manifest(build_publication_plan(SITE))
    declared = manifest["artifacts"]["average_age_by_division"]
    assert declared["renderer"] == "grouped_line_chart"
    assert declared["traces"][0]["error_y"] == ["min_age_years", "max_age_years"]
    assert declared["provenance"]["default_visible"] == ["Makuuchi"]
    assert any(
        note["id"] == "average_age_jonokuchi_may"
        and "influx of newcomers each May" in note["text"]
        for note in declared["notes"]
    )
    panel = next(
        panel for panel in manifest["ui"]["content_panels"]
        if panel["page_id"] == "average_age_by_division"
    )
    error_bars = panel["contents"]["filter_section"]["filters"][0]
    assert error_bars["id"] == "error_bars"
    assert error_bars["label"] == "Min & Max"
    assert error_bars["default"] is False

    prospects_artifact = manifest["artifacts"]["prospects"]
    assert prospects_artifact["renderer"] == "prospects"
    assert prospects_artifact["data_sources"][0]["path"] == "age/prospects/data/trajectory_master.json"

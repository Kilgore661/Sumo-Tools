from src.products.make_site89.manifest.artifacts import (
    PROMOTION_OZEKI_ARTIFACT,
    PROMOTION_YOKOZUNA_ARTIFACT,
)
from src.products.make_site89.publication_model import build_publication_plan
from src.products.make_site89.render import render_site_shell
from src.products.make_site89.site_definition import SITE
from src.products.make_site89.site_manifest import (
    build_public_site_shell,
    build_runtime_manifest,
)


def content_panel_by_artifact(manifest: dict, artifact_id: str) -> dict:
    return next(
        panel
        for panel in manifest["ui"]["content_panels"]
        if panel["contents"]["pa_panel"]["pa"]["artifact_id"] == artifact_id
    )


def test_promotion_pages_are_published_under_research() -> None:
    plan = build_publication_plan(SITE)
    shell = build_public_site_shell(plan)
    promotion = next(
        item
        for item in shell.navigation_bar.research_navigation_tree
        if item.id == "promotion"
    )

    assert plan.pages["promotion_yokozuna"].route.parts == (
        "promotion",
        "yokozuna",
    )
    assert plan.pages["promotion_ozeki"].route.parts == (
        "promotion",
        "ozeki",
    )
    assert [item.label for item in promotion.children] == ["Yokozuna", "Ozeki"]
    assert [item.href for item in promotion.children] == [
        "index.html?page=promotion_yokozuna",
        "index.html?page=promotion_ozeki",
    ]
    assert all(item.included for item in promotion.children)


def test_promotion_pages_use_the_existing_prose_renderer() -> None:
    manifest = build_runtime_manifest(build_publication_plan(SITE))

    expected = (
        (PROMOTION_YOKOZUNA_ARTIFACT, "prose/YokYDJ.html"),
        (PROMOTION_OZEKI_ARTIFACT, "prose/Ozeki32.html"),
    )
    for artifact, path in expected:
        panel = content_panel_by_artifact(manifest, artifact.id)
        declared = manifest["artifacts"][artifact.id]

        assert panel["contents"]["pa_panel"]["pa"]["artifact_id"] == artifact.id
        assert declared["kind"] == "prose"
        assert declared["renderer"] == "prose"
        assert declared["path"] == path


def test_promotion_links_are_rendered_in_the_site_shell() -> None:
    shell = build_public_site_shell(build_publication_plan(SITE))
    html = render_site_shell(shell)

    assert 'data-page-id="promotion_yokozuna"' in html
    assert 'data-page-id="promotion_ozeki"' in html

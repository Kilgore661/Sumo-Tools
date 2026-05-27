from src.products.make_site2.publication_model import NavigationItem, build_publication_plan
from src.products.make_site2.render import render_site_shell
from src.products.make_site2.site_definition import SITE
from src.products.make_site2.site_manifest import build_public_site_shell
from src.products.make_site2.ui_model import (
    NavigationBar,
    NavigationCollapseControl,
    PublicSiteShell,
)


def test_navigation_hider_is_structural_part_of_navigation_bar() -> None:
    shell = PublicSiteShell(
        navigation_bar=NavigationBar(
            heading="Gaspode-san's\nSumo Lab",
            quick_links=(),
            navigation_tree=(
                NavigationItem(
                    id="one",
                    label="One",
                    slug="one",
                    page_id="one",
                    href="?page=one",
                    included=True,
                ),
            ),
            collapse_control=NavigationCollapseControl(
                enabled=True,
                storage_key="test.nav",
            ),
        ),
        content_panels=(),
    )

    html = render_site_shell(shell)

    assert '<nav id="site-nav" class="site-nav" data-nav-panel' in html
    assert '<div class="nav-hider-strip">' in html
    assert '<button type="button" class="nav-toggle" data-nav-toggle' in html
    assert '<div id="site-nav-content" class="nav-content" data-nav-content>' in html
    assert 'aria-controls="site-nav-content"' in html
    assert html.index('<div class="nav-hider-strip">') < html.index(
        '<div id="site-nav-content" class="nav-content" data-nav-content>'
    )


def test_home_navigation_node_links_to_landing_page() -> None:
    shell = build_public_site_shell(build_publication_plan(SITE))
    home = next(item for item in shell.navigation_bar.navigation_tree if item.id == "home")
    html = render_site_shell(shell)

    assert home.href == "index.html"
    assert home.page_id is None
    assert '<a class="nav-link" href="index.html">Home</a>' in html
    assert 'href="index.html" data-page-id' not in html


def test_page_summary_can_carry_trusted_inline_html() -> None:
    shell = build_public_site_shell(build_publication_plan(SITE))
    panel = next(panel for panel in shell.content_panels if panel.page_id == "first_chii_appearance")

    assert (
        '<a href="https://sumodb.sumogames.de/">SumoDB</a> for each chii.'
        in panel.heading.summary
    )

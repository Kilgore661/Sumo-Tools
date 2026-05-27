from src.products.make_site2.publication_model import NavigationItem
from src.products.make_site2.render import render_site_shell
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

"""Static asset declarations for the public site."""

from __future__ import annotations

from .site_config import ANALYSIS_ROOT, PRODUCT_ROOT
from .site_refs import asset


GLOBAL_ASSETS = (
    asset(
        id="site_shell_css",
        source_path=PRODUCT_ROOT / "files" / "site-shell.css",
        output_path="site-shell.css",
        media_type="text/css",
    ),
    asset(
        id="site_shell_js",
        source_path=PRODUCT_ROOT / "files" / "site-shell.js",
        output_path="site-shell.js",
        media_type="application/javascript",
    ),
    asset(
        id="nav_toggle_js",
        source_path=PRODUCT_ROOT / "files" / "nav-toggle.js",
        output_path="nav-toggle.js",
        media_type="application/javascript",
    ),
    asset(
        id="site_page_css",
        source_path=PRODUCT_ROOT / "files" / "site-page.css",
        output_path="site-page.css",
        media_type="text/css",
    ),
    asset(
        id="site_wide_css",
        source_path=ANALYSIS_ROOT / "common" / "files" / "site-wide.css",
        output_path="common/files/site-wide.css",
        media_type="text/css",
    ),
    asset(
        id="tool_layout_css",
        source_path=ANALYSIS_ROOT / "common" / "files" / "tool-layout.css",
        output_path="common/files/tool-layout.css",
        media_type="text/css",
    ),
)


STANDINGS_ASSETS = (
    asset(
        id="standings_css",
        source_path=ANALYSIS_ROOT / "standings" / "files" / "standings.css",
        output_path="current-sumo/standings-by-wins/standings.css",
        media_type="text/css",
    ),
    asset(
        id="standings_js",
        source_path=ANALYSIS_ROOT / "standings" / "files" / "standings.js",
        output_path="current-sumo/standings-by-wins/standings.js",
        media_type="application/javascript",
    ),
)


BANZUKE_CHANGES_ASSETS = (
    asset(
        id="banzuke_changes_css",
        source_path=ANALYSIS_ROOT
        / "banzuke_compare"
        / "files"
        / "banzuke_change_report.css",
        output_path="current-sumo/banzuke-changes/banzuke_change_report.css",
        media_type="text/css",
    ),
    asset(
        id="banzuke_changes_js",
        source_path=ANALYSIS_ROOT
        / "banzuke_compare"
        / "files"
        / "banzuke_change_report.js",
        output_path="current-sumo/banzuke-changes/banzuke_change_report.js",
        media_type="application/javascript",
    ),
)

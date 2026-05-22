"""Experimental PA-manifest runtime skeleton writer."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, is_dataclass
from html import escape
from pathlib import Path
from typing import Any, Mapping

from .classes import NavigationTree, Site, SiteBuildConfig
from .filesystem import copy_file
from .pa_manifest import ACTIVE_PA_MANIFESTS
from .routes import PageRoute, html_href
from .site_config import PRODUCT_ROOT
from .site_urls import cache_busted_url


RUNTIME_DIR = "runtime-skeleton"
RUNTIME_ASSET_VERSION = "20260514-dev-cache"


def write_pa_runtime_skeleton(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    build_stamp: str,
    cache_bust_token: str,
) -> None:
    """Write a parallel shell showing the intended PA-manifest runtime shape."""

    root = config.output_root / RUNTIME_DIR
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    write_manifest_files(root)
    write_runtime_assets(root)
    write_runtime_index(site, config, page_routes, root, build_stamp, cache_bust_token)
    for page_id, page_route in page_routes.items():
        if page_id in ACTIVE_PA_MANIFESTS:
            write_runtime_page(
                site,
                config,
                page_routes,
                root,
                page_id,
                page_route,
                build_stamp,
                cache_bust_token,
            )
            copy_runtime_page_data(root, page_route)


def copy_runtime_page_data(root: Path, page_route: PageRoute) -> None:
    for data_ref in page_route.page.data:
        target_path = root / Path(data_ref.output_path.as_posix())
        copy_file(data_ref.source_path, target_path)


def write_manifest_files(root: Path) -> None:
    manifests_dir = root / "manifests"
    manifests_dir.mkdir()
    index: dict[str, str] = {}
    for page_id, manifest in sorted(ACTIVE_PA_MANIFESTS.items()):
        manifest_path = manifests_dir / f"{page_id}.json"
        manifest_path.write_text(
            json.dumps(tagged_manifest(page_id, manifest), indent=2),
            encoding="utf-8",
        )
        index[page_id] = f"manifests/{page_id}.json"
    (root / "manifest-index.json").write_text(
        json.dumps(index, indent=2),
        encoding="utf-8",
    )


def tagged_manifest(page_id: str, manifest: Any) -> dict[str, Any]:
    manifest.validate()
    return {
        "tag": page_id,
        "manifest_class": type(manifest).__name__,
        "manifest": dataclass_to_plain(manifest),
    }


def dataclass_to_plain(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, tuple):
        return [dataclass_to_plain(item) for item in value]
    if isinstance(value, list):
        return [dataclass_to_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: dataclass_to_plain(item) for key, item in value.items()}
    return value


def write_runtime_assets(root: Path) -> None:
    copy_file(PRODUCT_ROOT / "files" / "site-page.css", root / "site-page.css")
    copy_file(PRODUCT_ROOT / "files" / "pa-runtime.css", root / "pa-runtime.css")
    copy_file(PRODUCT_ROOT / "files" / "site-url.js", root / "site-url.js")
    copy_file(PRODUCT_ROOT / "files" / "pa-runtime.js", root / "pa-runtime.js")
    copy_file(PRODUCT_ROOT / "files" / "nav-toggle.js", root / "nav-toggle.js")


def write_runtime_index(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    root: Path,
    build_stamp: str,
    cache_bust_token: str,
) -> None:
    write_runtime_shell_html(
        site=site,
        config=config,
        page_routes=page_routes,
        target_path=root / "index.html",
        selected_page_id="",
        asset_prefix="",
        build_stamp=build_stamp,
        cache_bust_token=cache_bust_token,
    )


def write_runtime_page(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    root: Path,
    page_id: str,
    page_route: PageRoute,
    build_stamp: str,
    cache_bust_token: str,
) -> None:
    target_path = root.joinpath(*page_route.parts, "index.html")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    asset_prefix = "../" * len(page_route.parts)
    write_runtime_shell_html(
        site=site,
        config=config,
        page_routes=page_routes,
        target_path=target_path,
        selected_page_id=page_id,
        asset_prefix=asset_prefix,
        build_stamp=build_stamp,
        cache_bust_token=cache_bust_token,
    )


def write_embedded_runtime_page(
    page_route: PageRoute,
    config: SiteBuildConfig,
    build_stamp: str,
    cache_bust_token: str,
) -> None:
    """Write one PA-manifest page for use inside the normal site shell."""

    output_root = config.output_root
    target_path = output_root.joinpath(*page_route.parts, "index.html")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    asset_prefix = "../" * len(page_route.parts)
    page = page_route.page
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(page.title)}</title>",
            (
                '<link rel="stylesheet" '
                f'href="{escape(cache_busted_url(f"{asset_prefix}site-page.css?v={RUNTIME_ASSET_VERSION}", config, cache_bust_token))}">'
            ),
            (
                '<link rel="stylesheet" '
                f'href="{escape(cache_busted_url(f"{asset_prefix}pa-runtime.css?v={RUNTIME_ASSET_VERSION}", config, cache_bust_token))}">'
            ),
            "</head>",
            (
                f'<body class="runtime-embedded" data-selected-page-id="{escape(page.id)}" '
                f'data-runtime-root="{escape(asset_prefix)}" '
                f'data-page-summary="{escape(page.summary)}" '
                f'data-cache-mode="{escape(config.cache_mode)}" '
                f'data-cache-bust="{escape(cache_bust_token)}" '
                f'data-cache-bust-param="{escape(config.cache_bust_param)}" '
                f'data-deep-link-page-param="{escape(config.deep_link_page_param)}">'
            ),
            '<main class="runtime-main">',
            '<header class="runtime-header">',
            '<h1 id="page-heading"></h1>',
            '<p id="page-summary" class="runtime-note"></p>',
            "</header>",
            '<section class="runtime-content">',
            '<aside id="options-panel" class="runtime-options"></aside>',
            '<section id="pa-panel" class="runtime-pa"></section>',
            "</section>",
            "</main>",
            f'<script src="{escape(cache_busted_url(f"{asset_prefix}site-url.js?v={RUNTIME_ASSET_VERSION}", config, cache_bust_token))}"></script>',
            f'<script src="{escape(cache_busted_url(f"{asset_prefix}pa-runtime.js?v={RUNTIME_ASSET_VERSION}", config, cache_bust_token))}"></script>',
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


def write_runtime_shell_html(
    *,
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    target_path: Path,
    selected_page_id: str,
    asset_prefix: str,
    build_stamp: str,
    cache_bust_token: str,
) -> None:
    title = site.pages.pages[selected_page_id].title if selected_page_id else site.title
    page_summary = (
        site.pages.pages[selected_page_id].summary
        if selected_page_id
        else ""
    )
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(title)}</title>",
            (
                '<link rel="stylesheet" '
                f'href="{escape(cache_busted_url(f"{asset_prefix}site-page.css?v={RUNTIME_ASSET_VERSION}", config, cache_bust_token))}">'
            ),
            (
                '<link rel="stylesheet" '
                f'href="{escape(cache_busted_url(f"{asset_prefix}pa-runtime.css?v={RUNTIME_ASSET_VERSION}", config, cache_bust_token))}">'
            ),
            "</head>",
            (
                f'<body data-selected-page-id="{escape(selected_page_id)}" '
                f'data-runtime-root="{escape(asset_prefix)}" '
                f'data-page-summary="{escape(page_summary)}" '
                f'data-cache-mode="{escape(config.cache_mode)}" '
                f'data-cache-bust="{escape(cache_bust_token)}" '
                f'data-cache-bust-param="{escape(config.cache_bust_param)}" '
                f'data-deep-link-page-param="{escape(config.deep_link_page_param)}">'
            ),
            '<div class="runtime-shell" data-nav-shell>',
            (
                '<button type="button" class="nav-toggle" data-nav-toggle '
                'aria-controls="site-nav" aria-expanded="true" '
                'aria-label="Hide navigation" title="Hide navigation">&lt;</button>'
            ),
            '<aside id="site-nav" class="runtime-nav" data-nav-panel aria-label="Site navigation">',
            f"<h2>{escape(site.title)}</h2>",
            f'<p class="runtime-note">{escape(build_stamp)}</p>',
            render_runtime_navigation(site.navigation, config, page_routes, cache_bust_token),
            "</aside>",
            '<main class="runtime-main">',
            '<header class="runtime-header">',
            '<h1 id="page-heading"></h1>',
            '<p id="page-summary" class="runtime-note"></p>',
            "</header>",
            '<section class="runtime-content">',
            '<aside id="options-panel" class="runtime-options"></aside>',
            '<section id="pa-panel" class="runtime-pa"></section>',
            "</section>",
            "</main>",
            "</div>",
            f'<script src="{escape(cache_busted_url(f"{asset_prefix}nav-toggle.js?v={RUNTIME_ASSET_VERSION}", config, cache_bust_token))}"></script>',
            f'<script src="{escape(cache_busted_url(f"{asset_prefix}site-url.js?v={RUNTIME_ASSET_VERSION}", config, cache_bust_token))}"></script>',
            f'<script src="{escape(cache_busted_url(f"{asset_prefix}pa-runtime.js?v={RUNTIME_ASSET_VERSION}", config, cache_bust_token))}"></script>',
            "</body>",
            "</html>",
            "",
        )
    )
    target_path.write_text(html, encoding="utf-8")


def render_runtime_navigation(
    node: NavigationTree,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    cache_bust_token: str,
) -> str:
    children = "".join(
        render_runtime_navigation_node(child, config, page_routes, cache_bust_token)
        for child in node.children
    )
    return f"<ol>{children}</ol>"


def render_runtime_navigation_node(
    node: NavigationTree,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    cache_bust_token: str,
) -> str:
    label = escape(node.label)
    if node.page_id is None or node.page_id not in ACTIVE_PA_MANIFESTS:
        heading = f"<span>{label}</span>"
    else:
        route = page_routes[node.page_id]
        href = cache_busted_url(
            html_href(f"{config.base_route.rstrip('/')}/{RUNTIME_DIR}", route.parts),
            config,
            cache_bust_token,
        )
        heading = (
            f'<a href="{escape(href)}" data-page-id="{escape(node.page_id)}">'
            f"{label}</a>"
        )
    children = "".join(
        render_runtime_navigation_node(child, config, page_routes, cache_bust_token)
        for child in node.children
    )
    if children:
        return f"<li>{heading}<ol>{children}</ol></li>"
    return f"<li>{heading}</li>"



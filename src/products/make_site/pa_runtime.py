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


RUNTIME_DIR = "runtime-skeleton"
RUNTIME_ASSET_VERSION = "20260509-pa-runtime-skeleton"


def write_pa_runtime_skeleton(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    build_stamp: str,
) -> None:
    """Write a parallel shell showing the intended PA-manifest runtime shape."""

    root = config.output_root / RUNTIME_DIR
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    write_manifest_files(root)
    write_runtime_assets(root)
    write_runtime_index(site, config, page_routes, root, build_stamp)
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
    copy_file(PRODUCT_ROOT / "files" / "pa-runtime.css", root / "pa-runtime.css")
    copy_file(PRODUCT_ROOT / "files" / "pa-runtime.js", root / "pa-runtime.js")


def write_runtime_index(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    root: Path,
    build_stamp: str,
) -> None:
    write_runtime_shell_html(
        site=site,
        config=config,
        page_routes=page_routes,
        target_path=root / "index.html",
        selected_page_id="",
        asset_prefix="",
        build_stamp=build_stamp,
    )


def write_runtime_page(
    site: Site,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
    root: Path,
    page_id: str,
    page_route: PageRoute,
    build_stamp: str,
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
    )


def write_embedded_runtime_page(
    page_route: PageRoute,
    output_root: Path,
    build_stamp: str,
) -> None:
    """Write one PA-manifest page for use inside the normal site shell."""

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
            f'<link rel="stylesheet" href="{asset_prefix}pa-runtime.css?v={RUNTIME_ASSET_VERSION}">',
            "</head>",
            (
                f'<body class="runtime-embedded" data-selected-page-id="{escape(page.id)}" '
                f'data-runtime-root="{escape(asset_prefix)}">'
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
            f'<script src="{asset_prefix}pa-runtime.js?v={RUNTIME_ASSET_VERSION}"></script>',
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
) -> None:
    title = site.pages.pages[selected_page_id].title if selected_page_id else site.title
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(title)}</title>",
            f'<link rel="stylesheet" href="{asset_prefix}pa-runtime.css?v={RUNTIME_ASSET_VERSION}">',
            "</head>",
            (
                f'<body data-selected-page-id="{escape(selected_page_id)}" '
                f'data-runtime-root="{escape(asset_prefix)}">'
            ),
            '<div class="runtime-shell">',
            '<aside id="site-nav" class="runtime-nav" aria-label="Site navigation">',
            f"<h2>{escape(site.title)}</h2>",
            f'<p class="runtime-note">{escape(build_stamp)}</p>',
            render_runtime_navigation(site.navigation, config, page_routes),
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
            f'<script src="{asset_prefix}pa-runtime.js?v={RUNTIME_ASSET_VERSION}"></script>',
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
) -> str:
    children = "".join(
        render_runtime_navigation_node(child, config, page_routes)
        for child in node.children
    )
    return f"<ol>{children}</ol>"


def render_runtime_navigation_node(
    node: NavigationTree,
    config: SiteBuildConfig,
    page_routes: Mapping[str, PageRoute],
) -> str:
    label = escape(node.label)
    if node.page_id is None or node.page_id not in ACTIVE_PA_MANIFESTS:
        heading = f"<span>{label}</span>"
    else:
        route = page_routes[node.page_id]
        href = html_href(f"{config.base_route.rstrip('/')}/{RUNTIME_DIR}", route.parts)
        heading = (
            f'<a href="{escape(href)}" data-page-id="{escape(node.page_id)}">'
            f"{label}</a>"
        )
    children = "".join(
        render_runtime_navigation_node(child, config, page_routes)
        for child in node.children
    )
    if children:
        return f"<li>{heading}<ol>{children}</ol></li>"
    return f"<li>{heading}</li>"



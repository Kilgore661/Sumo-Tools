"""Build the static public site output tree."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .classes import (
    AssetRef,
    CustomView,
    DataRef,
    EssayView,
    PlotlyJsonView,
    Site,
    SiteBuildConfig,
    StandaloneHtmlView,
    TableAppView,
    ViewRef,
)
from .filesystem import clear_dir, copy_file
from .pa_runtime import (
    write_embedded_runtime_page,
    write_manifest_files,
    write_pa_runtime_skeleton,
    write_runtime_assets,
)
from .render import (
    write_custom_page,
    write_plotly_json_page,
    write_site_index,
)
from .routes import PageRoute, derive_page_routes


def build_site(site: Site, config: SiteBuildConfig) -> None:
    page_routes = derive_page_routes(site)
    build_stamp = datetime.now().strftime("Generated %Y-%m-%d %H:%M")
    clear_dir(config.output_root)
    write_site_index(site, config, page_routes, build_stamp)
    copy_file_refs(site.global_assets, config.output_root)
    write_manifest_files(config.output_root)
    write_runtime_assets(config.output_root)
    for page_route in page_routes.values():
        write_page(page_route, config.output_root, build_stamp)
        copy_file_refs(page_route.page.assets, config.output_root)
        copy_file_refs(page_route.page.data, config.output_root)
    write_pa_runtime_skeleton(site, config, page_routes, build_stamp)


def write_page(page_route: PageRoute, output_root: Path, build_stamp: str) -> None:
    target_path = output_root.joinpath(*page_route.parts, "index.html")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    asset_prefix = "../" * len(page_route.parts)
    match page_route.page.view:
        case StandaloneHtmlView(source=source):
            copy_view(source, target_path)
        case TableAppView(entrypoint=entrypoint):
            copy_view(entrypoint, target_path)
        case EssayView(source=source):
            copy_view(source, target_path)
        case PlotlyJsonView(data=data, template=template, config=config):
            write_plotly_json_page(page_route.page, data, template, config, target_path)
        case CustomView(kind="pa_runtime_page"):
            write_embedded_runtime_page(page_route, output_root, build_stamp)
        case CustomView(kind=kind):
            write_custom_page(page_route.page, kind, target_path, asset_prefix)


def copy_view(view_ref: ViewRef, target_path: Path) -> None:
    copy_file(view_ref.source_path, target_path)


def copy_file_refs(
    file_refs: tuple[AssetRef, ...] | tuple[DataRef, ...],
    output_root: Path,
) -> None:
    for file_ref in file_refs:
        target_path = output_root / Path(file_ref.output_path.as_posix())
        copy_file(file_ref.source_path, target_path)

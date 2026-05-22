"""Build the static public site output tree."""

from __future__ import annotations

from datetime import datetime
from html.parser import HTMLParser
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
from .site_urls import cache_busted_url


def build_site(site: Site, config: SiteBuildConfig) -> None:
    page_routes = derive_page_routes(site)
    build_time = datetime.now()
    build_stamp = build_time.strftime("Generated %Y-%m-%d %H:%M")
    cache_bust_token = build_time.strftime("%Y%m%d-%H%M%S")
    clear_dir(config.output_root)
    write_site_index(site, config, page_routes, build_stamp, cache_bust_token)
    copy_file_refs(site.global_assets, config.output_root)
    write_manifest_files(config.output_root)
    write_runtime_assets(config.output_root)
    for page_route in page_routes.values():
        write_page(page_route, config, build_stamp, cache_bust_token)
        copy_file_refs(page_route.page.assets, config.output_root)
        copy_file_refs(page_route.page.data, config.output_root)
    write_pa_runtime_skeleton(site, config, page_routes, build_stamp, cache_bust_token)


def write_page(
    page_route: PageRoute,
    config: SiteBuildConfig,
    build_stamp: str,
    cache_bust_token: str,
) -> None:
    output_root = config.output_root
    target_path = output_root.joinpath(*page_route.parts, "index.html")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    asset_prefix = "../" * len(page_route.parts)
    match page_route.page.view:
        case StandaloneHtmlView(source=source):
            copy_view(source, target_path)
        case TableAppView(entrypoint=entrypoint):
            copy_html_view_with_cache_busted_assets(
                entrypoint,
                target_path,
                config,
                cache_bust_token,
            )
        case EssayView(source=source):
            copy_view(source, target_path)
        case PlotlyJsonView(data=data, template=template, config=config):
            write_plotly_json_page(page_route.page, data, template, config, target_path)
        case CustomView(kind="pa_runtime_page"):
            write_embedded_runtime_page(page_route, config, build_stamp, cache_bust_token)
        case CustomView(kind=kind):
            write_custom_page(page_route.page, kind, target_path, asset_prefix)


def copy_view(view_ref: ViewRef, target_path: Path) -> None:
    copy_file(view_ref.source_path, target_path)


def copy_html_view_with_cache_busted_assets(
    view_ref: ViewRef,
    target_path: Path,
    config: SiteBuildConfig,
    cache_bust_token: str,
) -> None:
    html = view_ref.source_path.read_text(encoding="utf-8")
    html = cache_bust_html_assets(html, config, cache_bust_token)
    target_path.write_text(html, encoding="utf-8")


def cache_bust_html_assets(
    html: str,
    config: SiteBuildConfig,
    cache_bust_token: str,
) -> str:
    parser = AssetUrlRewriter(config, cache_bust_token)
    parser.feed(html)
    parser.close()
    return parser.html()


class AssetUrlRewriter(HTMLParser):
    """Add dev cache-bust params to local HTML asset URLs."""

    ASSET_ATTRS = {
        "link": {"href"},
        "script": {"src"},
    }

    def __init__(self, config: SiteBuildConfig, cache_bust_token: str) -> None:
        super().__init__(convert_charrefs=False)
        self.config = config
        self.cache_bust_token = cache_bust_token
        self.parts: list[str] = []

    def html(self) -> str:
        return "".join(self.parts)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append(self.render_tag(tag, attrs, closed=False))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.parts.append(self.render_tag(tag, attrs, closed=True))

    def handle_endtag(self, tag: str) -> None:
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.parts.append(f"<!{decl}>")

    def handle_pi(self, data: str) -> None:
        self.parts.append(f"<?{data}>")

    def render_tag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
        *,
        closed: bool,
    ) -> str:
        asset_attrs = self.ASSET_ATTRS.get(tag.lower(), set())
        rendered_attrs = []
        for name, value in attrs:
            if value is not None and name.lower() in asset_attrs:
                value = self.rewrite_asset_url(value)
            rendered_attrs.append(self.render_attr(name, value))
        suffix = " />" if closed else ">"
        return f"<{tag}{''.join(rendered_attrs)}{suffix}"

    def render_attr(self, name: str, value: str | None) -> str:
        if value is None:
            return f" {name}"
        escaped = (
            value.replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return f' {name}="{escaped}"'

    def rewrite_asset_url(self, url: str) -> str:
        if not is_local_asset_url(url):
            return url
        return cache_busted_url(url, self.config, self.cache_bust_token)


def is_local_asset_url(url: str) -> bool:
    lowered = url.lower()
    if lowered.startswith(("http://", "https://", "//", "data:", "mailto:", "#")):
        return False
    return True


def copy_file_refs(
    file_refs: tuple[AssetRef, ...] | tuple[DataRef, ...],
    output_root: Path,
) -> None:
    for file_ref in file_refs:
        target_path = output_root / Path(file_ref.output_path.as_posix())
        copy_file(file_ref.source_path, target_path)

"""Build the make_site89 static output tree from produced site data."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from .bundle import copy_site_data_bundle, load_site_data_bundle
from .models import BuildOutput
from .publication_model import build_publication_plan
from .render import render_site_shell
from .site_definition import SITE
from .site_manifest import build_public_site_shell, build_runtime_manifest


PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_ROOT.parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "files" / "output" / "make_site89"
RUNTIME_CSS_SOURCE_ROOT = PACKAGE_ROOT / "runtime" / "css"
RUNTIME_MODULE_SOURCE_ROOT = PACKAGE_ROOT / "runtime" / "site-refactor"
PROSE_SOURCE_ROOT = PACKAGE_ROOT / "prose"
INPUT_ASSET_ROOT = REPO_ROOT / "files" / "input"
OUTPUT_ASSET_ROOT_NAME = "assets"
STATIC_ASSETS = {
    "trash.svg": INPUT_ASSET_ROOT / "trash.svg",
    "eye.svg": INPUT_ASSET_ROOT / "eye.svg",
    "eye-closed.svg": INPUT_ASSET_ROOT / "eye-closed.svg",
    "start.svg": INPUT_ASSET_ROOT / "start.svg",
    "back.svg": INPUT_ASSET_ROOT / "back.svg",
    "next.svg": INPUT_ASSET_ROOT / "next.svg",
    "end.svg": INPUT_ASSET_ROOT / "end.svg",
}
MODULE_IMPORT_RE = re.compile(
    r'(?P<prefix>(?:from\s+|import\s+)["\'])(?P<path>\.{1,2}/[^"\']+\.js)(?P<suffix>["\'])'
)


def build_site(
    *,
    data_bundle: Path,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    cache_mode: str = "dev",
    cache_bust_token: str | None = None,
) -> BuildOutput:
    """Build make_site89 using only an already-produced site-data bundle."""

    if cache_mode not in {"dev", "prod"}:
        raise ValueError(f"Unsupported cache mode: {cache_mode!r}")
    bundle = load_site_data_bundle(data_bundle)
    resolved_cache_bust_token = (
        cache_bust_token
        if cache_bust_token is not None
        else datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    )

    output_root.mkdir(parents=True, exist_ok=True)
    for child in output_root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    (output_root / "runtime").mkdir(parents=True, exist_ok=True)

    copy_site_data_bundle(bundle, output_root)
    plan = build_publication_plan(SITE)
    (output_root / "index.html").write_text(
        render_site_shell(
            build_public_site_shell(plan),
            cache_mode=cache_mode,
            cache_bust_token=resolved_cache_bust_token,
        ),
        encoding="utf-8",
    )
    runtime_manifest = build_runtime_manifest(plan)
    _materialise_standings_paths(runtime_manifest, bundle.site_root)
    (output_root / "runtime" / "site-manifest.json").write_text(
        json.dumps(runtime_manifest, indent=2),
        encoding="utf-8",
    )
    (output_root / "runtime" / "site-data-bundle.json").write_text(
        json.dumps(bundle.manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    shutil.copyfile(
        PACKAGE_ROOT / "runtime" / "site.css",
        output_root / "runtime" / "site.css",
    )
    copy_static_assets(output_root=output_root)
    copy_prose(output_root=output_root)
    copy_runtime_css(output_root=output_root)
    copy_runtime_modules(
        output_root=output_root,
        cache_mode=cache_mode,
        cache_bust_token=resolved_cache_bust_token,
    )
    return BuildOutput(
        root=output_root,
        entrypoint=output_root / "index.html",
        file_count=count_output_files(output_root),
    )


def copy_static_assets(*, output_root: Path) -> None:
    asset_output_root = output_root / OUTPUT_ASSET_ROOT_NAME
    asset_output_root.mkdir(parents=True, exist_ok=True)
    for output_name, source in STATIC_ASSETS.items():
        if not source.is_file():
            raise FileNotFoundError(f"Static asset not found: {source}")
        shutil.copyfile(source, asset_output_root / output_name)


def copy_prose(*, output_root: Path) -> None:
    if PROSE_SOURCE_ROOT.is_dir():
        shutil.copytree(PROSE_SOURCE_ROOT, output_root / "prose")


def copy_runtime_css(*, output_root: Path) -> None:
    shutil.copytree(RUNTIME_CSS_SOURCE_ROOT, output_root / "runtime" / "css")


def copy_runtime_modules(
    *, output_root: Path, cache_mode: str, cache_bust_token: str
) -> None:
    runtime_output_root = output_root / "runtime"
    for source_path in RUNTIME_MODULE_SOURCE_ROOT.rglob("*"):
        if not source_path.is_file() or source_path.name == "README.md":
            continue
        destination = runtime_output_root / source_path.relative_to(
            RUNTIME_MODULE_SOURCE_ROOT
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source_path.suffix == ".js" and cache_mode == "dev" and cache_bust_token:
            content = source_path.read_text(encoding="utf-8")
            destination.write_text(
                cache_bust_module_imports(content, cache_bust_token),
                encoding="utf-8",
            )
        else:
            shutil.copyfile(source_path, destination)


def cache_bust_module_imports(content: str, cache_bust_token: str) -> str:
    query = urlencode({"cb": cache_bust_token})
    return MODULE_IMPORT_RE.sub(
        lambda match: (
            f'{match.group("prefix")}{match.group("path")}?{query}'
            f'{match.group("suffix")}'
        ),
        content,
    )


def count_output_files(output_root: Path) -> int:
    return sum(1 for path in output_root.rglob("*") if path.is_file())


def _materialise_standings_paths(manifest: dict, site_root: Path) -> None:
    config_path = site_root / "current-sumo/standings-by-wins/data/site_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    anchor = config.get("anchor_token")
    if not isinstance(anchor, str) or not anchor:
        raise ValueError("Standings site config has no anchor_token")
    artifact = manifest["artifacts"]["standings_by_wins"]
    for source in artifact["data_sources"]:
        source["path"] = source["path"].replace("__ANCHOR_TOKEN__", anchor)
        source["metadata_path"] = source["metadata_path"].replace(
            "__ANCHOR_TOKEN__", anchor
        )

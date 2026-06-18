"""Build the first make_site2 static output tree."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from src.infra.live_store.api import get_history
from src.sumo_core.History import History

from .career_length_views import materialize_career_length_longest_views
from .data_output import (
    CAREER_LENGTH_SOURCE_ROOT,
    build_basho_results_data_output,
    build_career_comparisons_data_output,
    copy_banzuke_changes_data_output,
    copy_banzuke_division_by_era_data_output,
    copy_career_length_data_output,
    copy_division_stability_data_output,
    copy_first_chii_appearance_data_output,
    copy_finish_by_chii_data_output,
    copy_makuuchi_rank_by_era_data_output,
    copy_most_career_losses_data_output,
    copy_most_career_wins_data_output,
    copy_most_consecutive_bouts_data_output,
    copy_rank_at_retirement_data_output,
    copy_standings_by_wins_data_output,
    copy_typical_equelo_values_data_output,
    copy_win_probability_by_standing_data_output,
    load_history_from_zip,
)
from .models import BuildOutput
from .publication_model import build_publication_plan
from .render import render_site_shell
from .site_manifest import build_public_site_shell, build_runtime_manifest
from .site_definition import SITE


PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_ROOT.parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "files" / "output" / "make_site2"
RUNTIME_CSS_SOURCE_ROOT = PACKAGE_ROOT / "runtime" / "css"
RUNTIME_MODULE_SOURCE_ROOT = PACKAGE_ROOT / "runtime" / "site-refactor"
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
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    *,
    history: History | None = None,
    history_zip: Path | None = None,
    basho_results_payload_mode: str = "all",
    cache_mode: str = "dev",
    cache_bust_token: str | None = None,
    full_navigation: bool = False,
) -> BuildOutput:
    """Write the first make_site2 static output tree."""

    if cache_mode not in {"dev", "prod"}:
        raise ValueError(f"Unsupported cache mode: {cache_mode!r}")
    if history is not None and history_zip is not None:
        raise ValueError("Pass either history or history_zip, not both")
    resolved_history = (
        history
        if history is not None
        else load_history_from_zip(history_zip)
        if history_zip is not None
        else get_history()
    )
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

    build_basho_results_data_output(
        history=resolved_history,
        output_root=output_root,
        payload_mode=basho_results_payload_mode,
    )
    build_career_comparisons_data_output(
        history=resolved_history,
        output_root=output_root,
    )
    copy_banzuke_changes_data_output(output_root=output_root)
    copy_standings_by_wins_data_output(output_root=output_root)
    copy_finish_by_chii_data_output(output_root=output_root)
    copy_banzuke_division_by_era_data_output(output_root=output_root)
    copy_makuuchi_rank_by_era_data_output(output_root=output_root)
    copy_division_stability_data_output(output_root=output_root)
    copy_first_chii_appearance_data_output(output_root=output_root)
    copy_rank_at_retirement_data_output(output_root=output_root)
    copy_career_length_data_output(output_root=output_root)
    materialize_career_length_longest_views(
        output_root=output_root,
        source_root=CAREER_LENGTH_SOURCE_ROOT,
    )
    copy_most_consecutive_bouts_data_output(output_root=output_root)
    copy_most_career_wins_data_output(output_root=output_root)
    copy_most_career_losses_data_output(output_root=output_root)
    copy_typical_equelo_values_data_output(output_root=output_root)
    copy_win_probability_by_standing_data_output(output_root=output_root)
    plan = build_publication_plan(SITE)
    (output_root / "index.html").write_text(
        render_site_shell(
            build_public_site_shell(plan, full_navigation=full_navigation),
            cache_mode=cache_mode,
            cache_bust_token=resolved_cache_bust_token,
        ),
        encoding="utf-8",
    )
    (output_root / "runtime" / "site-manifest.json").write_text(
        json.dumps(
            build_runtime_manifest(plan, full_navigation=full_navigation),
            indent=2,
        ),
        encoding="utf-8",
    )
    shutil.copyfile(
        PACKAGE_ROOT / "runtime" / "site.css",
        output_root / "runtime" / "site.css",
    )
    copy_static_assets(output_root=output_root)
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
    """Copy source assets into the generated static site tree."""

    asset_output_root = output_root / OUTPUT_ASSET_ROOT_NAME
    asset_output_root.mkdir(parents=True, exist_ok=True)
    for output_name, source in STATIC_ASSETS.items():
        if not source.is_file():
            raise FileNotFoundError(f"Static asset not found: {source}")
        shutil.copyfile(source, asset_output_root / output_name)


def copy_runtime_css(*, output_root: Path) -> None:
    """Copy split runtime CSS files referenced by runtime/site.css imports."""

    shutil.copytree(
        RUNTIME_CSS_SOURCE_ROOT,
        output_root / "runtime" / "css",
    )


def copy_runtime_modules(
    *, output_root: Path, cache_mode: str, cache_bust_token: str
) -> None:
    """Copy modular browser runtime, preserving dev cache-bust behaviour."""

    runtime_output_root = output_root / "runtime"
    for source_path in RUNTIME_MODULE_SOURCE_ROOT.rglob("*"):
        if not source_path.is_file() or source_path.name == "README.md":
            continue
        destination = runtime_output_root / source_path.relative_to(RUNTIME_MODULE_SOURCE_ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source_path.suffix == ".js" and cache_mode == "dev" and cache_bust_token:
            content = source_path.read_text(encoding="utf-8")
            content = cache_bust_module_imports(content, cache_bust_token)
            destination.write_text(content, encoding="utf-8")
        else:
            shutil.copyfile(source_path, destination)


def cache_bust_module_imports(content: str, cache_bust_token: str) -> str:
    query = urlencode({"cb": cache_bust_token})
    return MODULE_IMPORT_RE.sub(
        lambda match: (
            f'{match.group("prefix")}{match.group("path")}?{query}{match.group("suffix")}'
        ),
        content,
    )


def count_output_files(output_root: Path) -> int:
    return sum(1 for path in output_root.rglob("*") if path.is_file())

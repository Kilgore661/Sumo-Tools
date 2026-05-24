"""Build the first make_site2 static output tree."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.infra.live_store.api import get_history
from src.sumo_core.History import History

from .data_output import (
    build_basho_results_data_output,
    copy_banzuke_changes_data_output,
    copy_banzuke_division_by_era_data_output,
    copy_career_length_data_output,
    copy_division_stability_data_output,
    copy_first_chii_appearance_data_output,
    copy_finish_by_chii_data_output,
    copy_makuuchi_rank_by_era_data_output,
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
RUNTIME_MODULE_SOURCE_ROOT = PACKAGE_ROOT / "runtime" / "site-refactor"


def build_site(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    *,
    history: History | None = None,
    history_zip: Path | None = None,
    basho_results_payload_mode: str = "all",
    cache_mode: str = "dev",
    cache_bust_token: str | None = None,
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
    copy_banzuke_changes_data_output(output_root=output_root)
    copy_standings_by_wins_data_output(output_root=output_root)
    copy_finish_by_chii_data_output(output_root=output_root)
    copy_banzuke_division_by_era_data_output(output_root=output_root)
    copy_makuuchi_rank_by_era_data_output(output_root=output_root)
    copy_division_stability_data_output(output_root=output_root)
    copy_first_chii_appearance_data_output(output_root=output_root)
    copy_rank_at_retirement_data_output(output_root=output_root)
    copy_career_length_data_output(output_root=output_root)
    copy_typical_equelo_values_data_output(output_root=output_root)
    copy_win_probability_by_standing_data_output(output_root=output_root)
    plan = build_publication_plan(SITE)
    (output_root / "index.html").write_text(
        render_site_shell(
            build_public_site_shell(plan),
            cache_mode=cache_mode,
            cache_bust_token=resolved_cache_bust_token,
        ),
        encoding="utf-8",
    )
    (output_root / "runtime" / "site-manifest.json").write_text(
        json.dumps(build_runtime_manifest(plan), indent=2),
        encoding="utf-8",
    )
    shutil.copyfile(
        PACKAGE_ROOT / "runtime" / "site.css",
        output_root / "runtime" / "site.css",
    )
    shutil.copytree(
        RUNTIME_MODULE_SOURCE_ROOT,
        output_root / "runtime",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("README.md"),
    )
    return BuildOutput(
        root=output_root,
        entrypoint=output_root / "index.html",
        file_count=count_output_files(output_root),
    )


def count_output_files(output_root: Path) -> int:
    return sum(1 for path in output_root.rglob("*") if path.is_file())

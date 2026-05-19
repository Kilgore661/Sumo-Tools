"""Build the first make_site2 static output tree."""

from __future__ import annotations

import shutil
import json
from pathlib import Path

from .data_output import build_basho_results_data_output
from .publication_model import build_publication_plan
from .render import render_site_shell
from .site_manifest import build_public_site_shell, build_runtime_manifest
from .site_definition import SITE


PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_ROOT.parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "files" / "output" / "make_site2"
DEFAULT_HISTORY_ZIP = REPO_ROOT / "files" / "output" / "Historys" / "1978_01 to 1980_11.zip"


def build_site(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    *,
    history_zip: Path = DEFAULT_HISTORY_ZIP,
    basho_results_payload_mode: str = "all",
) -> Path:
    """Write the first make_site2 static output tree."""

    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "runtime").mkdir(parents=True, exist_ok=True)

    build_basho_results_data_output(
        history_zip=history_zip,
        output_root=output_root,
        payload_mode=basho_results_payload_mode,
    )
    plan = build_publication_plan(SITE)
    (output_root / "index.html").write_text(
        render_site_shell(build_public_site_shell(plan)),
        encoding="utf-8",
    )
    (output_root / "runtime" / "site-manifest.json").write_text(
        json.dumps(build_runtime_manifest(plan), indent=2),
        encoding="utf-8",
    )
    (output_root / "runtime").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        PACKAGE_ROOT / "runtime" / "site.css",
        output_root / "runtime" / "site.css",
    )
    shutil.copyfile(
        PACKAGE_ROOT / "runtime" / "site.js",
        output_root / "runtime" / "site.js",
    )
    return output_root

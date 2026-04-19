"""
Small utility helpers for the standings package.

Contains narrow, reusable formatting, JSON-writing, and file-copy helpers
that do not belong to the core domain model.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path


def escape_date(date) -> str:
    return str(date).replace("/", "_")


def make_run_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def write_json(output_file: Path, payload: dict) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def copy_file(source_file: Path, target_file: Path) -> None:
    target_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_file, target_file)

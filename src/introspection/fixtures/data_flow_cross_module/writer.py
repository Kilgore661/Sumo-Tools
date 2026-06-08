"""Writer fixture for cross-module data-flow propagation."""

from __future__ import annotations

from pathlib import Path


DEFAULT_DIR = Path("files/output/introspection/fixtures/default")
INDEX_FILE_NAME = "index.txt"


def write_index(output_dir: Path = DEFAULT_DIR) -> Path:
    path = output_dir / INDEX_FILE_NAME
    path.write_text("fixture", encoding="utf-8")
    return path

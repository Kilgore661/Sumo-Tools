"""Writer fixture for cross-module data-flow propagation."""

from __future__ import annotations

from pathlib import Path


DEFAULT_DIR = Path("files/output/introspection/fixtures/default")
INDEX_FILE_NAME = "index.txt"


def write_index(output_dir: Path = DEFAULT_DIR) -> Path:
    return output_dir / INDEX_FILE_NAME

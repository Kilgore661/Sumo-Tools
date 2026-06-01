"""Discover project Python modules and derive dotted module names."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


DEFAULT_SOURCE_DIRS = ("src", "tests")
DEFAULT_OUTPUT_DIR = Path("files") / "output" / "introspection"


def repo_root_from_this_file() -> Path:
    """Return the repository root when this module lives under ``src/introspection``."""

    return Path(__file__).resolve().parents[2]


def module_name_for_path(repo_root: Path, path: Path) -> str:
    """Convert a Python source path into the importable project module name."""

    relative = path.relative_to(repo_root).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def iter_python_paths(repo_root: Path, source_dirs: Iterable[str]) -> list[Path]:
    """Find Python files under the configured project source roots."""

    paths: list[Path] = []
    for source_dir in source_dirs:
        root = repo_root / source_dir
        if root.exists():
            paths.extend(path for path in root.rglob("*.py") if path.is_file())
    return sorted(paths)


def build_module_index(repo_root: Path, python_paths: list[Path]) -> dict[str, Path]:
    """Return ``module_name -> relative path`` for discovered Python files."""

    return {
        module_name_for_path(repo_root, path): path.relative_to(repo_root)
        for path in python_paths
    }

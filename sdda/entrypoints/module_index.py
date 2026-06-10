from __future__ import annotations

from pathlib import Path

from .models import ModuleRecord

SKIPPED_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "files",
}


def build_module_index(import_root: Path) -> dict[str, ModuleRecord]:
    root = import_root.resolve()
    if not root.exists():
        raise FileNotFoundError(root)
    if not root.is_dir():
        raise NotADirectoryError(root)

    index: dict[str, ModuleRecord] = {}
    for path in sorted(root.rglob("*.py")):
        if _is_skipped(path, root):
            continue
        module_name = _module_name_for_path(path, root)
        index[module_name] = ModuleRecord(
            module=module_name,
            path=path,
            is_dunder_main=path.name == "__main__.py",
        )
    return index


def _is_skipped(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return any(part in SKIPPED_DIRS for part in relative.parts)


def _module_name_for_path(path: Path, root: Path) -> str:
    relative = path.relative_to(root).with_suffix("")
    return ".".join(relative.parts)

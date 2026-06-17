"""Repository tree walking for the mojibake audit."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import SKIP_DIR_NAMES, SKIP_PATH_PARTS, TEXT_SUFFIXES


def walk_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if SKIP_DIR_NAMES.intersection(path.relative_to(root).parts):
            continue
        if has_skipped_path_part(path.relative_to(root).parts):
            continue
        yield path


def has_skipped_path_part(parts: tuple[str, ...]) -> bool:
    for skipped_parts in SKIP_PATH_PARTS:
        for offset in range(0, len(parts) - len(skipped_parts) + 1):
            if parts[offset : offset + len(skipped_parts)] == skipped_parts:
                return True
    return False


def display_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def is_probable_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES

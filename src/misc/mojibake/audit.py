"""Audit orchestration for mojibake and text-boundary reports."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .findings import Finding
from .python_scan import audit_python_source
from .text_scan import audit_utf8_bytes
from .tree import display_path, is_probable_text_file, walk_files


def audit_tree(root: Path) -> Iterable[Finding]:
    for path in walk_files(root):
        relative_path = display_path(root, path)
        if is_probable_text_file(path):
            yield from audit_utf8_bytes(path, relative_path)
        if path.suffix == ".py":
            yield from audit_python_source(path, relative_path)

"""Data model for static Python import introspection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PythonModule:
    """A Python file discovered under one of the inspected source roots."""

    path: Path
    module_name: str
    has_main_guard: bool
    defines_main: bool
    parse_status: str
    parse_error: str


@dataclass(frozen=True)
class ImportEdge:
    """One syntactic import statement edge found in a project module."""

    importer_path: Path
    importer_module: str
    import_style: str
    imported_module_text: str
    imported_symbol: str
    imported_alias: str
    level: int
    is_relative: bool
    resolved_module: str
    resolved_path: str
    resolved_symbol_module: str
    resolved_symbol_path: str
    resolution_status: str

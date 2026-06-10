from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModuleRecord:
    module: str
    path: Path
    is_dunder_main: bool


@dataclass(frozen=True)
class ProgramEvidenceRecord:
    module: str
    path: str
    line: int
    statement_kind: str
    reason: str


@dataclass(frozen=True)
class ReferenceRecord:
    source_module: str
    target_module: str
    reference_kind: str
    imported_name: str
    line: int


@dataclass(frozen=True)
class WarningRecord:
    source_module: str
    line: int
    severity: str
    warning_kind: str
    imported_name: str
    resolved_module: str
    detail: str


@dataclass(frozen=True)
class ModuleIndexRecord:
    module: str
    path: str
    module_kind: str
    program_kind: str
    program_subtype: str
    standalone_subtype: str
    inbound_reference_count: int
    imported_by: str
    first_non_declarative_line: int
    first_non_declarative_kind: str
    has_main_guard: bool
    is_dunder_main: bool


@dataclass(frozen=True)
class EntrypointAnalysisResult:
    import_root: Path
    output_dir: Path
    modules: list[ModuleRecord]
    module_index_rows: list[ModuleIndexRecord]
    program_evidence: list[ProgramEvidenceRecord]
    references: list[ReferenceRecord]
    warnings: list[WarningRecord]

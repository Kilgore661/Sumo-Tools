from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModuleRecord:
    name: str
    path: Path
    canonical_name: str


@dataclass(frozen=True)
class ImportRecord:
    source_module: str
    target_module: str
    import_kind: str
    imported_name: str
    as_name: str
    level: int
    line: int
    resolved: bool
    reason: str


@dataclass(frozen=True)
class ScopeRecord:
    module: str
    scope_id: str
    scope_kind: str
    qualname: str
    line_start: int
    line_end: int


@dataclass(frozen=True)
class FileUseRecord:
    module: str
    scope_kind: str
    scope_name: str
    line: int
    action: str
    raw_expression: str
    resolved_expression: str
    confidence: str
    reason: str


@dataclass(frozen=True)
class FileFamilyRecord:
    family_id: str
    family_kind: str
    family_pattern: str
    actions: str
    evidence_count: int
    modules: str
    first_module: str
    first_scope: str
    first_line: int
    confidence: str
    reason: str


@dataclass(frozen=True)
class FileFamilyEvidenceRecord:
    family_id: str
    module: str
    scope_kind: str
    scope_name: str
    line: int
    action: str
    raw_expression: str
    resolved_expression: str
    reason: str


@dataclass(frozen=True)
class UnresolvedRecord:
    module: str
    scope_kind: str
    scope_name: str
    line: int
    source_expression: str
    reason: str


@dataclass(frozen=True)
class AnalysisResult:
    root_module: str
    import_root: Path
    output_dir: Path
    modules: list[ModuleRecord]
    imports: list[ImportRecord]
    reachable_modules: list[str]
    scopes: list[ScopeRecord]
    file_uses: list[FileUseRecord]
    file_families: list[FileFamilyRecord]
    file_family_evidence: list[FileFamilyEvidenceRecord]
    unresolved: list[UnresolvedRecord]

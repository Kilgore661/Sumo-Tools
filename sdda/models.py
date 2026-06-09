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
class TypeFactRecord:
    module: str
    owner_kind: str
    owner_qualname: str
    owner_full_name: str
    fact_kind: str
    name: str
    annotation: str
    line: int
    reason: str


@dataclass(frozen=True)
class ValueFactRecord:
    module: str
    scope_kind: str
    scope_name: str
    name: str
    inferred_type: str
    source_expression: str
    source_full_name: str
    line: int
    reason: str


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
class FileFamilyClassificationRecord:
    family_id: str
    family_kind: str
    family_pattern: str
    actions: str
    classification: str
    confidence: str
    reason: str
    evidence_count: int
    modules: str
    review_priority: str


@dataclass(frozen=True)
class DistributionCandidateRecord:
    family_id: str
    family_pattern: str
    classification: str
    distribution_decision: str
    review_priority: str
    reason: str
    actions: str
    family_kind: str
    evidence_count: int
    modules: str


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
    type_facts: list[TypeFactRecord]
    value_facts: list[ValueFactRecord]
    file_uses: list[FileUseRecord]
    file_families: list[FileFamilyRecord]
    file_family_evidence: list[FileFamilyEvidenceRecord]
    file_family_classification: list[FileFamilyClassificationRecord]
    distribution_candidates: list[DistributionCandidateRecord]
    unresolved: list[UnresolvedRecord]

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
class FieldFactRecord:
    module: str
    scope_kind: str
    scope_name: str
    expression: str
    receiver_name: str
    receiver_type: str
    field_name: str
    field_annotation: str
    line: int
    reason: str


@dataclass(frozen=True)
class CallArgumentBindingRecord:
    caller_module: str
    caller_scope: str
    call_line: int
    callee_full_name: str
    parameter_name: str
    parameter_annotation: str
    argument_expression: str
    argument_name: str
    argument_value_sources: str
    reason: str


@dataclass(frozen=True)
class ParameterFieldProvenanceRecord:
    consumer_module: str
    consumer_scope: str
    consumer_line: int
    consumer_expression: str
    parameter_name: str
    parameter_type: str
    field_name: str
    field_annotation: str
    caller_module: str
    caller_scope: str
    call_line: int
    argument_expression: str
    argument_value_source: str
    interpretation: str
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
class FileUseResolutionRecord:
    module: str
    scope_kind: str
    scope_name: str
    line: int
    action: str
    raw_expression: str
    resolved_expression: str
    resolution_kind: str
    resolved_owner_type: str
    resolved_field_name: str
    resolved_field_annotation: str
    reason: str


@dataclass(frozen=True)
class ProducerReturnBindingRecord:
    producer_function: str
    output_type: str
    output_field: str
    source_name: str
    source_expression: str
    return_line: int
    reason: str


@dataclass(frozen=True)
class ProducerWriteBindingRecord:
    producer_function: str
    source_name: str
    write_action: str
    write_expression: str
    write_line: int
    reason: str


@dataclass(frozen=True)
class ProducerOutputRecord:
    consumer_module: str
    consumer_scope: str
    consumer_line: int
    consumer_action: str
    consumer_expression: str
    producer_function: str
    output_type: str
    output_field: str
    producer_source_name: str
    producer_source_expression: str
    producer_write_action: str
    producer_write_expression: str
    producer_write_line: int
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
class ReviewCandidateRecord:
    family_id: str
    family_pattern: str
    classification: str
    distribution_decision: str
    review_priority: str
    classification_reason: str
    distribution_reason: str
    actions: str
    family_kind: str
    evidence_count: int
    modules: str
    first_module: str
    first_scope: str
    first_line: int
    first_raw_expression: str
    first_resolved_expression: str
    first_evidence_reason: str


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
    field_facts: list[FieldFactRecord]
    call_edges: list[object]
    execution_call_slice: list[object]
    execution_review_candidates: list[object]
    call_argument_bindings: list[CallArgumentBindingRecord]
    parameter_field_provenance: list[ParameterFieldProvenanceRecord]
    parameter_file_provenance: list[object]
    file_uses: list[FileUseRecord]
    file_use_resolutions: list[FileUseResolutionRecord]
    producer_return_bindings: list[ProducerReturnBindingRecord]
    producer_write_bindings: list[ProducerWriteBindingRecord]
    producer_outputs: list[ProducerOutputRecord]
    file_families: list[FileFamilyRecord]
    file_family_evidence: list[FileFamilyEvidenceRecord]
    file_family_classification: list[FileFamilyClassificationRecord]
    distribution_candidates: list[DistributionCandidateRecord]
    review_candidates: list[ReviewCandidateRecord]
    unresolved: list[UnresolvedRecord]

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Product:
    product_id: str
    builder_root_module: str
    import_root: Path
    artifact_description: str
    distribution_mode: str
    output_dir: Path


@dataclass(frozen=True)
class ProductEvidenceRecord:
    product_id: str
    builder_root_module: str
    family_id: str
    family_pattern: str
    source_distribution_bucket: str
    source_distribution_decision: str
    classification: str
    distribution_decision: str
    execution_status: str
    effective_review_priority: str
    actions: str
    family_kind: str
    evidence_count: int
    modules: str
    reason: str


@dataclass(frozen=True)
class ProductSummaryRecord:
    product_id: str
    metric: str
    value: str


@dataclass(frozen=True)
class InputWorklistRecord:
    input_id: str
    input_pattern: str
    needed_by_product: str
    needed_by_builder: str
    source_bucket: str
    source_decision: str
    status: str
    candidate_next_action: str
    classification: str
    execution_status: str
    effective_review_priority: str
    actions: str
    family_kind: str
    evidence_count: int
    modules: str
    reason: str


@dataclass(frozen=True)
class InputActionRecord:
    input_id: str
    input_pattern: str
    needed_by_product: str
    status: str
    action: str
    handler: str
    action_result: str
    reason: str


@dataclass(frozen=True)
class ProducerSearchRecord:
    input_id: str
    input_pattern: str
    candidate_producer_module: str
    candidate_producer_scope: str
    candidate_line: int
    write_pattern: str
    match_kind: str
    confidence: str
    write_action: str
    raw_expression: str
    reason: str


@dataclass(frozen=True)
class InputResolutionRecord:
    input_id: str
    input_pattern: str
    needed_by_product: str
    status: str
    resolution: str
    candidate_count: int
    candidate_producer_modules: str
    next_action: str
    reason: str

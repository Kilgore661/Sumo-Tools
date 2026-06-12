from __future__ import annotations

import hashlib

from .models import InputWorklistRecord, Product, ProductEvidenceRecord

WORKLIST_BUCKETS = {
    "precomputed_artifact_input",
    "mode_dependent_review",
    "state_or_control_review",
    "pipeline_tree_review",
    "unresolved_execution_parameter",
    "unresolved_non_execution_parameter",
    "requires_review",
    "review",
}


def build_input_worklist(
    product: Product,
    evidence: list[ProductEvidenceRecord],
) -> list[InputWorklistRecord]:
    rows = [
        _worklist_record(product, row)
        for row in evidence
        if _needs_follow_up(row)
    ]
    return sorted(rows, key=lambda row: (_status_order(row.status), row.input_pattern))


def _needs_follow_up(row: ProductEvidenceRecord) -> bool:
    if row.source_distribution_bucket in WORKLIST_BUCKETS:
        return True
    if row.source_distribution_decision in {"review", "include_or_regenerate"}:
        return True
    if row.effective_review_priority == "high":
        return True
    return False


def _worklist_record(product: Product, row: ProductEvidenceRecord) -> InputWorklistRecord:
    status, next_action = _status_and_action(row)
    return InputWorklistRecord(
        input_id=_input_id(product.product_id, row.family_pattern),
        input_pattern=row.family_pattern,
        needed_by_product=product.product_id,
        needed_by_builder=product.builder_root_module,
        source_bucket=row.source_distribution_bucket,
        source_decision=row.source_distribution_decision,
        status=status,
        candidate_next_action=next_action,
        classification=row.classification,
        execution_status=row.execution_status,
        effective_review_priority=row.effective_review_priority,
        actions=row.actions,
        family_kind=row.family_kind,
        evidence_count=row.evidence_count,
        modules=row.modules,
        reason=row.reason,
    )


def _status_and_action(row: ProductEvidenceRecord) -> tuple[str, str]:
    bucket = row.source_distribution_bucket
    if bucket == "precomputed_artifact_input":
        return "find_producer_or_include", "search_for_builder_that_writes_input"
    if bucket == "pipeline_tree_review":
        return "review_pipeline_tree", "decide_whether_tree_is_product_output_or_input"
    if bucket == "mode_dependent_review":
        return "review_mode_dependent_source", "separate_build_mode_from_existing_output_mode"
    if bucket == "state_or_control_review":
        return "review_state_or_control", "decide_whether_state_file_affects_distribution_contract"
    if bucket in {"unresolved_execution_parameter", "unresolved_non_execution_parameter"}:
        return "resolve_parameter", "trace_or_annotate_parameter_source"
    if row.effective_review_priority == "high":
        return "review_high_priority", "inspect_evidence_and_choose_policy"
    return "review_policy", "choose_include_regenerate_exclude_or_declare_external"


def _input_id(product_id: str, input_pattern: str) -> str:
    digest = hashlib.sha1(f"{product_id}:{input_pattern}".encode("utf-8")).hexdigest()[:12]
    return f"in_{digest}"


def _status_order(status: str) -> int:
    order = {
        "find_producer_or_include": 0,
        "resolve_parameter": 1,
        "review_pipeline_tree": 2,
        "review_mode_dependent_source": 3,
        "review_state_or_control": 4,
        "review_high_priority": 5,
        "review_policy": 6,
    }
    return order.get(status, 99)

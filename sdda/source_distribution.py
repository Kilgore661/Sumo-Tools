from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDistributionInputRecord:
    family_id: str
    family_pattern: str
    source_distribution_bucket: str
    source_distribution_decision: str
    classification: str
    distribution_decision: str
    review_priority: str
    effective_review_priority: str
    execution_status: str
    actions: str
    family_kind: str
    evidence_count: int
    modules: str
    reason: str


def derive_source_distribution_inputs(
    distribution_candidates: list[object],
    execution_review_candidates: list[object],
) -> list[SourceDistributionInputRecord]:
    execution_by_family_id = {
        getattr(row, "family_id"): row for row in execution_review_candidates
    }
    rows: list[SourceDistributionInputRecord] = []
    for candidate in distribution_candidates:
        execution = execution_by_family_id.get(getattr(candidate, "family_id"))
        rows.append(_derive_record(candidate, execution))
    return sorted(
        rows,
        key=lambda row: (
            _bucket_order(row.source_distribution_bucket),
            row.family_pattern,
        ),
    )


def _derive_record(candidate: object, execution: object | None) -> SourceDistributionInputRecord:
    classification = getattr(candidate, "classification")
    execution_status = _execution_status(execution)
    effective_review_priority = _effective_review_priority(candidate, execution)
    bucket, decision, reason = _source_distribution_policy(candidate, execution)
    return SourceDistributionInputRecord(
        family_id=getattr(candidate, "family_id"),
        family_pattern=getattr(candidate, "family_pattern"),
        source_distribution_bucket=bucket,
        source_distribution_decision=decision,
        classification=classification,
        distribution_decision=getattr(candidate, "distribution_decision"),
        review_priority=getattr(candidate, "review_priority"),
        effective_review_priority=effective_review_priority,
        execution_status=execution_status,
        actions=getattr(candidate, "actions"),
        family_kind=getattr(candidate, "family_kind"),
        evidence_count=getattr(candidate, "evidence_count"),
        modules=getattr(candidate, "modules"),
        reason=reason,
    )


def _source_distribution_policy(candidate: object, execution: object | None) -> tuple[str, str, str]:
    classification = getattr(candidate, "classification")
    distribution_decision = getattr(candidate, "distribution_decision")
    execution_status = _execution_status(execution)
    effective_review_priority = _effective_review_priority(candidate, execution)

    if execution_status == "not_in_execution_slice":
        return "not_in_execution_slice", "exclude_from_current_product_slice", "not_in_execution_slice"

    if classification == "required_distribution_input":
        return "must_include", "include", "required_distribution_input"

    if classification == "environment_setting":
        return "external_runtime_assumption", "document", "environment_setting"

    if classification == "internet_source":
        return "external_runtime_assumption", "document_or_regenerate", "internet_source"

    if classification == "mode_dependent_deployment_source":
        return "mode_dependent_review", "review", "mode_dependent_deployment_source"

    if classification in {"generated_then_consumed", "generated_output"}:
        return "exclude", "exclude", classification

    if distribution_decision == "exclude":
        return "exclude", "exclude", "distribution_decision_exclude"

    if effective_review_priority == "high":
        return "requires_review", "review", "effective_high_priority_review"

    if distribution_decision == "include":
        return "must_include", "include", "distribution_decision_include"

    return "review", "review", "fallback_review"


def _execution_status(execution: object | None) -> str:
    if execution is None:
        return "not_review_candidate"
    return getattr(execution, "execution_status")


def _effective_review_priority(candidate: object, execution: object | None) -> str:
    if execution is None:
        return getattr(candidate, "review_priority")
    return getattr(execution, "effective_review_priority")


def _bucket_order(bucket: str) -> int:
    order = {
        "must_include": 0,
        "mode_dependent_review": 1,
        "external_runtime_assumption": 2,
        "requires_review": 3,
        "review": 4,
        "exclude": 5,
        "not_in_execution_slice": 6,
    }
    return order.get(bucket, 99)

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
    execution_by_family_pattern = {
        getattr(row, "family_pattern"): row for row in execution_review_candidates
    }
    rows: list[SourceDistributionInputRecord] = []
    for candidate in distribution_candidates:
        execution = execution_by_family_id.get(getattr(candidate, "family_id"))
        if execution is None:
            execution = execution_by_family_pattern.get(getattr(candidate, "family_pattern"))
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
    family_pattern = getattr(candidate, "family_pattern")
    classification = getattr(candidate, "classification")
    distribution_decision = getattr(candidate, "distribution_decision")
    execution_status = _execution_status(execution)
    effective_review_priority = _effective_review_priority(candidate, execution)

    if execution_status == "not_in_execution_slice":
        return "not_in_execution_slice", "exclude_from_current_product_slice", "not_in_execution_slice"

    if classification in {"generated_then_consumed", "generated_output"}:
        return "generated_or_intermediate_output", "exclude", classification

    if classification == "mode_dependent_deployment_source":
        return "mode_dependent_review", "review", "mode_dependent_deployment_source"

    if classification == "possible_state_or_control_file":
        return "state_or_control_review", "review", "possible_state_or_control_file"

    if _is_output_parameter_family(family_pattern):
        return "scoped_output_parameter", "document_as_output_location", "scoped_output_parameter_not_source_input"

    if _is_unresolved_scoped_parameter_family(family_pattern, execution):
        return _scoped_parameter_policy(execution_status)

    if classification == "required_distribution_input":
        return _required_input_policy(family_pattern)

    if classification == "environment_setting":
        return "external_runtime_assumption", "document", "environment_setting"

    if classification == "internet_source":
        return "external_runtime_assumption", "document_or_regenerate", "internet_source"

    if distribution_decision == "exclude":
        return "exclude", "exclude", "distribution_decision_exclude"

    if effective_review_priority == "high":
        return "requires_review", "review", "effective_high_priority_review"

    if distribution_decision == "include":
        return _required_input_policy(family_pattern)

    return "review", "review", "fallback_review"


def _required_input_policy(family_pattern: str) -> tuple[str, str, str]:
    if family_pattern.startswith("files/output/"):
        return "precomputed_artifact_input", "include_or_regenerate", "required_precomputed_artifact_input"
    if family_pattern.startswith("src/"):
        return "repository_source_input", "include", "required_repository_source_input"
    return "required_input_unclassified", "include", "required_input_unclassified"


def _scoped_parameter_policy(execution_status: str) -> tuple[str, str, str]:
    if execution_status == "execution_reachable":
        return "unresolved_execution_parameter", "review", "scoped_execution_parameter_without_concrete_source_pattern"
    return "unresolved_non_execution_parameter", "review", "scoped_non_execution_parameter_without_concrete_source_pattern"


def _is_output_parameter_family(family_pattern: str) -> bool:
    if family_pattern.endswith(":output_root"):
        return True
    if family_pattern.endswith(":output_dir"):
        return True
    if family_pattern.endswith(":destination"):
        return True
    if family_pattern.endswith(":target") or family_pattern.endswith(":target_path"):
        return True
    return False


def _is_unresolved_scoped_parameter_family(family_pattern: str, execution: object | None) -> bool:
    if not _is_scoped_family(family_pattern):
        return False
    if _is_concrete_path_family(family_pattern):
        return False
    if execution is not None and _execution_status(execution) == "not_in_execution_slice":
        return False
    return True


def _is_scoped_family(family_pattern: str) -> bool:
    return family_pattern.count(":") >= 2


def _is_concrete_path_family(family_pattern: str) -> bool:
    return family_pattern.startswith("files/") or family_pattern.startswith("src/")


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
        "repository_source_input": 0,
        "precomputed_artifact_input": 1,
        "required_input_unclassified": 2,
        "mode_dependent_review": 3,
        "state_or_control_review": 4,
        "external_runtime_assumption": 5,
        "requires_review": 6,
        "unresolved_execution_parameter": 7,
        "unresolved_non_execution_parameter": 8,
        "scoped_output_parameter": 9,
        "review": 10,
        "generated_or_intermediate_output": 11,
        "exclude": 12,
        "not_in_execution_slice": 13,
    }
    return order.get(bucket, 99)

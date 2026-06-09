from __future__ import annotations

from .models import DistributionCandidateRecord, FileFamilyClassificationRecord

INCLUDE_CLASSIFICATIONS = {"required_distribution_input", "environment_setting"}
REVIEW_CLASSIFICATIONS = {
    "possible_efficiency_cache",
    "possible_pipeline_intermediate",
    "possible_state_or_control_file",
    "unknown_review_needed",
}
EXCLUDE_CLASSIFICATIONS = {"generated_output", "internet_source"}


def derive_distribution_candidates(
    classifications: list[FileFamilyClassificationRecord],
) -> list[DistributionCandidateRecord]:
    return [_candidate(row) for row in classifications]


def _candidate(row: FileFamilyClassificationRecord) -> DistributionCandidateRecord:
    decision, reason = _decision(row)
    return DistributionCandidateRecord(
        family_id=row.family_id,
        family_pattern=row.family_pattern,
        classification=row.classification,
        distribution_decision=decision,
        review_priority=_review_priority(row, decision),
        reason=reason,
        actions=row.actions,
        family_kind=row.family_kind,
        evidence_count=row.evidence_count,
        modules=row.modules,
    )


def _decision(row: FileFamilyClassificationRecord) -> tuple[str, str]:
    if row.classification in INCLUDE_CLASSIFICATIONS:
        return "include", f"classification:{row.classification}"
    if row.classification in REVIEW_CLASSIFICATIONS:
        return "review", f"classification:{row.classification}"
    if row.classification in EXCLUDE_CLASSIFICATIONS:
        return "exclude", f"classification:{row.classification}"
    return "review", "classification:unrecognised"


def _review_priority(row: FileFamilyClassificationRecord, decision: str) -> str:
    if decision == "include":
        return "low"
    if decision == "exclude" and row.confidence != "low":
        return "low"
    if row.review_priority == "high":
        return "high"
    return "medium"

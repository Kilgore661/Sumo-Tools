from __future__ import annotations

from .models import (
    DistributionCandidateRecord,
    FileFamilyClassificationRecord,
    FileFamilyEvidenceRecord,
    FileFamilyRecord,
    ReviewCandidateRecord,
)


def build_review_candidates(
    distribution_candidates: list[DistributionCandidateRecord],
    classifications: list[FileFamilyClassificationRecord],
    families: list[FileFamilyRecord],
    evidence: list[FileFamilyEvidenceRecord],
) -> list[ReviewCandidateRecord]:
    classifications_by_id = {row.family_id: row for row in classifications}
    families_by_id = {row.family_id: row for row in families}
    first_evidence_by_id = _first_evidence_by_family(evidence)
    rows: list[ReviewCandidateRecord] = []
    for candidate in distribution_candidates:
        if candidate.distribution_decision != "review":
            continue
        classification = classifications_by_id[candidate.family_id]
        family = families_by_id[candidate.family_id]
        first_evidence = first_evidence_by_id[candidate.family_id]
        rows.append(
            ReviewCandidateRecord(
                family_id=candidate.family_id,
                family_pattern=candidate.family_pattern,
                classification=candidate.classification,
                distribution_decision=candidate.distribution_decision,
                review_priority=candidate.review_priority,
                classification_reason=classification.reason,
                distribution_reason=candidate.reason,
                actions=candidate.actions,
                family_kind=candidate.family_kind,
                evidence_count=candidate.evidence_count,
                modules=candidate.modules,
                first_module=family.first_module,
                first_scope=family.first_scope,
                first_line=family.first_line,
                first_raw_expression=first_evidence.raw_expression,
                first_resolved_expression=first_evidence.resolved_expression,
                first_evidence_reason=first_evidence.reason,
            )
        )
    return sorted(rows, key=_sort_key)


def _first_evidence_by_family(
    evidence: list[FileFamilyEvidenceRecord],
) -> dict[str, FileFamilyEvidenceRecord]:
    first_by_id: dict[str, FileFamilyEvidenceRecord] = {}
    for row in evidence:
        first_by_id.setdefault(row.family_id, row)
    return first_by_id


def _sort_key(row: ReviewCandidateRecord) -> tuple[int, str, str]:
    priority_order = {"high": 0, "medium": 1, "low": 2}
    return (priority_order.get(row.review_priority, 3), row.classification, row.family_pattern)

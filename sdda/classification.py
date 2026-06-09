from __future__ import annotations

from .models import FileFamilyClassificationRecord, FileFamilyRecord

CONTENT_READ_ACTIONS = {"may_read", "may_observe", "may_download"}
EXISTENCE_ACTIONS = {"may_existence_check"}
WRITE_ACTIONS = {"may_write", "may_create_directory", "may_delete", "may_copy"}


def classify_file_families(
    families: list[FileFamilyRecord],
) -> list[FileFamilyClassificationRecord]:
    return [_classify_family(family) for family in families]


def _classify_family(family: FileFamilyRecord) -> FileFamilyClassificationRecord:
    actions = _actions(family)
    classification, confidence, reason = _classification(family, actions)
    return FileFamilyClassificationRecord(
        family_id=family.family_id,
        family_kind=family.family_kind,
        family_pattern=family.family_pattern,
        actions=family.actions,
        classification=classification,
        confidence=confidence,
        reason=reason,
        evidence_count=family.evidence_count,
        modules=family.modules,
        review_priority=_review_priority(classification, confidence),
    )


def _classification(
    family: FileFamilyRecord,
    actions: set[str],
) -> tuple[str, str, str]:
    if family.family_kind == "environment_setting":
        return "environment_setting", "high", "family_kind:environment_setting"
    if family.family_kind == "url_family":
        return "internet_source", "high", "family_kind:url_family"
    if family.confidence == "low":
        return "unknown_review_needed", "low", "family_confidence:low"

    content_reads = bool(actions & CONTENT_READ_ACTIONS)
    existence_checks = bool(actions & EXISTENCE_ACTIONS)
    writes = bool(actions & WRITE_ACTIONS)
    if content_reads and writes:
        return _content_read_write_classification(family, actions)
    if existence_checks and writes:
        return _existence_write_classification(family, actions)
    if content_reads:
        return _read_only_classification(family, actions)
    if existence_checks:
        return "possible_state_or_control_file", "medium", "existence_check_without_content_read"
    if writes:
        return _write_only_classification(family, actions)
    return "unknown_review_needed", "low", "no_file_actions"


def _content_read_write_classification(
    family: FileFamilyRecord,
    actions: set[str],
) -> tuple[str, str, str]:
    if family.family_kind == "directory_family":
        return "possible_state_or_control_file", "medium", "directory_content_read_plus_write"
    return "possible_efficiency_cache", "medium", "content_read_or_observe_plus_write"


def _existence_write_classification(
    family: FileFamilyRecord, actions: set[str]
) -> tuple[str, str, str]:
    if actions <= {"may_existence_check", "may_delete", "may_create_directory"}:
        return "generated_output", "medium", "existence_check_plus_cleanup_or_recreate"
    if actions <= {"may_existence_check", "may_write", "may_create_directory"}:
        return "possible_efficiency_cache", "medium", "existence_check_plus_write"
    return "possible_state_or_control_file", "medium", "existence_check_plus_mixed_write"


def _read_only_classification(
    family: FileFamilyRecord,
    actions: set[str],
) -> tuple[str, str, str]:
    if "may_download" in actions:
        return "internet_source", "medium", "download_action"
    if family.family_kind == "glob_family" and _is_constant_glob(family.family_pattern):
        return "required_distribution_input", "medium", "constant_glob_observed_without_write"
    if family.family_kind == "glob_family":
        return "possible_pipeline_intermediate", "medium", "variable_glob_observed_without_write"
    return "required_distribution_input", "medium", "content_read_or_observe_without_write"


def _write_only_classification(
    family: FileFamilyRecord,
    actions: set[str],
) -> tuple[str, str, str]:
    if family.family_kind == "directory_family":
        return "generated_output", "medium", "directory_created_without_read"
    if "may_delete" in actions and len(actions) == 1:
        return "generated_output", "low", "delete_without_read"
    return "generated_output", "medium", "write_without_read"


def _is_constant_glob(pattern: str) -> bool:
    base = pattern.split("/", 1)[0]
    return base.isupper()


def _review_priority(classification: str, confidence: str) -> str:
    if classification == "unknown_review_needed":
        return "high"
    if confidence == "low":
        return "medium"
    if classification in {
        "possible_efficiency_cache",
        "possible_pipeline_intermediate",
        "possible_state_or_control_file",
    }:
        return "medium"
    return "low"


def _actions(family: FileFamilyRecord) -> set[str]:
    return {action for action in family.actions.split(";") if action}

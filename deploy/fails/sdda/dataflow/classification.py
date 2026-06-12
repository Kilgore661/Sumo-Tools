from __future__ import annotations

from .models import (
    FileFamilyClassificationRecord,
    FileFamilyRecord,
    ParameterFieldProvenanceRecord,
    ProducerOutputRecord,
)

CONTENT_READ_ACTIONS = {"may_read", "may_observe", "may_download"}
EXISTENCE_ACTIONS = {"may_existence_check"}
WRITE_ACTIONS = {"may_write", "may_create_directory", "may_delete", "may_copy"}
DEPLOY_MODULE = "src.products.make_site2.deploy"


def classify_file_families(
    families: list[FileFamilyRecord],
    producer_outputs: list[ProducerOutputRecord] | None = None,
    parameter_field_provenance: list[ParameterFieldProvenanceRecord] | None = None,
    parameter_file_provenance: list[object] | None = None,
) -> list[FileFamilyClassificationRecord]:
    generated_then_consumed = _generated_then_consumed_patterns(producer_outputs or [])
    mode_dependent_deployment_sources = _mode_dependent_deployment_source_patterns(
        parameter_field_provenance or []
    )
    parameter_path_inputs = _parameter_path_input_patterns(parameter_file_provenance or [])
    mode_dependent_parameter_sources = _mode_dependent_parameter_source_patterns(
        parameter_file_provenance or [],
        mode_dependent_deployment_sources,
    )
    return [
        _classify_family(
            family,
            generated_then_consumed,
            mode_dependent_deployment_sources,
            parameter_path_inputs,
            mode_dependent_parameter_sources,
        )
        for family in families
    ]


def _classify_family(
    family: FileFamilyRecord,
    generated_then_consumed: set[str],
    mode_dependent_deployment_sources: set[str],
    parameter_path_inputs: set[str],
    mode_dependent_parameter_sources: set[str],
) -> FileFamilyClassificationRecord:
    actions = _actions(family)
    classification, confidence, reason = _classification(
        family,
        actions,
        generated_then_consumed,
        mode_dependent_deployment_sources,
        parameter_path_inputs,
        mode_dependent_parameter_sources,
    )
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
    generated_then_consumed: set[str],
    mode_dependent_deployment_sources: set[str],
    parameter_path_inputs: set[str],
    mode_dependent_parameter_sources: set[str],
) -> tuple[str, str, str]:
    if family.family_pattern in generated_then_consumed:
        return "generated_then_consumed", "high", "producer_output_written_then_consumed"
    if _matches_any_field_pattern(family.family_pattern, mode_dependent_deployment_sources):
        return "mode_dependent_deployment_source", "high", "parameter_field_has_generated_and_external_sources"
    if family.family_pattern in mode_dependent_parameter_sources:
        return "mode_dependent_deployment_source", "high", "parameter_alias_inherits_mode_dependent_source"
    if family.family_pattern in parameter_path_inputs:
        return "required_distribution_input", "high", "parameter_file_use_bound_to_path_expression"
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
    if _has_unresolved_variable_path_segment(family.family_pattern):
        return "unknown_review_needed", "medium", "unresolved_variable_path_segment"
    if _is_non_root_main_local(family.family_pattern):
        return "unknown_review_needed", "medium", "non_root_main_scope_read"
    if _is_scoped_local_or_parameter(family.family_pattern):
        return "unknown_review_needed", "medium", "scoped_local_or_parameter_read"
    if _is_object_field_expression(family.family_pattern):
        return "possible_pipeline_intermediate", "medium", "object_field_read_without_value_flow"
    if family.family_kind == "glob_family" and _is_concrete_repository_glob(family.family_pattern):
        return "required_distribution_input", "high", "concrete_repository_glob_without_write"
    if family.family_kind == "glob_family" and _is_constant_glob(family.family_pattern):
        return "required_distribution_input", "medium", "constant_glob_observed_without_write"
    if family.family_kind == "glob_family":
        return "possible_pipeline_intermediate", "medium", "variable_glob_observed_without_write"
    if _is_deploy_module_only(family):
        return "possible_pipeline_intermediate", "medium", "deploy_read_without_producer_matching"
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


def _generated_then_consumed_patterns(
    producer_outputs: list[ProducerOutputRecord],
) -> set[str]:
    return {row.consumer_expression for row in producer_outputs}


def _mode_dependent_deployment_source_patterns(
    provenance: list[ParameterFieldProvenanceRecord],
) -> set[str]:
    interpretations_by_expression: dict[str, set[str]] = {}
    for row in provenance:
        interpretations_by_expression.setdefault(row.consumer_expression, set()).add(row.interpretation)
    return {
        expression
        for expression, interpretations in interpretations_by_expression.items()
        if "generated_output_tree" in interpretations
        and "externally_supplied_existing_output" in interpretations
    }


def _parameter_path_input_patterns(provenance: list[object]) -> set[str]:
    patterns: set[str] = set()
    for row in provenance:
        if getattr(row, "interpretation", "") not in {
            "parameter_from_path_expression",
            "parameter_from_iterator_path_family",
            "parameter_from_default_path_expression",
        }:
            continue
        expression = getattr(row, "consumer_expression")
        patterns.add(expression)
        patterns.add(f"{getattr(row, 'consumer_module')}:{getattr(row, 'consumer_scope')}:{expression}")
    return patterns


def _mode_dependent_parameter_source_patterns(
    provenance: list[object],
    mode_dependent_deployment_sources: set[str],
) -> set[str]:
    patterns: set[str] = set()
    for row in provenance:
        if getattr(row, "interpretation", "") != "parameter_from_local_path_alias":
            continue
        argument_expression = getattr(row, "argument_expression", "")
        if not _matches_any_field_pattern(argument_expression, mode_dependent_deployment_sources):
            continue
        expression = getattr(row, "consumer_expression")
        patterns.add(expression)
        patterns.add(f"{getattr(row, 'consumer_module')}:{getattr(row, 'consumer_scope')}:{expression}")
    return patterns


def _matches_any_field_pattern(pattern: str, fields: set[str]) -> bool:
    return any(pattern == field or pattern.startswith(f"{field}/") for field in fields)


def _is_concrete_repository_glob(pattern: str) -> bool:
    return pattern.startswith("src/") or pattern.startswith("files/")


def _is_constant_glob(pattern: str) -> bool:
    base = pattern.split("/", 1)[0]
    return base.isupper()


def _is_deploy_module_only(family: FileFamilyRecord) -> bool:
    modules = {module for module in family.modules.split(";") if module}
    return modules == {DEPLOY_MODULE}


def _has_unresolved_variable_path_segment(pattern: str) -> bool:
    if "/" not in pattern:
        return False
    dynamic_names = {"filename", "name", "source", "source_path", "target", "target_path"}
    return any(segment in dynamic_names for segment in pattern.split("/"))


def _is_non_root_main_local(pattern: str) -> bool:
    return ":main:" in pattern and not pattern.startswith("src.products.make_site2.__main__:main:")


def _is_scoped_local_or_parameter(pattern: str) -> bool:
    return pattern.count(":") >= 2


def _is_object_field_expression(pattern: str) -> bool:
    return pattern.startswith("producer_output.")


def _review_priority(classification: str, confidence: str) -> str:
    if classification == "unknown_review_needed":
        return "high"
    if confidence == "low":
        return "medium"
    if classification in {
        "mode_dependent_deployment_source",
        "possible_efficiency_cache",
        "possible_pipeline_intermediate",
        "possible_state_or_control_file",
    }:
        return "medium"
    return "low"


def _actions(family: FileFamilyRecord) -> set[str]:
    return {action for action in family.actions.split(";") if action}

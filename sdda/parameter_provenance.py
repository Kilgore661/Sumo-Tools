from __future__ import annotations

from .models import CallArgumentBindingRecord, FieldFactRecord, ParameterFieldProvenanceRecord


def extract_parameter_field_provenance(
    call_argument_bindings: list[CallArgumentBindingRecord],
    field_facts: list[FieldFactRecord],
) -> list[ParameterFieldProvenanceRecord]:
    bindings_by_callee_parameter = _bindings_by_callee_parameter(call_argument_bindings)
    records: list[ParameterFieldProvenanceRecord] = []
    seen: set[tuple[str, str, str, str, str, int]] = set()
    for field in field_facts:
        key = (field.module, field.scope_name, field.receiver_name)
        for binding in bindings_by_callee_parameter.get(key, ()):
            sources = _argument_sources(binding)
            if not sources:
                records.append(_record(field, binding, "", "parameter_argument_without_value_source"))
                continue
            for source in sources:
                interpretation = _interpretation(source)
                dedupe_key = (
                    field.module,
                    field.scope_name,
                    field.expression,
                    binding.caller_module,
                    source,
                    binding.call_line,
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                records.append(_record(field, binding, source, interpretation))
    return records


def _bindings_by_callee_parameter(
    bindings: list[CallArgumentBindingRecord],
) -> dict[tuple[str, str, str], tuple[CallArgumentBindingRecord, ...]]:
    grouped: dict[tuple[str, str, str], list[CallArgumentBindingRecord]] = {}
    for binding in bindings:
        module, scope = _split_function_name(binding.callee_full_name)
        if module == "" or scope == "":
            continue
        grouped.setdefault((module, scope, binding.parameter_name), []).append(binding)
    return {key: tuple(value) for key, value in grouped.items()}


def _record(
    field: FieldFactRecord,
    binding: CallArgumentBindingRecord,
    source: str,
    interpretation: str,
) -> ParameterFieldProvenanceRecord:
    return ParameterFieldProvenanceRecord(
        consumer_module=field.module,
        consumer_scope=field.scope_name,
        consumer_line=field.line,
        consumer_expression=field.expression,
        parameter_name=field.receiver_name,
        parameter_type=field.receiver_type,
        field_name=field.field_name,
        field_annotation=field.field_annotation,
        caller_module=binding.caller_module,
        caller_scope=binding.caller_scope,
        call_line=binding.call_line,
        argument_expression=binding.argument_expression,
        argument_value_source=source,
        interpretation=interpretation,
        reason="parameter_field_read_from_call_argument_source",
    )


def _argument_sources(binding: CallArgumentBindingRecord) -> tuple[str, ...]:
    return tuple(source for source in binding.argument_value_sources.split(";") if source)


def _interpretation(source: str) -> str:
    if source.endswith(".build_site"):
        return "generated_output_tree"
    if source.endswith(".build_output_from_existing"):
        return "externally_supplied_existing_output"
    return "unknown_argument_source"


def _split_function_name(full_name: str) -> tuple[str, str]:
    parts = full_name.split(".")
    if len(parts) < 2:
        return "", ""
    return ".".join(parts[:-1]), parts[-1]

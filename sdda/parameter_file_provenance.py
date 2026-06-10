from __future__ import annotations

from .models import CallArgumentBindingRecord, FileUseRecord, ParameterFileProvenanceRecord


def extract_parameter_file_provenance(
    call_argument_bindings: list[CallArgumentBindingRecord],
    file_uses: list[FileUseRecord],
) -> list[ParameterFileProvenanceRecord]:
    bindings_by_callee_parameter = _bindings_by_callee_parameter(call_argument_bindings)
    records: list[ParameterFileProvenanceRecord] = []
    seen: set[tuple[str, str, int, str, str, int]] = set()
    for file_use in file_uses:
        parameter_name = _parameter_name(file_use.resolved_expression)
        if parameter_name == "":
            continue
        key = (file_use.module, file_use.scope_name, parameter_name)
        for binding in bindings_by_callee_parameter.get(key, ()):
            dedupe_key = (
                file_use.module,
                file_use.scope_name,
                file_use.line,
                parameter_name,
                binding.caller_module,
                binding.call_line,
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            records.append(
                ParameterFileProvenanceRecord(
                    consumer_module=file_use.module,
                    consumer_scope=file_use.scope_name,
                    consumer_line=file_use.line,
                    consumer_action=file_use.action,
                    consumer_expression=file_use.resolved_expression,
                    parameter_name=parameter_name,
                    caller_module=binding.caller_module,
                    caller_scope=binding.caller_scope,
                    call_line=binding.call_line,
                    argument_expression=binding.argument_expression,
                    argument_name=binding.argument_name,
                    argument_value_sources=binding.argument_value_sources,
                    interpretation=_interpretation(binding.argument_expression, binding.argument_value_sources),
                    reason="parameter_file_use_from_call_argument",
                )
            )
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


def _parameter_name(expression: str) -> str:
    if expression.isidentifier():
        return expression
    return ""


def _interpretation(argument_expression: str, argument_value_sources: str) -> str:
    if argument_value_sources:
        return "parameter_from_value_sources"
    if "/" in argument_expression or "Path(" in argument_expression:
        return "parameter_from_path_expression"
    return "parameter_from_unresolved_argument"


def _split_function_name(full_name: str) -> tuple[str, str]:
    parts = full_name.split(".")
    if len(parts) < 2:
        return "", ""
    return ".".join(parts[:-1]), parts[-1]

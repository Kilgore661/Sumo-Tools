from __future__ import annotations

import ast

from .models import CallArgumentBindingRecord, ImportRecord, ScopeRecord, TypeFactRecord, ValueFactRecord
from .source import unparse


def extract_call_argument_bindings(
    module_name: str,
    tree: ast.Module,
    scopes: list[ScopeRecord],
    imports: list[ImportRecord],
    type_facts: list[TypeFactRecord],
    value_facts: list[ValueFactRecord],
) -> list[CallArgumentBindingRecord]:
    module_imports = [record for record in imports if record.source_module == module_name]
    parameter_index = _parameter_index(type_facts)
    value_index = _value_index(module_name, value_facts)
    records: list[CallArgumentBindingRecord] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        callee = _resolve_call_target(module_name, node.func, module_imports)
        if callee == "":
            continue
        parameters = parameter_index.get(callee, ())
        if not parameters:
            continue
        scope = _scope_for_line(scopes, node.lineno)
        records.extend(
            _positional_argument_bindings(
                module_name,
                scope,
                node,
                callee,
                parameters,
                value_index,
            )
        )
        records.extend(
            _keyword_argument_bindings(
                module_name,
                scope,
                node,
                callee,
                parameters,
                value_index,
            )
        )
    return records


def _positional_argument_bindings(
    module_name: str,
    scope: ScopeRecord,
    node: ast.Call,
    callee: str,
    parameters: tuple[TypeFactRecord, ...],
    value_index: dict[tuple[str, str], tuple[ValueFactRecord, ...]],
) -> list[CallArgumentBindingRecord]:
    records: list[CallArgumentBindingRecord] = []
    positional_parameters = [parameter for parameter in parameters if parameter.name not in {"self", "cls"}]
    for index, argument in enumerate(node.args):
        if index >= len(positional_parameters):
            continue
        parameter = positional_parameters[index]
        records.append(
            _binding_record(
                module_name,
                scope,
                node,
                callee,
                parameter,
                argument,
                value_index,
                reason="positional_argument_to_annotated_parameter",
            )
        )
    return records


def _keyword_argument_bindings(
    module_name: str,
    scope: ScopeRecord,
    node: ast.Call,
    callee: str,
    parameters: tuple[TypeFactRecord, ...],
    value_index: dict[tuple[str, str], tuple[ValueFactRecord, ...]],
) -> list[CallArgumentBindingRecord]:
    records: list[CallArgumentBindingRecord] = []
    parameters_by_name = {parameter.name: parameter for parameter in parameters}
    for keyword in node.keywords:
        if keyword.arg is None:
            continue
        if keyword.arg not in parameters_by_name:
            continue
        records.append(
            _binding_record(
                module_name,
                scope,
                node,
                callee,
                parameters_by_name[keyword.arg],
                keyword.value,
                value_index,
                reason="keyword_argument_to_annotated_parameter",
            )
        )
    return records


def _binding_record(
    module_name: str,
    scope: ScopeRecord,
    node: ast.Call,
    callee: str,
    parameter: TypeFactRecord,
    argument: ast.AST,
    value_index: dict[tuple[str, str], tuple[ValueFactRecord, ...]],
    reason: str,
) -> CallArgumentBindingRecord:
    argument_name = _argument_name(argument)
    sources = value_index.get((scope.qualname, argument_name), ()) if argument_name else ()
    return CallArgumentBindingRecord(
        caller_module=module_name,
        caller_scope=scope.qualname,
        call_line=node.lineno,
        callee_full_name=callee,
        parameter_name=parameter.name,
        parameter_annotation=parameter.annotation,
        argument_expression=unparse(argument),
        argument_name=argument_name,
        argument_value_sources=";".join(source.source_full_name for source in sources),
        reason=reason,
    )


def _parameter_index(type_facts: list[TypeFactRecord]) -> dict[str, tuple[TypeFactRecord, ...]]:
    grouped: dict[str, list[TypeFactRecord]] = {}
    for fact in type_facts:
        if fact.fact_kind != "function_parameter":
            continue
        grouped.setdefault(fact.owner_full_name, []).append(fact)
    return {key: tuple(value) for key, value in grouped.items()}


def _value_index(
    module_name: str,
    value_facts: list[ValueFactRecord],
) -> dict[tuple[str, str], tuple[ValueFactRecord, ...]]:
    grouped: dict[tuple[str, str], list[ValueFactRecord]] = {}
    for fact in value_facts:
        if fact.module != module_name:
            continue
        grouped.setdefault((fact.scope_name, fact.name), []).append(fact)
    return {key: tuple(value) for key, value in grouped.items()}


def _resolve_call_target(
    module_name: str,
    node: ast.AST,
    imports: list[ImportRecord],
) -> str:
    if isinstance(node, ast.Name):
        return _resolve_name_call(module_name, node.id, imports)
    if isinstance(node, ast.Attribute):
        receiver = _dotted_name(node.value)
        if receiver == "":
            return ""
        for record in imports:
            if record.import_kind != "import" or not record.resolved:
                continue
            local_name = record.as_name or record.imported_name.split(".", maxsplit=1)[0]
            if receiver == local_name:
                return f"{record.target_module}.{node.attr}"
    return ""


def _resolve_name_call(module_name: str, name: str, imports: list[ImportRecord]) -> str:
    for record in imports:
        if record.import_kind != "from_import" or not record.resolved:
            continue
        local_name = record.as_name or record.imported_name
        if local_name == name:
            return f"{record.target_module}.{record.imported_name}"
    return f"{module_name}.{name}"


def _argument_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _dotted_name(node.value)
        if prefix:
            return f"{prefix}.{node.attr}"
    return ""


def _scope_for_line(scopes: list[ScopeRecord], line: int) -> ScopeRecord:
    containing = [scope for scope in scopes if scope.line_start <= line <= scope.line_end]
    if not containing:
        raise AssertionError(f"No scope for line {line}")
    return max(containing, key=lambda scope: scope.line_start)

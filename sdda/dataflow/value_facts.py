from __future__ import annotations

import ast

from .models import ImportRecord, ScopeRecord, TypeFactRecord, ValueFactRecord
from .source import unparse


def extract_value_facts(
    module_name: str,
    tree: ast.Module,
    scopes: list[ScopeRecord],
    imports: list[ImportRecord],
    type_facts: list[TypeFactRecord],
) -> list[ValueFactRecord]:
    module_imports = [record for record in imports if record.source_module == module_name]
    type_index = _build_type_index(type_facts)
    facts: list[ValueFactRecord] = []
    for node in ast.walk(tree):
        assignment = _assignment_value_fact(
            module_name,
            node,
            scopes,
            module_imports,
            type_index,
        )
        if assignment is not None:
            facts.append(assignment)
    return facts


def _assignment_value_fact(
    module_name: str,
    node: ast.AST,
    scopes: list[ScopeRecord],
    imports: list[ImportRecord],
    type_index: dict[str, dict[str, str]],
) -> ValueFactRecord | None:
    target, value = _assignment_parts(node)
    if target is None:
        return None
    if not isinstance(value, ast.Call):
        return None
    call_target = _resolve_call_target(module_name, value.func, imports)
    if call_target == "":
        return None
    inferred_type = _inferred_call_type(call_target, type_index)
    if inferred_type == "":
        return None
    scope = _scope_for_line(scopes, node.lineno)
    return ValueFactRecord(
        module=module_name,
        scope_kind=scope.scope_kind,
        scope_name=scope.qualname,
        name=target,
        inferred_type=inferred_type,
        source_expression=unparse(value),
        source_full_name=call_target,
        line=node.lineno,
        reason="assignment_from_typed_call",
    )


def _assignment_parts(node: ast.AST) -> tuple[str | None, ast.AST | None]:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target = node.targets[0]
        if isinstance(target, ast.Name):
            return target.id, node.value
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id, node.value
    return None, None


def _build_type_index(type_facts: list[TypeFactRecord]) -> dict[str, dict[str, str]]:
    function_returns: dict[str, str] = {}
    classes: dict[str, str] = {}
    for fact in type_facts:
        if fact.fact_kind == "function_return":
            function_returns[fact.owner_full_name] = fact.annotation
        if fact.fact_kind in {"class", "dataclass"}:
            classes[fact.owner_full_name] = fact.owner_full_name
    return {
        "function_returns": function_returns,
        "classes": classes,
    }


def _inferred_call_type(call_target: str, type_index: dict[str, dict[str, str]]) -> str:
    function_returns = type_index["function_returns"]
    if call_target in function_returns:
        return function_returns[call_target]
    classes = type_index["classes"]
    if call_target in classes:
        return classes[call_target]
    return ""


def _resolve_call_target(
    module_name: str,
    node: ast.AST,
    imports: list[ImportRecord],
) -> str:
    if isinstance(node, ast.Name):
        return _resolve_name_call(module_name, node.id, imports)
    if isinstance(node, ast.Attribute):
        return _resolve_attribute_call(module_name, node, imports)
    return ""


def _resolve_name_call(module_name: str, name: str, imports: list[ImportRecord]) -> str:
    for record in imports:
        if record.import_kind != "from_import" or not record.resolved:
            continue
        local_name = record.as_name or record.imported_name
        if local_name == name:
            return f"{record.target_module}.{record.imported_name}"
    return f"{module_name}.{name}"


def _resolve_attribute_call(module_name: str, node: ast.Attribute, imports: list[ImportRecord]) -> str:
    receiver_name = _dotted_name(node.value)
    if receiver_name == "":
        return ""
    for record in imports:
        if record.import_kind != "import" or not record.resolved:
            continue
        local_name = record.as_name or record.imported_name.split(".", maxsplit=1)[0]
        if receiver_name == local_name:
            return f"{record.target_module}.{node.attr}"
    return f"{receiver_name}.{node.attr}"


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

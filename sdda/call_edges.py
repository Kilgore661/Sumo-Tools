from __future__ import annotations

import ast
import builtins
from dataclasses import dataclass

from .models import ImportRecord, ScopeRecord, TypeFactRecord
from .source import unparse

BUILTIN_CALL_NAMES = set(dir(builtins))


@dataclass(frozen=True)
class CallEdgeRecord:
    caller_module: str
    caller_scope: str
    call_line: int
    callee_expression: str
    callee_full_name: str
    resolution_kind: str
    reason: str


def extract_call_edges(
    module_name: str,
    tree: ast.Module,
    scopes: list[ScopeRecord],
    imports: list[ImportRecord],
    type_facts: list[TypeFactRecord],
) -> list[CallEdgeRecord]:
    module_imports = [record for record in imports if record.source_module == module_name]
    local_defs = _local_definition_names(module_name, type_facts)
    records: list[CallEdgeRecord] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        scope = _scope_for_line(scopes, node.lineno)
        callee_expression = unparse(node.func)
        callee_full_name, resolution_kind, reason = _resolve_call_target(
            module_name,
            scope,
            node.func,
            module_imports,
            local_defs,
        )
        records.append(
            CallEdgeRecord(
                caller_module=module_name,
                caller_scope=scope.qualname,
                call_line=node.lineno,
                callee_expression=callee_expression,
                callee_full_name=callee_full_name,
                resolution_kind=resolution_kind,
                reason=reason,
            )
        )
    return sorted(records, key=lambda row: (row.caller_module, row.caller_scope, row.call_line, row.callee_expression))


def _local_definition_names(module_name: str, type_facts: list[TypeFactRecord]) -> set[str]:
    names: set[str] = set()
    prefix = f"{module_name}."
    for fact in type_facts:
        if fact.owner_full_name.startswith(prefix):
            relative_name = fact.owner_full_name.removeprefix(prefix).split(".", maxsplit=1)[0]
            if relative_name:
                names.add(relative_name)
    return names


def _resolve_call_target(
    module_name: str,
    scope: ScopeRecord,
    node: ast.AST,
    imports: list[ImportRecord],
    local_defs: set[str],
) -> tuple[str, str, str]:
    if isinstance(node, ast.Name):
        return _resolve_name_call(module_name, node.id, imports, local_defs)
    if isinstance(node, ast.Attribute):
        receiver = _dotted_name(node.value)
        if receiver == "self":
            class_name = _class_scope_name(scope.qualname)
            if class_name:
                return f"{module_name}.{class_name}.{node.attr}", "current_class_method", "self_method_call"
        if receiver == "cls":
            class_name = _class_scope_name(scope.qualname)
            if class_name:
                return f"{module_name}.{class_name}.{node.attr}", "current_class_method", "cls_method_call"
        if receiver:
            imported, resolution_kind = _resolve_import_attribute(receiver, node.attr, imports)
            if imported:
                return imported, resolution_kind, "imported_module_attribute_call"
        return "", "unresolved_attribute", "attribute_receiver_not_resolved"
    return "", "unresolved_dynamic", "dynamic_call_expression"


def _resolve_name_call(
    module_name: str,
    name: str,
    imports: list[ImportRecord],
    local_defs: set[str],
) -> tuple[str, str, str]:
    for record in imports:
        if record.import_kind != "from_import":
            continue
        local_name = record.as_name or record.imported_name
        if local_name != name:
            continue
        resolution_kind = "from_import" if record.resolved else "external_from_import"
        return f"{record.target_module}.{record.imported_name}", resolution_kind, "from_import_name_call"
    if name in local_defs:
        return f"{module_name}.{name}", "same_module_definition", "same_module_name_call"
    if name in BUILTIN_CALL_NAMES:
        return f"builtins.{name}", "builtin", "builtin_name_call"
    return "", "unresolved_name", "name_not_imported_or_defined_in_module"


def _resolve_import_attribute(receiver: str, attr: str, imports: list[ImportRecord]) -> tuple[str, str]:
    for record in imports:
        if record.import_kind != "import":
            continue
        local_name = record.as_name or record.imported_name.split(".", maxsplit=1)[0]
        resolution_kind = "imported_attribute" if record.resolved else "external_imported_attribute"
        if receiver == local_name:
            return f"{record.target_module}.{attr}", resolution_kind
        if receiver.startswith(f"{local_name}."):
            suffix = receiver.removeprefix(f"{local_name}.")
            return f"{record.target_module}.{suffix}.{attr}", resolution_kind
    return "", ""


def _class_scope_name(scope_name: str) -> str:
    if "." not in scope_name:
        return ""
    return scope_name.split(".", maxsplit=1)[0]


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

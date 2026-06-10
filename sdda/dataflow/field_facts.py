from __future__ import annotations

import ast
from dataclasses import dataclass

from .models import FieldFactRecord, ImportRecord, ScopeRecord, TypeFactRecord, ValueFactRecord
from .source import unparse


@dataclass(frozen=True)
class LocalTypeFact:
    name: str
    annotation: str
    reason: str
    line: int


def extract_field_facts(
    module_name: str,
    tree: ast.Module,
    scopes: list[ScopeRecord],
    imports: list[ImportRecord],
    type_facts: list[TypeFactRecord],
    value_facts: list[ValueFactRecord],
) -> list[FieldFactRecord]:
    module_imports = [record for record in imports if record.source_module == module_name]
    dataclass_fields = _dataclass_fields(type_facts)
    local_types_by_scope = _local_types_by_scope(module_name, type_facts, value_facts)
    facts: list[FieldFactRecord] = []
    seen: set[tuple[str, str, str, int]] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if not isinstance(node.value, ast.Name):
            continue
        scope = _scope_for_line(scopes, node.lineno)
        local_type = local_types_by_scope.get((scope.qualname, node.value.id))
        if local_type is None:
            continue
        owner_full_name = _resolve_type_name(local_type.annotation, module_name, module_imports, type_facts)
        if owner_full_name == "":
            continue
        fields = dataclass_fields.get(owner_full_name, {})
        if node.attr not in fields:
            continue
        key = (scope.qualname, node.value.id, node.attr, node.lineno)
        if key in seen:
            continue
        seen.add(key)
        facts.append(
            FieldFactRecord(
                module=module_name,
                scope_kind=scope.scope_kind,
                scope_name=scope.qualname,
                expression=unparse(node),
                receiver_name=node.value.id,
                receiver_type=owner_full_name,
                field_name=node.attr,
                field_annotation=fields[node.attr],
                line=node.lineno,
                reason=f"dataclass_field_from_{local_type.reason}",
            )
        )
    return facts


def _dataclass_fields(type_facts: list[TypeFactRecord]) -> dict[str, dict[str, str]]:
    fields: dict[str, dict[str, str]] = {}
    for fact in type_facts:
        if fact.fact_kind != "dataclass_field":
            continue
        fields.setdefault(fact.owner_full_name, {})[fact.name] = fact.annotation
    return fields


def _local_types_by_scope(
    module_name: str,
    type_facts: list[TypeFactRecord],
    value_facts: list[ValueFactRecord],
) -> dict[tuple[str, str], LocalTypeFact]:
    local_types: dict[tuple[str, str], LocalTypeFact] = {}
    for fact in type_facts:
        if fact.module != module_name:
            continue
        if fact.fact_kind != "function_parameter":
            continue
        local_types[(fact.owner_qualname, fact.name)] = LocalTypeFact(
            name=fact.name,
            annotation=fact.annotation,
            reason="parameter_annotation",
            line=fact.line,
        )
    for fact in value_facts:
        if fact.module != module_name:
            continue
        local_types[(fact.scope_name, fact.name)] = LocalTypeFact(
            name=fact.name,
            annotation=fact.inferred_type,
            reason="value_fact",
            line=fact.line,
        )
    return local_types


def _resolve_type_name(
    annotation: str,
    module_name: str,
    imports: list[ImportRecord],
    type_facts: list[TypeFactRecord],
) -> str:
    clean_annotation = _clean_annotation(annotation)
    if clean_annotation == "":
        return ""
    class_names = _class_names(type_facts)
    if clean_annotation in class_names:
        return clean_annotation
    for record in imports:
        if record.import_kind != "from_import" or not record.resolved:
            continue
        local_name = record.as_name or record.imported_name
        if local_name == clean_annotation:
            return f"{record.target_module}.{record.imported_name}"
    same_module_name = f"{module_name}.{clean_annotation}"
    if same_module_name in class_names:
        return same_module_name
    short_matches = [full_name for full_name in class_names if full_name.rsplit(".", maxsplit=1)[-1] == clean_annotation]
    if len(short_matches) == 1:
        return short_matches[0]
    return ""


def _clean_annotation(annotation: str) -> str:
    annotation = annotation.strip()
    if "|" in annotation:
        parts = [part.strip() for part in annotation.split("|")]
        concrete_parts = [part for part in parts if part != "None"]
        if len(concrete_parts) == 1:
            return concrete_parts[0]
        return ""
    return annotation


def _class_names(type_facts: list[TypeFactRecord]) -> set[str]:
    return {
        fact.owner_full_name
        for fact in type_facts
        if fact.fact_kind in {"class", "dataclass"}
    }


def _scope_for_line(scopes: list[ScopeRecord], line: int) -> ScopeRecord:
    containing = [scope for scope in scopes if scope.line_start <= line <= scope.line_end]
    if not containing:
        raise AssertionError(f"No scope for line {line}")
    return max(containing, key=lambda scope: scope.line_start)

from __future__ import annotations

import ast

from .models import ModuleRecord, ReferenceRecord


def extract_references(
    module_name: str,
    tree: ast.Module,
    module_index: dict[str, ModuleRecord],
) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    for statement in ast.walk(tree):
        if isinstance(statement, ast.Import):
            records.extend(_import_references(module_name, statement, module_index))
        elif isinstance(statement, ast.ImportFrom):
            records.extend(_from_import_references(module_name, statement, module_index))
    return records


def inbound_references_by_module(references: list[ReferenceRecord]) -> dict[str, list[ReferenceRecord]]:
    grouped: dict[str, list[ReferenceRecord]] = {}
    for record in references:
        if record.source_module == record.target_module:
            continue
        grouped.setdefault(record.target_module, []).append(record)
    return grouped


def _import_references(
    source_module: str,
    statement: ast.Import,
    module_index: dict[str, ModuleRecord],
) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    for alias in statement.names:
        target = _resolve_module(alias.name, module_index)
        if not target:
            continue
        records.append(
            ReferenceRecord(
                source_module=source_module,
                target_module=target,
                reference_kind="import",
                imported_name=alias.name,
                line=statement.lineno,
            )
        )
    return records


def _from_import_references(
    source_module: str,
    statement: ast.ImportFrom,
    module_index: dict[str, ModuleRecord],
) -> list[ReferenceRecord]:
    base_module = _resolve_relative_module(source_module, statement.module or "", statement.level)
    records: list[ReferenceRecord] = []

    if base_module:
        base_target = _resolve_module(base_module, module_index)
        if base_target:
            for alias in statement.names:
                records.append(
                    ReferenceRecord(
                        source_module=source_module,
                        target_module=base_target,
                        reference_kind="from_import_module",
                        imported_name=alias.name,
                        line=statement.lineno,
                    )
                )

    for alias in statement.names:
        candidate = f"{base_module}.{alias.name}" if base_module else alias.name
        target = _resolve_module(candidate, module_index)
        if not target:
            continue
        records.append(
            ReferenceRecord(
                source_module=source_module,
                target_module=target,
                reference_kind="from_import_submodule",
                imported_name=alias.name,
                line=statement.lineno,
            )
        )
    return records


def _resolve_module(name: str, module_index: dict[str, ModuleRecord]) -> str:
    if name in module_index:
        return name
    parts = name.split(".")
    while parts:
        candidate = ".".join(parts)
        if candidate in module_index:
            return candidate
        parts.pop()
    return ""


def _resolve_relative_module(source_module: str, imported_module: str, level: int) -> str:
    if level <= 0:
        return imported_module
    package_parts = source_module.split(".")[:-1]
    keep_count = max(len(package_parts) - level + 1, 0)
    base_parts = package_parts[:keep_count]
    if imported_module:
        base_parts.extend(imported_module.split("."))
    return ".".join(part for part in base_parts if part)

from __future__ import annotations

import ast
from collections import deque

from .models import ImportRecord, ModuleRecord


def build_reachable_imports(
    root_module: str,
    module_index: dict[str, ModuleRecord],
) -> tuple[list[str], list[ImportRecord]]:
    if root_module not in module_index:
        raise KeyError(f"Root module is not in module index: {root_module}")

    imports: list[ImportRecord] = []
    seen: set[str] = set()
    queue: deque[str] = deque([root_module])

    while queue:
        module_name = queue.popleft()
        if module_name in seen:
            continue
        seen.add(module_name)

        module_record = module_index[module_name]
        tree = ast.parse(module_record.path.read_text(encoding="utf-8"))
        module_imports = _extract_imports(module_name, tree, module_index)
        imports.extend(module_imports)

        for import_record in module_imports:
            if import_record.resolved and import_record.target_module not in seen:
                queue.append(import_record.target_module)

    return sorted(seen), imports


def _extract_imports(
    source_module: str,
    tree: ast.AST,
    module_index: dict[str, ModuleRecord],
) -> list[ImportRecord]:
    records: list[ImportRecord] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            records.extend(_import_records(source_module, node, module_index))
        elif isinstance(node, ast.ImportFrom):
            records.extend(_from_import_records(source_module, node, module_index))
    return records


def _import_records(
    source_module: str,
    node: ast.Import,
    module_index: dict[str, ModuleRecord],
) -> list[ImportRecord]:
    records: list[ImportRecord] = []
    for alias in node.names:
        target = _resolve_absolute_import(alias.name, module_index)
        records.append(
            ImportRecord(
                source_module=source_module,
                target_module=target or alias.name,
                import_kind="import",
                imported_name=alias.name,
                as_name=alias.asname or "",
                level=0,
                line=node.lineno,
                resolved=target is not None,
                reason="project_module" if target else "external_or_unresolved",
            )
        )
    return records


def _from_import_records(
    source_module: str,
    node: ast.ImportFrom,
    module_index: dict[str, ModuleRecord],
) -> list[ImportRecord]:
    records: list[ImportRecord] = []
    base_module = _resolve_from_base(source_module, node)
    for alias in node.names:
        candidate = _resolve_from_target(base_module, alias.name, module_index)
        target = candidate or base_module or alias.name
        records.append(
            ImportRecord(
                source_module=source_module,
                target_module=target,
                import_kind="from_import",
                imported_name=alias.name,
                as_name=alias.asname or "",
                level=node.level,
                line=node.lineno,
                resolved=candidate is not None,
                reason="project_module" if candidate else "external_or_unresolved",
            )
        )
    return records


def _resolve_absolute_import(
    name: str,
    module_index: dict[str, ModuleRecord],
) -> str | None:
    parts = name.split(".")
    for end in range(len(parts), 0, -1):
        candidate = ".".join(parts[:end])
        if candidate in module_index:
            return candidate
    return None


def _resolve_from_base(source_module: str, node: ast.ImportFrom) -> str:
    module = node.module or ""
    if node.level == 0:
        return module

    source_parts = source_module.split(".")
    package_parts = source_parts[:-1]
    if node.level > 1:
        package_parts = package_parts[: -(node.level - 1)]
    if module:
        package_parts.extend(module.split("."))
    return ".".join(package_parts)


def _resolve_from_target(
    base_module: str,
    imported_name: str,
    module_index: dict[str, ModuleRecord],
) -> str | None:
    candidates = []
    if base_module and imported_name != "*":
        candidates.append(f"{base_module}.{imported_name}")
    if base_module:
        candidates.append(base_module)
    for candidate in candidates:
        if candidate in module_index:
            return candidate
    return None

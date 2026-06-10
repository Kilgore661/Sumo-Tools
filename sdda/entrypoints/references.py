from __future__ import annotations

import ast

from .models import ModuleRecord, ReferenceRecord, WarningRecord


def extract_references(
    module_name: str,
    tree: ast.Module,
    module_index: dict[str, ModuleRecord],
    import_root_package: str,
) -> tuple[list[ReferenceRecord], list[WarningRecord]]:
    references: list[ReferenceRecord] = []
    warnings: list[WarningRecord] = []
    resolver = _ModuleResolver(module_index, import_root_package)

    for statement in ast.walk(tree):
        if isinstance(statement, ast.Import):
            new_references, new_warnings = _import_references(module_name, statement, resolver)
            references.extend(new_references)
            warnings.extend(new_warnings)
        elif isinstance(statement, ast.ImportFrom):
            new_references, new_warnings = _from_import_references(module_name, statement, resolver)
            references.extend(new_references)
            warnings.extend(new_warnings)
    return references, warnings


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
    resolver: "_ModuleResolver",
) -> tuple[list[ReferenceRecord], list[WarningRecord]]:
    records: list[ReferenceRecord] = []
    warnings: list[WarningRecord] = []
    for alias in statement.names:
        resolution = resolver.resolve(alias.name)
        warnings.extend(
            _resolution_warnings(
                source_module=source_module,
                line=statement.lineno,
                imported_name=alias.name,
                resolution=resolution,
            )
        )
        if not resolution.target:
            continue
        records.append(
            ReferenceRecord(
                source_module=source_module,
                target_module=resolution.target,
                reference_kind=_reference_kind("import", resolution),
                imported_name=alias.name,
                line=statement.lineno,
            )
        )
    return records, warnings


def _from_import_references(
    source_module: str,
    statement: ast.ImportFrom,
    resolver: "_ModuleResolver",
) -> tuple[list[ReferenceRecord], list[WarningRecord]]:
    base_module = _resolve_relative_module(source_module, statement.module or "", statement.level)
    records: list[ReferenceRecord] = []
    warnings: list[WarningRecord] = []

    if base_module:
        base_resolution = resolver.resolve(base_module)
        warnings.extend(
            _resolution_warnings(
                source_module=source_module,
                line=statement.lineno,
                imported_name=base_module,
                resolution=base_resolution,
            )
        )
        if base_resolution.target:
            for alias in statement.names:
                records.append(
                    ReferenceRecord(
                        source_module=source_module,
                        target_module=base_resolution.target,
                        reference_kind=_reference_kind("from_import_module", base_resolution),
                        imported_name=alias.name,
                        line=statement.lineno,
                    )
                )

    for alias in statement.names:
        candidate = f"{base_module}.{alias.name}" if base_module else alias.name
        resolution = resolver.resolve(candidate)
        warnings.extend(
            _resolution_warnings(
                source_module=source_module,
                line=statement.lineno,
                imported_name=candidate,
                resolution=resolution,
            )
        )
        if not resolution.target:
            continue
        records.append(
            ReferenceRecord(
                source_module=source_module,
                target_module=resolution.target,
                reference_kind=_reference_kind("from_import_submodule", resolution),
                imported_name=alias.name,
                line=statement.lineno,
            )
        )
    return records, warnings


class _Resolution:
    def __init__(self, target: str = "", method: str = "", detail: str = "") -> None:
        self.target = target
        self.method = method
        self.detail = detail


class _ModuleResolver:
    def __init__(self, module_index: dict[str, ModuleRecord], import_root_package: str) -> None:
        self.module_index = module_index
        self.import_root_package = import_root_package

    def resolve(self, name: str) -> _Resolution:
        exact = self._resolve_exact_or_parent(name)
        if exact.target:
            return exact
        return self._resolve_import_root_relative(name)

    def _resolve_exact_or_parent(self, name: str) -> _Resolution:
        if name in self.module_index:
            return _Resolution(target=name, method="exact")
        parts = name.split(".")
        while parts:
            candidate = ".".join(parts)
            if candidate in self.module_index:
                return _Resolution(target=candidate, method="parent")
            parts.pop()
        return _Resolution()

    def _resolve_import_root_relative(self, name: str) -> _Resolution:
        if not self.import_root_package:
            return _Resolution()
        prefix = f"{self.import_root_package}."
        if not name.startswith(prefix):
            return _Resolution()
        local_name = name[len(prefix):]
        if not local_name:
            return _Resolution()
        exact = self._resolve_exact_or_parent(local_name)
        if not exact.target:
            return _Resolution(
                method="unresolved_import_root_relative",
                detail=(
                    f"Import starts with narrowed import root package `{self.import_root_package}`, "
                    f"but local candidate `{local_name}` is not indexed."
                ),
            )
        return _Resolution(
            target=exact.target,
            method="import_root_relative",
            detail=(
                f"Resolved absolute import `{name}` to local module `{exact.target}` "
                f"inside import root package `{self.import_root_package}`."
            ),
        )


def _reference_kind(base_kind: str, resolution: _Resolution) -> str:
    if resolution.method == "import_root_relative":
        return f"{base_kind}_import_root_relative"
    return base_kind


def _resolution_warnings(
    *,
    source_module: str,
    line: int,
    imported_name: str,
    resolution: _Resolution,
) -> list[WarningRecord]:
    if resolution.method == "import_root_relative":
        return [
            WarningRecord(
                source_module=source_module,
                line=line,
                severity="note",
                warning_kind="import_root_relative_resolution",
                imported_name=imported_name,
                resolved_module=resolution.target,
                detail=resolution.detail,
            )
        ]
    if resolution.method == "unresolved_import_root_relative":
        return [
            WarningRecord(
                source_module=source_module,
                line=line,
                severity="warning",
                warning_kind="unresolved_import_root_relative_import",
                imported_name=imported_name,
                resolved_module="",
                detail=resolution.detail,
            )
        ]
    return []


def _resolve_relative_module(source_module: str, imported_module: str, level: int) -> str:
    if level <= 0:
        return imported_module
    package_parts = source_module.split(".")[:-1]
    keep_count = max(len(package_parts) - level + 1, 0)
    base_parts = package_parts[:keep_count]
    if imported_module:
        base_parts.extend(imported_module.split("."))
    return ".".join(part for part in base_parts if part)

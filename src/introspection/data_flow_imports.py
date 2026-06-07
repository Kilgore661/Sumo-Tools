"""Import discovery and transitive reachability for data-flow introspection."""

from __future__ import annotations

import ast
from pathlib import Path

from src.introspection.data_flow_model import ImportRef, ModuleRef


def build_module_index(import_root: Path) -> dict[str, ModuleRef]:
    """Return module-name to module reference for Python files below ``import_root``."""

    result: dict[str, ModuleRef] = {}
    for path in sorted(import_root.rglob("*.py")):
        if any(part in {".git", "__pycache__", ".venv", "venv"} for part in path.parts):
            continue
        module_name = module_name_for_path(import_root, path)
        result[module_name] = ModuleRef(module_name=module_name, path=path)
    return result


def module_name_for_path(import_root: Path, path: Path) -> str:
    """Return dotted module name for a path below ``import_root``."""

    relative = path.relative_to(import_root).with_suffix("")
    return ".".join(relative.parts)


def parse_python(path: Path) -> ast.AST | None:
    """Parse a Python file, returning None if parsing fails."""

    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return None


def import_refs_for_tree(
    module_name: str,
    tree: ast.AST,
    module_index: dict[str, ModuleRef],
) -> list[ImportRef]:
    """Return internal imports from ``tree``."""

    imports: list[ImportRef] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(import_refs_for_import(module_name, node, module_index))
        elif isinstance(node, ast.ImportFrom):
            imports.extend(import_refs_for_import_from(module_name, node, module_index))
    return imports


def import_refs_for_import(
    module_name: str,
    node: ast.Import,
    module_index: dict[str, ModuleRef],
) -> list[ImportRef]:
    """Return internal import refs for an ``import x`` node."""

    refs: list[ImportRef] = []
    for alias in node.names:
        imported_module = resolve_absolute_import(alias.name, module_index)
        if not imported_module:
            continue
        refs.append(
            ImportRef(
                importer_module=module_name,
                imported_module=imported_module,
                imported_name="",
                alias=alias.asname or alias.name.split(".")[-1],
                import_style="import",
                line_number=node.lineno,
            )
        )
    return refs


def import_refs_for_import_from(
    module_name: str,
    node: ast.ImportFrom,
    module_index: dict[str, ModuleRef],
) -> list[ImportRef]:
    """Return internal import refs for a ``from x import y`` node."""

    base_module = resolve_import_from_base(module_name, node, module_index)
    if not base_module:
        return []

    refs: list[ImportRef] = []
    for alias in node.names:
        imported_module = resolve_imported_symbol(base_module, alias.name, module_index)
        refs.append(
            ImportRef(
                importer_module=module_name,
                imported_module=imported_module,
                imported_name=alias.name,
                alias=alias.asname or alias.name,
                import_style="from",
                line_number=node.lineno,
            )
        )
    return refs


def resolve_absolute_import(name: str, module_index: dict[str, ModuleRef]) -> str:
    """Resolve an absolute import to the nearest discovered project module."""

    parts = name.split(".")
    for end in range(len(parts), 0, -1):
        candidate = ".".join(parts[:end])
        if candidate in module_index:
            return candidate
    return ""


def resolve_import_from_base(
    current_module: str,
    node: ast.ImportFrom,
    module_index: dict[str, ModuleRef],
) -> str:
    """Resolve the base module in a from-import node."""

    if node.level == 0:
        return resolve_absolute_import(node.module or "", module_index)

    current_parts = current_module.split(".")[:-1]
    if node.level > len(current_parts) + 1:
        return ""
    base_parts = current_parts[: len(current_parts) - node.level + 1]
    if node.module:
        base_parts.extend(node.module.split("."))
    return resolve_absolute_import(".".join(base_parts), module_index)


def resolve_imported_symbol(
    base_module: str,
    symbol_name: str,
    module_index: dict[str, ModuleRef],
) -> str:
    """Resolve ``from base import symbol`` to a module when symbol is a module."""

    candidate = f"{base_module}.{symbol_name}"
    if candidate in module_index:
        return candidate
    return base_module


def reachable_module_distances(
    root_module: str,
    imports_by_module: dict[str, tuple[ImportRef, ...]],
) -> dict[str, int]:
    """Return transitive internal modules reachable from ``root_module``."""

    distances = {root_module: 0}
    queue = [root_module]
    while queue:
        module_name = queue.pop(0)
        next_distance = distances[module_name] + 1
        for import_ref in imports_by_module.get(module_name, ()):
            imported_module = import_ref.imported_module
            if imported_module in distances:
                continue
            distances[imported_module] = next_distance
            queue.append(imported_module)
    return distances

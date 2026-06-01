"""Parse Python modules and extract raw import syntax."""

from __future__ import annotations

import ast
from pathlib import Path

from src.introspection.python_import_model import ImportEdge, PythonModule
from src.introspection.python_import_resolution import (
    find_project_module_path,
    resolve_relative_module,
    resolution_status,
)
from src.introspection.python_module_discovery import module_name_for_path


def is_name_main_check(node: ast.AST) -> bool:
    """Return true for the literal expression ``__name__ == "__main__"``."""

    if not isinstance(node, ast.Compare):
        return False
    if len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq):
        return False
    if len(node.comparators) != 1:
        return False

    left = node.left
    right = node.comparators[0]
    return (
        isinstance(left, ast.Name)
        and left.id == "__name__"
        and isinstance(right, ast.Constant)
        and right.value == "__main__"
    ) or (
        isinstance(right, ast.Name)
        and right.id == "__name__"
        and isinstance(left, ast.Constant)
        and left.value == "__main__"
    )


def has_main_guard(tree: ast.Module) -> bool:
    """Detect a top-level ``if __name__ == "__main__"`` guard."""

    return any(isinstance(node, ast.If) and is_name_main_check(node.test) for node in tree.body)


def defines_main(tree: ast.Module) -> bool:
    """Detect a top-level function named ``main``."""

    return any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"
        for node in tree.body
    )


def inspect_module(repo_root: Path, path: Path) -> tuple[PythonModule, ast.Module | None]:
    """Parse one Python file and return module facts plus its AST when available."""

    module_name = module_name_for_path(repo_root, path)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    except SyntaxError as error:
        module = PythonModule(
            path=path.relative_to(repo_root),
            module_name=module_name,
            has_main_guard=False,
            defines_main=False,
            parse_status="syntax_error",
            parse_error=str(error),
        )
        return module, None

    module = PythonModule(
        path=path.relative_to(repo_root),
        module_name=module_name,
        has_main_guard=has_main_guard(tree),
        defines_main=defines_main(tree),
        parse_status="ok",
        parse_error="",
    )
    return module, tree


def import_edges_for_tree(
    module: PythonModule,
    tree: ast.Module,
    module_index: dict[str, Path],
) -> list[ImportEdge]:
    """Extract syntactic import edges from an AST."""

    edges: list[ImportEdge] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            edges.extend(import_edges_from_import_node(module, node, module_index))
        if isinstance(node, ast.ImportFrom):
            edges.extend(import_edges_from_import_from_node(module, node, module_index))
    return edges


def import_edges_from_import_node(
    module: PythonModule,
    node: ast.Import,
    module_index: dict[str, Path],
) -> list[ImportEdge]:
    """Extract import edges from an ``import x`` AST node."""

    edges: list[ImportEdge] = []
    for alias in node.names:
        resolved_module = alias.name
        resolved_path = find_project_module_path(module_index, resolved_module)
        edges.append(
            ImportEdge(
                importer_path=module.path,
                importer_module=module.module_name,
                import_style="import",
                imported_module_text=alias.name,
                imported_symbol="",
                imported_alias=alias.asname or "",
                level=0,
                is_relative=False,
                resolved_module=resolved_module,
                resolved_path=resolved_path,
                resolved_symbol_module="",
                resolved_symbol_path="",
                resolution_status=resolution_status(resolved_module, resolved_path, ""),
            )
        )
    return edges


def import_edges_from_import_from_node(
    module: PythonModule,
    node: ast.ImportFrom,
    module_index: dict[str, Path],
) -> list[ImportEdge]:
    """Extract import edges from a ``from x import y`` AST node."""

    module_text = node.module or ""
    if node.level:
        resolved_module = resolve_relative_module(
            module.path,
            module.module_name,
            node.level,
            module_text,
        )
    else:
        resolved_module = module_text

    resolved_path = find_project_module_path(module_index, resolved_module)
    edges: list[ImportEdge] = []
    for alias in node.names:
        resolved_symbol_module = ""
        resolved_symbol_path = ""
        if alias.name != "*":
            candidate_symbol_module = f"{resolved_module}.{alias.name}" if resolved_module else alias.name
            candidate_symbol_path = find_project_module_path(module_index, candidate_symbol_module)
            if candidate_symbol_path:
                resolved_symbol_module = candidate_symbol_module
                resolved_symbol_path = candidate_symbol_path

        edges.append(
            ImportEdge(
                importer_path=module.path,
                importer_module=module.module_name,
                import_style="from",
                imported_module_text=module_text,
                imported_symbol=alias.name,
                imported_alias=alias.asname or "",
                level=node.level,
                is_relative=bool(node.level),
                resolved_module=resolved_module,
                resolved_path=resolved_path,
                resolved_symbol_module=resolved_symbol_module,
                resolved_symbol_path=resolved_symbol_path,
                resolution_status=resolution_status(
                    resolved_module,
                    resolved_path,
                    resolved_symbol_module,
                ),
            )
        )
    return edges

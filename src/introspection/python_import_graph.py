"""Build a static import graph for project Python modules.

This module inspects Python source files with ``ast`` and writes two CSV files:

* ``python_modules.csv`` records one row per discovered module.
* ``python_import_edges.csv`` records one row per import edge.

The output is intentionally mechanical evidence. It does not try to decide final
module ownership or producer status.
"""

from __future__ import annotations

import argparse
import ast
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_SOURCE_DIRS = ("src", "tests")
DEFAULT_OUTPUT_DIR = Path("files") / "output" / "introspection"


@dataclass(frozen=True)
class PythonModule:
    """A Python file discovered under one of the inspected source roots."""

    path: Path
    module_name: str
    has_main_guard: bool
    defines_main: bool
    parse_status: str
    parse_error: str


@dataclass(frozen=True)
class ImportEdge:
    """One syntactic import statement edge found in a project module."""

    importer_path: Path
    importer_module: str
    import_style: str
    imported_module_text: str
    imported_symbol: str
    imported_alias: str
    level: int
    is_relative: bool
    resolved_module: str
    resolved_path: str
    resolved_symbol_module: str
    resolved_symbol_path: str
    resolution_status: str


def repo_root_from_this_file() -> Path:
    """Return the repository root when this module lives under ``src/introspection``."""

    return Path(__file__).resolve().parents[2]


def module_name_for_path(repo_root: Path, path: Path) -> str:
    """Convert a Python source path into the importable project module name."""

    relative = path.relative_to(repo_root).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def package_name_for_module(path: Path, module_name: str) -> str:
    """Return the package context used to resolve relative imports."""

    if path.name == "__init__.py":
        return module_name
    return module_name.rpartition(".")[0]


def iter_python_paths(repo_root: Path, source_dirs: Iterable[str]) -> list[Path]:
    """Find Python files under the configured project source roots."""

    paths: list[Path] = []
    for source_dir in source_dirs:
        root = repo_root / source_dir
        if root.exists():
            paths.extend(path for path in root.rglob("*.py") if path.is_file())
    return sorted(paths)


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
        isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == "main"
        for node in tree.body
    )


def resolve_relative_module(importer_path: Path, importer_module: str, level: int, module_text: str) -> str:
    """Resolve the module portion of a relative import into a dotted module name."""

    package = package_name_for_module(importer_path, importer_module)
    package_parts = package.split(".") if package else []
    if level > 1:
        package_parts = package_parts[: -(level - 1)]
    module_parts = module_text.split(".") if module_text else []
    return ".".join([*package_parts, *module_parts])


def find_project_module_path(module_index: dict[str, Path], module_name: str) -> str:
    """Return a project path for a resolved module name, if known."""

    if module_name in module_index:
        return module_index[module_name].as_posix()
    return ""


def resolution_status(resolved_module: str, resolved_path: str, resolved_symbol_module: str) -> str:
    """Classify whether an import resolved to known project source."""

    if resolved_symbol_module:
        return "resolved_symbol_module"
    if resolved_path:
        return "resolved_module"
    if resolved_module.startswith("src.") or resolved_module.startswith("tests."):
        return "unresolved_project_module"
    return "external_or_stdlib"


def import_edges_for_tree(
    module: PythonModule,
    tree: ast.Module,
    module_index: dict[str, Path],
) -> list[ImportEdge]:
    """Extract syntactic import edges from an AST."""

    edges: list[ImportEdge] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
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

        if isinstance(node, ast.ImportFrom):
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

            for alias in node.names:
                symbol = alias.name
                resolved_symbol_module = ""
                resolved_symbol_path = ""
                if symbol != "*":
                    candidate_symbol_module = f"{resolved_module}.{symbol}" if resolved_module else symbol
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
                        imported_symbol=symbol,
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


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Write dictionaries to a UTF-8 CSV file with a stable header."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def module_rows(modules: list[PythonModule], edges: list[ImportEdge]) -> list[dict[str, object]]:
    """Build summary rows for discovered modules."""

    imported_by_modules: dict[str, set[str]] = {module.module_name: set() for module in modules}
    imported_symbols: dict[str, set[str]] = {module.module_name: set() for module in modules}
    imported_main_by: dict[str, set[str]] = {module.module_name: set() for module in modules}
    imported_non_main_by: dict[str, set[str]] = {module.module_name: set() for module in modules}

    for edge in edges:
        target_module = edge.resolved_module
        if not target_module:
            continue
        if target_module not in imported_by_modules:
            continue
        imported_by_modules[target_module].add(edge.importer_module)
        if edge.imported_symbol:
            imported_symbols[target_module].add(edge.imported_symbol)
            if edge.imported_symbol == "main":
                imported_main_by[target_module].add(edge.importer_module)
            else:
                imported_non_main_by[target_module].add(edge.importer_module)

    rows: list[dict[str, object]] = []
    for module in modules:
        importers = sorted(imported_by_modules[module.module_name])
        rows.append(
            {
                "module_path": module.path.as_posix(),
                "module_name": module.module_name,
                "has_main_guard": module.has_main_guard,
                "defines_main": module.defines_main,
                "parse_status": module.parse_status,
                "parse_error": module.parse_error,
                "imported_by_count": len(importers),
                "imported_by_modules": ";".join(importers),
                "imported_symbols": ";".join(sorted(imported_symbols[module.module_name])),
                "main_imported_by_modules": ";".join(sorted(imported_main_by[module.module_name])),
                "non_main_imported_by_modules": ";".join(
                    sorted(imported_non_main_by[module.module_name])
                ),
            }
        )
    return rows


def edge_rows(edges: list[ImportEdge]) -> list[dict[str, object]]:
    """Build CSV rows for import edges."""

    return [
        {
            "importer_path": edge.importer_path.as_posix(),
            "importer_module": edge.importer_module,
            "import_style": edge.import_style,
            "imported_module_text": edge.imported_module_text,
            "imported_symbol": edge.imported_symbol,
            "imported_alias": edge.imported_alias,
            "level": edge.level,
            "is_relative": edge.is_relative,
            "resolved_module": edge.resolved_module,
            "resolved_path": edge.resolved_path,
            "resolved_symbol_module": edge.resolved_symbol_module,
            "resolved_symbol_path": edge.resolved_symbol_path,
            "resolution_status": edge.resolution_status,
        }
        for edge in edges
    ]


def run_audit(repo_root: Path, source_dirs: list[str], output_dir: Path) -> None:
    """Inspect project Python imports and write the two audit CSV files."""

    python_paths = iter_python_paths(repo_root, source_dirs)
    module_index = {
        module_name_for_path(repo_root, path): path.relative_to(repo_root)
        for path in python_paths
    }

    modules: list[PythonModule] = []
    trees: dict[str, ast.Module] = {}
    for path in python_paths:
        module, tree = inspect_module(repo_root, path)
        modules.append(module)
        if tree is not None:
            trees[module.module_name] = tree

    edges: list[ImportEdge] = []
    module_by_name = {module.module_name: module for module in modules}
    for module_name in sorted(trees):
        module = module_by_name[module_name]
        edges.extend(import_edges_for_tree(module, trees[module_name], module_index))

    write_csv(
        output_dir / "python_modules.csv",
        [
            "module_path",
            "module_name",
            "has_main_guard",
            "defines_main",
            "parse_status",
            "parse_error",
            "imported_by_count",
            "imported_by_modules",
            "imported_symbols",
            "main_imported_by_modules",
            "non_main_imported_by_modules",
        ],
        module_rows(modules, edges),
    )
    write_csv(
        output_dir / "python_import_edges.csv",
        [
            "importer_path",
            "importer_module",
            "import_style",
            "imported_module_text",
            "imported_symbol",
            "imported_alias",
            "level",
            "is_relative",
            "resolved_module",
            "resolved_path",
            "resolved_symbol_module",
            "resolved_symbol_path",
            "resolution_status",
        ],
        edge_rows(edges),
    )

    print(f"Wrote {output_dir / 'python_modules.csv'}")
    print(f"Wrote {output_dir / 'python_import_edges.csv'}")
    print(f"Modules: {len(modules)}")
    print(f"Import edges: {len(edges)}")


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for the import graph audit."""

    parser = argparse.ArgumentParser(
        description="Write a static Python import graph for project modules."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=repo_root_from_this_file(),
        help="Repository root. Defaults to the root inferred from this file.",
    )
    parser.add_argument(
        "--source-dir",
        action="append",
        dest="source_dirs",
        default=None,
        help="Source directory to scan. May be supplied more than once.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for CSV outputs. Defaults to files/output/introspection.",
    )
    return parser


def main() -> None:
    """Run the import graph audit from the command line."""

    parser = build_parser()
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    source_dirs = args.source_dirs if args.source_dirs is not None else list(DEFAULT_SOURCE_DIRS)
    output_dir = args.output_dir if args.output_dir is not None else repo_root / DEFAULT_OUTPUT_DIR
    run_audit(repo_root, source_dirs, output_dir)


if __name__ == "__main__":
    main()

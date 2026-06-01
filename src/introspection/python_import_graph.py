"""Command-line entry point for static Python import graph introspection."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

from src.introspection.python_import_model import ImportEdge, PythonModule
from src.introspection.python_import_parser import import_edges_for_tree, inspect_module
from src.introspection.python_import_reports import write_reports
from src.introspection.python_module_discovery import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_DIRS,
    build_module_index,
    iter_python_paths,
    repo_root_from_this_file,
)


def run_audit(repo_root: Path, source_dirs: list[str], output_dir: Path) -> None:
    """Inspect project Python imports and write audit CSV files."""

    python_paths = iter_python_paths(repo_root, source_dirs)
    module_index = build_module_index(repo_root, python_paths)

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

    write_reports(output_dir, modules, edges)

    print(f"Wrote {output_dir / 'python_modules.csv'}")
    print(f"Wrote {output_dir / 'python_import_edges.csv'}")
    print(f"Wrote {output_dir / 'python_entry_candidates.csv'}")
    print(f"Wrote {output_dir / 'python_imported_main.csv'}")
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

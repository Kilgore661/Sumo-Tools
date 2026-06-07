"""Build and persist transitive data-flow evidence for a Python module."""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

from src.introspection.data_flow_artifacts import artifact_uses_for_module
from src.introspection.data_flow_imports import (
    build_module_index,
    import_refs_for_tree,
    parse_python,
    reachable_module_distances,
)
from src.introspection.data_flow_model import DataFlowGraph
from src.introspection.data_flow_paths import (
    build_local_constants_by_module,
    build_visible_constants_by_module,
)
from src.introspection.data_flow_reports import write_data_flow_reports


DEFAULT_OUTPUT_ROOT = Path("files") / "output" / "introspection" / "data_flow"


def build_data_flow_graph(module_id: str, import_root: Path = Path(".")) -> DataFlowGraph:
    """Build transitive data-flow evidence for ``module_id``."""

    resolved_import_root = import_root.resolve()
    module_index = build_module_index(resolved_import_root)
    if module_id not in module_index:
        raise ValueError(f"Module not found below {resolved_import_root}: {module_id}")

    parsed_trees = parse_modules(module_index)
    imports_by_module = {
        module_name: tuple(import_refs_for_tree(module_name, tree, module_index))
        for module_name, tree in parsed_trees.items()
    }
    local_constants_by_module = build_local_constants_by_module(parsed_trees)
    constants_by_module = build_visible_constants_by_module(
        local_constants_by_module,
        imports_by_module,
        parsed_trees,
    )

    distances = reachable_module_distances(module_id, imports_by_module)
    sorted_module_names = sorted(distances, key=lambda name: (distances[name], name))
    modules = tuple(module_index[module_name] for module_name in sorted_module_names)
    imports = tuple(
        import_ref
        for module_name in sorted_module_names
        for import_ref in imports_by_module.get(module_name, ())
        if import_ref.imported_module in distances
    )
    artifact_uses = tuple(
        use
        for module_name in sorted_module_names
        for use in artifact_uses_for_module(
            module_name,
            parsed_trees[module_name],
            distances[module_name],
            constants_by_module.get(module_name, {}),
        )
    )

    return DataFlowGraph(
        root_module=module_id,
        modules=modules,
        imports=imports,
        artifact_uses=artifact_uses,
    )


def parse_modules(module_index: dict[str, object]) -> dict[str, ast.AST]:
    """Parse every module in ``module_index`` that can be parsed."""

    parsed_trees: dict[str, ast.AST] = {}
    for module_name, module_ref in module_index.items():
        tree = parse_python(module_ref.path)
        if tree is not None:
            parsed_trees[module_name] = tree
    return parsed_trees


def safe_name(name: str) -> str:
    """Return a filesystem-safe name."""

    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._-")
    return safe or "root"


def build_parser() -> argparse.ArgumentParser:
    """Create command-line parser."""

    parser = argparse.ArgumentParser(description="Extract transitive file data-flow evidence for a Python module.")
    parser.add_argument("module_id", help="Dotted module id, e.g. src.products.make_site2.__main__.")
    parser.add_argument(
        "--import-root",
        type=Path,
        default=Path("."),
        help="Path that dotted module names are relative to. Defaults to current directory.",
    )
    return parser


def main() -> None:
    """Run data-flow extraction from the command line."""

    parser = build_parser()
    args = parser.parse_args()
    graph = build_data_flow_graph(args.module_id, args.import_root)
    output_dir = (DEFAULT_OUTPUT_ROOT / safe_name(args.module_id)).resolve()
    write_data_flow_reports(graph, output_dir)

    print(f"Wrote {output_dir / 'data_flow.json'}")
    print(f"Wrote {output_dir / 'modules.csv'}")
    print(f"Wrote {output_dir / 'imports.csv'}")
    print(f"Wrote {output_dir / 'artifact_uses.csv'}")
    print(f"Wrote {output_dir / 'artifacts.csv'}")
    print(f"Wrote {output_dir / 'generated_prerequisites.csv'}")
    print(f"Wrote {output_dir / 'summary.csv'}")
    print(f"Modules: {len(graph.modules)}")
    print(f"Imports: {len(graph.imports)}")
    print(f"Artifact uses: {len(graph.artifact_uses)}")
    print(f"Inputs: {len(graph.input_artifacts)}")
    print(f"Outputs: {len(graph.output_artifacts)}")
    print(f"Generated prerequisites: {len(graph.generated_prerequisites)}")


if __name__ == "__main__":
    main()

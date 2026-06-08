"""Build and persist transitive data-flow evidence for a Python module."""

from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from src.introspection.data_flow_artifacts import (
    artifact_uses_for_module,
    cross_module_function_seed_constants,
)
from src.introspection.data_flow_imports import (
    build_module_index,
    import_refs_for_tree,
    parse_python,
    reachable_module_distances,
)
from src.introspection.data_flow_model import DataFlowGraph, ModuleRef
from src.introspection.data_flow_paths import (
    build_local_constants_by_module,
    build_visible_constants_by_module,
)
from src.introspection.data_flow_reports import write_data_flow_reports


DEFAULT_OUTPUT_ROOT = Path("files") / "output" / "introspection" / "data_flow"


@dataclass(frozen=True)
class TimedDataFlowGraph:
    """A data-flow graph plus coarse build timings."""

    graph: DataFlowGraph
    timings: tuple[tuple[str, float], ...]


def build_data_flow_graph(module_id: str, import_root: Path = Path(".")) -> DataFlowGraph:
    """Build transitive data-flow evidence for ``module_id``."""

    return build_timed_data_flow_graph(module_id, import_root).graph


def build_timed_data_flow_graph(
    module_id: str,
    import_root: Path = Path("."),
) -> TimedDataFlowGraph:
    """Build transitive data-flow evidence and coarse timing information."""

    timings: list[tuple[str, float]] = []
    total_start = perf_counter()

    phase_start = perf_counter()
    resolved_import_root = import_root.resolve()
    module_index = build_module_index(resolved_import_root)
    if module_id not in module_index:
        raise ValueError(f"Module not found below {resolved_import_root}: {module_id}")
    record_timing(timings, "index modules", phase_start)

    phase_start = perf_counter()
    parsed_trees = parse_modules(module_index)
    imports_by_module = {
        module_name: tuple(import_refs_for_tree(module_name, tree, module_index))
        for module_name, tree in parsed_trees.items()
    }
    record_timing(timings, "parse modules and imports", phase_start)

    phase_start = perf_counter()
    local_constants_by_module = build_local_constants_by_module(parsed_trees, module_index)
    constants_by_module = build_visible_constants_by_module(
        local_constants_by_module,
        imports_by_module,
        parsed_trees,
    )
    function_seed_constants_by_module = cross_module_function_seed_constants(
        parsed_trees,
        imports_by_module,
        constants_by_module,
    )
    record_timing(timings, "resolve constants", phase_start)

    phase_start = perf_counter()
    distances = reachable_module_distances(module_id, imports_by_module)
    sorted_module_names = sorted(distances, key=lambda name: (distances[name], name))
    modules = tuple(module_index[module_name] for module_name in sorted_module_names)
    imports = tuple(
        import_ref
        for module_name in sorted_module_names
        for import_ref in imports_by_module.get(module_name, ())
        if import_ref.imported_module in distances
    )
    record_timing(timings, "compute reachability", phase_start)

    phase_start = perf_counter()
    artifact_uses = tuple(
        use
        for module_name in sorted_module_names
        for use in artifact_uses_for_module(
            module_name,
            parsed_trees[module_name],
            distances[module_name],
            constants_by_module.get(module_name, {}),
            function_seed_constants_by_module.get(module_name, {}),
        )
    )
    record_timing(timings, "extract artifacts", phase_start)

    graph = DataFlowGraph(
        root_module=module_id,
        modules=modules,
        imports=imports,
        artifact_uses=artifact_uses,
    )
    timings.append(("total build", perf_counter() - total_start))
    return TimedDataFlowGraph(graph=graph, timings=tuple(timings))


def record_timing(timings: list[tuple[str, float]], label: str, start: float) -> None:
    """Append elapsed time for a named phase."""

    timings.append((label, perf_counter() - start))


def parse_modules(module_index: dict[str, ModuleRef]) -> dict[str, ast.AST]:
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

    total_start = perf_counter()
    parser = build_parser()
    args = parser.parse_args()
    timed_graph = build_timed_data_flow_graph(args.module_id, args.import_root)
    graph = timed_graph.graph
    output_dir = (DEFAULT_OUTPUT_ROOT / safe_name(args.module_id)).resolve()

    report_start = perf_counter()
    write_data_flow_reports(graph, output_dir)
    report_elapsed = perf_counter() - report_start
    total_elapsed = perf_counter() - total_start

    print(f"Wrote {output_dir / 'data_flow.json'}")
    print(f"Wrote {output_dir / 'modules.csv'}")
    print(f"Wrote {output_dir / 'imports.csv'}")
    print(f"Wrote {output_dir / 'artifact_uses.csv'}")
    print(f"Wrote {output_dir / 'artifacts.csv'}")
    print(f"Wrote {output_dir / 'generated_prerequisites.csv'}")
    print(f"Wrote {output_dir / 'root_artifacts.csv'}")
    print(f"Wrote {output_dir / 'upstream_rules.csv'}")
    print(f"Wrote {output_dir / 'root_rule.csv'}")
    print(f"Wrote {output_dir / 'Makefile.candidate'}")
    print(f"Wrote {output_dir / 'summary.csv'}")
    print(f"Modules: {len(graph.modules)}")
    print(f"Imports: {len(graph.imports)}")
    print(f"Artifact uses: {len(graph.artifact_uses)}")
    print(f"Inputs: {len(graph.input_artifacts)}")
    print(f"Outputs: {len(graph.output_artifacts)}")
    print(f"Generated prerequisites: {len(graph.generated_prerequisites)}")
    print("Timings:")
    for label, elapsed in timed_graph.timings:
        print(f"  {label}: {elapsed:.3f}s")
    print(f"  write reports: {report_elapsed:.3f}s")
    print(f"  total command: {total_elapsed:.3f}s")


if __name__ == "__main__":
    main()

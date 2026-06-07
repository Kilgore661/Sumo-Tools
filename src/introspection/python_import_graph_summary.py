"""Command-line graph summary for static Python import graph CSV outputs."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("files") / "output" / "introspection"


@dataclass(frozen=True)
class GraphNode:
    """One project Python module in the import graph."""

    module_name: str
    module_path: str


@dataclass(frozen=True)
class GraphEdge:
    """One directed project import edge."""

    importer_module: str
    imported_module: str


def repo_root_from_this_file() -> Path:
    """Return the repository root when this module lives under ``src/introspection``."""

    return Path(__file__).resolve().parents[2]


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV file into dictionaries."""

    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Write dictionaries to a UTF-8 CSV file with a stable header."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_nodes(modules_csv: Path) -> dict[str, GraphNode]:
    """Load graph nodes from ``python_modules.csv``."""

    nodes: dict[str, GraphNode] = {}
    for row in read_csv(modules_csv):
        module_name = row["module_name"]
        nodes[module_name] = GraphNode(
            module_name=module_name,
            module_path=row["module_path"],
        )
    return nodes


def target_module_for_edge(row: dict[str, str], known_modules: set[str]) -> str:
    """Return the resolved project target module for an import-edge row."""

    resolved_symbol_module = row["resolved_symbol_module"]
    if resolved_symbol_module in known_modules:
        return resolved_symbol_module

    resolved_module = row["resolved_module"]
    if resolved_module in known_modules:
        return resolved_module

    return ""


def load_edges(edges_csv: Path, known_modules: set[str]) -> set[GraphEdge]:
    """Load directed project import edges from ``python_import_edges.csv``."""

    edges: set[GraphEdge] = set()
    for row in read_csv(edges_csv):
        importer_module = row["importer_module"]
        if importer_module not in known_modules:
            continue

        imported_module = target_module_for_edge(row, known_modules)
        if not imported_module:
            continue

        if importer_module == imported_module:
            continue

        edges.add(
            GraphEdge(
                importer_module=importer_module,
                imported_module=imported_module,
            )
        )

    return edges


def build_directed_neighbours(
    nodes: dict[str, GraphNode],
    edges: set[GraphEdge],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Return outgoing and incoming neighbour maps for directed graph edges."""

    outgoing: dict[str, set[str]] = {module_name: set() for module_name in nodes}
    incoming: dict[str, set[str]] = {module_name: set() for module_name in nodes}

    for edge in edges:
        outgoing[edge.importer_module].add(edge.imported_module)
        incoming[edge.imported_module].add(edge.importer_module)

    return outgoing, incoming


def build_weak_neighbours(
    nodes: dict[str, GraphNode],
    edges: set[GraphEdge],
) -> dict[str, set[str]]:
    """Return neighbours for the graph with import direction ignored."""

    neighbours: dict[str, set[str]] = {module_name: set() for module_name in nodes}
    for edge in edges:
        neighbours[edge.importer_module].add(edge.imported_module)
        neighbours[edge.imported_module].add(edge.importer_module)
    return neighbours


def connected_components(
    nodes: dict[str, GraphNode],
    edges: set[GraphEdge],
) -> list[list[str]]:
    """Return weakly connected components sorted by size and module name."""

    neighbours = build_weak_neighbours(nodes, edges)
    unseen = set(nodes)
    components: list[list[str]] = []

    while unseen:
        start = min(unseen)
        stack = [start]
        component: set[str] = set()

        while stack:
            module_name = stack.pop()
            if module_name in component:
                continue
            component.add(module_name)
            unseen.discard(module_name)

            for neighbour in sorted(neighbours[module_name], reverse=True):
                if neighbour not in component:
                    stack.append(neighbour)

        components.append(sorted(component))

    return sorted(components, key=lambda component: (-len(component), component[0]))


def component_id_by_module(components: list[list[str]]) -> dict[str, int]:
    """Return a one-based component id for each module."""

    result: dict[str, int] = {}
    for index, component in enumerate(components, start=1):
        for module_name in component:
            result[module_name] = index
    return result


def node_rows(
    nodes: dict[str, GraphNode],
    outgoing: dict[str, set[str]],
    incoming: dict[str, set[str]],
    components: list[list[str]],
) -> list[dict[str, object]]:
    """Build rows for ``python_graph_nodes.csv``."""

    component_ids = component_id_by_module(components)
    component_sizes = {
        index: len(component)
        for index, component in enumerate(components, start=1)
    }

    rows: list[dict[str, object]] = []
    for module_name in sorted(nodes):
        indegree = len(incoming[module_name])
        outdegree = len(outgoing[module_name])
        component_id = component_ids[module_name]
        component_size = component_sizes[component_id]
        rows.append(
            {
                "module_name": module_name,
                "module_path": nodes[module_name].module_path,
                "indegree": indegree,
                "outdegree": outdegree,
                "is_source": indegree == 0,
                "is_sink": outdegree == 0,
                "imports": ";".join(sorted(outgoing[module_name])),
                "imported_by": ";".join(sorted(incoming[module_name])),
                "component_id": component_id,
                "component_size": component_size,
                "is_singleton_component": component_size == 1,
            }
        )

    return rows


def component_rows(
    components: list[list[str]],
    outgoing: dict[str, set[str]],
    incoming: dict[str, set[str]],
) -> list[dict[str, object]]:
    """Build rows for ``python_graph_components.csv``."""

    rows: list[dict[str, object]] = []
    for component_id, component in enumerate(components, start=1):
        source_count = sum(1 for module_name in component if not incoming[module_name])
        sink_count = sum(1 for module_name in component if not outgoing[module_name])
        rows.append(
            {
                "component_id": component_id,
                "component_size": len(component),
                "source_count": source_count,
                "sink_count": sink_count,
                "is_singleton_component": len(component) == 1,
                "module_names": ";".join(component),
            }
        )

    return rows


def summary_rows(
    nodes: dict[str, GraphNode],
    edges: set[GraphEdge],
    outgoing: dict[str, set[str]],
    incoming: dict[str, set[str]],
    components: list[list[str]],
) -> list[dict[str, object]]:
    """Build rows for ``python_graph_summary.csv``."""

    source_count = sum(1 for module_name in nodes if not incoming[module_name])
    sink_count = sum(1 for module_name in nodes if not outgoing[module_name])
    singleton_count = sum(1 for component in components if len(component) == 1)

    return [
        {"metric": "module_count", "value": len(nodes)},
        {"metric": "edge_count", "value": len(edges)},
        {"metric": "source_count", "value": source_count},
        {"metric": "sink_count", "value": sink_count},
        {"metric": "component_count", "value": len(components)},
        {"metric": "singleton_component_count", "value": singleton_count},
        {
            "metric": "non_singleton_component_count",
            "value": len(components) - singleton_count,
        },
    ]


def run_summary(input_dir: Path, output_dir: Path) -> None:
    """Read import graph CSVs and write graph summary CSVs."""

    modules_csv = input_dir / "python_modules.csv"
    edges_csv = input_dir / "python_import_edges.csv"

    nodes = load_nodes(modules_csv)
    edges = load_edges(edges_csv, set(nodes))
    outgoing, incoming = build_directed_neighbours(nodes, edges)
    components = connected_components(nodes, edges)

    write_csv(
        output_dir / "python_graph_nodes.csv",
        [
            "module_name",
            "module_path",
            "indegree",
            "outdegree",
            "is_source",
            "is_sink",
            "imports",
            "imported_by",
            "component_id",
            "component_size",
            "is_singleton_component",
        ],
        node_rows(nodes, outgoing, incoming, components),
    )

    write_csv(
        output_dir / "python_graph_components.csv",
        [
            "component_id",
            "component_size",
            "source_count",
            "sink_count",
            "is_singleton_component",
            "module_names",
        ],
        component_rows(components, outgoing, incoming),
    )

    write_csv(
        output_dir / "python_graph_summary.csv",
        ["metric", "value"],
        summary_rows(nodes, edges, outgoing, incoming, components),
    )

    print(f"Wrote {output_dir / 'python_graph_nodes.csv'}")
    print(f"Wrote {output_dir / 'python_graph_components.csv'}")
    print(f"Wrote {output_dir / 'python_graph_summary.csv'}")
    print(f"Modules: {len(nodes)}")
    print(f"Edges: {len(edges)}")
    print(f"Components: {len(components)}")


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for graph summary generation."""

    parser = argparse.ArgumentParser(
        description="Summarise the static Python import graph CSV outputs."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing python_modules.csv and python_import_edges.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for graph summary CSV outputs.",
    )
    return parser


def main() -> None:
    """Run the graph summary command."""

    parser = build_parser()
    args = parser.parse_args()

    repo_root = repo_root_from_this_file()
    input_dir = args.input_dir if args.input_dir is not None else repo_root / DEFAULT_OUTPUT_DIR
    output_dir = args.output_dir if args.output_dir is not None else input_dir

    run_summary(input_dir, output_dir)


if __name__ == "__main__":
    main()

"""Command-line reachability analysis for static Python import graph CSV outputs."""

from __future__ import annotations

import argparse
import csv
from collections import deque
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("files") / "output" / "introspection"
DEFAULT_ENTRY_POINT = "src.products.make_site2.__main__"


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


def build_outgoing_neighbours(
    nodes: dict[str, GraphNode],
    edges: set[GraphEdge],
) -> dict[str, set[str]]:
    """Return outgoing neighbour map for directed graph edges."""

    outgoing: dict[str, set[str]] = {module_name: set() for module_name in nodes}
    for edge in edges:
        outgoing[edge.importer_module].add(edge.imported_module)
    return outgoing


def build_directed_neighbours(
    module_names: set[str],
    edges: set[GraphEdge],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Return outgoing and incoming maps restricted to the supplied modules."""

    outgoing: dict[str, set[str]] = {module_name: set() for module_name in module_names}
    incoming: dict[str, set[str]] = {module_name: set() for module_name in module_names}

    for edge in edges:
        if edge.importer_module not in module_names or edge.imported_module not in module_names:
            continue
        outgoing[edge.importer_module].add(edge.imported_module)
        incoming[edge.imported_module].add(edge.importer_module)

    return outgoing, incoming


def build_weak_neighbours(
    module_names: set[str],
    edges: set[GraphEdge],
) -> dict[str, set[str]]:
    """Return weak neighbours restricted to the supplied modules."""

    neighbours: dict[str, set[str]] = {module_name: set() for module_name in module_names}
    for edge in edges:
        if edge.importer_module not in module_names or edge.imported_module not in module_names:
            continue
        neighbours[edge.importer_module].add(edge.imported_module)
        neighbours[edge.imported_module].add(edge.importer_module)
    return neighbours


def connected_components(module_names: set[str], edges: set[GraphEdge]) -> list[list[str]]:
    """Return weakly connected components restricted to the supplied modules."""

    neighbours = build_weak_neighbours(module_names, edges)
    unseen = set(module_names)
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


def shortest_reachability(
    entry_point: str,
    outgoing: dict[str, set[str]],
) -> dict[str, tuple[int, str]]:
    """Return reachable modules with distance and parent from one entry point."""

    if entry_point not in outgoing:
        return {}

    reached: dict[str, tuple[int, str]] = {entry_point: (0, "")}
    queue: deque[str] = deque([entry_point])

    while queue:
        module_name = queue.popleft()
        distance, _parent = reached[module_name]
        for child in sorted(outgoing[module_name]):
            if child in reached:
                continue
            reached[child] = (distance + 1, module_name)
            queue.append(child)

    return reached


def path_from_entry(
    module_name: str,
    reached: dict[str, tuple[int, str]],
) -> str:
    """Return one shortest path from the entry point to a reached module."""

    if module_name not in reached:
        return ""

    path = [module_name]
    parent = reached[module_name][1]
    while parent:
        path.append(parent)
        parent = reached[parent][1]
    return " -> ".join(reversed(path))


def reached_by_any_entry(
    nodes: dict[str, GraphNode],
    entry_points: list[str],
    outgoing: dict[str, set[str]],
) -> tuple[dict[str, set[str]], dict[str, list[int]]]:
    """Return entry-point coverage and distances for each module."""

    reached_by_entry: dict[str, set[str]] = {module_name: set() for module_name in nodes}
    distances: dict[str, list[int]] = {module_name: [] for module_name in nodes}

    for entry_point in entry_points:
        reached = shortest_reachability(entry_point, outgoing)
        for module_name, (distance, _parent) in reached.items():
            reached_by_entry[module_name].add(entry_point)
            distances[module_name].append(distance)

    return reached_by_entry, distances


def unreachable_module_names(
    nodes: dict[str, GraphNode],
    entry_points: list[str],
    outgoing: dict[str, set[str]],
) -> set[str]:
    """Return modules not reachable from any supplied entry point."""

    reached_by_entry, _distances = reached_by_any_entry(nodes, entry_points, outgoing)
    return {
        module_name
        for module_name in nodes
        if not reached_by_entry[module_name]
    }


def reachability_rows(
    nodes: dict[str, GraphNode],
    entry_points: list[str],
    outgoing: dict[str, set[str]],
) -> list[dict[str, object]]:
    """Build one reachability row per entry point per module."""

    rows: list[dict[str, object]] = []
    for entry_point in entry_points:
        reached = shortest_reachability(entry_point, outgoing)
        for module_name in sorted(nodes):
            is_reachable = module_name in reached
            distance = reached[module_name][0] if is_reachable else ""
            parent = reached[module_name][1] if is_reachable else ""
            rows.append(
                {
                    "entry_point": entry_point,
                    "module_name": module_name,
                    "module_path": nodes[module_name].module_path,
                    "is_reachable": is_reachable,
                    "distance": distance,
                    "parent_module": parent,
                    "path_from_entry": path_from_entry(module_name, reached),
                }
            )
    return rows


def unreachable_rows(
    nodes: dict[str, GraphNode],
    entry_points: list[str],
    outgoing: dict[str, set[str]],
) -> list[dict[str, object]]:
    """Build compact rows for modules not reached by any supplied entry point."""

    reached_by_entry, _distances = reached_by_any_entry(nodes, entry_points, outgoing)

    rows: list[dict[str, object]] = []
    for module_name in sorted(nodes):
        if reached_by_entry[module_name]:
            continue
        rows.append(
            {
                "module_name": module_name,
                "module_path": nodes[module_name].module_path,
                "reached_by_entry_points": "",
                "minimum_distance": "",
            }
        )
    return rows


def coverage_rows(
    nodes: dict[str, GraphNode],
    entry_points: list[str],
    outgoing: dict[str, set[str]],
) -> list[dict[str, object]]:
    """Build one coverage row per module across all supplied entry points."""

    reached_by_entry, distances = reached_by_any_entry(nodes, entry_points, outgoing)

    rows: list[dict[str, object]] = []
    for module_name in sorted(nodes):
        module_distances = distances[module_name]
        rows.append(
            {
                "module_name": module_name,
                "module_path": nodes[module_name].module_path,
                "is_reachable_from_any_entry": bool(reached_by_entry[module_name]),
                "reached_by_entry_points": ";".join(sorted(reached_by_entry[module_name])),
                "minimum_distance": min(module_distances) if module_distances else "",
            }
        )
    return rows


def unreachable_component_maps(
    unreachable: set[str],
    edges: set[GraphEdge],
) -> tuple[list[list[str]], dict[str, int], dict[int, int]]:
    """Return components plus lookup maps for the unreachable induced subgraph."""

    components = connected_components(unreachable, edges)
    component_id_by_module: dict[str, int] = {}
    component_size_by_id: dict[int, int] = {}

    for component_id, component in enumerate(components, start=1):
        component_size_by_id[component_id] = len(component)
        for module_name in component:
            component_id_by_module[module_name] = component_id

    return components, component_id_by_module, component_size_by_id


def unreachable_node_rows(
    nodes: dict[str, GraphNode],
    unreachable: set[str],
    edges: set[GraphEdge],
) -> list[dict[str, object]]:
    """Build node rows for the unreachable induced subgraph."""

    outgoing, incoming = build_directed_neighbours(unreachable, edges)
    _components, component_ids, component_sizes = unreachable_component_maps(unreachable, edges)

    rows: list[dict[str, object]] = []
    for module_name in sorted(unreachable):
        component_id = component_ids[module_name]
        component_size = component_sizes[component_id]
        rows.append(
            {
                "module_name": module_name,
                "module_path": nodes[module_name].module_path,
                "indegree_within_unreachable": len(incoming[module_name]),
                "outdegree_within_unreachable": len(outgoing[module_name]),
                "is_source_within_unreachable": len(incoming[module_name]) == 0,
                "is_sink_within_unreachable": len(outgoing[module_name]) == 0,
                "imports_within_unreachable": ";".join(sorted(outgoing[module_name])),
                "imported_by_within_unreachable": ";".join(sorted(incoming[module_name])),
                "component_id": component_id,
                "component_size": component_size,
                "is_singleton_component": component_size == 1,
            }
        )
    return rows


def unreachable_component_rows(
    unreachable: set[str],
    edges: set[GraphEdge],
) -> list[dict[str, object]]:
    """Build component rows for the unreachable induced subgraph."""

    outgoing, incoming = build_directed_neighbours(unreachable, edges)
    components = connected_components(unreachable, edges)

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
    entry_points: list[str],
    outgoing: dict[str, set[str]],
    unreachable: set[str],
    unreachable_components: list[list[str]],
) -> list[dict[str, object]]:
    """Build summary metric rows for reachability analysis."""

    reached_any: set[str] = set()
    rows: list[dict[str, object]] = [
        {"metric": "module_count", "value": len(nodes)},
        {"metric": "entry_point_count", "value": len(entry_points)},
    ]

    for entry_point in entry_points:
        reached = shortest_reachability(entry_point, outgoing)
        reached_any.update(reached)
        rows.append(
            {
                "metric": f"reachable_from:{entry_point}",
                "value": len(reached),
            }
        )
        rows.append(
            {
                "metric": f"unreachable_from:{entry_point}",
                "value": len(nodes) - len(reached),
            }
        )

    singleton_count = sum(1 for component in unreachable_components if len(component) == 1)
    rows.extend(
        [
            {"metric": "reachable_from_any_entry", "value": len(reached_any)},
            {"metric": "unreachable_from_all_entries", "value": len(unreachable)},
            {"metric": "unreachable_component_count", "value": len(unreachable_components)},
            {"metric": "unreachable_singleton_component_count", "value": singleton_count},
            {
                "metric": "unreachable_non_singleton_component_count",
                "value": len(unreachable_components) - singleton_count,
            },
        ]
    )
    return rows


def validate_entry_points(entry_points: list[str], nodes: dict[str, GraphNode]) -> None:
    """Raise a clear error if any requested entry point is not a known module."""

    missing = [entry_point for entry_point in entry_points if entry_point not in nodes]
    if not missing:
        return

    available_hint = "\n".join(
        module_name for module_name in sorted(nodes) if module_name.endswith(".__main__")
    )
    raise SystemExit(
        "Unknown entry point(s): "
        + ", ".join(missing)
        + "\nKnown __main__ modules include:\n"
        + available_hint
    )


def run_reachability(input_dir: Path, output_dir: Path, entry_points: list[str]) -> None:
    """Read import graph CSVs and write reachability CSVs."""

    modules_csv = input_dir / "python_modules.csv"
    edges_csv = input_dir / "python_import_edges.csv"

    nodes = load_nodes(modules_csv)
    validate_entry_points(entry_points, nodes)
    edges = load_edges(edges_csv, set(nodes))
    outgoing = build_outgoing_neighbours(nodes, edges)
    unreachable = unreachable_module_names(nodes, entry_points, outgoing)
    unreachable_components = connected_components(unreachable, edges)

    write_csv(
        output_dir / "python_reachability.csv",
        [
            "entry_point",
            "module_name",
            "module_path",
            "is_reachable",
            "distance",
            "parent_module",
            "path_from_entry",
        ],
        reachability_rows(nodes, entry_points, outgoing),
    )
    write_csv(
        output_dir / "python_unreachable_from_entry.csv",
        [
            "module_name",
            "module_path",
            "reached_by_entry_points",
            "minimum_distance",
        ],
        unreachable_rows(nodes, entry_points, outgoing),
    )
    write_csv(
        output_dir / "python_entry_coverage.csv",
        [
            "module_name",
            "module_path",
            "is_reachable_from_any_entry",
            "reached_by_entry_points",
            "minimum_distance",
        ],
        coverage_rows(nodes, entry_points, outgoing),
    )
    write_csv(
        output_dir / "python_unreachable_nodes.csv",
        [
            "module_name",
            "module_path",
            "indegree_within_unreachable",
            "outdegree_within_unreachable",
            "is_source_within_unreachable",
            "is_sink_within_unreachable",
            "imports_within_unreachable",
            "imported_by_within_unreachable",
            "component_id",
            "component_size",
            "is_singleton_component",
        ],
        unreachable_node_rows(nodes, unreachable, edges),
    )
    write_csv(
        output_dir / "python_unreachable_components.csv",
        [
            "component_id",
            "component_size",
            "source_count",
            "sink_count",
            "is_singleton_component",
            "module_names",
        ],
        unreachable_component_rows(unreachable, edges),
    )
    write_csv(
        output_dir / "python_reachability_summary.csv",
        ["metric", "value"],
        summary_rows(nodes, entry_points, outgoing, unreachable, unreachable_components),
    )

    print(f"Wrote {output_dir / 'python_reachability.csv'}")
    print(f"Wrote {output_dir / 'python_unreachable_from_entry.csv'}")
    print(f"Wrote {output_dir / 'python_entry_coverage.csv'}")
    print(f"Wrote {output_dir / 'python_unreachable_nodes.csv'}")
    print(f"Wrote {output_dir / 'python_unreachable_components.csv'}")
    print(f"Wrote {output_dir / 'python_reachability_summary.csv'}")
    print(f"Modules: {len(nodes)}")
    print(f"Entry points: {len(entry_points)}")
    print(f"Unreachable modules: {len(unreachable)}")
    print(f"Unreachable components: {len(unreachable_components)}")


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for reachability generation."""

    parser = argparse.ArgumentParser(
        description="Report directed module reachability from one or more entry points."
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
        help="Directory for reachability CSV outputs.",
    )
    parser.add_argument(
        "--entry-point",
        action="append",
        dest="entry_points",
        default=None,
        help="Entry-point module to walk from. May be supplied more than once.",
    )
    return parser


def main() -> None:
    """Run the reachability command."""

    parser = build_parser()
    args = parser.parse_args()

    repo_root = repo_root_from_this_file()
    input_dir = args.input_dir if args.input_dir is not None else repo_root / DEFAULT_OUTPUT_DIR
    output_dir = args.output_dir if args.output_dir is not None else input_dir
    entry_points = args.entry_points if args.entry_points is not None else [DEFAULT_ENTRY_POINT]

    run_reachability(input_dir, output_dir, entry_points)


if __name__ == "__main__":
    main()

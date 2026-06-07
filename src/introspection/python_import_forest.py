"""Build and persist a directed forest of Python module imports.

The forest is the internal import digraph induced by a folder of Python files.  Edges
use the convention ``importer -> imported``.  Weakly connected components are
expected to have exactly one source module, where a source has indegree zero.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from src.introspection.python_import_model import ImportEdge, PythonModule
from src.introspection.python_import_parser import import_edges_for_tree, inspect_module
from src.introspection.python_module_discovery import module_name_for_path


OUTPUT_SUFFIX = "import_forest"


@dataclass(frozen=True)
class ForestNode:
    """One Python module in an import forest."""

    module_name: str
    module_path: str
    has_main_guard: bool
    defines_main: bool
    parse_status: str
    parse_error: str


@dataclass(frozen=True)
class ForestEdge:
    """One directed internal import edge in an import forest."""

    importer_module: str
    imported_module: str
    import_style: str
    imported_module_text: str
    imported_symbol: str
    imported_alias: str
    level: int
    is_relative: bool
    resolution_status: str


@dataclass(frozen=True)
class ForestComponent:
    """One weakly connected component of the import forest."""

    component_id: int
    module_names: tuple[str, ...]
    source_modules: tuple[str, ...]
    sink_modules: tuple[str, ...]
    status: str

    @property
    def component_size(self) -> int:
        """Return the number of modules in the component."""

        return len(self.module_names)

    @property
    def source_count(self) -> int:
        """Return the number of source modules in the component."""

        return len(self.source_modules)

    @property
    def sink_count(self) -> int:
        """Return the number of sink modules in the component."""

        return len(self.sink_modules)

    @property
    def is_valid_tree(self) -> bool:
        """Return true when the component satisfies the one-source invariant."""

        return self.status == "valid_tree"


@dataclass(frozen=True)
class PythonImportForest:
    """An in-memory directed forest of internal Python module imports."""

    folder: Path
    import_root: Path
    nodes: dict[str, ForestNode]
    edges: frozenset[ForestEdge]
    outgoing: dict[str, frozenset[str]]
    incoming: dict[str, frozenset[str]]
    components: tuple[ForestComponent, ...]

    @property
    def source_modules(self) -> tuple[str, ...]:
        """Return all modules with no incoming internal import edges."""

        return tuple(module_name for module_name in sorted(self.nodes) if not self.incoming[module_name])

    @property
    def sink_modules(self) -> tuple[str, ...]:
        """Return all modules with no outgoing internal import edges."""

        return tuple(module_name for module_name in sorted(self.nodes) if not self.outgoing[module_name])

    @property
    def valid_components(self) -> tuple[ForestComponent, ...]:
        """Return components satisfying the one-source invariant."""

        return tuple(component for component in self.components if component.status == "valid_tree")

    @property
    def invalid_components(self) -> tuple[ForestComponent, ...]:
        """Return components that do not satisfy the one-source invariant."""

        return tuple(
            component
            for component in self.components
            if component.status in {"zero_sources", "multiple_sources"}
        )

    @property
    def isolated_components(self) -> tuple[ForestComponent, ...]:
        """Return one-node components with no internal imports."""

        return tuple(component for component in self.components if component.status == "isolated")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation of the forest."""

        return {
            "folder": self.folder.as_posix(),
            "import_root": self.import_root.as_posix(),
            "nodes": [node_to_dict(self.nodes[module_name]) for module_name in sorted(self.nodes)],
            "edges": [edge_to_dict(edge) for edge in sorted_edges(self.edges)],
            "components": [component_to_dict(component) for component in self.components],
        }

    def write_json(self, path: Path) -> None:
        """Persist the forest as canonical UTF-8 JSON."""

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def write_csvs(self, output_dir: Path, output_stem: str | None = None) -> None:
        """Persist node, edge, component, and summary CSV files.

        When ``output_stem`` is omitted, filenames are derived from the input
        folder, for example ``src_import_forest_nodes.csv``.
        """

        write_forest_csvs(output_dir, self, output_stem)


def node_to_dict(node: ForestNode) -> dict[str, Any]:
    """Return a JSON-serialisable node dictionary."""

    return {
        "module_name": node.module_name,
        "module_path": node.module_path,
        "has_main_guard": node.has_main_guard,
        "defines_main": node.defines_main,
        "parse_status": node.parse_status,
        "parse_error": node.parse_error,
    }


def edge_to_dict(edge: ForestEdge) -> dict[str, Any]:
    """Return a JSON-serialisable edge dictionary."""

    return {
        "importer_module": edge.importer_module,
        "imported_module": edge.imported_module,
        "import_style": edge.import_style,
        "imported_module_text": edge.imported_module_text,
        "imported_symbol": edge.imported_symbol,
        "imported_alias": edge.imported_alias,
        "level": edge.level,
        "is_relative": edge.is_relative,
        "resolution_status": edge.resolution_status,
    }


def component_to_dict(component: ForestComponent) -> dict[str, Any]:
    """Return a JSON-serialisable component dictionary."""

    return {
        "component_id": component.component_id,
        "component_size": component.component_size,
        "source_count": component.source_count,
        "sink_count": component.sink_count,
        "status": component.status,
        "module_names": list(component.module_names),
        "source_modules": list(component.source_modules),
        "sink_modules": list(component.sink_modules),
    }


def read_python_import_forest(path: Path) -> PythonImportForest:
    """Load a persisted forest JSON file into memory."""

    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = {
        row["module_name"]: ForestNode(
            module_name=row["module_name"],
            module_path=row["module_path"],
            has_main_guard=bool(row["has_main_guard"]),
            defines_main=bool(row["defines_main"]),
            parse_status=row["parse_status"],
            parse_error=row["parse_error"],
        )
        for row in data["nodes"]
    }
    edges = frozenset(
        ForestEdge(
            importer_module=row["importer_module"],
            imported_module=row["imported_module"],
            import_style=row["import_style"],
            imported_module_text=row["imported_module_text"],
            imported_symbol=row["imported_symbol"],
            imported_alias=row["imported_alias"],
            level=int(row["level"]),
            is_relative=bool(row["is_relative"]),
            resolution_status=row["resolution_status"],
        )
        for row in data["edges"]
    )
    outgoing, incoming = build_directed_neighbours(nodes.keys(), edges)
    components = tuple(
        ForestComponent(
            component_id=int(row["component_id"]),
            module_names=tuple(row["module_names"]),
            source_modules=tuple(row["source_modules"]),
            sink_modules=tuple(row["sink_modules"]),
            status=row["status"],
        )
        for row in data["components"]
    )
    return PythonImportForest(
        folder=Path(data["folder"]),
        import_root=Path(data["import_root"]),
        nodes=nodes,
        edges=edges,
        outgoing=outgoing,
        incoming=incoming,
        components=components,
    )


def build_python_import_forest(folder: Path, import_root: Path | None = None) -> PythonImportForest:
    """Build an import forest from Python files below ``folder``.

    ``folder`` defines the files to scan.  ``import_root`` defines the path that
    dotted module names are relative to.  When omitted, module names are relative
    to ``folder`` itself.
    """

    resolved_folder = folder.resolve()
    resolved_import_root = (import_root or folder).resolve()
    python_paths = iter_python_paths_under(resolved_folder)
    module_index = build_module_index_for_paths(resolved_import_root, python_paths)

    modules: list[PythonModule] = []
    trees = {}
    for path in python_paths:
        module, tree = inspect_module(resolved_import_root, path)
        modules.append(module)
        if tree is not None:
            trees[module.module_name] = tree

    raw_edges: list[ImportEdge] = []
    module_by_name = {module.module_name: module for module in modules}
    for module_name in sorted(trees):
        module = module_by_name[module_name]
        raw_edges.extend(import_edges_for_tree(module, trees[module_name], module_index))

    nodes = forest_nodes_from_modules(modules)
    edges = forest_edges_from_import_edges(raw_edges, set(nodes))
    outgoing, incoming = build_directed_neighbours(nodes.keys(), edges)
    components = build_forest_components(nodes.keys(), edges, outgoing, incoming)

    return PythonImportForest(
        folder=resolved_folder,
        import_root=resolved_import_root,
        nodes=nodes,
        edges=edges,
        outgoing=outgoing,
        incoming=incoming,
        components=components,
    )


def iter_python_paths_under(folder: Path) -> list[Path]:
    """Return sorted Python files below ``folder``."""

    return sorted(path for path in folder.rglob("*.py") if path.is_file())


def build_module_index_for_paths(import_root: Path, python_paths: Iterable[Path]) -> dict[str, Path]:
    """Return ``module_name -> relative path`` for discovered Python files."""

    return {
        module_name_for_path(import_root, path): path.relative_to(import_root)
        for path in python_paths
    }


def forest_nodes_from_modules(modules: list[PythonModule]) -> dict[str, ForestNode]:
    """Convert parser module facts into forest nodes."""

    return {
        module.module_name: ForestNode(
            module_name=module.module_name,
            module_path=module.path.as_posix(),
            has_main_guard=module.has_main_guard,
            defines_main=module.defines_main,
            parse_status=module.parse_status,
            parse_error=module.parse_error,
        )
        for module in modules
    }


def target_module_for_import_edge(edge: ImportEdge, known_modules: set[str]) -> str:
    """Return the internal module targeted by a raw import edge, if any."""

    if edge.resolved_symbol_module in known_modules:
        return edge.resolved_symbol_module
    if edge.resolved_module in known_modules:
        return edge.resolved_module
    return ""


def forest_edges_from_import_edges(
    raw_edges: Iterable[ImportEdge],
    known_modules: set[str],
) -> frozenset[ForestEdge]:
    """Convert raw import evidence into internal forest edges."""

    edges: set[ForestEdge] = set()
    for raw_edge in raw_edges:
        if raw_edge.importer_module not in known_modules:
            continue
        imported_module = target_module_for_import_edge(raw_edge, known_modules)
        if not imported_module or imported_module == raw_edge.importer_module:
            continue
        edges.add(
            ForestEdge(
                importer_module=raw_edge.importer_module,
                imported_module=imported_module,
                import_style=raw_edge.import_style,
                imported_module_text=raw_edge.imported_module_text,
                imported_symbol=raw_edge.imported_symbol,
                imported_alias=raw_edge.imported_alias,
                level=raw_edge.level,
                is_relative=raw_edge.is_relative,
                resolution_status=raw_edge.resolution_status,
            )
        )
    return frozenset(edges)


def build_directed_neighbours(
    module_names: Iterable[str],
    edges: Iterable[ForestEdge],
) -> tuple[dict[str, frozenset[str]], dict[str, frozenset[str]]]:
    """Return outgoing and incoming neighbours for directed import edges."""

    names = set(module_names)
    outgoing: dict[str, set[str]] = {module_name: set() for module_name in names}
    incoming: dict[str, set[str]] = {module_name: set() for module_name in names}

    for edge in edges:
        if edge.importer_module not in names or edge.imported_module not in names:
            continue
        outgoing[edge.importer_module].add(edge.imported_module)
        incoming[edge.imported_module].add(edge.importer_module)

    return freeze_neighbour_map(outgoing), freeze_neighbour_map(incoming)


def freeze_neighbour_map(neighbours: dict[str, set[str]]) -> dict[str, frozenset[str]]:
    """Return a deterministic immutable-neighbour mapping."""

    return {module_name: frozenset(values) for module_name, values in neighbours.items()}


def build_weak_neighbours(
    module_names: Iterable[str],
    edges: Iterable[ForestEdge],
) -> dict[str, frozenset[str]]:
    """Return neighbours with import direction ignored."""

    names = set(module_names)
    neighbours: dict[str, set[str]] = {module_name: set() for module_name in names}
    for edge in edges:
        if edge.importer_module not in names or edge.imported_module not in names:
            continue
        neighbours[edge.importer_module].add(edge.imported_module)
        neighbours[edge.imported_module].add(edge.importer_module)
    return freeze_neighbour_map(neighbours)


def connected_components(
    module_names: Iterable[str],
    edges: Iterable[ForestEdge],
) -> tuple[tuple[str, ...], ...]:
    """Return weakly connected components sorted by size and module name."""

    names = set(module_names)
    neighbours = build_weak_neighbours(names, edges)
    unseen = set(names)
    components: list[tuple[str, ...]] = []

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

        components.append(tuple(sorted(component)))

    return tuple(sorted(components, key=lambda component: (-len(component), component[0])))


def build_forest_components(
    module_names: Iterable[str],
    edges: Iterable[ForestEdge],
    outgoing: dict[str, frozenset[str]],
    incoming: dict[str, frozenset[str]],
) -> tuple[ForestComponent, ...]:
    """Return classified weak components of the import forest."""

    components = connected_components(module_names, edges)
    result: list[ForestComponent] = []
    for component_id, component in enumerate(components, start=1):
        source_modules = tuple(module_name for module_name in component if not incoming[module_name])
        sink_modules = tuple(module_name for module_name in component if not outgoing[module_name])
        result.append(
            ForestComponent(
                component_id=component_id,
                module_names=component,
                source_modules=source_modules,
                sink_modules=sink_modules,
                status=component_status(component, source_modules, sink_modules),
            )
        )
    return tuple(result)


def component_status(
    module_names: tuple[str, ...],
    source_modules: tuple[str, ...],
    sink_modules: tuple[str, ...],
) -> str:
    """Classify one weak component against the forest invariant."""

    if len(module_names) == 1 and len(source_modules) == 1 and len(sink_modules) == 1:
        return "isolated"
    if len(source_modules) == 1:
        return "valid_tree"
    if not source_modules:
        return "zero_sources"
    return "multiple_sources"


def sorted_edges(edges: Iterable[ForestEdge]) -> list[ForestEdge]:
    """Return edges in deterministic order."""

    return sorted(
        edges,
        key=lambda edge: (
            edge.importer_module,
            edge.imported_module,
            edge.import_style,
            edge.imported_module_text,
            edge.imported_symbol,
        ),
    )


def safe_output_name(path: Path) -> str:
    """Return a filesystem-safe output base name derived from an input path."""

    name = path.resolve().name or "root"
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._-")
    return safe or "root"


def forest_output_stem(folder: Path) -> str:
    """Return the default output stem for a forest built from ``folder``."""

    return f"{safe_output_name(folder)}_{OUTPUT_SUFFIX}"


def forest_output_paths(output_dir: Path, folder: Path, output_stem: str | None = None) -> dict[str, Path]:
    """Return all default output paths for a forest input folder."""

    stem = output_stem or forest_output_stem(folder)
    return {
        "json": output_dir / f"{stem}.json",
        "nodes": output_dir / f"{stem}_nodes.csv",
        "edges": output_dir / f"{stem}_edges.csv",
        "components": output_dir / f"{stem}_components.csv",
        "summary": output_dir / f"{stem}_summary.csv",
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Write dictionaries to a UTF-8 CSV file with a stable header."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_forest_csvs(
    output_dir: Path,
    forest: PythonImportForest,
    output_stem: str | None = None,
) -> None:
    """Write CSV projections of an import forest."""

    paths = forest_output_paths(output_dir, forest.folder, output_stem)
    write_csv(
        paths["nodes"],
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
            "component_status",
            "has_main_guard",
            "defines_main",
            "parse_status",
            "parse_error",
        ],
        forest_node_rows(forest),
    )
    write_csv(
        paths["edges"],
        [
            "importer_module",
            "imported_module",
            "import_style",
            "imported_module_text",
            "imported_symbol",
            "imported_alias",
            "level",
            "is_relative",
            "resolution_status",
        ],
        forest_edge_rows(forest),
    )
    write_csv(
        paths["components"],
        [
            "component_id",
            "component_size",
            "source_count",
            "sink_count",
            "status",
            "source_modules",
            "sink_modules",
            "module_names",
        ],
        forest_component_rows(forest),
    )
    write_csv(
        paths["summary"],
        ["metric", "value"],
        forest_summary_rows(forest),
    )


def component_by_module(forest: PythonImportForest) -> dict[str, ForestComponent]:
    """Return a component lookup for every module in the forest."""

    return {
        module_name: component
        for component in forest.components
        for module_name in component.module_names
    }


def forest_node_rows(forest: PythonImportForest) -> list[dict[str, object]]:
    """Return node rows for CSV persistence."""

    components = component_by_module(forest)
    rows: list[dict[str, object]] = []
    for module_name in sorted(forest.nodes):
        node = forest.nodes[module_name]
        component = components[module_name]
        rows.append(
            {
                "module_name": module_name,
                "module_path": node.module_path,
                "indegree": len(forest.incoming[module_name]),
                "outdegree": len(forest.outgoing[module_name]),
                "is_source": not forest.incoming[module_name],
                "is_sink": not forest.outgoing[module_name],
                "imports": ";".join(sorted(forest.outgoing[module_name])),
                "imported_by": ";".join(sorted(forest.incoming[module_name])),
                "component_id": component.component_id,
                "component_size": component.component_size,
                "component_status": component.status,
                "has_main_guard": node.has_main_guard,
                "defines_main": node.defines_main,
                "parse_status": node.parse_status,
                "parse_error": node.parse_error,
            }
        )
    return rows


def forest_edge_rows(forest: PythonImportForest) -> list[dict[str, object]]:
    """Return edge rows for CSV persistence."""

    return [edge_to_dict(edge) for edge in sorted_edges(forest.edges)]


def forest_component_rows(forest: PythonImportForest) -> list[dict[str, object]]:
    """Return component rows for CSV persistence."""

    return [
        {
            "component_id": component.component_id,
            "component_size": component.component_size,
            "source_count": component.source_count,
            "sink_count": component.sink_count,
            "status": component.status,
            "source_modules": ";".join(component.source_modules),
            "sink_modules": ";".join(component.sink_modules),
            "module_names": ";".join(component.module_names),
        }
        for component in forest.components
    ]


def forest_summary_rows(forest: PythonImportForest) -> list[dict[str, object]]:
    """Return summary metric rows for CSV persistence."""

    status_counts: dict[str, int] = {}
    for component in forest.components:
        status_counts[component.status] = status_counts.get(component.status, 0) + 1

    rows: list[dict[str, object]] = [
        {"metric": "module_count", "value": len(forest.nodes)},
        {"metric": "edge_count", "value": len(forest.edges)},
        {"metric": "source_count", "value": len(forest.source_modules)},
        {"metric": "sink_count", "value": len(forest.sink_modules)},
        {"metric": "component_count", "value": len(forest.components)},
        {"metric": "valid_component_count", "value": len(forest.valid_components)},
        {"metric": "invalid_component_count", "value": len(forest.invalid_components)},
        {"metric": "isolated_component_count", "value": len(forest.isolated_components)},
    ]
    rows.extend(
        {"metric": f"component_status:{status}", "value": count}
        for status, count in sorted(status_counts.items())
    )
    return rows


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for forest generation."""

    parser = argparse.ArgumentParser(
        description="Build and persist a directed forest of Python module imports."
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="Folder of Python modules to scan recursively.",
    )
    parser.add_argument(
        "--import-root",
        type=Path,
        default=None,
        help="Path that dotted module names are relative to. Defaults to folder.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("files") / "output" / "introspection",
        help="Directory for JSON and CSV outputs.",
    )
    parser.add_argument(
        "--output-stem",
        default=None,
        help="Output filename stem. Defaults to '<input-folder>_import_forest'.",
    )
    return parser


def main() -> None:
    """Run the forest builder from the command line."""

    parser = build_parser()
    args = parser.parse_args()
    forest = build_python_import_forest(args.folder, args.import_root)
    output_dir = args.output_dir.resolve()
    output_stem = args.output_stem or forest_output_stem(args.folder)
    paths = forest_output_paths(output_dir, args.folder, output_stem)

    forest.write_json(paths["json"])
    forest.write_csvs(output_dir, output_stem)

    print(f"Wrote {paths['json']}")
    print(f"Wrote {paths['nodes']}")
    print(f"Wrote {paths['edges']}")
    print(f"Wrote {paths['components']}")
    print(f"Wrote {paths['summary']}")
    print(f"Modules: {len(forest.nodes)}")
    print(f"Edges: {len(forest.edges)}")
    print(f"Components: {len(forest.components)}")
    print(f"Invalid components: {len(forest.invalid_components)}")


if __name__ == "__main__":
    main()

"""Extract a simple data-flow view for a Python module.

Given a module id, this evidence-first analyser reports file-like artifacts read
or written by the named module and by transitive project modules reachable through
internal imports.  It is intended to support Makefile discovery, not to prove
complete Python semantics.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_OUTPUT_ROOT = Path("files") / "output" / "introspection" / "data_flow"
READ_METHODS = {"read_text", "read_bytes"}
WRITE_METHODS = {"write_text", "write_bytes"}
GLOB_METHODS = {"glob", "rglob"}
WRITE_MODE_CHARS = {"w", "a", "x", "+"}


@dataclass(frozen=True)
class ModuleRef:
    """A Python module discovered below the import root."""

    module_name: str
    path: Path


@dataclass(frozen=True)
class ImportRef:
    """One internal import edge discovered in source code."""

    importer_module: str
    imported_module: str
    imported_name: str
    alias: str
    import_style: str
    line_number: int


@dataclass(frozen=True)
class ArtifactUse:
    """One piece of evidence that a module reads or writes a file-like artifact."""

    module_name: str
    distance_from_root: int
    scope: str
    action: str
    artifact: str
    evidence: str
    line_number: int
    confidence: str


@dataclass(frozen=True)
class DataFlowGraph:
    """Data-flow evidence reachable from one root module."""

    root_module: str
    modules: tuple[ModuleRef, ...]
    imports: tuple[ImportRef, ...]
    artifact_uses: tuple[ArtifactUse, ...]

    @property
    def direct_artifact_uses(self) -> tuple[ArtifactUse, ...]:
        """Return artifact uses from the root module only."""

        return tuple(use for use in self.artifact_uses if use.distance_from_root == 0)

    @property
    def transitive_artifact_uses(self) -> tuple[ArtifactUse, ...]:
        """Return artifact uses from modules reachable from the root."""

        return tuple(use for use in self.artifact_uses if use.distance_from_root > 0)

    @property
    def input_artifacts(self) -> tuple[str, ...]:
        """Return unique read/glob artifacts."""

        return tuple(sorted({use.artifact for use in self.artifact_uses if use.action in {"read", "glob"}}))

    @property
    def output_artifacts(self) -> tuple[str, ...]:
        """Return unique written artifacts."""

        return tuple(sorted({use.artifact for use in self.artifact_uses if use.action == "write"}))

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation."""

        return {
            "root_module": self.root_module,
            "modules": [module_ref_to_dict(module) for module in self.modules],
            "imports": [import_ref_to_dict(import_ref) for import_ref in self.imports],
            "artifact_uses": [artifact_use_to_dict(use) for use in self.artifact_uses],
            "input_artifacts": list(self.input_artifacts),
            "output_artifacts": list(self.output_artifacts),
        }


def module_ref_to_dict(module: ModuleRef) -> dict[str, object]:
    """Return a JSON-serialisable module row."""

    return {"module_name": module.module_name, "path": module.path.as_posix()}


def import_ref_to_dict(import_ref: ImportRef) -> dict[str, object]:
    """Return a JSON-serialisable import row."""

    return {
        "importer_module": import_ref.importer_module,
        "imported_module": import_ref.imported_module,
        "imported_name": import_ref.imported_name,
        "alias": import_ref.alias,
        "import_style": import_ref.import_style,
        "line_number": import_ref.line_number,
    }


def artifact_use_to_dict(use: ArtifactUse) -> dict[str, object]:
    """Return a JSON-serialisable artifact-use row."""

    return {
        "module_name": use.module_name,
        "distance_from_root": use.distance_from_root,
        "scope": use.scope,
        "action": use.action,
        "artifact": use.artifact,
        "evidence": use.evidence,
        "line_number": use.line_number,
        "confidence": use.confidence,
    }


def build_data_flow_graph(module_id: str, import_root: Path = Path(".")) -> DataFlowGraph:
    """Build transitive data-flow evidence for ``module_id``."""

    resolved_import_root = import_root.resolve()
    module_index = build_module_index(resolved_import_root)
    if module_id not in module_index:
        raise ValueError(f"Module not found below {resolved_import_root}: {module_id}")

    parsed_trees: dict[str, ast.AST] = {}
    imports_by_module: dict[str, tuple[ImportRef, ...]] = {}
    for module_name, module_ref in module_index.items():
        tree = parse_python(module_ref.path)
        if tree is None:
            continue
        parsed_trees[module_name] = tree
        imports_by_module[module_name] = tuple(import_refs_for_tree(module_name, tree, module_index))

    distances = reachable_module_distances(module_id, imports_by_module)
    modules = tuple(
        module_index[module_name]
        for module_name in sorted(distances, key=lambda name: (distances[name], name))
    )
    imports = tuple(
        import_ref
        for module_name in sorted(distances, key=lambda name: (distances[name], name))
        for import_ref in imports_by_module.get(module_name, ())
        if import_ref.imported_module in distances
    )
    artifact_uses = tuple(
        use
        for module_name in sorted(distances, key=lambda name: (distances[name], name))
        for use in artifact_uses_for_module(module_name, parsed_trees[module_name], distances[module_name])
    )

    return DataFlowGraph(
        root_module=module_id,
        modules=modules,
        imports=imports,
        artifact_uses=artifact_uses,
    )


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
            for alias in node.names:
                imported_module = resolve_absolute_import(alias.name, module_index)
                if imported_module:
                    imports.append(
                        ImportRef(
                            importer_module=module_name,
                            imported_module=imported_module,
                            imported_name="",
                            alias=alias.asname or "",
                            import_style="import",
                            line_number=node.lineno,
                        )
                    )
        elif isinstance(node, ast.ImportFrom):
            base_module = resolve_import_from_base(module_name, node, module_index)
            if not base_module:
                continue
            for alias in node.names:
                imported_module = resolve_imported_symbol(base_module, alias.name, module_index)
                imports.append(
                    ImportRef(
                        importer_module=module_name,
                        imported_module=imported_module,
                        imported_name=alias.name,
                        alias=alias.asname or "",
                        import_style="from",
                        line_number=node.lineno,
                    )
                )
    return imports


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


def artifact_uses_for_module(
    module_name: str,
    tree: ast.AST,
    distance_from_root: int,
) -> list[ArtifactUse]:
    """Return file-like artifact evidence for one module."""

    constants = collect_path_constants(tree)
    parent_by_child = parent_map(tree)
    uses: list[ArtifactUse] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        scope = enclosing_scope(node, parent_by_child)
        use = artifact_use_for_call(module_name, distance_from_root, scope, node, constants)
        if use is not None:
            uses.append(use)

    return sorted(uses, key=lambda use: (use.line_number, use.action, use.artifact))


def collect_path_constants(tree: ast.AST) -> dict[str, str]:
    """Collect simple module-level path/string constants."""

    constants: dict[str, str] = {}
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign):
            value = resolve_path_expr(node.value, constants)
            if not value:
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            value = resolve_path_expr(node.value, constants) if node.value is not None else ""
            if value:
                constants[node.target.id] = value
    return constants


def artifact_use_for_call(
    module_name: str,
    distance_from_root: int,
    scope: str,
    node: ast.Call,
    constants: dict[str, str],
) -> ArtifactUse | None:
    """Return artifact-use evidence for a call node when recognised."""

    line_number = getattr(node, "lineno", 0)
    if isinstance(node.func, ast.Attribute):
        method_name = node.func.attr
        if method_name in READ_METHODS | WRITE_METHODS | GLOB_METHODS:
            artifact = resolve_path_expr(node.func.value, constants)
            if not artifact:
                artifact = ast.unparse(node.func.value)
            if method_name in READ_METHODS:
                action = "read"
            elif method_name in WRITE_METHODS:
                action = "write"
            else:
                action = "glob"
                if node.args:
                    pattern = resolve_path_expr(node.args[0], constants) or ast.unparse(node.args[0])
                    artifact = f"{artifact}/{pattern}"
            return ArtifactUse(
                module_name=module_name,
                distance_from_root=distance_from_root,
                scope=scope,
                action=action,
                artifact=artifact,
                evidence=f"{method_name}()",
                line_number=line_number,
                confidence="high" if artifact else "low",
            )

    if isinstance(node.func, ast.Name) and node.func.id == "open" and node.args:
        artifact = resolve_path_expr(node.args[0], constants) or ast.unparse(node.args[0])
        mode = resolve_open_mode(node)
        action = "write" if any(char in mode for char in WRITE_MODE_CHARS) else "read"
        return ArtifactUse(
            module_name=module_name,
            distance_from_root=distance_from_root,
            scope=scope,
            action=action,
            artifact=artifact,
            evidence=f"open(..., mode={mode!r})",
            line_number=line_number,
            confidence="medium",
        )

    return None


def resolve_open_mode(node: ast.Call) -> str:
    """Return the literal open mode, defaulting to read mode."""

    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
        return node.args[1].value
    for keyword in node.keywords:
        if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
            return keyword.value.value
    return "r"


def resolve_path_expr(node: ast.AST | None, constants: dict[str, str]) -> str:
    """Resolve simple path expressions to readable strings."""

    if node is None:
        return ""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return constants.get(node.id, node.id if node.id.isupper() else "")
    if isinstance(node, ast.Call) and path_constructor_name(node.func) and node.args:
        parts = [resolve_path_expr(arg, constants) or ast.unparse(arg) for arg in node.args]
        return "/".join(part.strip("/\\") for part in parts if part)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = resolve_path_expr(node.left, constants) or ast.unparse(node.left)
        right = resolve_path_expr(node.right, constants) or ast.unparse(node.right)
        return f"{left.rstrip('/\\')}/{right.strip('/\\')}"
    if isinstance(node, ast.JoinedStr):
        return ast.unparse(node)
    return ""


def path_constructor_name(node: ast.AST) -> str:
    """Return constructor name when a call looks like Path(...)."""

    if isinstance(node, ast.Name) and node.id in {"Path", "PurePath"}:
        return node.id
    if isinstance(node, ast.Attribute) and node.attr in {"Path", "PurePath"}:
        return node.attr
    return ""


def parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    """Return child-to-parent mapping for an AST."""

    return {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}


def enclosing_scope(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str:
    """Return nearest enclosing function/class scope for ``node``."""

    current = node
    while current in parents:
        current = parents[current]
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current.name
        if isinstance(current, ast.ClassDef):
            return current.name
    return "<module>"


def safe_name(name: str) -> str:
    """Return a filesystem-safe name."""

    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._-")
    return safe or "root"


def write_data_flow_reports(graph: DataFlowGraph, output_dir: Path) -> None:
    """Persist data-flow JSON and CSV reports."""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "data_flow.json").write_text(
        json.dumps(graph.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_csv(
        output_dir / "modules.csv",
        ["module_name", "path"],
        [module_ref_to_dict(module) for module in graph.modules],
    )
    write_csv(
        output_dir / "imports.csv",
        ["importer_module", "imported_module", "imported_name", "alias", "import_style", "line_number"],
        [import_ref_to_dict(import_ref) for import_ref in graph.imports],
    )
    write_csv(
        output_dir / "artifact_uses.csv",
        [
            "module_name",
            "distance_from_root",
            "scope",
            "action",
            "artifact",
            "evidence",
            "line_number",
            "confidence",
        ],
        [artifact_use_to_dict(use) for use in graph.artifact_uses],
    )
    write_csv(
        output_dir / "summary.csv",
        ["kind", "artifact"],
        [{"kind": "input", "artifact": artifact} for artifact in graph.input_artifacts]
        + [{"kind": "output", "artifact": artifact} for artifact in graph.output_artifacts],
    )


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    """Write dictionaries to CSV."""

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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
    print(f"Wrote {output_dir / 'summary.csv'}")
    print(f"Modules: {len(graph.modules)}")
    print(f"Imports: {len(graph.imports)}")
    print(f"Artifact uses: {len(graph.artifact_uses)}")
    print(f"Inputs: {len(graph.input_artifacts)}")
    print(f"Outputs: {len(graph.output_artifacts)}")


if __name__ == "__main__":
    main()

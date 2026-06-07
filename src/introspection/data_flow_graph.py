"""Extract a simple data-flow view for a Python module.

Given a module id, this evidence-first analyser reports file-like artifacts read
or written by the named module and by transitive project modules reachable through
internal imports. It is intended to support Makefile discovery, not to prove
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
SYMBOLIC_ARTIFACT_NAMES = {
    "path",
    "fn",
    "config_path",
    "source_path",
    "destination",
    "data_path",
    "report_path",
    "output_path",
}


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
    artifact_kind: str
    evidence: str
    line_number: int
    confidence: str


@dataclass(frozen=True)
class ArtifactSummary:
    """Aggregated evidence for one artifact."""

    artifact: str
    artifact_kind: str
    read_count: int
    write_count: int
    glob_count: int
    producer_modules: tuple[str, ...]
    consumer_modules: tuple[str, ...]


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

    @property
    def concrete_input_artifacts(self) -> tuple[str, ...]:
        """Return concrete read/glob artifacts."""

        return tuple(
            sorted(
                {
                    use.artifact
                    for use in self.artifact_uses
                    if use.action in {"read", "glob"} and use.artifact_kind == "concrete"
                }
            )
        )

    @property
    def concrete_output_artifacts(self) -> tuple[str, ...]:
        """Return concrete written artifacts."""

        return tuple(
            sorted(
                {
                    use.artifact
                    for use in self.artifact_uses
                    if use.action == "write" and use.artifact_kind == "concrete"
                }
            )
        )

    @property
    def artifact_summaries(self) -> tuple[ArtifactSummary, ...]:
        """Return producer/consumer summaries for each artifact."""

        return tuple(build_artifact_summaries(self.artifact_uses))

    @property
    def generated_prerequisites(self) -> tuple[ArtifactSummary, ...]:
        """Return artifacts that are both produced and consumed in reachable code."""

        return tuple(
            summary
            for summary in self.artifact_summaries
            if summary.write_count > 0 and (summary.read_count > 0 or summary.glob_count > 0)
        )

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation."""

        return {
            "root_module": self.root_module,
            "modules": [module_ref_to_dict(module) for module in self.modules],
            "imports": [import_ref_to_dict(import_ref) for import_ref in self.imports],
            "artifact_uses": [artifact_use_to_dict(use) for use in self.artifact_uses],
            "artifacts": [artifact_summary_to_dict(summary) for summary in self.artifact_summaries],
            "generated_prerequisites": [
                artifact_summary_to_dict(summary) for summary in self.generated_prerequisites
            ],
            "input_artifacts": list(self.input_artifacts),
            "output_artifacts": list(self.output_artifacts),
            "concrete_input_artifacts": list(self.concrete_input_artifacts),
            "concrete_output_artifacts": list(self.concrete_output_artifacts),
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
        "artifact_kind": use.artifact_kind,
        "evidence": use.evidence,
        "line_number": use.line_number,
        "confidence": use.confidence,
    }


def artifact_summary_to_dict(summary: ArtifactSummary) -> dict[str, object]:
    """Return a JSON-serialisable artifact summary row."""

    return {
        "artifact": summary.artifact,
        "artifact_kind": summary.artifact_kind,
        "read_count": summary.read_count,
        "write_count": summary.write_count,
        "glob_count": summary.glob_count,
        "producer_modules": ";".join(summary.producer_modules),
        "consumer_modules": ";".join(summary.consumer_modules),
    }


def build_data_flow_graph(module_id: str, import_root: Path = Path(".")) -> DataFlowGraph:
    """Build transitive data-flow evidence for ``module_id``."""

    resolved_import_root = import_root.resolve()
    module_index = build_module_index(resolved_import_root)
    if module_id not in module_index:
        raise ValueError(f"Module not found below {resolved_import_root}: {module_id}")

    parsed_trees: dict[str, ast.AST] = {}
    imports_by_module: dict[str, tuple[ImportRef, ...]] = {}
    local_constants_by_module: dict[str, dict[str, str]] = {}
    for module_name, module_ref in module_index.items():
        tree = parse_python(module_ref.path)
        if tree is None:
            continue
        parsed_trees[module_name] = tree
        imports_by_module[module_name] = tuple(import_refs_for_tree(module_name, tree, module_index))
        local_constants_by_module[module_name] = collect_path_constants(tree, {})

    constants_by_module = build_visible_constants_by_module(
        local_constants_by_module,
        imports_by_module,
    )
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
                            alias=alias.asname or alias.name.split(".")[-1],
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
                        alias=alias.asname or alias.name,
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


def build_visible_constants_by_module(
    local_constants_by_module: dict[str, dict[str, str]],
    imports_by_module: dict[str, tuple[ImportRef, ...]],
) -> dict[str, dict[str, str]]:
    """Return local constants plus simple imported module constants."""

    result: dict[str, dict[str, str]] = {}
    for module_name, local_constants in local_constants_by_module.items():
        constants = dict(local_constants)
        for import_ref in imports_by_module.get(module_name, ()):
            imported_constants = local_constants_by_module.get(import_ref.imported_module, {})
            if not imported_constants:
                continue
            if import_ref.import_style == "from" and import_ref.imported_name in imported_constants:
                constants[import_ref.alias or import_ref.imported_name] = imported_constants[import_ref.imported_name]
            module_alias = import_ref.alias or import_ref.imported_module.split(".")[-1]
            for const_name, const_value in imported_constants.items():
                constants[f"{module_alias}.{const_name}"] = const_value
        result[module_name] = constants
    return result


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
    constants: dict[str, str],
) -> list[ArtifactUse]:
    """Return file-like artifact evidence for one module."""

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


def collect_path_constants(tree: ast.AST, constants: dict[str, str]) -> dict[str, str]:
    """Collect simple module-level path/string constants."""

    result = dict(constants)
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign):
            value = resolve_path_expr(node.value, result)
            if not value:
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    result[target.id] = value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            value = resolve_path_expr(node.value, result) if node.value is not None else ""
            if value:
                result[node.target.id] = value
    return result


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
            return make_artifact_use(
                module_name=module_name,
                distance_from_root=distance_from_root,
                scope=scope,
                action=action,
                artifact=artifact,
                evidence=f"{method_name}()",
                line_number=line_number,
            )

    if isinstance(node.func, ast.Name) and node.func.id == "open" and node.args:
        artifact = resolve_path_expr(node.args[0], constants) or ast.unparse(node.args[0])
        mode = resolve_open_mode(node)
        action = "write" if any(char in mode for char in WRITE_MODE_CHARS) else "read"
        return make_artifact_use(
            module_name=module_name,
            distance_from_root=distance_from_root,
            scope=scope,
            action=action,
            artifact=artifact,
            evidence=f"open(..., mode={mode!r})",
            line_number=line_number,
        )

    return None


def make_artifact_use(
    module_name: str,
    distance_from_root: int,
    scope: str,
    action: str,
    artifact: str,
    evidence: str,
    line_number: int,
) -> ArtifactUse:
    """Create an artifact use with kind and confidence classification."""

    artifact_kind = classify_artifact(artifact)
    if artifact_kind == "concrete":
        confidence = "high"
    elif artifact_kind == "symbolic":
        confidence = "low"
    else:
        confidence = "medium"
    return ArtifactUse(
        module_name=module_name,
        distance_from_root=distance_from_root,
        scope=scope,
        action=action,
        artifact=artifact,
        artifact_kind=artifact_kind,
        evidence=evidence,
        line_number=line_number,
        confidence=confidence,
    )


def classify_artifact(artifact: str) -> str:
    """Classify artifact strings as concrete, symbolic, or expression."""

    if not artifact:
        return "symbolic"
    if artifact in SYMBOLIC_ARTIFACT_NAMES:
        return "symbolic"
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", artifact) and not artifact.isupper():
        return "symbolic"
    if any(token in artifact for token in ("(", ")", "{", "}", "[", "]")):
        return "expression"
    if "/" in artifact or "\\" in artifact or "." in Path(artifact).name or "*" in artifact:
        return "concrete"
    if artifact.isupper():
        return "expression"
    return "symbolic"


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
    if isinstance(node, ast.Attribute):
        dotted = dotted_name(node)
        if dotted in constants:
            return constants[dotted]
        return dotted if dotted and dotted.split(".")[-1].isupper() else ""
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


def dotted_name(node: ast.AST) -> str:
    """Return dotted name for simple attribute expressions."""

    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
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


def build_artifact_summaries(uses: Iterable[ArtifactUse]) -> list[ArtifactSummary]:
    """Aggregate artifact uses into producer/consumer summaries."""

    by_artifact: dict[str, list[ArtifactUse]] = {}
    for use in uses:
        by_artifact.setdefault(use.artifact, []).append(use)

    summaries: list[ArtifactSummary] = []
    for artifact, artifact_uses in sorted(by_artifact.items()):
        read_uses = [use for use in artifact_uses if use.action == "read"]
        write_uses = [use for use in artifact_uses if use.action == "write"]
        glob_uses = [use for use in artifact_uses if use.action == "glob"]
        kinds = {use.artifact_kind for use in artifact_uses}
        artifact_kind = "concrete" if kinds == {"concrete"} else ";".join(sorted(kinds))
        summaries.append(
            ArtifactSummary(
                artifact=artifact,
                artifact_kind=artifact_kind,
                read_count=len(read_uses),
                write_count=len(write_uses),
                glob_count=len(glob_uses),
                producer_modules=tuple(sorted({use.module_name for use in write_uses})),
                consumer_modules=tuple(sorted({use.module_name for use in read_uses + glob_uses})),
            )
        )
    return summaries


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
            "artifact_kind",
            "evidence",
            "line_number",
            "confidence",
        ],
        [artifact_use_to_dict(use) for use in graph.artifact_uses],
    )
    write_csv(
        output_dir / "artifacts.csv",
        [
            "artifact",
            "artifact_kind",
            "read_count",
            "write_count",
            "glob_count",
            "producer_modules",
            "consumer_modules",
        ],
        [artifact_summary_to_dict(summary) for summary in graph.artifact_summaries],
    )
    write_csv(
        output_dir / "generated_prerequisites.csv",
        [
            "artifact",
            "artifact_kind",
            "read_count",
            "write_count",
            "glob_count",
            "producer_modules",
            "consumer_modules",
        ],
        [artifact_summary_to_dict(summary) for summary in graph.generated_prerequisites],
    )
    write_csv(
        output_dir / "summary.csv",
        ["kind", "artifact"],
        [{"kind": "input", "artifact": artifact} for artifact in graph.input_artifacts]
        + [{"kind": "output", "artifact": artifact} for artifact in graph.output_artifacts]
        + [{"kind": "concrete_input", "artifact": artifact} for artifact in graph.concrete_input_artifacts]
        + [{"kind": "concrete_output", "artifact": artifact} for artifact in graph.concrete_output_artifacts],
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

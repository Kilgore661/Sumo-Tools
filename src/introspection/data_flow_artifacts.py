"""Artifact extraction from Python ASTs for data-flow introspection."""

from __future__ import annotations

import ast

from src.introspection.data_flow_model import ArtifactUse
from src.introspection.data_flow_paths import classify_artifact, resolve_path_expr


READ_METHODS = {"read_text", "read_bytes"}
WRITE_METHODS = {"write_text", "write_bytes"}
GLOB_METHODS = {"glob", "rglob"}
WRITE_MODE_CHARS = {"w", "a", "x", "+"}


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


def resolve_open_mode(node: ast.Call) -> str:
    """Return the literal open mode, defaulting to read mode."""

    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
        return node.args[1].value
    for keyword in node.keywords:
        if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
            return keyword.value.value
    return "r"


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

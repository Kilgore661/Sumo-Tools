"""Artifact extraction from Python ASTs for data-flow introspection."""

from __future__ import annotations

import ast

from src.introspection.data_flow_model import ArtifactUse
from src.introspection.data_flow_paths import classify_artifact, collect_path_constants, resolve_path_expr


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
    function_defs = function_defs_by_name(tree)
    function_constants = constants_by_function_scope(tree, constants, function_defs)
    uses: list[ArtifactUse] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        scope = enclosing_scope(node, parent_by_child)
        scope_constants = function_constants.get(scope, constants)
        use = artifact_use_for_call(module_name, distance_from_root, scope, node, scope_constants)
        if use is not None:
            uses.append(use)

    return sorted(uses, key=lambda use: (use.line_number, use.action, use.artifact))


def function_defs_by_name(tree: ast.AST) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    """Return top-level function definitions by name."""

    return {
        node.name: node
        for node in getattr(tree, "body", [])
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def constants_by_function_scope(
    tree: ast.AST,
    module_constants: dict[str, str],
    function_defs: dict[str, ast.FunctionDef | ast.AsyncFunctionDef],
) -> dict[str, dict[str, str]]:
    """Return constants visible within each function scope."""

    result = {"<module>": module_constants}
    for name, node in function_defs.items():
        result[name] = constants_for_function(node, module_constants)

    parent_by_child = parent_map(tree)
    for _ in range(max(1, len(function_defs))):
        changed = False
        next_result = dict(result)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            callee_name = node.func.id
            if callee_name not in function_defs:
                continue
            caller_scope = enclosing_scope(node, parent_by_child)
            caller_constants = result.get(caller_scope, module_constants)
            argument_constants = constants_from_call_arguments(
                node,
                function_defs[callee_name],
                caller_constants,
            )
            if not argument_constants:
                continue
            callee_constants = dict(result.get(callee_name, module_constants))
            callee_constants.update(argument_constants)
            callee_constants = collect_path_constants(function_defs[callee_name], callee_constants)
            if callee_constants != result.get(callee_name, {}):
                next_result[callee_name] = callee_constants
                changed = True
        result = next_result
        if not changed:
            break
    return result


def constants_from_call_arguments(
    call_node: ast.Call,
    function_node: ast.FunctionDef | ast.AsyncFunctionDef,
    caller_constants: dict[str, str],
) -> dict[str, str]:
    """Map callee parameter names to path-like argument values from one call site."""

    constants: dict[str, str] = {}
    positional_args = list(function_node.args.args)
    if positional_args and positional_args[0].arg == "self":
        positional_args = positional_args[1:]

    for parameter, argument in zip(positional_args, call_node.args, strict=False):
        value = resolve_path_expr(argument, caller_constants)
        if value:
            constants[parameter.arg] = value

    keyword_parameters = {argument.arg for argument in positional_args}
    keyword_parameters.update(argument.arg for argument in function_node.args.kwonlyargs)
    for keyword in call_node.keywords:
        if keyword.arg is None or keyword.arg not in keyword_parameters:
            continue
        value = resolve_path_expr(keyword.value, caller_constants)
        if value:
            constants[keyword.arg] = value

    return constants


def constants_for_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    module_constants: dict[str, str],
) -> dict[str, str]:
    """Return constants visible in a function, including simple default arguments."""

    constants = dict(module_constants)
    positional_defaults = list(node.args.defaults)
    positional_args = node.args.args[-len(positional_defaults):] if positional_defaults else []
    for arg, default in zip(positional_args, positional_defaults, strict=False):
        value = resolve_path_expr(default, constants)
        if value:
            constants[arg.arg] = value
    for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults, strict=False):
        if default is None:
            continue
        value = resolve_path_expr(default, constants)
        if value:
            constants[arg.arg] = value
    return collect_path_constants(node, constants)


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

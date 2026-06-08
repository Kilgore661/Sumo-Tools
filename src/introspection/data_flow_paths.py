"""Path and constant resolution helpers for data-flow introspection."""

from __future__ import annotations

import ast
import re
from pathlib import Path

from src.introspection.data_flow_model import ImportRef, ModuleRef


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


def build_local_constants_by_module(
    trees: dict[str, ast.AST],
    module_index: dict[str, ModuleRef],
) -> dict[str, dict[str, str]]:
    """Return local path constants for each module."""

    result: dict[str, dict[str, str]] = {}
    for module_name, tree in trees.items():
        module_ref = module_index[module_name]
        seed_constants = {"__file__": module_ref.path.as_posix()}
        result[module_name] = collect_path_constants(tree, seed_constants)
    return result


def build_visible_constants_by_module(
    local_constants_by_module: dict[str, dict[str, str]],
    imports_by_module: dict[str, tuple[ImportRef, ...]],
    trees: dict[str, ast.AST],
) -> dict[str, dict[str, str]]:
    """Return imported constants plus constants resolved with those imports."""

    visible_constants = {
        module_name: dict(constants)
        for module_name, constants in local_constants_by_module.items()
    }
    for _ in range(max(1, len(trees))):
        changed = False
        next_visible_constants = dict(visible_constants)
        for module_name, tree in trees.items():
            seed_constants = imported_constants_for_module(
                module_name,
                visible_constants,
                imports_by_module,
            )
            seed_constants.update({
                key: value
                for key, value in local_constants_by_module.get(module_name, {}).items()
                if key == "__file__"
            })
            constants = collect_path_constants(tree, seed_constants)
            if constants != visible_constants.get(module_name, {}):
                changed = True
                next_visible_constants[module_name] = constants
        visible_constants = next_visible_constants
        if not changed:
            break
    return visible_constants


def imported_constants_for_module(
    module_name: str,
    constants_by_module: dict[str, dict[str, str]],
    imports_by_module: dict[str, tuple[ImportRef, ...]],
) -> dict[str, str]:
    """Return visible constants introduced by direct imports."""

    constants: dict[str, str] = {}
    for import_ref in imports_by_module.get(module_name, ()):
        imported_constants = constants_by_module.get(import_ref.imported_module, {})
        if not imported_constants:
            continue
        if import_ref.import_style == "from" and import_ref.imported_name in imported_constants:
            constants[import_ref.alias or import_ref.imported_name] = imported_constants[import_ref.imported_name]
        module_alias = import_ref.alias or import_ref.imported_module.split(".")[-1]
        for const_name, const_value in imported_constants.items():
            constants[f"{module_alias}.{const_name}"] = const_value
    return constants


def collect_path_constants(tree: ast.AST, constants: dict[str, str]) -> dict[str, str]:
    """Collect simple assignment path/string constants from a module or function body."""

    result = dict(constants)
    for _ in range(3):
        changed = False
        for target_name, value in loop_target_constants(tree, result).items():
            if result.get(target_name) != value:
                result[target_name] = value
                changed = True
        for node in assignment_nodes(tree):
            value = resolve_path_expr(assignment_value(node), result)
            if not value:
                continue
            for target_name in assignment_target_names(node):
                if result.get(target_name) != value:
                    result[target_name] = value
                    changed = True
        if not changed:
            break
    return result


def assignment_nodes(tree: ast.AST) -> list[ast.Assign | ast.AnnAssign]:
    """Return assignment nodes in source order."""

    nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
    ]
    return sorted(nodes, key=lambda node: getattr(node, "lineno", 0))


def assignment_value(node: ast.Assign | ast.AnnAssign) -> ast.AST | None:
    """Return the value expression for an assignment node."""

    return node.value


def assignment_target_names(node: ast.Assign | ast.AnnAssign) -> list[str]:
    """Return simple assigned target names."""

    if isinstance(node, ast.Assign):
        return [target.id for target in node.targets if isinstance(target, ast.Name)]
    if isinstance(node.target, ast.Name):
        return [node.target.id]
    return []


def loop_target_constants(tree: ast.AST, constants: dict[str, str]) -> dict[str, str]:
    """Return simple loop target path approximations.

    ``for source_path in ROOT.rglob("*")`` becomes ``source_path = ROOT/*``.
    """

    result: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.For) or not isinstance(node.target, ast.Name):
            continue
        value = loop_iter_path(node.iter, constants)
        if value:
            result[node.target.id] = value
    return result


def loop_iter_path(node: ast.AST, constants: dict[str, str]) -> str:
    """Return path approximation for simple glob/rglob loop iterators."""

    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        return ""
    if node.func.attr not in {"glob", "rglob"}:
        return ""
    base = resolve_path_expr(node.func.value, constants)
    if not base:
        return ""
    pattern = resolve_path_expr(node.args[0], constants) if node.args else "*"
    pattern = pattern or "*"
    return f"{base.rstrip('/\\')}/{pattern.strip('/\\')}"


def resolve_path_expr(node: ast.AST | None, constants: dict[str, str]) -> str:
    """Resolve simple path expressions to readable strings."""

    if node is None:
        return ""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return constants.get(node.id, node.id if node.id.isupper() else "")
    if isinstance(node, ast.Attribute):
        resolved_attribute = resolve_path_attribute(node, constants)
        if resolved_attribute:
            return resolved_attribute
        dotted = dotted_name(node)
        if dotted in constants:
            return constants[dotted]
        return dotted if dotted and dotted.split(".")[-1].isupper() else ""
    if isinstance(node, ast.Call):
        resolved_call = resolve_path_call(node, constants)
        if resolved_call:
            return resolved_call
    if isinstance(node, ast.Subscript):
        resolved_subscript = resolve_path_subscript(node, constants)
        if resolved_subscript:
            return resolved_subscript
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = resolve_path_expr(node.left, constants) or ast.unparse(node.left)
        right = resolve_path_expr(node.right, constants) or ast.unparse(node.right)
        return f"{left.rstrip('/\\')}/{right.strip('/\\')}"
    if isinstance(node, ast.JoinedStr):
        return ast.unparse(node)
    return ""


def resolve_path_call(node: ast.Call, constants: dict[str, str]) -> str:
    """Resolve simple path-oriented calls."""

    if path_constructor_name(node.func) and node.args:
        parts = [resolve_path_expr(arg, constants) or ast.unparse(arg) for arg in node.args]
        return "/".join(part.strip("/\\") for part in parts if part)
    if isinstance(node.func, ast.Attribute) and node.func.attr in {"resolve", "absolute"}:
        return resolve_path_expr(node.func.value, constants)
    if isinstance(node.func, ast.Attribute) and node.func.attr == "relative_to" and node.args:
        return resolve_relative_to(node, constants)
    return ""


def resolve_relative_to(node: ast.Call, constants: dict[str, str]) -> str:
    """Resolve a simple ``path.relative_to(root)`` expression."""

    path_value = resolve_path_expr(node.func.value, constants)
    root_value = resolve_path_expr(node.args[0], constants)
    if not path_value or not root_value:
        return ""
    normalized_path = path_value.replace("\\", "/").rstrip("/")
    normalized_root = root_value.replace("\\", "/").rstrip("/")
    if normalized_path == normalized_root:
        return ""
    if normalized_path.startswith(normalized_root + "/"):
        return normalized_path[len(normalized_root) + 1:]
    return ""


def resolve_path_attribute(node: ast.Attribute, constants: dict[str, str]) -> str:
    """Resolve simple path attributes such as ``some_path.parent``."""

    if node.attr == "parent":
        value = resolve_path_expr(node.value, constants)
        return Path(value).parent.as_posix() if value else ""
    return ""


def resolve_path_subscript(node: ast.Subscript, constants: dict[str, str]) -> str:
    """Resolve simple path subscript expressions such as ``some_path.parents[2]``."""

    if not isinstance(node.value, ast.Attribute) or node.value.attr != "parents":
        return ""
    path_value = resolve_path_expr(node.value.value, constants)
    if not path_value:
        return ""
    index = integer_literal(node.slice)
    if index is None or index < 0:
        return ""
    parents = Path(path_value).parents
    if index >= len(parents):
        return ""
    return parents[index].as_posix()


def integer_literal(node: ast.AST) -> int | None:
    """Return integer literal value, if ``node`` is an integer literal."""

    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    return None


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

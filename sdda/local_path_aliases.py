from __future__ import annotations

import ast

from .models import ModuleRecord, ScopeRecord
from .path_constants import PathConstantMap
from .source import parse_python_file

LocalPathAliasMap = dict[tuple[str, str], dict[str, str]]


def build_local_path_alias_map(
    module_index: dict[str, ModuleRecord],
    reachable_modules: list[str],
    scopes: list[ScopeRecord],
    path_constants: PathConstantMap,
) -> LocalPathAliasMap:
    aliases: LocalPathAliasMap = {}
    scopes_by_module = _scopes_by_module(scopes)
    for module_name in reachable_modules:
        tree = parse_python_file(module_index[module_name].path)
        for scope in scopes_by_module.get(module_name, []):
            scope_node = _scope_node(tree, scope)
            if scope_node is None:
                continue
            scope_aliases = _aliases_from_scope(scope_node, path_constants.get(module_name, {}))
            if scope_aliases:
                aliases[(module_name, scope.qualname)] = scope_aliases
    return aliases


def _scopes_by_module(scopes: list[ScopeRecord]) -> dict[str, list[ScopeRecord]]:
    grouped: dict[str, list[ScopeRecord]] = {}
    for scope in scopes:
        grouped.setdefault(scope.module, []).append(scope)
    return grouped


def _scope_node(tree: ast.Module, scope: ScopeRecord) -> ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | None:
    if scope.qualname == "<module>":
        return tree
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if node.lineno == scope.line_start:
            return node
    return None


def _aliases_from_scope(
    scope_node: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
    constants: dict[str, str],
) -> dict[str, str]:
    aliases: dict[str, str] = dict(constants)
    output: dict[str, str] = {}
    for node in scope_node.body:
        target, value = _assignment_parts(node)
        if target is not None and value is not None:
            resolved = _eval_path_expression(value, aliases)
            if resolved is not None:
                aliases[target] = resolved
                if not target.isupper():
                    output[target] = resolved
            continue

        if isinstance(node, ast.For):
            loop_aliases = _loop_aliases(node, aliases)
            aliases.update(loop_aliases)
            output.update(loop_aliases)
    return output


def _assignment_parts(node: ast.stmt) -> tuple[str | None, ast.AST | None]:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target = node.targets[0]
        if isinstance(target, ast.Name):
            return target.id, node.value
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id, node.value
    return None, None


def _loop_aliases(node: ast.For, aliases: dict[str, str]) -> dict[str, str]:
    choices = _eval_choice_expression(node.iter, aliases)
    if choices is None:
        return {}
    targets = _loop_target_names(node.target)
    if not targets:
        return {}
    return {targets[0]: choices}


def _loop_target_names(target: ast.AST) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        return [element.id for element in target.elts if isinstance(element, ast.Name)]
    return []


def _eval_path_expression(node: ast.AST, aliases: dict[str, str]) -> str | None:
    choices = _eval_choice_expression(node, aliases)
    if choices is not None:
        return choices
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return aliases.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _eval_path_expression(node.left, aliases)
        right = _eval_path_expression(node.right, aliases)
        if left is None or right is None:
            return None
        return f"{left}/{right}"
    if isinstance(node, ast.Call):
        return _eval_call(node, aliases)
    if isinstance(node, ast.Attribute):
        return _eval_attribute(node, aliases)
    return None


def _eval_choice_expression(node: ast.AST, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        value = aliases.get(node.id)
        if value is not None and value.startswith("{") and value.endswith("}"):
            return value
    if isinstance(node, (ast.Tuple, ast.List)):
        values = []
        for element in node.elts:
            if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                return None
            values.append(element.value)
        return _choice_pattern(values)
    if isinstance(node, ast.Call) and _call_name(node.func) == "zip" and node.args:
        return _eval_choice_expression(node.args[0], aliases)
    return None


def _eval_call(node: ast.Call, aliases: dict[str, str]) -> str | None:
    if isinstance(node.func, ast.Name) and node.func.id == "Path" and len(node.args) == 1:
        return _eval_path_expression(node.args[0], aliases)
    if isinstance(node.func, ast.Attribute) and node.func.attr == "resolve":
        return _eval_path_expression(node.func.value, aliases)
    return None


def _eval_attribute(node: ast.Attribute, aliases: dict[str, str]) -> str | None:
    value = _eval_path_expression(node.value, aliases)
    if value is None:
        return None
    if node.attr == "parent":
        parts = [part for part in value.split("/") if part]
        return "/".join(parts[:-1])
    return None


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _choice_pattern(values: list[str]) -> str | None:
    if not values:
        return None
    return "{" + ",".join(values) + "}"

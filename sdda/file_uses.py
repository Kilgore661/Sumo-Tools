from __future__ import annotations

import ast

from .models import FileUseRecord, ScopeRecord, UnresolvedRecord
from .source import unparse

READ_METHODS = {"read_text", "read_bytes"}
WRITE_METHODS = {"write_text", "write_bytes"}
GLOB_METHODS = {"glob", "rglob"}
EXISTS_METHODS = {"exists", "is_file", "is_dir"}
MKDIR_METHODS = {"mkdir"}
DELETE_METHODS = {"unlink", "rmdir"}
URL_METHODS = {"get", "post", "put", "request", "urlopen"}
COPY_FUNCTIONS = {"copy", "copy2", "copyfile", "copytree"}
DELETE_FUNCTIONS = {"rmtree", "remove"}


def extract_file_uses(
    module_name: str,
    tree: ast.Module,
    scopes: list[ScopeRecord],
) -> tuple[list[FileUseRecord], list[UnresolvedRecord]]:
    uses: list[FileUseRecord] = []
    unresolved: list[UnresolvedRecord] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            scope = _scope_for_line(scopes, node.lineno)
            use = _file_use_from_call(module_name, scope, node)
            if use is not None:
                uses.append(use)
            unresolved_call = _unresolved_from_call(module_name, scope, node)
            if unresolved_call is not None:
                unresolved.append(unresolved_call)
        elif isinstance(node, ast.Subscript):
            scope = _scope_for_line(scopes, node.lineno)
            use = _env_use_from_subscript(module_name, scope, node)
            if use is not None:
                uses.append(use)
    return uses, unresolved


def _file_use_from_call(
    module_name: str,
    scope: ScopeRecord,
    node: ast.Call,
) -> FileUseRecord | None:
    func_name = _call_name(node.func)
    if func_name == "open":
        return _record(module_name, scope, node, "may_read_or_write", _arg(node, 0), "open_call")
    if func_name in {"Path", "PurePath"}:
        return None

    method = _attribute_name(node.func)
    if method in READ_METHODS:
        return _record(module_name, scope, node, "may_read", node.func, f"path_method:{method}")
    if method in WRITE_METHODS:
        return _record(module_name, scope, node, "may_write", node.func, f"path_method:{method}")
    if method in GLOB_METHODS:
        return _record(module_name, scope, node, "may_observe", node, f"path_method:{method}")
    if method in EXISTS_METHODS:
        return _record(module_name, scope, node, "may_existence_check", node.func, f"path_method:{method}")
    if method in MKDIR_METHODS:
        return _record(module_name, scope, node, "may_create_directory", node.func, f"path_method:{method}")
    if method in DELETE_METHODS:
        return _record(module_name, scope, node, "may_delete", node.func, f"path_method:{method}")

    dotted = _dotted_name(node.func)
    if dotted in {"glob.glob", "glob.iglob"}:
        return _record(module_name, scope, node, "may_observe", _arg(node, 0), dotted)
    if dotted in {f"shutil.{name}" for name in COPY_FUNCTIONS}:
        return _record(module_name, scope, node, "may_copy", node, dotted)
    if dotted in {f"shutil.{name}" for name in DELETE_FUNCTIONS}:
        return _record(module_name, scope, node, "may_delete", node, dotted)
    if method in URL_METHODS or dotted in {f"requests.{name}" for name in URL_METHODS}:
        return _record(module_name, scope, node, "may_download", _arg(node, 0), dotted or method)
    if dotted in {"os.getenv"}:
        return _record(module_name, scope, node, "may_read_environment", _arg(node, 0), dotted)
    return None


def _env_use_from_subscript(
    module_name: str,
    scope: ScopeRecord,
    node: ast.Subscript,
) -> FileUseRecord | None:
    if _dotted_name(node.value) != "os.environ":
        return None
    return FileUseRecord(
        module=module_name,
        scope_kind=scope.scope_kind,
        scope_name=scope.qualname,
        line=node.lineno,
        action="may_read_environment",
        raw_expression=unparse(node),
        resolved_expression=unparse(node.slice),
        confidence="medium",
        reason="os.environ_subscript",
    )


def _unresolved_from_call(
    module_name: str,
    scope: ScopeRecord,
    node: ast.Call,
) -> UnresolvedRecord | None:
    if isinstance(node.func, ast.Attribute):
        value = node.func.value
        if isinstance(value, ast.Name) and value.id not in {"os", "Path", "shutil", "glob", "requests"}:
            return UnresolvedRecord(
                module=module_name,
                scope_kind=scope.scope_kind,
                scope_name=scope.qualname,
                line=node.lineno,
                source_expression=unparse(node),
                reason="object_method_dispatch_not_resolved",
            )
    return None


def _record(
    module_name: str,
    scope: ScopeRecord,
    call: ast.Call,
    action: str,
    expression: ast.AST | None,
    reason: str,
) -> FileUseRecord:
    raw = unparse(call)
    resolved = unparse(expression) if expression is not None else ""
    return FileUseRecord(
        module=module_name,
        scope_kind=scope.scope_kind,
        scope_name=scope.qualname,
        line=call.lineno,
        action=action,
        raw_expression=raw,
        resolved_expression=resolved,
        confidence="medium",
        reason=reason,
    )


def _scope_for_line(scopes: list[ScopeRecord], line: int) -> ScopeRecord:
    containing = [scope for scope in scopes if scope.line_start <= line <= scope.line_end]
    if not containing:
        raise AssertionError(f"No scope for line {line}")
    return max(containing, key=lambda scope: scope.line_start)


def _arg(node: ast.Call, index: int) -> ast.AST | None:
    if len(node.args) > index:
        return node.args[index]
    return None


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _attribute_name(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _dotted_name(node.value)
        if prefix:
            return f"{prefix}.{node.attr}"
    return ""

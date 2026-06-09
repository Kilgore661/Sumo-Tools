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
REQUESTS_METHODS = {"get", "post", "put", "request"}
COPY_FUNCTIONS = {"copy", "copy2", "copyfile", "copytree"}
DELETE_FUNCTIONS = {"rmtree", "remove"}

BENIGN_METHODS = {
    "add",
    "add_argument",
    "append",
    "as_posix",
    "close",
    "compile",
    "dirname",
    "dumps",
    "end",
    "endswith",
    "error",
    "exit",
    "extend",
    "findall",
    "finditer",
    "fullmatch",
    "get",
    "group",
    "groups",
    "items",
    "join",
    "keys",
    "load",
    "loads",
    "now",
    "parse",
    "parse_args",
    "relative_to",
    "replace",
    "resolve",
    "search",
    "sort",
    "split",
    "start",
    "startswith",
    "strftime",
    "strip",
    "strptime",
    "time",
    "update",
    "values",
    "write",
    "writeheader",
    "writerow",
    "writerows",
}
KNOWN_MODULE_RECEIVERS = {
    "argparse",
    "csv",
    "datetime",
    "gzip",
    "html",
    "json",
    "logging",
    "object",
    "os",
    "pickle",
    "posixpath",
    "re",
    "shared_memory",
    "sys",
    "time",
}


def extract_file_uses(
    module_name: str, tree: ast.Module, scopes: list[ScopeRecord]
) -> tuple[list[FileUseRecord], list[UnresolvedRecord]]:
    uses: list[FileUseRecord] = []
    unresolved: list[UnresolvedRecord] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            scope = _scope_for_line(scopes, node.lineno)
            uses.extend(_file_uses_from_call(module_name, scope, node))
            unresolved_call = _unresolved_from_call(module_name, scope, node)
            if unresolved_call is not None:
                unresolved.append(unresolved_call)
        elif isinstance(node, ast.Subscript):
            scope = _scope_for_line(scopes, node.lineno)
            use = _env_use_from_subscript(module_name, scope, node)
            if use is not None:
                uses.append(use)
    return uses, unresolved


def _file_uses_from_call(module_name: str, scope: ScopeRecord, node: ast.Call) -> list[FileUseRecord]:
    func_name = _call_name(node.func)
    if func_name == "open":
        return [_record(module_name, scope, node, _open_action(node, 1), _arg(node, 0), "open_call")]
    if func_name in {"Path", "PurePath"}:
        return []

    method = _attribute_name(node.func)
    receiver = _receiver(node.func)
    if method == "open":
        return [_record(module_name, scope, node, _open_action(node, 0), receiver, "path_method:open")]
    if method in READ_METHODS:
        return [_record(module_name, scope, node, "may_read", receiver, f"path_method:{method}")]
    if method in WRITE_METHODS:
        return [_record(module_name, scope, node, "may_write", receiver, f"path_method:{method}")]
    if method in GLOB_METHODS:
        return [_record(module_name, scope, node, "may_observe", node, f"path_method:{method}")]
    if method in EXISTS_METHODS:
        return [_record(module_name, scope, node, "may_existence_check", receiver, f"path_method:{method}")]
    if method in MKDIR_METHODS:
        return [_record(module_name, scope, node, "may_create_directory", receiver, f"path_method:{method}")]
    if method in DELETE_METHODS:
        return [_record(module_name, scope, node, "may_delete", receiver, f"path_method:{method}")]

    dotted = _dotted_name(node.func)
    if dotted in {"glob.glob", "glob.iglob"}:
        return [_record(module_name, scope, node, "may_observe", _arg(node, 0), dotted)]
    if dotted in {"os.makedirs"}:
        return [_record(module_name, scope, node, "may_create_directory", _arg(node, 0), dotted)]
    if dotted in {"os.remove", "os.rmdir"}:
        return [_record(module_name, scope, node, "may_delete", _arg(node, 0), dotted)]
    if dotted in {"os.path.exists", "os.path.isfile", "os.path.isdir"}:
        return [_record(module_name, scope, node, "may_existence_check", _arg(node, 0), dotted)]
    if dotted in {f"shutil.{name}" for name in COPY_FUNCTIONS}:
        return _copy_records(module_name, scope, node, dotted)
    if dotted in {f"shutil.{name}" for name in DELETE_FUNCTIONS}:
        return [_record(module_name, scope, node, "may_delete", _arg(node, 0), dotted)]
    if dotted in {f"requests.{name}" for name in REQUESTS_METHODS}:
        return [_record(module_name, scope, node, "may_download", _arg(node, 0), dotted)]
    if dotted in {"urllib.request.urlopen", "urlopen"}:
        return [_record(module_name, scope, node, "may_download", _arg(node, 0), dotted)]
    if dotted in {"os.getenv"}:
        return [_record(module_name, scope, node, "may_read_environment", _arg(node, 0), dotted)]
    return []


def _copy_records(module_name: str, scope: ScopeRecord, node: ast.Call, reason: str) -> list[FileUseRecord]:
    return [
        _record(module_name, scope, node, "may_read", _arg(node, 0), f"{reason}:source"),
        _record(module_name, scope, node, "may_write", _arg(node, 1), f"{reason}:destination"),
    ]


def _env_use_from_subscript(module_name: str, scope: ScopeRecord, node: ast.Subscript) -> FileUseRecord | None:
    if _dotted_name(node.value) != "os.environ":
        return None
    return FileUseRecord(module_name, scope.scope_kind, scope.qualname, node.lineno, "may_read_environment", unparse(node), unparse(node.slice), "medium", "os.environ_subscript")


def _unresolved_from_call(module_name: str, scope: ScopeRecord, node: ast.Call) -> UnresolvedRecord | None:
    if _file_uses_from_call(module_name, scope, node):
        return None
    if not isinstance(node.func, ast.Attribute):
        return None

    method = node.func.attr
    receiver = node.func.value
    if method in BENIGN_METHODS:
        return None
    if isinstance(receiver, ast.Name) and receiver.id in KNOWN_MODULE_RECEIVERS:
        return None
    if isinstance(receiver, ast.Name) and receiver.id[:1].isupper():
        return None

    return UnresolvedRecord(module_name, scope.scope_kind, scope.qualname, node.lineno, unparse(node), "object_method_dispatch_not_resolved")


def _open_action(node: ast.Call, mode_index: int) -> str:
    mode = _literal_string_arg(node, mode_index)
    if mode == "":
        return "may_read"
    if any(marker in mode for marker in ("w", "a", "x", "+")):
        return "may_write"
    if "r" in mode:
        return "may_read"
    return "may_read_or_write"


def _literal_string_arg(node: ast.Call, index: int) -> str:
    arg = _arg(node, index)
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value
    return ""


def _record(module_name: str, scope: ScopeRecord, call: ast.Call, action: str, expression: ast.AST | None, reason: str) -> FileUseRecord:
    return FileUseRecord(
        module=module_name,
        scope_kind=scope.scope_kind,
        scope_name=scope.qualname,
        line=call.lineno,
        action=action,
        raw_expression=unparse(call),
        resolved_expression=unparse(expression) if expression is not None else "",
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


def _receiver(node: ast.AST) -> ast.AST | None:
    if isinstance(node, ast.Attribute):
        return node.value
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

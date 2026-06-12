from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

from sdda.dataflow.file_families import normalise_file_families
from sdda.dataflow.file_uses import extract_file_uses
from sdda.dataflow.import_graph import _extract_imports
from sdda.dataflow.local_path_aliases import build_local_path_alias_map
from sdda.dataflow.module_index import build_module_index
from sdda.dataflow.path_constants import build_path_constant_map
from sdda.dataflow.scopes import extract_scopes
from sdda.dataflow.source import parse_python_file

from .models import FileEffectRootRecord, ModuleFileRootRecord

READ_ACTIONS = {"may_read", "may_observe", "may_download", "may_read_environment"}
WRITE_ACTIONS = {"may_write", "may_create_directory", "may_copy", "may_delete"}
MIXED_ACTIONS = {"may_read_or_write"}
KNOWN_FILE_SUFFIXES = {
    "csv",
    "html",
    "htm",
    "json",
    "js",
    "css",
    "pkl",
    "pickle",
    "txt",
    "zip",
    "gz",
    "png",
    "jpg",
    "jpeg",
    "svg",
}


def analyse_file_roots() -> tuple[list[FileEffectRootRecord], list[ModuleFileRootRecord]]:
    import_root = Path(".")
    module_index = {
        name: record
        for name, record in build_module_index(import_root).items()
        if name == "src" or name.startswith("src.")
    }
    module_names = sorted(module_index)
    parsed_trees = {}
    scopes = []
    file_uses = []
    imports = []

    for module_name in module_names:
        tree = parse_python_file(module_index[module_name].path)
        parsed_trees[module_name] = tree
        module_scopes = extract_scopes(module_name, tree)
        module_uses, _unresolved = extract_file_uses(module_name, tree, module_scopes)
        imports.extend(_extract_imports(module_name, tree, module_index))
        scopes.extend(module_scopes)
        file_uses.extend(module_uses)

    path_constants = build_path_constant_map(module_index, imports, module_names, import_root)
    local_aliases = build_local_path_alias_map(module_index, module_names, scopes, path_constants)
    families, family_evidence = normalise_file_families(file_uses, path_constants, local_aliases)
    family_pattern_by_id = {family.family_id: family.family_pattern for family in families}
    symbolic_aliases = _build_symbolic_aliases(parsed_trees, path_constants)

    effects = [
        _effect_record(row, family)
        for row in family_evidence
        for family in _resolve_symbolic_families(
            row,
            family_pattern_by_id.get(row.family_id, row.resolved_expression),
            symbolic_aliases,
        )
    ]
    module_roots = _module_roots(module_names, effects)
    return (
        sorted(effects, key=lambda row: (row.module, row.direction, row.root_pattern, row.line)),
        module_roots,
    )


def _effect_record(row: object, family_pattern: str) -> FileEffectRootRecord:
    family_pattern = _normalise_path(family_pattern)
    root, member, shape, confidence, reason = _split_family(family_pattern)
    normalisation_status = _normalisation_status(shape, member)
    return FileEffectRootRecord(
        module=row.module,
        scope=row.scope_name,
        line=row.line,
        action=row.action,
        direction=_direction(row.action),
        path_pattern=_normalised_path_pattern(family_pattern, normalisation_status),
        normalisation_status=normalisation_status,
        symbolic_source=family_pattern if normalisation_status in {"unresolved", "constant_name"} else "",
        family_pattern=family_pattern,
        root_pattern=root,
        member_pattern=member,
        shape=shape,
        confidence=confidence,
        raw_expression=row.raw_expression,
        reason=reason,
    )


def _direction(action: str) -> str:
    if action in READ_ACTIONS:
        return "read"
    if action in WRITE_ACTIONS:
        return "write"
    if action in MIXED_ACTIONS:
        return "read_or_write"
    return "other"


def _split_family(pattern: str) -> tuple[str, str, str, str, str]:
    normalised = _normalise_path(pattern)
    if normalised == "":
        return "", "", "empty", "low", "empty_pattern"
    if normalised.startswith("http://") or normalised.startswith("https://"):
        return _url_root(normalised)
    if _is_constant_name(normalised):
        return normalised, "", "constant_name", "medium", "constant_name"
    if _is_scoped_or_symbolic(normalised):
        return "", normalised, "unresolved_expression", "low", "scoped_or_symbolic_expression"

    parts = normalised.split("/")
    if "**" in parts:
        index = parts.index("**")
        root = "/".join(parts[:index])
        member = "/".join(parts[index:])
        return root, member, "recursive_glob", "medium", "recursive_glob_root"

    dynamic_index = _first_dynamic_segment(parts)
    if dynamic_index is not None:
        root = "/".join(parts[:dynamic_index])
        member = "/".join(parts[dynamic_index:])
        shape = "glob" if "*" in member else "template_or_choice"
        return root, member, shape, "medium", "dynamic_suffix_root"

    if _looks_like_file(parts[-1]):
        return "/".join(parts[:-1]), parts[-1], "concrete_file", "high", "concrete_file_parent"

    return normalised, "", "concrete_or_symbolic_directory", "medium", "directory_or_extensionless_path"


def _normalisation_status(shape: str, member: str) -> str:
    if shape == "unresolved_expression":
        return "unresolved"
    if shape in {"concrete_file", "template_or_choice"} and member:
        return "normalised_file_template" if "{" in member or "*" in member else "normalised_file_path"
    if shape in {"glob", "recursive_glob"}:
        return "glob"
    if shape == "url":
        return "url"
    if shape == "constant_name":
        return "constant_name"
    if shape == "concrete_or_symbolic_directory":
        return "directory"
    return "other"


def _normalised_path_pattern(family_pattern: str, normalisation_status: str) -> str:
    if normalisation_status in {"normalised_file_path", "normalised_file_template", "glob"}:
        return family_pattern
    return ""


def _url_root(url: str) -> tuple[str, str, str, str, str]:
    without_scheme = url.split("://", 1)[1]
    host, _, path = without_scheme.partition("/")
    return host, path, "url", "medium", "url_host_root"


def _is_constant_name(pattern: str) -> bool:
    return "/" not in pattern and pattern.isupper()


def _is_scoped_or_symbolic(pattern: str) -> bool:
    if "/" in pattern and "{" in pattern and "}" in pattern:
        return False
    if ":" in pattern and not _has_windows_drive_prefix(pattern):
        return True
    if "(" in pattern or ")" in pattern:
        return True
    if "/" not in pattern and "." in pattern:
        return True
    return False


def _has_windows_drive_prefix(pattern: str) -> bool:
    return len(pattern) >= 3 and pattern[1:3] == ":/" and pattern[0].isalpha()


def _first_dynamic_segment(parts: list[str]) -> int | None:
    for index, part in enumerate(parts):
        if "*" in part or "{" in part or "}" in part:
            return index
    return None


def _looks_like_file(part: str) -> bool:
    if "." not in part:
        return False
    suffix = part.rsplit(".", 1)[-1]
    return suffix.lower() in KNOWN_FILE_SUFFIXES


def _module_roots(
    module_names: list[str],
    effects: list[FileEffectRootRecord],
) -> list[ModuleFileRootRecord]:
    keyed_effects: dict[tuple[str, str, str], list[FileEffectRootRecord]] = defaultdict(list)
    effects_by_module: dict[str, list[FileEffectRootRecord]] = defaultdict(list)
    for effect in effects:
        if effect.root_pattern:
            keyed_effects[(effect.module, effect.direction, effect.root_pattern)].append(effect)
        effects_by_module[effect.module].append(effect)

    records: list[ModuleFileRootRecord] = []
    for key, rows in sorted(keyed_effects.items()):
        module, direction, root = key
        records.append(
            ModuleFileRootRecord(
                module=module,
                direction=direction,
                root_pattern=root,
                status="known",
                confidence=_combined_confidence(rows),
                effect_count=len(rows),
                shapes=";".join(sorted({row.shape for row in rows})),
                actions=";".join(sorted({row.action for row in rows})),
                reason="grouped_from_file_effect_roots",
            )
        )

    known_modules = {record.module for record in records}
    for module_name in module_names:
        if module_name in known_modules:
            continue
        module_effects = effects_by_module.get(module_name, [])
        if module_effects:
            reason = "file_effects_without_known_root"
            effect_count = len(module_effects)
        else:
            reason = "no_file_effects"
            effect_count = 0
        records.append(
            ModuleFileRootRecord(
                module=module_name,
                direction="any",
                root_pattern="",
                status="not_known",
                confidence="none",
                effect_count=effect_count,
                shapes=";".join(sorted({row.shape for row in module_effects})),
                actions=";".join(sorted({row.action for row in module_effects})),
                reason=reason,
            )
        )
    return sorted(records, key=lambda row: (row.status != "known", row.module, row.direction, row.root_pattern))


def _combined_confidence(rows: list[FileEffectRootRecord]) -> str:
    confidences = {row.confidence for row in rows}
    if "high" in confidences:
        return "high"
    if "medium" in confidences:
        return "medium"
    if "low" in confidences:
        return "low"
    return "none"


def _normalise_path(pattern: str) -> str:
    normalised = pattern.replace("\\", "/").strip()
    while normalised.startswith("./"):
        normalised = normalised[2:]
    return normalised


def _resolve_symbolic_families(
    row: object,
    family_pattern: str,
    symbolic_aliases: dict[tuple[str, str, str], set[str]],
) -> set[str]:
    dotted = _resolve_dotted_symbolic_family(row, family_pattern, symbolic_aliases)
    if dotted:
        return dotted
    if ":" not in family_pattern:
        return {family_pattern}
    parts = family_pattern.split(":")
    if len(parts) < 3:
        return {family_pattern}
    module = parts[0]
    scope = parts[1]
    name = parts[-1]
    return symbolic_aliases.get((module, scope, name), {family_pattern})


def _resolve_dotted_symbolic_family(
    row: object,
    family_pattern: str,
    symbolic_aliases: dict[tuple[str, str, str], set[str]],
) -> set[str]:
    if ":" in family_pattern or "/" in family_pattern or "." not in family_pattern:
        return set()
    name, attr = family_pattern.split(".", 1)
    values = symbolic_aliases.get((row.module, row.scope_name, name), set())
    if not values:
        return set()
    if attr == "parent":
        return {_symbolic_parent(value) for value in values}
    return {f"{value}.{attr}" for value in values}


def _symbolic_parent(value: str) -> str:
    value = _normalise_path(value)
    if "/" not in value:
        return value
    return value.rsplit("/", 1)[0]


def _build_symbolic_aliases(
    parsed_trees: dict[str, ast.Module],
    path_constants: dict[str, dict[str, str]],
) -> dict[tuple[str, str, str], set[str]]:
    aliases: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for module_name, tree in parsed_trees.items():
        constants = path_constants.get(module_name, {})
        module_functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        for class_node in [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]:
            field_sources = _self_field_sources(class_node)
            method_returns = _single_return_methods(class_node)
            for method in [node for node in class_node.body if isinstance(node, ast.FunctionDef)]:
                scope = f"{class_node.name}.{method.name}"
                local_values = _local_symbolic_values(method.body, constants, field_sources, method_returns, module_functions)
                for name, value in local_values.items():
                    aliases[(module_name, scope, name)].add(value)

        for func in module_functions.values():
            local_values = _local_symbolic_values(func.body, constants, {}, {}, module_functions)
            for name, value in local_values.items():
                aliases[(module_name, func.name, name)].add(value)
            _add_call_argument_aliases(module_name, func, constants, local_values, module_functions, aliases)
    return aliases


def _self_field_sources(class_node: ast.ClassDef) -> dict[str, str]:
    output: dict[str, str] = {}
    init_node = next(
        (node for node in class_node.body if isinstance(node, ast.FunctionDef) and node.name == "__init__"),
        None,
    )
    if init_node is None:
        return output
    parameter_names = {arg.arg for arg in init_node.args.args if arg.arg != "self"}
    for statement in init_node.body:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        if _is_self_attribute(target) and isinstance(statement.value, ast.Name) and statement.value.id in parameter_names:
            output[target.attr] = statement.value.id
    return output


def _single_return_methods(class_node: ast.ClassDef) -> dict[str, ast.AST]:
    output: dict[str, ast.AST] = {}
    for node in class_node.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        body = [statement for statement in node.body if not _is_docstring_expr(statement)]
        if len(body) == 1 and isinstance(body[0], ast.Return) and body[0].value is not None:
            output[node.name] = body[0].value
    return output


def _is_docstring_expr(statement: ast.stmt) -> bool:
    return isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str)


def _local_symbolic_values(
    statements: list[ast.stmt],
    constants: dict[str, str],
    field_sources: dict[str, str],
    method_returns: dict[str, ast.AST],
    module_functions: dict[str, ast.FunctionDef],
    initial_values: dict[str, str] | None = None,
) -> dict[str, str]:
    local_values: dict[str, str] = dict(initial_values or {})
    for statement in statements:
        target, value = _assignment_parts(statement)
        if target is None or value is None:
            continue
        resolved = _eval_symbolic(value, constants, local_values, field_sources, method_returns, module_functions)
        if resolved:
            local_values[target] = resolved
    return local_values


def _add_call_argument_aliases(
    module_name: str,
    func: ast.FunctionDef,
    constants: dict[str, str],
    local_values: dict[str, str],
    module_functions: dict[str, ast.FunctionDef],
    aliases: dict[tuple[str, str, str], set[str]],
) -> None:
    for statement in func.body:
        for call in [node for node in ast.walk(statement) if isinstance(node, ast.Call)]:
            if not isinstance(call.func, ast.Name) or call.func.id not in module_functions:
                continue
            callee = module_functions[call.func.id]
            parameter_names = [arg.arg for arg in callee.args.args]
            for index, argument in enumerate(call.args):
                if index >= len(parameter_names):
                    continue
                value = _eval_symbolic(argument, constants, local_values, {}, {}, module_functions)
                if value:
                    aliases[(module_name, callee.name, parameter_names[index])].add(value)


def _assignment_parts(statement: ast.stmt) -> tuple[str | None, ast.AST | None]:
    if isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
        return statement.targets[0].id, statement.value
    if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
        return statement.target.id, statement.value
    return None, None


def _eval_symbolic(
    node: ast.AST,
    constants: dict[str, str],
    local_values: dict[str, str],
    field_sources: dict[str, str],
    method_returns: dict[str, ast.AST],
    module_functions: dict[str, ast.FunctionDef],
) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in local_values:
            return local_values[node.id]
        if node.id in constants:
            return constants[node.id]
        return "{" + node.id + "}"
    if isinstance(node, ast.JoinedStr):
        parts = [_eval_symbolic(part, constants, local_values, field_sources, method_returns, module_functions) for part in node.values]
        return "".join(parts) if all(parts) else ""
    if isinstance(node, ast.FormattedValue):
        value = _eval_symbolic(node.value, constants, local_values, field_sources, method_returns, module_functions)
        if node.format_spec is not None and value.startswith("{") and value.endswith("}"):
            spec = _format_spec_text(node.format_spec)
            if spec:
                return "{" + value[1:-1] + ":" + spec + "}"
        return value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _eval_symbolic(node.left, constants, local_values, field_sources, method_returns, module_functions)
        right = _eval_symbolic(node.right, constants, local_values, field_sources, method_returns, module_functions)
        return f"{left.rstrip('/')}/{right.lstrip('/')}" if left and right else ""
    if isinstance(node, ast.Attribute) and _is_self_attribute(node):
        return "{" + field_sources.get(node.attr, node.attr) + "}"
    if isinstance(node, ast.Attribute):
        base = _eval_symbolic(node.value, constants, local_values, field_sources, method_returns, module_functions)
        if base.startswith("{") and base.endswith("}"):
            return "{" + base[1:-1] + "." + node.attr + "}"
        if base:
            return f"{base}.{node.attr}"
    if isinstance(node, ast.Call):
        return _eval_symbolic_call(node, constants, local_values, field_sources, method_returns, module_functions)
    return ""


def _eval_symbolic_call(
    node: ast.Call,
    constants: dict[str, str],
    local_values: dict[str, str],
    field_sources: dict[str, str],
    method_returns: dict[str, ast.AST],
    module_functions: dict[str, ast.FunctionDef],
) -> str:
    if isinstance(node.func, ast.Name) and node.func.id in {"Path", "Request"} and len(node.args) >= 1:
        return _eval_symbolic(node.args[0], constants, local_values, field_sources, method_returns, module_functions)
    if isinstance(node.func, ast.Name) and node.func.id in {"int", "str"} and len(node.args) == 1:
        return _eval_symbolic(node.args[0], constants, local_values, field_sources, method_returns, module_functions)
    if isinstance(node.func, ast.Name) and node.func.id in module_functions:
        return _eval_function_return(node.func.id, node.args, constants, local_values, module_functions)
    if not isinstance(node.func, ast.Attribute):
        return ""
    if _is_os_path_join(node.func):
        parts = [_eval_symbolic(arg, constants, local_values, field_sources, method_returns, module_functions) for arg in node.args]
        if all(parts):
            return "/".join(part.strip("/") for part in parts)
    receiver = node.func.value
    if node.func.attr == "lower":
        value = _eval_symbolic(receiver, constants, local_values, field_sources, method_returns, module_functions)
        if value.startswith("{") and value.endswith("}"):
            return "{lower(" + value[1:-1] + ")}"
        return value.lower() if value else ""
    if isinstance(receiver, ast.Name) and receiver.id == "self" and node.func.attr in method_returns:
        return _eval_symbolic(method_returns[node.func.attr], constants, local_values, field_sources, method_returns, module_functions)
    return ""


def _eval_function_return(
    function_name: str,
    arguments: list[ast.AST],
    constants: dict[str, str],
    caller_values: dict[str, str],
    module_functions: dict[str, ast.FunctionDef],
) -> str:
    function = module_functions[function_name]
    parameter_values: dict[str, str] = {}
    parameter_names = [arg.arg for arg in function.args.args]
    for index, argument in enumerate(arguments):
        if index >= len(parameter_names):
            continue
        value = _eval_symbolic(argument, constants, caller_values, {}, {}, module_functions)
        if value:
            parameter_values[parameter_names[index]] = value
    local_values = dict(parameter_values)
    for statement in function.body:
        if isinstance(statement, ast.Return) and statement.value is not None:
            return _eval_symbolic(statement.value, constants, local_values, {}, {}, module_functions)
        target, value = _assignment_parts(statement)
        if target is not None and value is not None:
            resolved = _eval_symbolic(value, constants, local_values, {}, {}, module_functions)
            if resolved:
                local_values[target] = resolved
    return ""


def _format_spec_text(node: ast.AST) -> str:
    if isinstance(node, ast.JoinedStr):
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            else:
                return ""
        return "".join(parts)
    return ""


def _is_os_path_join(node: ast.Attribute) -> bool:
    return (
        node.attr == "join"
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "path"
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "os"
    )


def _is_self_attribute(node: ast.AST) -> bool:
    return isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self"

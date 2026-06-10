from __future__ import annotations

import ast
from dataclasses import dataclass

from .models import CallArgumentBindingRecord, FileUseRecord, ModuleRecord
from .path_constants import PathConstantMap
from .source import parse_python_file, unparse


@dataclass(frozen=True)
class ParameterFileProvenanceRecord:
    consumer_module: str
    consumer_scope: str
    consumer_line: int
    consumer_action: str
    consumer_expression: str
    parameter_name: str
    caller_module: str
    caller_scope: str
    call_line: int
    argument_expression: str
    argument_name: str
    argument_value_sources: str
    interpretation: str
    reason: str


def extract_parameter_file_provenance(
    call_argument_bindings: list[CallArgumentBindingRecord],
    file_uses: list[FileUseRecord],
    module_index: dict[str, ModuleRecord] | None = None,
    path_constants: PathConstantMap | None = None,
    local_aliases: dict[tuple[str, str], dict[str, str]] | None = None,
) -> list[ParameterFileProvenanceRecord]:
    modules = module_index or {}
    constants = path_constants or {}
    bindings_by_callee_parameter = _bindings_by_callee_parameter(call_argument_bindings)
    default_arguments = _default_argument_bindings(modules, constants)
    iterator_bindings = _iterator_argument_bindings(modules, constants)
    aliases = local_aliases or {}
    records: list[ParameterFileProvenanceRecord] = []
    seen: set[tuple[str, str, int, str, str, int, str]] = set()
    for file_use in file_uses:
        parameter_name = _parameter_name(file_use.resolved_expression)
        if parameter_name == "":
            continue
        key = (file_use.module, file_use.scope_name, parameter_name)
        for binding in bindings_by_callee_parameter.get(key, ()): 
            argument_expression, interpretation, reason = _argument_provenance(
                binding,
                iterator_bindings,
                aliases,
            )
            dedupe_key = (
                file_use.module,
                file_use.scope_name,
                file_use.line,
                parameter_name,
                binding.caller_module,
                binding.call_line,
                interpretation,
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            records.append(
                ParameterFileProvenanceRecord(
                    consumer_module=file_use.module,
                    consumer_scope=file_use.scope_name,
                    consumer_line=file_use.line,
                    consumer_action=file_use.action,
                    consumer_expression=file_use.resolved_expression,
                    parameter_name=parameter_name,
                    caller_module=binding.caller_module,
                    caller_scope=binding.caller_scope,
                    call_line=binding.call_line,
                    argument_expression=argument_expression,
                    argument_name=binding.argument_name,
                    argument_value_sources=binding.argument_value_sources,
                    interpretation=interpretation,
                    reason=reason,
                )
            )
        default_expression = default_arguments.get(key)
        if default_expression is None:
            continue
        dedupe_key = (
            file_use.module,
            file_use.scope_name,
            file_use.line,
            parameter_name,
            file_use.module,
            0,
            "parameter_from_default_path_expression",
        )
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        records.append(
            ParameterFileProvenanceRecord(
                consumer_module=file_use.module,
                consumer_scope=file_use.scope_name,
                consumer_line=file_use.line,
                consumer_action=file_use.action,
                consumer_expression=file_use.resolved_expression,
                parameter_name=parameter_name,
                caller_module=file_use.module,
                caller_scope=file_use.scope_name,
                call_line=0,
                argument_expression=default_expression,
                argument_name=parameter_name,
                argument_value_sources="",
                interpretation="parameter_from_default_path_expression",
                reason="parameter_file_use_from_default_argument",
            )
        )
    return records


def _argument_provenance(
    binding: CallArgumentBindingRecord,
    iterator_bindings: dict[tuple[str, str, str], str],
    aliases: dict[tuple[str, str], dict[str, str]],
) -> tuple[str, str, str]:
    alias_binding = aliases.get((binding.caller_module, binding.caller_scope), {}).get(
        binding.argument_expression
    )
    if alias_binding is not None:
        return alias_binding, "parameter_from_local_path_alias", "parameter_file_use_from_local_alias_argument"
    iterator_binding = iterator_bindings.get(
        (binding.caller_module, binding.caller_scope, binding.argument_expression)
    )
    if iterator_binding is not None:
        return iterator_binding, "parameter_from_iterator_path_family", "parameter_file_use_from_iterator_argument"
    return (
        binding.argument_expression,
        _interpretation(binding.argument_expression, binding.argument_value_sources),
        "parameter_file_use_from_call_argument",
    )


def _bindings_by_callee_parameter(
    bindings: list[CallArgumentBindingRecord],
) -> dict[tuple[str, str, str], tuple[CallArgumentBindingRecord, ...]]:
    grouped: dict[tuple[str, str, str], list[CallArgumentBindingRecord]] = {}
    for binding in bindings:
        module, scope = _split_function_name(binding.callee_full_name)
        if module == "" or scope == "":
            continue
        grouped.setdefault((module, scope, binding.parameter_name), []).append(binding)
    return {key: tuple(value) for key, value in grouped.items()}


def _default_argument_bindings(
    module_index: dict[str, ModuleRecord],
    path_constants: PathConstantMap,
) -> dict[tuple[str, str, str], str]:
    bindings: dict[tuple[str, str, str], str] = {}
    for module_name, module_record in module_index.items():
        tree = parse_python_file(module_record.path)
        constants = path_constants.get(module_name, {})
        for function_node in ast.walk(tree):
            if not isinstance(function_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            defaults = function_node.args.defaults
            if not defaults:
                continue
            positional_args = function_node.args.args[-len(defaults):]
            for argument, default in zip(positional_args, defaults):
                default_expression = _eval_default_expression(default, constants)
                if default_expression == "":
                    continue
                bindings[(module_name, function_node.name, argument.arg)] = default_expression
    return bindings


def _eval_default_expression(node: ast.AST, constants: dict[str, str]) -> str:
    if isinstance(node, ast.Name):
        return constants.get(node.id, node.id)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _eval_default_expression(node.left, constants)
        right = _eval_default_expression(node.right, constants)
        if left == "" or right == "":
            return ""
        return f"{left}/{right}"
    return ""


def _iterator_argument_bindings(
    module_index: dict[str, ModuleRecord],
    path_constants: PathConstantMap,
) -> dict[tuple[str, str, str], str]:
    bindings: dict[tuple[str, str, str], str] = {}
    for module_name, module_record in module_index.items():
        tree = parse_python_file(module_record.path)
        for function_node in ast.walk(tree):
            if not isinstance(function_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            scope_name = function_node.name
            for generator in ast.walk(function_node):
                if not isinstance(generator, ast.GeneratorExp):
                    continue
                if not isinstance(generator.elt, ast.Call):
                    continue
                if len(generator.generators) != 1:
                    continue
                comprehension = generator.generators[0]
                target_name = _target_name(comprehension.target)
                if target_name == "":
                    continue
                root_pattern = _iterdir_root_pattern(comprehension.iter, path_constants.get(module_name, {}))
                if root_pattern == "":
                    continue
                if not generator.elt.args:
                    continue
                argument = generator.elt.args[0]
                if not isinstance(argument, ast.Name) or argument.id != target_name:
                    continue
                pattern = _filtered_iterator_pattern(root_pattern, target_name, comprehension.ifs)
                bindings[(module_name, scope_name, target_name)] = pattern
    return bindings


def _target_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _iterdir_root_pattern(node: ast.AST, constants: dict[str, str]) -> str:
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sorted" and len(node.args) == 1:
        return _iterdir_root_pattern(node.args[0], constants)
    if not isinstance(node, ast.Call):
        return ""
    if not isinstance(node.func, ast.Attribute) or node.func.attr != "iterdir":
        return ""
    if not isinstance(node.func.value, ast.Name):
        return ""
    return constants.get(node.func.value.id, node.func.value.id)


def _filtered_iterator_pattern(root_pattern: str, target_name: str, filters: list[ast.expr]) -> str:
    prefix = "*"
    suffixes: list[str] = []
    for filter_node in filters:
        if _is_startswith_filter(filter_node, target_name):
            prefix = _startswith_value(filter_node)
        suffix_values = _suffix_filter_values(filter_node, target_name)
        if suffix_values:
            suffixes.extend(suffix_values)
    if suffixes:
        return f"{root_pattern}/{prefix}*{{{','.join(sorted(suffixes))}}}"
    return f"{root_pattern}/{prefix}*"


def _is_startswith_filter(node: ast.AST, target_name: str) -> bool:
    return _startswith_value(node) != "" and _filter_receiver(node) == f"{target_name}.name"


def _startswith_value(node: ast.AST) -> str:
    if not isinstance(node, ast.Call):
        return ""
    if not isinstance(node.func, ast.Attribute) or node.func.attr != "startswith":
        return ""
    if len(node.args) != 1:
        return ""
    if not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
        return ""
    return node.args[0].value


def _filter_receiver(node: ast.AST) -> str:
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        return unparse(node.func.value)
    return ""


def _suffix_filter_values(node: ast.AST, target_name: str) -> list[str]:
    if not isinstance(node, ast.Compare):
        return []
    if unparse(node.left) != f"{target_name}.suffix":
        return []
    if len(node.ops) != 1 or not isinstance(node.ops[0], ast.In):
        return []
    if len(node.comparators) != 1:
        return []
    comparator = node.comparators[0]
    if not isinstance(comparator, (ast.Set, ast.Tuple, ast.List)):
        return []
    values: list[str] = []
    for element in comparator.elts:
        if isinstance(element, ast.Constant) and isinstance(element.value, str):
            values.append(element.value)
    return values


def _parameter_name(expression: str) -> str:
    if expression.isidentifier():
        return expression
    return ""


def _interpretation(argument_expression: str, argument_value_sources: str) -> str:
    if argument_value_sources:
        return "parameter_from_value_sources"
    if "/" in argument_expression or "Path(" in argument_expression:
        return "parameter_from_path_expression"
    return "parameter_from_unresolved_argument"


def _split_function_name(full_name: str) -> tuple[str, str]:
    parts = full_name.split(".")
    if len(parts) < 2:
        return "", ""
    return ".".join(parts[:-1]), parts[-1]

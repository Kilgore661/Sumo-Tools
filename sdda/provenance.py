from __future__ import annotations

import ast
from dataclasses import dataclass

from .models import FileUseResolutionRecord, ImportRecord, ProducerOutputRecord, TypeFactRecord, ValueFactRecord
from .source import unparse


@dataclass(frozen=True)
class ReturnFieldBinding:
    producer_function: str
    output_type: str
    field_name: str
    source_name: str
    source_expression: str
    return_line: int


@dataclass(frozen=True)
class WriteBinding:
    producer_function: str
    source_name: str
    write_action: str
    write_expression: str
    write_line: int


def extract_producer_outputs(
    module_trees: dict[str, ast.Module],
    imports: list[ImportRecord],
    type_facts: list[TypeFactRecord],
    value_facts: list[ValueFactRecord],
    file_use_resolutions: list[FileUseResolutionRecord],
) -> list[ProducerOutputRecord]:
    returns: list[ReturnFieldBinding] = []
    writes: list[WriteBinding] = []
    for module_name, tree in module_trees.items():
        module_imports = [record for record in imports if record.source_module == module_name]
        returns.extend(_return_field_bindings(module_name, tree, module_imports, type_facts))
        writes.extend(_write_bindings(module_name, tree))

    records: list[ProducerOutputRecord] = []
    for resolution in file_use_resolutions:
        for value_fact in value_facts:
            if value_fact.module != resolution.module:
                continue
            if value_fact.scope_name != resolution.scope_name:
                continue
            if value_fact.name != _receiver_name(resolution.resolved_expression):
                continue
            for return_binding in returns:
                if not _same_function(return_binding.producer_function, value_fact):
                    continue
                if return_binding.field_name != resolution.resolved_field_name:
                    continue
                for write_binding in writes:
                    if write_binding.producer_function != return_binding.producer_function:
                        continue
                    if write_binding.source_name != return_binding.source_name:
                        continue
                    records.append(
                        ProducerOutputRecord(
                            consumer_module=resolution.module,
                            consumer_scope=resolution.scope_name,
                            consumer_line=resolution.line,
                            consumer_action=resolution.action,
                            consumer_expression=resolution.resolved_expression,
                            producer_function=return_binding.producer_function,
                            output_type=return_binding.output_type,
                            output_field=return_binding.field_name,
                            producer_source_name=return_binding.source_name,
                            producer_source_expression=return_binding.source_expression,
                            producer_write_action=write_binding.write_action,
                            producer_write_expression=write_binding.write_expression,
                            producer_write_line=write_binding.write_line,
                            reason="returned_field_written_then_consumed",
                        )
                    )
    return records


def _return_field_bindings(
    module_name: str,
    tree: ast.Module,
    imports: list[ImportRecord],
    type_facts: list[TypeFactRecord],
) -> list[ReturnFieldBinding]:
    bindings: list[ReturnFieldBinding] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        producer_function = f"{module_name}.{node.name}"
        for statement in ast.walk(node):
            if not isinstance(statement, ast.Return):
                continue
            if not isinstance(statement.value, ast.Call):
                continue
            output_type = _resolve_call_type(module_name, statement.value.func, imports, type_facts)
            if output_type == "":
                continue
            for keyword in statement.value.keywords:
                if keyword.arg is None:
                    continue
                source_name = _source_name(keyword.value)
                if source_name == "":
                    continue
                bindings.append(
                    ReturnFieldBinding(
                        producer_function=producer_function,
                        output_type=output_type,
                        field_name=keyword.arg,
                        source_name=source_name,
                        source_expression=unparse(keyword.value),
                        return_line=statement.lineno,
                    )
                )
    return bindings


def _write_bindings(module_name: str, tree: ast.Module) -> list[WriteBinding]:
    bindings: list[WriteBinding] = []
    for function_node in ast.walk(tree):
        if not isinstance(function_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        producer_function = f"{module_name}.{function_node.name}"
        for node in ast.walk(function_node):
            if not isinstance(node, ast.Call):
                continue
            write_action = _write_action(node)
            if write_action == "":
                continue
            source_name = _write_source_name(node)
            if source_name == "":
                continue
            bindings.append(
                WriteBinding(
                    producer_function=producer_function,
                    source_name=source_name,
                    write_action=write_action,
                    write_expression=unparse(node),
                    write_line=node.lineno,
                )
            )
    return bindings


def _write_action(node: ast.Call) -> str:
    if isinstance(node.func, ast.Attribute):
        if node.func.attr in {"write_text", "write_bytes"}:
            return node.func.attr
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "shutil" and node.func.attr in {"copy", "copy2", "copyfile"}:
            return node.func.attr
    if isinstance(node.func, ast.Name) and node.func.id == "open":
        return "open"
    return ""


def _write_source_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Attribute) and node.func.attr in {"write_text", "write_bytes"}:
        return _source_name(node.func.value)
    if isinstance(node.func, ast.Attribute) and node.func.attr in {"copy", "copy2", "copyfile"}:
        if len(node.args) >= 2:
            return _source_name(node.args[1])
    if isinstance(node.func, ast.Name) and node.func.id == "open":
        if node.args:
            return _source_name(node.args[0])
    return ""


def _same_function(producer_function: str, value_fact: ValueFactRecord) -> bool:
    if producer_function == value_fact.source_full_name:
        return True
    producer_name = producer_function.rsplit(".", maxsplit=1)[-1]
    source_name = value_fact.source_full_name.rsplit(".", maxsplit=1)[-1]
    expression_name = value_fact.source_expression.split("(", maxsplit=1)[0].split(".")[-1]
    return producer_name == source_name == expression_name


def _source_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _receiver_name(expression: str) -> str:
    return expression.split(".", maxsplit=1)[0]


def _resolve_call_type(
    module_name: str,
    node: ast.AST,
    imports: list[ImportRecord],
    type_facts: list[TypeFactRecord],
) -> str:
    if isinstance(node, ast.Name):
        full_name = _resolve_name(module_name, node.id, imports)
        if _is_class(full_name, type_facts):
            return full_name
    return ""


def _resolve_name(module_name: str, name: str, imports: list[ImportRecord]) -> str:
    for record in imports:
        if record.import_kind != "from_import" or not record.resolved:
            continue
        local_name = record.as_name or record.imported_name
        if local_name == name:
            return f"{record.target_module}.{record.imported_name}"
    return f"{module_name}.{name}"


def _is_class(full_name: str, type_facts: list[TypeFactRecord]) -> bool:
    return any(
        fact.owner_full_name == full_name and fact.fact_kind in {"class", "dataclass"}
        for fact in type_facts
    )

from __future__ import annotations

import ast

from .models import TypeFactRecord
from .source import unparse


def extract_type_facts(module_name: str, tree: ast.Module) -> list[TypeFactRecord]:
    facts: list[TypeFactRecord] = []
    for node in tree.body:
        facts.extend(_facts_from_node(module_name, node, parent=""))
    return facts


def _facts_from_node(
    module_name: str,
    node: ast.AST,
    parent: str,
) -> list[TypeFactRecord]:
    if isinstance(node, ast.ClassDef):
        return _class_facts(module_name, node, parent)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return _function_facts(module_name, node, parent, owner_kind="module")
    return []


def _class_facts(
    module_name: str,
    node: ast.ClassDef,
    parent: str,
) -> list[TypeFactRecord]:
    qualname = _qualname(parent, node.name)
    full_name = _full_name(module_name, qualname)
    dataclass_class = _is_dataclass(node)
    facts = [
        TypeFactRecord(
            module=module_name,
            owner_kind="class",
            owner_qualname=qualname,
            owner_full_name=full_name,
            fact_kind="dataclass" if dataclass_class else "class",
            name=node.name,
            annotation="",
            line=node.lineno,
            reason="class_definition",
        )
    ]
    if dataclass_class:
        facts.extend(_dataclass_field_facts(module_name, node, qualname, full_name))
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            facts.extend(_function_facts(module_name, child, qualname, owner_kind="class"))
        elif isinstance(child, ast.ClassDef):
            facts.extend(_class_facts(module_name, child, qualname))
    return facts


def _dataclass_field_facts(
    module_name: str,
    node: ast.ClassDef,
    qualname: str,
    full_name: str,
) -> list[TypeFactRecord]:
    facts: list[TypeFactRecord] = []
    for child in node.body:
        if not isinstance(child, ast.AnnAssign):
            continue
        if not isinstance(child.target, ast.Name):
            continue
        facts.append(
            TypeFactRecord(
                module=module_name,
                owner_kind="class",
                owner_qualname=qualname,
                owner_full_name=full_name,
                fact_kind="dataclass_field",
                name=child.target.id,
                annotation=unparse(child.annotation),
                line=child.lineno,
                reason="dataclass_field_annotation",
            )
        )
    return facts


def _function_facts(
    module_name: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    parent: str,
    owner_kind: str,
) -> list[TypeFactRecord]:
    qualname = _qualname(parent, node.name)
    full_name = _full_name(module_name, qualname)
    facts: list[TypeFactRecord] = []
    for parameter in _annotated_parameters(node.args):
        facts.append(
            TypeFactRecord(
                module=module_name,
                owner_kind=owner_kind,
                owner_qualname=qualname,
                owner_full_name=full_name,
                fact_kind="function_parameter",
                name=parameter.arg,
                annotation=unparse(parameter.annotation),
                line=node.lineno,
                reason="parameter_annotation",
            )
        )
    if node.returns is not None:
        facts.append(
            TypeFactRecord(
                module=module_name,
                owner_kind=owner_kind,
                owner_qualname=qualname,
                owner_full_name=full_name,
                fact_kind="function_return",
                name="return",
                annotation=unparse(node.returns),
                line=node.lineno,
                reason="return_annotation",
            )
        )
    return facts


def _annotated_parameters(arguments: ast.arguments) -> list[ast.arg]:
    parameters = [
        *arguments.posonlyargs,
        *arguments.args,
        *arguments.kwonlyargs,
    ]
    if arguments.vararg is not None:
        parameters.append(arguments.vararg)
    if arguments.kwarg is not None:
        parameters.append(arguments.kwarg)
    return [parameter for parameter in parameters if parameter.annotation is not None]


def _is_dataclass(node: ast.ClassDef) -> bool:
    return any(_decorator_name(decorator).endswith("dataclass") for decorator in node.decorator_list)


def _decorator_name(node: ast.AST) -> str:
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _decorator_name(node.value)
        if prefix:
            return f"{prefix}.{node.attr}"
        return node.attr
    return ""


def _qualname(parent: str, name: str) -> str:
    if parent:
        return f"{parent}.{name}"
    return name


def _full_name(module_name: str, qualname: str) -> str:
    return f"{module_name}.{qualname}"

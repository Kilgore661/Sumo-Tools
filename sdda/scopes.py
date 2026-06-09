from __future__ import annotations

import ast

from .models import ScopeRecord
from .source import node_end_line


def extract_scopes(module_name: str, tree: ast.Module) -> list[ScopeRecord]:
    scopes: list[ScopeRecord] = [
        ScopeRecord(
            module=module_name,
            scope_id=f"{module_name}:<module>",
            scope_kind="module_import_time",
            qualname="<module>",
            line_start=1,
            line_end=node_end_line(tree) or 1,
        )
    ]
    for node in tree.body:
        scopes.extend(_scopes_from_node(module_name, node, parent=""))
    return scopes


def _scopes_from_node(
    module_name: str,
    node: ast.AST,
    parent: str,
) -> list[ScopeRecord]:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        qualname = _qualname(parent, node.name)
        return [
            ScopeRecord(
                module=module_name,
                scope_id=f"{module_name}:{qualname}",
                scope_kind="function_body",
                qualname=qualname,
                line_start=node.lineno,
                line_end=node_end_line(node),
            )
        ]

    if isinstance(node, ast.ClassDef):
        qualname = _qualname(parent, node.name)
        records = [
            ScopeRecord(
                module=module_name,
                scope_id=f"{module_name}:{qualname}",
                scope_kind="class_body",
                qualname=qualname,
                line_start=node.lineno,
                line_end=node_end_line(node),
            )
        ]
        for child in node.body:
            child_records = _scopes_from_node(module_name, child, parent=qualname)
            records.extend(_mark_methods(child_records))
        return records

    return []


def _mark_methods(records: list[ScopeRecord]) -> list[ScopeRecord]:
    marked: list[ScopeRecord] = []
    for record in records:
        if record.scope_kind == "function_body":
            marked.append(
                ScopeRecord(
                    module=record.module,
                    scope_id=record.scope_id,
                    scope_kind="method_body",
                    qualname=record.qualname,
                    line_start=record.line_start,
                    line_end=record.line_end,
                )
            )
        else:
            marked.append(record)
    return marked


def _qualname(parent: str, name: str) -> str:
    if parent:
        return f"{parent}.{name}"
    return name

from __future__ import annotations

import ast
from pathlib import Path

from .models import ProgramEvidenceRecord


DECLARATIVE_NODE_TYPES = (
    ast.Import,
    ast.ImportFrom,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Pass,
)


def parse_python_file(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def classify_module(module_name: str, path: Path, tree: ast.Module, is_dunder_main: bool) -> tuple[str, list[ProgramEvidenceRecord]]:
    evidence: list[ProgramEvidenceRecord] = []
    if is_dunder_main:
        evidence.append(
            ProgramEvidenceRecord(
                module=module_name,
                path=str(path),
                line=1,
                statement_kind="__main__.py",
                reason="dunder_main_module",
            )
        )

    for statement in tree.body:
        if _is_declarative_statement(statement):
            continue
        evidence.append(
            ProgramEvidenceRecord(
                module=module_name,
                path=str(path),
                line=getattr(statement, "lineno", 0),
                statement_kind=type(statement).__name__,
                reason=_statement_reason(statement),
            )
        )

    module_kind = "program" if evidence else "library_module"
    return module_kind, evidence


def has_main_guard(tree: ast.Module) -> bool:
    return any(_is_main_guard(statement) for statement in tree.body if isinstance(statement, ast.If))


def _is_declarative_statement(statement: ast.stmt) -> bool:
    if isinstance(statement, DECLARATIVE_NODE_TYPES):
        return True
    return _is_module_docstring(statement)


def _is_module_docstring(statement: ast.stmt) -> bool:
    if not isinstance(statement, ast.Expr):
        return False
    value = statement.value
    return isinstance(value, ast.Constant) and isinstance(value.value, str)


def _statement_reason(statement: ast.stmt) -> str:
    if _is_main_guard(statement):
        return "main_guard"
    if isinstance(statement, ast.Assign):
        return "top_level_assignment"
    if isinstance(statement, ast.AnnAssign):
        return "top_level_annotated_assignment"
    if isinstance(statement, ast.AugAssign):
        return "top_level_augmented_assignment"
    if isinstance(statement, ast.Expr):
        return "top_level_expression"
    if isinstance(statement, ast.If):
        return "top_level_if"
    if isinstance(statement, (ast.For, ast.AsyncFor, ast.While)):
        return "top_level_loop"
    if isinstance(statement, (ast.With, ast.AsyncWith)):
        return "top_level_with"
    if isinstance(statement, ast.Try):
        return "top_level_try"
    return "top_level_non_declarative_statement"


def _is_main_guard(statement: ast.stmt) -> bool:
    if not isinstance(statement, ast.If):
        return False
    test = statement.test
    if not isinstance(test, ast.Compare):
        return False
    if not _is_name_dunder_name(test.left):
        return False
    if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return False
    if len(test.comparators) != 1:
        return False
    comparator = test.comparators[0]
    return isinstance(comparator, ast.Constant) and comparator.value == "__main__"


def _is_name_dunder_name(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and node.id == "__name__"

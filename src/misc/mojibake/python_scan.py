"""Python AST scanning for text-decoding boundaries."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable

from .config import HTTP_RESPONSE_NAMES
from .findings import Finding


def audit_python_source(path: Path, relative_path: str) -> Iterable[Finding]:
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        yield Finding(
            path=relative_path,
            line=0,
            kind="python_not_utf8",
            detail=str(error),
            evidence="",
        )
        return
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        yield Finding(
            path=relative_path,
            line=error.lineno or 0,
            kind="python_parse_error",
            detail=error.msg,
            evidence=error.text.strip() if error.text else "",
        )
        return
    visitor = PythonBoundaryVisitor(relative_path)
    visitor.visit(tree)
    yield from visitor.findings


class PythonBoundaryVisitor(ast.NodeVisitor):
    def __init__(self, relative_path: str) -> None:
        self.relative_path = relative_path
        self.findings: list[Finding] = []

    def visit_Call(self, node: ast.Call) -> None:
        call_name = dotted_call_name(node.func)
        if call_name == "open":
            self.audit_open_call(node)
        if call_name.endswith(".read_text"):
            self.audit_encoding_kw(node, "read_text_without_encoding")
        if call_name.endswith(".write_text"):
            self.audit_encoding_kw(node, "write_text_without_encoding")
        if call_name.endswith(".read_csv"):
            self.audit_encoding_kw(node, "read_csv_without_encoding")
        if call_name.endswith(".to_csv"):
            self.audit_encoding_kw(node, "to_csv_without_encoding")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "text" and is_http_response_text_attribute(node):
            self.findings.append(
                Finding(
                    path=self.relative_path,
                    line=node.lineno,
                    kind="response_text_candidate",
                    detail="HTTP response .text may decode bytes implicitly; inspect encoding contract.",
                    evidence=ast.unparse(node),
                )
            )
        self.generic_visit(node)

    def audit_open_call(self, node: ast.Call) -> None:
        mode = open_mode(node)
        if "b" in mode:
            return
        self.audit_encoding_kw(node, "open_without_encoding")

    def audit_encoding_kw(self, node: ast.Call, kind: str) -> None:
        if has_keyword(node, "encoding"):
            return
        self.findings.append(
            Finding(
                path=self.relative_path,
                line=node.lineno,
                kind=kind,
                detail="Text boundary has no explicit encoding.",
                evidence=ast.unparse(node)[:160],
            )
        )


def is_http_response_text_attribute(node: ast.Attribute) -> bool:
    if not isinstance(node.value, ast.Name):
        return False
    return node.value.id in HTTP_RESPONSE_NAMES


def dotted_call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_call_name(node.value)
        if not prefix:
            return node.attr
        return f"{prefix}.{node.attr}"
    return ""


def open_mode(node: ast.Call) -> str:
    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
        return str(node.args[1].value)
    for keyword in node.keywords:
        if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant):
            return str(keyword.value.value)
    return "r"


def has_keyword(node: ast.Call, keyword_name: str) -> bool:
    return any(keyword.arg == keyword_name for keyword in node.keywords)

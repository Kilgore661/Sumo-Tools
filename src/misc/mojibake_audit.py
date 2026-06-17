"""Audit project text boundaries and likely mojibake signatures.

The audit is deliberately read-only. It reports suspicious text I/O boundaries,
files that do not decode as UTF-8, and decoded text containing common mojibake
markers. It does not attempt to repair content.
"""

from __future__ import annotations

import argparse
import ast
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TEXT_SUFFIXES = frozenset(
    {
        ".cfg",
        ".css",
        ".csv",
        ".html",
        ".js",
        ".json",
        ".md",
        ".py",
        ".svg",
        ".toml",
        ".tsv",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }
)
SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        ".idea",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "node_modules",
    }
)
SKIP_PATH_PARTS = (
    ("files", "output"),
    ("files", "cache"),
)
THIS_TOOL_PATH = "src/misc/mojibake_audit.py"
MOJIBAKE_MARKERS = (
    "\ufffd",
    "Ã",
    "Â",
    "Å",
    "â€™",
    "â€œ",
    "â€\u009d",
    "â€“",
    "â€”",
    "â€¦",
)
HTTP_RESPONSE_NAMES = frozenset({"r", "resp", "response"})


@dataclass(frozen=True, kw_only=True)
class Finding:
    path: str
    line: int
    kind: str
    detail: str
    evidence: str


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    output_root = args.output.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    findings = sorted(
        audit_tree(root),
        key=lambda finding: (finding.path, finding.line, finding.kind, finding.detail),
    )
    write_findings(output_root / "findings.csv", findings)
    write_summary(output_root / "summary.csv", findings)
    print(f"wrote {len(findings)} findings to {output_root}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit UTF-8 boundaries and likely mojibake signatures."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root or subtree to audit. Defaults to the repo root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("files") / "output" / "mojibake_audit",
        help="Directory for CSV audit reports.",
    )
    return parser.parse_args()


def audit_tree(root: Path) -> Iterable[Finding]:
    for path in walk_files(root):
        relative_path = display_path(root, path)
        if is_probable_text_file(path):
            yield from audit_utf8_bytes(root, path, relative_path)
        if path.suffix == ".py":
            yield from audit_python_source(root, path, relative_path)


def walk_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if SKIP_DIR_NAMES.intersection(path.relative_to(root).parts):
            continue
        if has_skipped_path_part(path.relative_to(root).parts):
            continue
        yield path


def has_skipped_path_part(parts: tuple[str, ...]) -> bool:
    for skipped_parts in SKIP_PATH_PARTS:
        for offset in range(0, len(parts) - len(skipped_parts) + 1):
            if parts[offset : offset + len(skipped_parts)] == skipped_parts:
                return True
    return False


def is_probable_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES


def audit_utf8_bytes(root: Path, path: Path, relative_path: str) -> Iterable[Finding]:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        yield Finding(
            path=relative_path,
            line=0,
            kind="non_utf8_text_candidate",
            detail=str(error),
            evidence="",
        )
        return
    if relative_path == THIS_TOOL_PATH:
        return
    yield from scan_mojibake_markers(relative_path, text)


def scan_mojibake_markers(relative_path: str, text: str) -> Iterable[Finding]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        for marker in MOJIBAKE_MARKERS:
            if marker in line:
                yield Finding(
                    path=relative_path,
                    line=line_number,
                    kind="mojibake_marker",
                    detail=printable_marker(marker),
                    evidence=line.strip()[:160],
                )


def printable_marker(marker: str) -> str:
    if marker == "\ufffd":
        return "replacement_character"
    return marker


def audit_python_source(root: Path, path: Path, relative_path: str) -> Iterable[Finding]:
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


def write_findings(path: Path, findings: list[Finding]) -> None:
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=("path", "line", "kind", "detail", "evidence"),
        )
        writer.writeheader()
        for finding in findings:
            writer.writerow(
                {
                    "path": finding.path,
                    "line": finding.line,
                    "kind": finding.kind,
                    "detail": finding.detail,
                    "evidence": finding.evidence,
                }
            )


def write_summary(path: Path, findings: list[Finding]) -> None:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.kind] = counts.get(finding.kind, 0) + 1
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=("kind", "count"))
        writer.writeheader()
        for kind, count in sorted(counts.items()):
            writer.writerow({"kind": kind, "count": count})


def display_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


if __name__ == "__main__":
    main()

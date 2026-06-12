"""Scan project Python modules and report AST constructs relevant to Jervis.

The default scan is intentionally project-oriented: it scans ``src`` and writes
reports to ``files/output/jervis/src/raw_scan_src.*``.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_SOURCE_ROOT = Path("src")
DEFAULT_OUTPUT_DIR = Path("files") / "output" / "jervis"
MAX_EXAMPLES = 8


INTERESTING_NODES: tuple[tuple[type[ast.AST], str], ...] = (
    (ast.While, "While"),
    (ast.For, "For"),
    (ast.AsyncFor, "AsyncFor"),
    (ast.Try, "Try"),
    (ast.With, "With"),
    (ast.AsyncWith, "AsyncWith"),
    (ast.Import, "Import"),
    (ast.ImportFrom, "ImportFrom"),
    (ast.Global, "Global"),
    (ast.Nonlocal, "Nonlocal"),
    (ast.Lambda, "Lambda"),
    (ast.Yield, "Yield"),
    (ast.YieldFrom, "YieldFrom"),
    (ast.Await, "Await"),
    (ast.ListComp, "ListComp"),
    (ast.DictComp, "DictComp"),
    (ast.SetComp, "SetComp"),
    (ast.GeneratorExp, "GeneratorExp"),
    (ast.NamedExpr, "NamedExpr"),
    (ast.Delete, "Delete"),
    (ast.Raise, "Raise"),
    (ast.Assert, "Assert"),
    (ast.Match, "Match"),
    (ast.ClassDef, "ClassDef"),
    (ast.FunctionDef, "FunctionDef"),
    (ast.AsyncFunctionDef, "AsyncFunctionDef"),
    (ast.Return, "Return"),
    (ast.Break, "Break"),
    (ast.Continue, "Continue"),
)

WATCHED_CALLS = {
    "eval",
    "exec",
    "__import__",
    "importlib.import_module",
    "open",
    "Path.open",
    "json.load",
    "json.dump",
    "pickle.load",
    "pickle.dump",
}


@dataclass(frozen=True)
class Example:
    path: str
    line: int | str


@dataclass(frozen=True)
class ParseError:
    path: str
    line: int | None
    message: str


@dataclass(frozen=True)
class ScanReport:
    source_roots: list[str]
    output_path: str
    python_file_count: int
    parse_errors: list[ParseError]
    statement_counts: dict[str, int]
    expression_counts: dict[str, int]
    interesting_examples: dict[str, list[Example]]
    target_counts: dict[str, int]
    target_examples: dict[str, list[Example]]
    import_counts: dict[str, int]
    import_examples: dict[str, list[Example]]
    watched_call_counts: dict[str, int]
    watched_call_examples: dict[str, list[Example]]


def iter_python_files(source_roots: Iterable[Path]) -> list[Path]:
    files: set[Path] = set()
    for source_root in source_roots:
        if source_root.is_file() and source_root.suffix == ".py":
            files.add(source_root)
        elif source_root.exists():
            files.update(source_root.rglob("*.py"))
    return sorted(
        path
        for path in files
        if ".git" not in path.parts and ".venv" not in path.parts and "__pycache__" not in path.parts
    )


def add_example(examples: dict[str, list[Example]], key: str, path: Path, node: ast.AST) -> None:
    if len(examples[key]) < MAX_EXAMPLES:
        examples[key].append(Example(str(path), getattr(node, "lineno", "?")))


def target_kind(target: ast.AST) -> str:
    if isinstance(target, ast.Name):
        return "Name target"
    if isinstance(target, ast.Tuple):
        return "Tuple unpack target"
    if isinstance(target, ast.List):
        return "List unpack target"
    if isinstance(target, ast.Attribute):
        return "Attribute target"
    if isinstance(target, ast.Subscript):
        return "Subscript target"
    if isinstance(target, ast.Starred):
        return "Starred target"
    return f"{type(target).__name__} target"


def call_name(func: ast.AST) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        base = call_name(func.value)
        return f"{base}.{func.attr}" if base else func.attr
    return None


def sorted_counts(counter: Counter[str]) -> dict[str, int]:
    return dict(counter.most_common())


def root_label(source_roots: list[Path]) -> str:
    if len(source_roots) == 1:
        label = str(source_roots[0]).strip(".\\/")
    else:
        label = "combined"
    label = label.replace("\\", "_").replace("/", "_").replace(":", "")
    label = re.sub(r"[^A-Za-z0-9_.-]+", "_", label)
    return label or "root"


def scan(source_roots: list[Path], output_path: Path) -> ScanReport:
    files = iter_python_files(source_roots)
    statement_counts: Counter[str] = Counter()
    expression_counts: Counter[str] = Counter()
    target_counts: Counter[str] = Counter()
    import_counts: Counter[str] = Counter()
    watched_call_counts: Counter[str] = Counter()
    parse_errors: list[ParseError] = []
    interesting_examples: dict[str, list[Example]] = defaultdict(list)
    target_examples: dict[str, list[Example]] = defaultdict(list)
    import_examples: dict[str, list[Example]] = defaultdict(list)
    watched_call_examples: dict[str, list[Example]] = defaultdict(list)

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            parse_errors.append(ParseError(str(path), exc.lineno, exc.msg))
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.stmt):
                statement_counts[type(node).__name__] += 1
            if isinstance(node, ast.expr):
                expression_counts[type(node).__name__] += 1

            for node_type, name in INTERESTING_NODES:
                if isinstance(node, node_type):
                    add_example(interesting_examples, name, path, node)

            if isinstance(node, ast.Assign):
                for target in node.targets:
                    key = target_kind(target)
                    target_counts[key] += 1
                    add_example(target_examples, key, path, node)
            elif isinstance(node, ast.AnnAssign):
                key = target_kind(node.target)
                target_counts[key] += 1
                add_example(target_examples, key, path, node)
            elif isinstance(node, ast.AugAssign):
                key = f"Aug {target_kind(node.target)}"
                target_counts[key] += 1
                add_example(target_examples, key, path, node)
            elif isinstance(node, ast.For):
                key = f"For {target_kind(node.target)}"
                target_counts[key] += 1
                add_example(target_examples, key, path, node)

            if isinstance(node, ast.Import):
                for _alias in node.names:
                    import_counts["import"] += 1
                    add_example(import_examples, "import", path, node)
            elif isinstance(node, ast.ImportFrom):
                key = "from import *" if any(alias.name == "*" for alias in node.names) else "from import explicit"
                import_counts[key] += 1
                add_example(import_examples, key, path, node)

            if isinstance(node, ast.Call):
                name = call_name(node.func)
                if name in WATCHED_CALLS:
                    watched_call_counts[name] += 1
                    add_example(watched_call_examples, name, path, node)

    return ScanReport(
        source_roots=[str(path) for path in source_roots],
        output_path=str(output_path),
        python_file_count=len(files),
        parse_errors=parse_errors,
        statement_counts=sorted_counts(statement_counts),
        expression_counts=sorted_counts(expression_counts),
        interesting_examples=dict(sorted(interesting_examples.items())),
        target_counts=sorted_counts(target_counts),
        target_examples=dict(sorted(target_examples.items())),
        import_counts=sorted_counts(import_counts),
        import_examples=dict(sorted(import_examples.items())),
        watched_call_counts=sorted_counts(watched_call_counts),
        watched_call_examples=dict(sorted(watched_call_examples.items())),
    )


def render_counts(title: str, counts: dict[str, int]) -> list[str]:
    lines = [f"## {title}", ""]
    if not counts:
        return lines + ["None found.", ""]
    lines.append("```text")
    lines.extend(f"{key}: {value}" for key, value in counts.items())
    lines.append("```")
    lines.append("")
    return lines


def render_examples(title: str, examples: dict[str, list[Example]]) -> list[str]:
    lines = [f"## {title}", ""]
    if not examples:
        return lines + ["None found.", ""]
    for key, items in examples.items():
        lines.append(f"### {key}")
        lines.append("")
        for item in items:
            lines.append(f"* `{item.path}:{item.line}`")
        lines.append("")
    return lines


def render_markdown(report: ScanReport) -> str:
    lines = [
        "# Jervis AST Scan",
        "",
        "This report inventories Python syntax used by the scanned source roots.",
        "It is intended to identify where a Jervis-style `free(P)` analysis is straightforward and where it needs extra semantics or conservative warnings.",
        "",
        "## Summary",
        "",
        f"* Source roots: {', '.join(f'`{root}`' for root in report.source_roots)}",
        f"* Python files: `{report.python_file_count}`",
        f"* Parse errors: `{len(report.parse_errors)}`",
        f"* Output path: `{report.output_path}`",
        "",
    ]

    if report.parse_errors:
        lines.extend(["## Parse Errors", ""])
        for error in report.parse_errors:
            lines.append(f"* `{error.path}:{error.line}` {error.message}")
        lines.append("")

    lines.extend(render_counts("Statement Node Counts", report.statement_counts))
    lines.extend(render_counts("Expression Node Counts", report.expression_counts))
    lines.extend(render_counts("Assignment And Binding Targets", report.target_counts))
    lines.extend(render_counts("Import Forms", report.import_counts))
    lines.extend(render_counts("Watched Dynamic And File Calls", report.watched_call_counts))
    lines.extend(render_examples("Interesting Construct Examples", report.interesting_examples))
    lines.extend(render_examples("Assignment Target Examples", report.target_examples))
    lines.extend(render_examples("Import Examples", report.import_examples))
    lines.extend(render_examples("Watched Call Examples", report.watched_call_examples))
    return "\n".join(lines).rstrip() + "\n"


def write_report(report: ScanReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(report), encoding="utf-8")
    output_path.with_suffix(".json").write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan Python AST constructs for Jervis analysis.")
    parser.add_argument(
        "source_roots",
        nargs="*",
        type=Path,
        default=[DEFAULT_SOURCE_ROOT],
        help="Python files or directories to scan. Defaults to src.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    label = root_label(args.source_roots)
    output_path = DEFAULT_OUTPUT_DIR / label / f"raw_scan_{label}.md"
    report = scan(args.source_roots, output_path)
    write_report(report, output_path)
    print(f"Scanned {report.python_file_count} Python files.")
    print(f"Wrote {output_path}")
    print(f"Wrote {output_path.with_suffix('.json')}")


if __name__ == "__main__":
    main()

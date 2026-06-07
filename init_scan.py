import ast
from pathlib import Path


def has_module_docstring(body: list[ast.stmt]) -> bool:
    return (
        bool(body)
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    )


def body_without_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if has_module_docstring(body):
        return body[1:]
    return body


def init_kind(path: Path) -> str:
    text = path.read_text(encoding="utf-8")

    if not text.strip():
        return "empty"

    tree = ast.parse(text, filename=str(path))
    body = list(tree.body)

    if has_module_docstring(body) and not body_without_docstring(body):
        return "docstring_only"

    non_docstring_body = body_without_docstring(body)

    if non_docstring_body and all(
        isinstance(stmt, (ast.Import, ast.ImportFrom))
        for stmt in non_docstring_body
    ):
        return "import_only"

    return "executable"


init_files = sorted(Path("src").rglob("__init__.py")) + sorted(Path("tests").rglob("__init__.py"))

by_kind = {
    "empty": [],
    "docstring_only": [],
    "import_only": [],
    "executable": [],
}

for path in init_files:
    by_kind[init_kind(path)].append(path)

print(f"__init__.py files: {len(init_files)}")
print(f"empty: {len(by_kind['empty'])}")
print(f"docstring_only: {len(by_kind['docstring_only'])}")
print(f"import_only: {len(by_kind['import_only'])}")
print(f"executable: {len(by_kind['executable'])}")

for kind in ("empty", "docstring_only", "import_only", "executable"):
    print()
    print(f"{kind}:")
    for path in by_kind[kind]:
        print(path)


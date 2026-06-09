from __future__ import annotations

import ast
from pathlib import PurePosixPath

from .models import ImportRecord, ModuleRecord
from .source import parse_python_file

PathConstantMap = dict[str, dict[str, str]]


def build_path_constant_map(
    module_index: dict[str, ModuleRecord],
    imports: list[ImportRecord],
    reachable_modules: list[str],
    import_root: PurePosixPath,
) -> PathConstantMap:
    constants: PathConstantMap = {module: {} for module in reachable_modules}
    assignments = _module_assignments(module_index, reachable_modules)

    for _ in range(6):
        changed = False
        for module_name in reachable_modules:
            module_dir = _module_dir(module_index[module_name], import_root)
            for name, expression in assignments.get(module_name, {}).items():
                value = _eval_path_expression(expression, constants[module_name], module_dir)
                if value is not None and constants[module_name].get(name) != value:
                    constants[module_name][name] = value
                    changed = True
            if _copy_imported_constants(module_name, imports, constants):
                changed = True
        if not changed:
            break
    return constants


def _module_assignments(
    module_index: dict[str, ModuleRecord],
    reachable_modules: list[str],
) -> dict[str, dict[str, ast.AST]]:
    assignments: dict[str, dict[str, ast.AST]] = {}
    for module_name in reachable_modules:
        tree = parse_python_file(module_index[module_name].path)
        module_assignments: dict[str, ast.AST] = {}
        for node in tree.body:
            target, value = _assignment_parts(node)
            if target is not None and target.isupper() and value is not None:
                module_assignments[target] = value
        assignments[module_name] = module_assignments
    return assignments


def _assignment_parts(node: ast.stmt) -> tuple[str | None, ast.AST | None]:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target = node.targets[0]
        if isinstance(target, ast.Name):
            return target.id, node.value
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id, node.value
    return None, None


def _copy_imported_constants(
    module_name: str,
    imports: list[ImportRecord],
    constants: PathConstantMap,
) -> bool:
    changed = False
    for record in imports:
        if record.source_module != module_name:
            continue
        if record.import_kind != "from_import" or not record.resolved:
            continue
        imported = record.imported_name
        alias = record.as_name or imported
        value = constants.get(record.target_module, {}).get(imported)
        if value is not None and constants[module_name].get(alias) != value:
            constants[module_name][alias] = value
            changed = True
    return changed


def _eval_path_expression(
    node: ast.AST,
    constants: dict[str, str],
    module_dir: PurePosixPath,
) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        if node.id == "__file__":
            return str(module_dir / "__init__.py")
        return constants.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _eval_path_expression(node.left, constants, module_dir)
        right = _eval_path_expression(node.right, constants, module_dir)
        if left is None or right is None:
            return None
        return str(PurePosixPath(left) / right)
    if isinstance(node, ast.Call):
        return _eval_call(node, constants, module_dir)
    if isinstance(node, ast.Attribute):
        return _eval_attribute(node, constants, module_dir)
    if isinstance(node, ast.Subscript):
        return _eval_subscript(node, constants, module_dir)
    return None


def _eval_call(
    node: ast.Call,
    constants: dict[str, str],
    module_dir: PurePosixPath,
) -> str | None:
    if isinstance(node.func, ast.Name) and node.func.id == "Path" and len(node.args) == 1:
        arg = node.args[0]
        if isinstance(arg, ast.Name) and arg.id == "__file__":
            return str(module_dir / "__init__.py")
        return _eval_path_expression(arg, constants, module_dir)
    if isinstance(node.func, ast.Attribute) and node.func.attr == "resolve":
        return _eval_path_expression(node.func.value, constants, module_dir)
    return None


def _eval_attribute(
    node: ast.Attribute,
    constants: dict[str, str],
    module_dir: PurePosixPath,
) -> str | None:
    value = _eval_path_expression(node.value, constants, module_dir)
    if value is None:
        return None
    if node.attr == "parent":
        return str(PurePosixPath(value).parent)
    return None


def _eval_subscript(
    node: ast.Subscript,
    constants: dict[str, str],
    module_dir: PurePosixPath,
) -> str | None:
    if not isinstance(node.value, ast.Attribute) or node.value.attr != "parents":
        return None
    value = _eval_path_expression(node.value.value, constants, module_dir)
    index = _literal_int(node.slice)
    if value is None or index is None:
        return None
    parents = PurePosixPath(value).parents
    if index >= len(parents):
        return None
    return str(parents[index])


def _literal_int(node: ast.AST) -> int | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    return None


def _module_dir(module_record: ModuleRecord, import_root: PurePosixPath) -> PurePosixPath:
    path = PurePosixPath(module_record.path)
    try:
        relative = path.relative_to(import_root)
    except ValueError:
        relative = path
    return relative.parent

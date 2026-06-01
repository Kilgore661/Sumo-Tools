"""Resolve syntactic Python imports against discovered project modules."""

from __future__ import annotations

from pathlib import Path


def package_name_for_module(path: Path, module_name: str) -> str:
    """Return the package context used to resolve relative imports."""

    if path.name == "__init__.py":
        return module_name
    return module_name.rpartition(".")[0]


def resolve_relative_module(
    importer_path: Path,
    importer_module: str,
    level: int,
    module_text: str,
) -> str:
    """Resolve the module portion of a relative import into a dotted module name."""

    package = package_name_for_module(importer_path, importer_module)
    package_parts = package.split(".") if package else []
    if level > 1:
        package_parts = package_parts[: -(level - 1)]
    module_parts = module_text.split(".") if module_text else []
    return ".".join([*package_parts, *module_parts])


def find_project_module_path(module_index: dict[str, Path], module_name: str) -> str:
    """Return a project path for a resolved module name, if known."""

    if module_name in module_index:
        return module_index[module_name].as_posix()
    return ""


def resolution_status(resolved_module: str, resolved_path: str, resolved_symbol_module: str) -> str:
    """Classify whether an import resolved to known project source."""

    if resolved_symbol_module:
        return "resolved_symbol_module"
    if resolved_path:
        return "resolved_module"
    if resolved_module.startswith("src.") or resolved_module.startswith("tests."):
        return "unresolved_project_module"
    return "external_or_stdlib"

from __future__ import annotations

from pathlib import Path

from .file_families import normalise_file_families
from .file_uses import extract_file_uses
from .import_graph import build_reachable_imports
from .models import AnalysisResult, FileUseRecord, ScopeRecord, UnresolvedRecord
from .module_index import build_module_index
from .scopes import extract_scopes
from .source import parse_python_file


def analyse(root_module: str, import_root: Path, output_dir: Path | None = None) -> AnalysisResult:
    module_index = build_module_index(import_root)
    reachable_modules, imports = build_reachable_imports(root_module, module_index)
    scopes: list[ScopeRecord] = []
    file_uses: list[FileUseRecord] = []
    unresolved: list[UnresolvedRecord] = []

    for module_name in reachable_modules:
        module_record = module_index[module_name]
        tree = parse_python_file(module_record.path)
        module_scopes = extract_scopes(module_name, tree)
        module_uses, module_unresolved = extract_file_uses(module_name, tree, module_scopes)
        scopes.extend(module_scopes)
        file_uses.extend(module_uses)
        unresolved.extend(module_unresolved)

    file_families, file_family_evidence = normalise_file_families(file_uses)
    final_output_dir = output_dir or _default_output_dir(root_module)
    return AnalysisResult(
        root_module=root_module,
        import_root=import_root,
        output_dir=final_output_dir,
        modules=list(module_index.values()),
        imports=imports,
        reachable_modules=reachable_modules,
        scopes=scopes,
        file_uses=file_uses,
        file_families=file_families,
        file_family_evidence=file_family_evidence,
        unresolved=unresolved,
    )


def _default_output_dir(root_module: str) -> Path:
    return Path("files") / "output" / "sdda" / root_module

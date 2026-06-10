from __future__ import annotations

from pathlib import Path

from .classification import classify_file_families
from .distribution import derive_distribution_candidates
from .field_facts import extract_field_facts
from .file_families import normalise_file_families
from .file_use_resolution import resolve_file_uses
from .file_uses import extract_file_uses
from .import_graph import build_reachable_imports
from .local_path_aliases import build_local_path_alias_map
from .models import AnalysisResult, FieldFactRecord, FileUseRecord, FileUseResolutionRecord, ScopeRecord, TypeFactRecord, UnresolvedRecord, ValueFactRecord
from .module_index import build_module_index
from .path_constants import build_path_constant_map
from .provenance import extract_producer_outputs, extract_producer_return_bindings, extract_producer_write_bindings
from .scopes import extract_scopes
from .source import parse_python_file
from .type_facts import extract_type_facts
from .value_facts import extract_value_facts


def analyse(root_module: str, import_root: Path, output_dir: Path | None = None) -> AnalysisResult:
    module_index = build_module_index(import_root)
    reachable_modules, imports = build_reachable_imports(root_module, module_index)
    path_constants = build_path_constant_map(module_index, imports, reachable_modules, import_root)
    scopes: list[ScopeRecord] = []
    type_facts: list[TypeFactRecord] = []
    file_uses: list[FileUseRecord] = []
    unresolved: list[UnresolvedRecord] = []
    parsed_trees = {}

    for module_name in reachable_modules:
        module_record = module_index[module_name]
        tree = parse_python_file(module_record.path)
        parsed_trees[module_name] = tree
        module_scopes = extract_scopes(module_name, tree)
        module_uses, module_unresolved = extract_file_uses(module_name, tree, module_scopes)
        scopes.extend(module_scopes)
        type_facts.extend(extract_type_facts(module_name, tree))
        file_uses.extend(module_uses)
        unresolved.extend(module_unresolved)

    scopes_by_module = _scopes_by_module(scopes)
    value_facts: list[ValueFactRecord] = []
    for module_name in reachable_modules:
        value_facts.extend(extract_value_facts(module_name, parsed_trees[module_name], scopes_by_module[module_name], imports, type_facts))

    field_facts: list[FieldFactRecord] = []
    for module_name in reachable_modules:
        field_facts.extend(extract_field_facts(module_name, parsed_trees[module_name], scopes_by_module[module_name], imports, type_facts, value_facts))

    file_use_resolutions: list[FileUseResolutionRecord] = resolve_file_uses(file_uses, field_facts)
    producer_return_bindings = extract_producer_return_bindings(parsed_trees, imports, type_facts)
    producer_write_bindings = extract_producer_write_bindings(parsed_trees)
    producer_outputs = extract_producer_outputs(producer_return_bindings, producer_write_bindings, value_facts, file_use_resolutions)

    local_aliases = build_local_path_alias_map(module_index, reachable_modules, scopes, path_constants)
    file_families, file_family_evidence = normalise_file_families(file_uses, path_constants, local_aliases)
    file_family_classification = classify_file_families(file_families, producer_outputs)
    distribution_candidates = derive_distribution_candidates(file_family_classification)
    final_output_dir = output_dir or _default_output_dir(root_module)
    return AnalysisResult(
        root_module=root_module,
        import_root=import_root,
        output_dir=final_output_dir,
        modules=list(module_index.values()),
        imports=imports,
        reachable_modules=reachable_modules,
        scopes=scopes,
        type_facts=type_facts,
        value_facts=value_facts,
        field_facts=field_facts,
        file_uses=file_uses,
        file_use_resolutions=file_use_resolutions,
        producer_return_bindings=producer_return_bindings,
        producer_write_bindings=producer_write_bindings,
        producer_outputs=producer_outputs,
        file_families=file_families,
        file_family_evidence=file_family_evidence,
        file_family_classification=file_family_classification,
        distribution_candidates=distribution_candidates,
        unresolved=unresolved,
    )


def _default_output_dir(root_module: str) -> Path:
    return Path("files") / "output" / "sdda" / root_module


def _scopes_by_module(scopes: list[ScopeRecord]) -> dict[str, list[ScopeRecord]]:
    grouped: dict[str, list[ScopeRecord]] = {}
    for scope in scopes:
        grouped.setdefault(scope.module, []).append(scope)
    return grouped

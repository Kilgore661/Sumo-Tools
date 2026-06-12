from __future__ import annotations

from collections import defaultdict
from pathlib import Path, PurePosixPath

from sdda.dataflow.file_families import normalise_file_families
from sdda.dataflow.file_uses import extract_file_uses
from sdda.dataflow.local_path_aliases import build_local_path_alias_map
from sdda.dataflow.module_index import build_module_index
from sdda.dataflow.path_constants import build_path_constant_map
from sdda.dataflow.scopes import extract_scopes
from sdda.dataflow.source import parse_python_file

from .models import ModuleOutputRootRecord, OutputRootEvidenceRecord

OUTPUT_DIR = PurePosixPath("files/output")
WRITE_ACTIONS = {"may_write", "may_create_directory", "may_copy", "may_delete"}


def analyse_output_roots() -> tuple[list[OutputRootEvidenceRecord], list[ModuleOutputRootRecord]]:
    import_root = Path(".")
    module_index = {
        name: record
        for name, record in build_module_index(import_root).items()
        if name == "src" or name.startswith("src.")
    }
    module_names = sorted(module_index)
    scopes = []
    file_uses = []

    for module_name in module_names:
        tree = parse_python_file(module_index[module_name].path)
        module_scopes = extract_scopes(module_name, tree)
        module_uses, _unresolved = extract_file_uses(module_name, tree, module_scopes)
        scopes.extend(module_scopes)
        file_uses.extend(module_uses)

    path_constants = build_path_constant_map(module_index, [], module_names, import_root)
    local_aliases = build_local_path_alias_map(module_index, module_names, scopes, path_constants)
    families, family_evidence = normalise_file_families(file_uses, path_constants, local_aliases)
    family_pattern_by_id = {family.family_id: family.family_pattern for family in families}
    modules_with_writes = {
        use.module
        for use in file_uses
        if use.action in WRITE_ACTIONS
    }

    evidence: list[OutputRootEvidenceRecord] = []
    for row in family_evidence:
        if row.action not in WRITE_ACTIONS:
            continue
        family_pattern = family_pattern_by_id.get(row.family_id, row.resolved_expression)
        candidate_root, kind, confidence, reason = _candidate_output_root(family_pattern, row.action)
        if candidate_root == "":
            continue
        evidence.append(
            OutputRootEvidenceRecord(
                module=row.module,
                scope=row.scope_name,
                line=row.line,
                action=row.action,
                family_pattern=family_pattern,
                candidate_output_root=candidate_root,
                evidence_kind=kind,
                confidence=confidence,
                raw_expression=row.raw_expression,
                reason=reason,
            )
        )
    evidence.extend(_constant_output_root_evidence(path_constants, modules_with_writes))
    evidence.extend(_convention_output_root_evidence(module_names, modules_with_writes))

    module_roots = _module_output_roots(module_names, evidence)
    return sorted(evidence, key=lambda row: (row.module, row.candidate_output_root, row.line)), module_roots


def _candidate_output_root(pattern: str, action: str) -> tuple[str, str, str, str]:
    pattern = pattern.replace("\\", "/").removeprefix("./")
    if not pattern.startswith("files/output/") and pattern != "files/output":
        return "", "", "", "not_under_files_output"

    if pattern == "files/output":
        return pattern, "output_root", "high", "exact_files_output_root"

    parts = pattern.split("/")
    root_parts = parts[:2]
    tail = parts[2:]
    if not tail:
        return "files/output", "output_root", "high", "exact_files_output_root"

    stop = _first_dynamic_index(tail)
    if stop is not None:
        if stop == 0:
            return "files/output", "dynamic_under_files_output", "low", "dynamic_first_segment"
        return "/".join(root_parts + tail[:stop]), "static_prefix_before_dynamic_segment", "medium", "dynamic_suffix"

    if action == "may_create_directory":
        return pattern, "created_directory", "medium", "directory_create_under_files_output"

    if _looks_like_file(tail[-1]):
        return "/".join(root_parts + tail[:-1]), "file_parent", "high", "file_write_parent"

    return pattern, "path_without_file_extension", "medium", "path_under_files_output"


def _first_dynamic_index(parts: list[str]) -> int | None:
    for index, part in enumerate(parts):
        if "*" in part or "{" in part or "}" in part:
            return index
    return None


def _looks_like_file(part: str) -> bool:
    if "." not in part:
        return False
    suffix = part.rsplit(".", 1)[-1]
    return 1 <= len(suffix) <= 8 and suffix.replace("_", "").isalnum()


def _module_output_roots(
    module_names: list[str],
    evidence: list[OutputRootEvidenceRecord],
) -> list[ModuleOutputRootRecord]:
    evidence_by_module: dict[str, list[OutputRootEvidenceRecord]] = defaultdict(list)
    for row in evidence:
        evidence_by_module[row.module].append(row)

    records: list[ModuleOutputRootRecord] = []
    for module_name in module_names:
        module_evidence = evidence_by_module.get(module_name, [])
        convention_root = _convention_root(module_name)
        if not module_evidence:
            records.append(
                ModuleOutputRootRecord(
                    module=module_name,
                    output_root="",
                    status="not_known",
                    confidence="none",
                    evidence_count=0,
                    shortest_root="",
                    convention_root=convention_root,
                    roots_seen="",
                    reason="no_static_write_under_files_output",
                )
            )
            continue

        roots = sorted({row.candidate_output_root for row in module_evidence})
        shortest = min(roots, key=lambda root: (len(PurePosixPath(root).parts), root))
        common = _common_root(roots)
        selected = common or shortest
        status = "known"
        confidence = _module_confidence(selected, convention_root, module_evidence)
        records.append(
            ModuleOutputRootRecord(
                module=module_name,
                output_root=selected,
                status=status,
                confidence=confidence,
                evidence_count=len(module_evidence),
                shortest_root=shortest,
                convention_root=convention_root,
                roots_seen=";".join(roots),
                reason=_module_reason(selected, convention_root, roots),
            )
        )

    return sorted(records, key=lambda row: (row.status != "known", row.module))


def _constant_output_root_evidence(
    path_constants: dict[str, dict[str, str]],
    modules_with_writes: set[str],
) -> list[OutputRootEvidenceRecord]:
    rows: list[OutputRootEvidenceRecord] = []
    for module_name, constants in sorted(path_constants.items()):
        if module_name not in modules_with_writes:
            continue
        for name, value in sorted(constants.items()):
            candidate_root, kind, confidence, reason = _candidate_output_root(value, "may_write")
            if candidate_root == "":
                continue
            rows.append(
                OutputRootEvidenceRecord(
                    module=module_name,
                    scope="<module>",
                    line=0,
                    action="constant_path",
                    family_pattern=value,
                    candidate_output_root=candidate_root,
                    evidence_kind=f"module_constant:{kind}",
                    confidence=confidence,
                    raw_expression=name,
                    reason=f"module_constant_under_files_output:{reason}",
                )
            )
    return rows


def _convention_output_root_evidence(
    module_names: list[str],
    modules_with_writes: set[str],
) -> list[OutputRootEvidenceRecord]:
    rows: list[OutputRootEvidenceRecord] = []
    for module_name in module_names:
        if module_name not in modules_with_writes:
            continue
        for candidate in _convention_roots(module_name):
            if not Path(candidate).exists():
                continue
            rows.append(
                OutputRootEvidenceRecord(
                    module=module_name,
                    scope="<module>",
                    line=0,
                    action="convention_check",
                    family_pattern=candidate,
                    candidate_output_root=candidate,
                    evidence_kind="existing_convention_root",
                    confidence="medium",
                    raw_expression="",
                    reason="module_has_write_and_convention_root_exists",
                )
            )
    return rows


def _convention_roots(module_name: str) -> list[str]:
    roots = []
    if module_name.startswith("src."):
        suffix = module_name.removeprefix("src.")
        roots.append("files/output/" + suffix.replace(".", "/"))
        for removable_prefix in ("analysis.", "products."):
            if suffix.startswith(removable_prefix):
                roots.append("files/output/" + suffix.removeprefix(removable_prefix).replace(".", "/"))
    elif module_name == "src":
        roots.append("files/output")
    return list(dict.fromkeys(roots))


def _convention_root(module_name: str) -> str:
    roots = _convention_roots(module_name)
    return roots[0] if roots else ""


def _common_root(roots: list[str]) -> str:
    if not roots:
        return ""
    split_roots = [root.split("/") for root in roots]
    common: list[str] = []
    for parts in zip(*split_roots):
        if len(set(parts)) != 1:
            break
        common.append(parts[0])
    if len(common) < 2:
        return ""
    return "/".join(common)


def _module_confidence(
    selected: str,
    convention_root: str,
    evidence: list[OutputRootEvidenceRecord],
) -> str:
    if selected == convention_root:
        return "high"
    if any(row.confidence == "high" for row in evidence):
        return "medium"
    return "low"


def _module_reason(selected: str, convention_root: str, roots: list[str]) -> str:
    if selected == convention_root:
        return "matches_module_output_convention"
    if len(roots) == 1:
        return "single_static_output_root"
    return "common_static_output_root"

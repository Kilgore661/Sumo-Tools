from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from sdda.dataflow.file_families import normalise_file_families
from sdda.dataflow.file_uses import extract_file_uses
from sdda.dataflow.local_path_aliases import build_local_path_alias_map
from sdda.dataflow.module_index import build_module_index
from sdda.dataflow.path_constants import build_path_constant_map
from sdda.dataflow.scopes import extract_scopes
from sdda.dataflow.source import parse_python_file

from .models import (
    InputActionRecord,
    InputResolutionRecord,
    InputWorklistRecord,
    ProducerSearchRecord,
    Product,
)

WRITE_ACTIONS = {"may_write", "may_create_directory", "may_delete", "may_copy"}
AUTOMATIC_PRODUCER_STATUS = "find_producer_or_include"


@dataclass(frozen=True)
class _WriteEvidence:
    module: str
    scope: str
    line: int
    action: str
    raw_expression: str
    write_pattern: str
    reason: str


def perform_input_actions(
    product: Product,
    worklist: list[InputWorklistRecord],
) -> tuple[list[InputActionRecord], list[ProducerSearchRecord], list[InputResolutionRecord]]:
    writes = _collect_write_evidence(product)
    actions: list[InputActionRecord] = []
    producer_search: list[ProducerSearchRecord] = []
    resolutions: list[InputResolutionRecord] = []

    for item in worklist:
        if item.status == AUTOMATIC_PRODUCER_STATUS:
            matches = _producer_matches(item, writes)
            if not matches:
                matches = _textual_producer_matches(product, item, writes)
            producer_search.extend(matches)
            actions.append(_action_record(item, "automatic", "producer_search", _action_result(matches), "searched_static_write_families"))
            resolutions.append(_resolution_record(item, matches))
        else:
            actions.append(
                _action_record(
                    item,
                    "manual",
                    "human_review",
                    "manual_review_required",
                    "no_automatic_handler_for_status",
                )
            )
            resolutions.append(
                InputResolutionRecord(
                    input_id=item.input_id,
                    input_pattern=item.input_pattern,
                    needed_by_product=item.needed_by_product,
                    status=item.status,
                    resolution="manual_review_required",
                    candidate_count=0,
                    candidate_producer_modules="",
                    next_action=item.candidate_next_action,
                    reason="no_automatic_handler_for_status",
                )
            )

    return actions, producer_search, resolutions


def _collect_write_evidence(product: Product) -> list[_WriteEvidence]:
    module_index = {
        name: record
        for name, record in build_module_index(product.import_root).items()
        if name == "src" or name.startswith("src.")
    }
    module_names = sorted(module_index)
    parsed_trees = {}
    scopes = []
    file_uses = []

    for module_name in module_names:
        tree = parse_python_file(module_index[module_name].path)
        parsed_trees[module_name] = tree
        module_scopes = extract_scopes(module_name, tree)
        module_uses, _unresolved = extract_file_uses(module_name, tree, module_scopes)
        scopes.extend(module_scopes)
        file_uses.extend(module_uses)

    path_constants = build_path_constant_map(module_index, [], module_names, product.import_root)
    local_aliases = build_local_path_alias_map(module_index, module_names, scopes, path_constants)
    families, evidence = normalise_file_families(file_uses, path_constants, local_aliases)
    family_pattern_by_id = {family.family_id: family.family_pattern for family in families}
    use_by_evidence_key = {
        (use.module, use.scope_name, use.line, use.action, use.raw_expression): use
        for use in file_uses
    }

    writes: list[_WriteEvidence] = []
    for row in evidence:
        if row.action not in WRITE_ACTIONS:
            continue
        use = use_by_evidence_key.get((row.module, row.scope_name, row.line, row.action, row.raw_expression))
        writes.append(
            _WriteEvidence(
                module=row.module,
                scope=row.scope_name,
                line=row.line,
                action=row.action,
                raw_expression=row.raw_expression,
                write_pattern=family_pattern_by_id.get(row.family_id, row.resolved_expression),
                reason=use.reason if use is not None else row.reason,
            )
        )
    return writes


def _producer_matches(
    item: InputWorklistRecord,
    writes: list[_WriteEvidence],
) -> list[ProducerSearchRecord]:
    rows: list[ProducerSearchRecord] = []
    for write in writes:
        match_kind = _match_kind(item.input_pattern, write.write_pattern)
        if match_kind == "":
            continue
        rows.append(
            ProducerSearchRecord(
                input_id=item.input_id,
                input_pattern=item.input_pattern,
                candidate_producer_module=write.module,
                candidate_producer_scope=write.scope,
                candidate_line=write.line,
                write_pattern=write.write_pattern,
                match_kind=match_kind,
                confidence=_confidence(match_kind),
                write_action=write.action,
                raw_expression=write.raw_expression,
                reason=write.reason,
            )
        )
    return sorted(rows, key=lambda row: (row.match_kind, row.candidate_producer_module, row.candidate_line))


def _textual_producer_matches(
    product: Product,
    item: InputWorklistRecord,
    writes: list[_WriteEvidence],
) -> list[ProducerSearchRecord]:
    terms = _search_terms(item.input_pattern)
    if not terms:
        return []

    module_index = {
        name: record
        for name, record in build_module_index(product.import_root).items()
        if name == "src" or name.startswith("src.")
    }
    writes_by_module: dict[str, list[_WriteEvidence]] = {}
    for write in writes:
        writes_by_module.setdefault(write.module, []).append(write)

    rows: list[ProducerSearchRecord] = []
    for module_name in sorted(writes_by_module):
        module_record = module_index.get(module_name)
        if module_record is None:
            continue
        text = Path(module_record.path).read_text(encoding="utf-8", errors="replace")
        line = _first_term_line(text, terms)
        if line == 0:
            continue
        representative_write = writes_by_module[module_name][0]
        rows.append(
            ProducerSearchRecord(
                input_id=item.input_id,
                input_pattern=item.input_pattern,
                candidate_producer_module=module_name,
                candidate_producer_scope=representative_write.scope,
                candidate_line=line,
                write_pattern=representative_write.write_pattern,
                match_kind="textual_fragment_in_write_module",
                confidence="low",
                write_action=representative_write.action,
                raw_expression=representative_write.raw_expression,
                reason=f"module_has_write_and_mentions:{';'.join(terms)}",
            )
        )
    return rows[:12]


def _match_kind(input_pattern: str, write_pattern: str) -> str:
    input_pattern = _normalise_pattern(input_pattern)
    write_pattern = _normalise_pattern(write_pattern)
    if input_pattern == write_pattern:
        return "exact"
    if _abstract_pattern(input_pattern) == _abstract_pattern(write_pattern):
        return "same_template_shape"
    if _glob_covers(input_pattern, write_pattern):
        return "input_glob_covers_write"
    if _glob_covers(write_pattern, input_pattern):
        return "write_glob_covers_input"
    return ""


def _normalise_pattern(pattern: str) -> str:
    return pattern.replace("\\", "/").strip()


def _abstract_pattern(pattern: str) -> str:
    pattern = re.sub(r"\{[^}/]+\}", "*", pattern)
    return pattern


def _glob_covers(glob_pattern: str, candidate: str) -> bool:
    if "*" not in glob_pattern:
        return False
    regex = re.escape(_abstract_pattern(glob_pattern))
    regex = regex.replace(r"\*\*", ".*")
    regex = regex.replace(r"\*", "[^/]*")
    return re.fullmatch(regex, _abstract_pattern(candidate)) is not None


def _confidence(match_kind: str) -> str:
    if match_kind == "exact":
        return "high"
    return "medium"


def _search_terms(input_pattern: str) -> list[str]:
    generic = {
        "files",
        "output",
        "data",
        "site",
        "config",
        "latest",
        "publisher",
        "html",
        "json",
        "csv",
        "pmf",
        "cdf",
    }
    chunks = re.split(r"[^A-Za-z0-9_]+", input_pattern)
    terms = []
    for chunk in chunks:
        term = chunk.strip("_").lower()
        if len(term) < 3 or term in generic or term.isdigit():
            continue
        if term not in terms:
            terms.append(term)
    return terms[:6]


def _first_term_line(text: str, terms: list[str]) -> int:
    lowered_terms = [term.lower() for term in terms]
    for index, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if any(term in lowered for term in lowered_terms):
            return index
    return 0


def _action_result(matches: list[ProducerSearchRecord]) -> str:
    if matches:
        if all(row.confidence == "low" for row in matches):
            return "low_confidence_producer_candidate_found"
        return "producer_candidate_found"
    return "no_producer_candidate_found"


def _action_record(
    item: InputWorklistRecord,
    handler: str,
    action: str,
    result: str,
    reason: str,
) -> InputActionRecord:
    return InputActionRecord(
        input_id=item.input_id,
        input_pattern=item.input_pattern,
        needed_by_product=item.needed_by_product,
        status=item.status,
        action=action,
        handler=handler,
        action_result=result,
        reason=reason,
    )


def _resolution_record(
    item: InputWorklistRecord,
    matches: list[ProducerSearchRecord],
) -> InputResolutionRecord:
    modules = sorted({row.candidate_producer_module for row in matches})
    if matches:
        if all(row.confidence == "low" for row in matches):
            resolution = "low_confidence_producer_candidate_found"
            next_action = "review_textual_candidate_before_adding_product"
            reason = "low_confidence_textual_candidate_found"
        else:
            resolution = "producer_candidate_found"
            next_action = "review_candidate_producer_and_add_product_if_valid"
            reason = "static_write_family_match_found"
        return InputResolutionRecord(
            input_id=item.input_id,
            input_pattern=item.input_pattern,
            needed_by_product=item.needed_by_product,
            status=item.status,
            resolution=resolution,
            candidate_count=len(matches),
            candidate_producer_modules=";".join(modules),
            next_action=next_action,
            reason=reason,
        )
    return InputResolutionRecord(
        input_id=item.input_id,
        input_pattern=item.input_pattern,
        needed_by_product=item.needed_by_product,
        status=item.status,
        resolution="no_producer_candidate_found",
        candidate_count=0,
        candidate_producer_modules="",
        next_action="include_input_or_declare_manual_product",
        reason="no_static_write_family_match_found",
    )

from __future__ import annotations

import hashlib
import re
from collections import defaultdict

from .models import FileFamilyEvidenceRecord, FileFamilyRecord, FileUseRecord

_QUOTED_STRING = re.compile(r"^(['\"])(.*)\1$")
_INTEGER = re.compile(r"\b\d+\b")
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_OS_PATH_JOIN = re.compile(r"^os\.path\.join\((.*)\)$")
_PATH_GLOB = re.compile(r"^(.+)\.glob\((['\"])(.*)\2\)$")
_PATH_RGLOB = re.compile(r"^(.+)\.rglob\((['\"])(.*)\2\)$")


def normalise_file_families(
    file_uses: list[FileUseRecord],
) -> tuple[list[FileFamilyRecord], list[FileFamilyEvidenceRecord]]:
    evidence: list[FileFamilyEvidenceRecord] = []
    for use in file_uses:
        pattern = _family_pattern(use)
        family_id = _family_id(pattern)
        evidence.append(
            FileFamilyEvidenceRecord(
                family_id=family_id,
                module=use.module,
                scope_kind=use.scope_kind,
                scope_name=use.scope_name,
                line=use.line,
                action=use.action,
                raw_expression=use.raw_expression,
                resolved_expression=use.resolved_expression,
                reason=use.reason,
            )
        )

    families = _families_from_evidence(file_uses, evidence)
    return families, evidence


def _families_from_evidence(
    file_uses: list[FileUseRecord],
    evidence: list[FileFamilyEvidenceRecord],
) -> list[FileFamilyRecord]:
    uses_by_id: dict[str, list[FileUseRecord]] = defaultdict(list)
    evidence_by_id: dict[str, list[FileFamilyEvidenceRecord]] = defaultdict(list)

    for use, evidence_record in zip(file_uses, evidence, strict=True):
        uses_by_id[evidence_record.family_id].append(use)
        evidence_by_id[evidence_record.family_id].append(evidence_record)

    records: list[FileFamilyRecord] = []
    for family_id in sorted(evidence_by_id):
        family_evidence = evidence_by_id[family_id]
        family_uses = uses_by_id[family_id]
        first = family_evidence[0]
        pattern = _family_pattern(family_uses[0])
        records.append(
            FileFamilyRecord(
                family_id=family_id,
                family_kind=_family_kind(pattern, family_uses),
                family_pattern=pattern,
                actions=";".join(sorted({row.action for row in family_evidence})),
                evidence_count=len(family_evidence),
                modules=";".join(sorted({row.module for row in family_evidence})),
                first_module=first.module,
                first_scope=first.scope_name,
                first_line=first.line,
                confidence=_family_confidence(pattern),
                reason="normalised_from_file_uses",
            )
        )
    return records


def _family_pattern(use: FileUseRecord) -> str:
    expression = use.resolved_expression or use.raw_expression
    expression = expression.strip()
    expression = _strip_quotes(expression)
    expression = expression.replace("\\", "/")
    expression = _normalise_path_glob(expression)
    expression = _normalise_path_rglob(expression)
    expression = _normalise_os_path_join(expression)
    expression = _normalise_join_operator(expression)
    expression = _normalise_numeric_ids(expression)
    expression = _qualify_simple_local_name(use, expression)
    return expression


def _family_kind(pattern: str, uses: list[FileUseRecord]) -> str:
    if pattern.startswith("http://") or pattern.startswith("https://"):
        return "url_family"
    if any(use.action == "may_read_environment" for use in uses):
        return "environment_setting"
    if any("glob" in use.reason for use in uses):
        return "glob_family"
    if "*" in pattern:
        return "glob_family"
    if "{" in pattern and "}" in pattern:
        return "template_family"
    if pattern.endswith("/") or pattern.endswith("/**"):
        return "directory_family"
    return "file_or_expression_family"


def _family_confidence(pattern: str) -> str:
    if pattern == "":
        return "low"
    if "(" in pattern or ")" in pattern:
        return "low"
    if "{" in pattern and "}" in pattern:
        return "medium"
    return "medium"


def _family_id(pattern: str) -> str:
    digest = hashlib.sha1(pattern.encode("utf-8")).hexdigest()[:12]
    return f"ff_{digest}"


def _strip_quotes(expression: str) -> str:
    match = _QUOTED_STRING.match(expression)
    if match is None:
        return expression
    return match.group(2)


def _normalise_path_glob(expression: str) -> str:
    match = _PATH_GLOB.match(expression)
    if match is None:
        return expression
    base = match.group(1)
    pattern = match.group(3)
    return f"{base}/{pattern}"


def _normalise_path_rglob(expression: str) -> str:
    match = _PATH_RGLOB.match(expression)
    if match is None:
        return expression
    base = match.group(1)
    pattern = match.group(3)
    return f"{base}/**/{pattern}"


def _normalise_os_path_join(expression: str) -> str:
    match = _OS_PATH_JOIN.match(expression)
    if match is None:
        return expression
    parts = [_strip_quotes(part.strip()) for part in match.group(1).split(",")]
    return "/".join(part for part in parts if part)


def _normalise_join_operator(expression: str) -> str:
    return expression.replace(" / ", "/")


def _normalise_numeric_ids(expression: str) -> str:
    return _INTEGER.sub("{int}", expression)


def _qualify_simple_local_name(use: FileUseRecord, expression: str) -> str:
    if not _IDENTIFIER.match(expression):
        return expression
    if expression.isupper():
        return expression
    return f"{use.module}:{use.scope_name}:{expression}"

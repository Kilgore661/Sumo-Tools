from __future__ import annotations

from .models import FieldFactRecord, FileUseRecord, FileUseResolutionRecord


def resolve_file_uses(
    file_uses: list[FileUseRecord],
    field_facts: list[FieldFactRecord],
) -> list[FileUseResolutionRecord]:
    field_by_location = _field_facts_by_location(field_facts)
    resolutions: list[FileUseResolutionRecord] = []
    for file_use in file_uses:
        field_fact = field_by_location.get(
            (
                file_use.module,
                file_use.scope_name,
                file_use.line,
                file_use.resolved_expression,
            )
        )
        if field_fact is None:
            continue
        resolutions.append(
            FileUseResolutionRecord(
                module=file_use.module,
                scope_kind=file_use.scope_kind,
                scope_name=file_use.scope_name,
                line=file_use.line,
                action=file_use.action,
                raw_expression=file_use.raw_expression,
                resolved_expression=file_use.resolved_expression,
                resolution_kind="typed_dataclass_field",
                resolved_owner_type=field_fact.receiver_type,
                resolved_field_name=field_fact.field_name,
                resolved_field_annotation=field_fact.field_annotation,
                reason="file_use_expression_matches_field_fact",
            )
        )
    return resolutions


def _field_facts_by_location(
    field_facts: list[FieldFactRecord],
) -> dict[tuple[str, str, int, str], FieldFactRecord]:
    index: dict[tuple[str, str, int, str], FieldFactRecord] = {}
    for fact in field_facts:
        key = (fact.module, fact.scope_name, fact.line, fact.expression)
        index[key] = fact
    return index

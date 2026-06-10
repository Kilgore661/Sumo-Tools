from __future__ import annotations

from dataclasses import dataclass

from .models import ReviewCandidateRecord


@dataclass(frozen=True)
class ExecutionReviewCandidateRecord:
    family_id: str
    family_pattern: str
    classification: str
    distribution_decision: str
    review_priority: str
    classification_reason: str
    first_module: str
    first_scope: str
    first_line: int
    first_resolved_expression: str
    execution_status: str
    execution_depth: str
    execution_reason: str


def build_execution_review_candidates(
    review_candidates: list[ReviewCandidateRecord],
    execution_call_slice: list[object],
) -> list[ExecutionReviewCandidateRecord]:
    reachable = _reachable_functions(execution_call_slice)
    rows: list[ExecutionReviewCandidateRecord] = []
    for row in review_candidates:
        function_name = _function_full_name(row.first_module, row.first_scope)
        depth = reachable.get(function_name)
        if row.first_scope == "<module>":
            execution_status = "module_level"
            execution_depth = ""
            execution_reason = "module_level_file_use_not_call_scoped"
        elif depth is None:
            execution_status = "not_in_execution_slice"
            execution_depth = ""
            execution_reason = "first_scope_not_reached_by_project_call_slice"
        else:
            execution_status = "execution_reachable"
            execution_depth = str(depth)
            execution_reason = "first_scope_reached_by_project_call_slice"
        rows.append(
            ExecutionReviewCandidateRecord(
                family_id=row.family_id,
                family_pattern=row.family_pattern,
                classification=row.classification,
                distribution_decision=row.distribution_decision,
                review_priority=row.review_priority,
                classification_reason=row.classification_reason,
                first_module=row.first_module,
                first_scope=row.first_scope,
                first_line=row.first_line,
                first_resolved_expression=row.first_resolved_expression,
                execution_status=execution_status,
                execution_depth=execution_depth,
                execution_reason=execution_reason,
            )
        )
    return sorted(rows, key=lambda item: (item.review_priority, item.execution_status, item.family_pattern))


def _reachable_functions(execution_call_slice: list[object]) -> dict[str, int]:
    reachable: dict[str, int] = {}
    for row in execution_call_slice:
        caller = getattr(row, "caller_full_name", "")
        callee = getattr(row, "callee_full_name", "")
        depth = int(getattr(row, "depth", 0))
        if caller:
            reachable[caller] = min(depth, reachable.get(caller, depth))
        if callee:
            reachable[callee] = min(depth + 1, reachable.get(callee, depth + 1))
    return reachable


def _function_full_name(module: str, scope: str) -> str:
    return f"{module}.{scope}"

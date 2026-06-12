from __future__ import annotations

from dataclasses import dataclass
from collections import deque

PROJECT_RESOLUTION_KINDS = {
    "from_import",
    "same_module_definition",
    "imported_attribute",
    "current_class_method",
}


@dataclass(frozen=True)
class ExecutionCallRecord:
    caller_full_name: str
    caller_module: str
    caller_scope: str
    call_line: int
    callee_expression: str
    callee_full_name: str
    resolution_kind: str
    reason: str
    depth: int


def derive_execution_call_slice(root_module: str, call_edges: list[object]) -> list[ExecutionCallRecord]:
    edges_by_caller = _edges_by_caller(call_edges)
    seeds = [f"{root_module}.<module>", f"{root_module}.main"]
    queue: deque[tuple[str, int]] = deque((seed, 0) for seed in seeds)
    seen_callers: set[str] = set()
    emitted: list[ExecutionCallRecord] = []
    emitted_keys: set[tuple[str, int, str]] = set()

    while queue:
        caller_full_name, depth = queue.popleft()
        if caller_full_name in seen_callers:
            continue
        seen_callers.add(caller_full_name)
        for edge in edges_by_caller.get(caller_full_name, ()): 
            key = (caller_full_name, getattr(edge, "call_line"), getattr(edge, "callee_expression"))
            if key in emitted_keys:
                continue
            emitted_keys.add(key)
            record = ExecutionCallRecord(
                caller_full_name=caller_full_name,
                caller_module=getattr(edge, "caller_module"),
                caller_scope=getattr(edge, "caller_scope"),
                call_line=getattr(edge, "call_line"),
                callee_expression=getattr(edge, "callee_expression"),
                callee_full_name=getattr(edge, "callee_full_name"),
                resolution_kind=getattr(edge, "resolution_kind"),
                reason=getattr(edge, "reason"),
                depth=depth,
            )
            emitted.append(record)
            if _is_project_edge(edge):
                queue.append((getattr(edge, "callee_full_name"), depth + 1))
    return sorted(emitted, key=lambda row: (row.depth, row.caller_full_name, row.call_line, row.callee_expression))


def _edges_by_caller(call_edges: list[object]) -> dict[str, tuple[object, ...]]:
    grouped: dict[str, list[object]] = {}
    for edge in call_edges:
        caller = _caller_full_name(getattr(edge, "caller_module"), getattr(edge, "caller_scope"))
        grouped.setdefault(caller, []).append(edge)
    return {key: tuple(value) for key, value in grouped.items()}


def _caller_full_name(module: str, scope: str) -> str:
    return f"{module}.{scope}"


def _is_project_edge(edge: object) -> bool:
    return bool(getattr(edge, "callee_full_name")) and getattr(edge, "resolution_kind") in PROJECT_RESOLUTION_KINDS

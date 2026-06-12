from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FileEffectRootRecord:
    module: str
    scope: str
    line: int
    action: str
    direction: str
    path_pattern: str
    normalisation_status: str
    symbolic_source: str
    family_pattern: str
    root_pattern: str
    member_pattern: str
    shape: str
    confidence: str
    raw_expression: str
    reason: str


@dataclass(frozen=True)
class ModuleFileRootRecord:
    module: str
    direction: str
    root_pattern: str
    status: str
    confidence: str
    effect_count: int
    shapes: str
    actions: str
    reason: str

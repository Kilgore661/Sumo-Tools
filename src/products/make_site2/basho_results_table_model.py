"""Basho Results 7.1 presentation-model fork.

This module is intentionally separate from ``artifact_model.py`` while the
7.1 table redesign is developed. The existing shared table model remains the
prototype path for current pages; these types describe the new 7.1-specific
TableSpec / presentation-model path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SortDirection = Literal["ascending", "descending"]
TableValue = str | int | float | bool | None


@dataclass(frozen=True, kw_only=True)
class TableSpecColumn:
    key: str
    value_sort: str


@dataclass(frozen=True, kw_only=True)
class TableSpecGroup:
    key: str
    children: tuple["TableSpecNode", ...]


TableSpecNode = TableSpecColumn | TableSpecGroup


@dataclass(frozen=True, kw_only=True)
class TableHeader:
    heading: str
    subheading: str | None = None


@dataclass(frozen=True, kw_only=True)
class TableProjection:
    visible_paths: tuple[str, ...]


@dataclass(frozen=True, kw_only=True)
class TableSortSpec:
    path: str
    sort_kind: str = "text"
    default_direction: SortDirection | None = None


@dataclass(frozen=True, kw_only=True)
class BashoResultsPresentationModel:
    header: TableHeader | None
    table_spec: tuple[TableSpecNode, ...]
    values: tuple[dict[str, TableValue], ...]
    projection: TableProjection
    sort_specs: tuple[TableSortSpec, ...] = ()


def column(key: str, value_sort: str) -> TableSpecColumn:
    return TableSpecColumn(key=key, value_sort=value_sort)


def group(key: str, children: tuple[TableSpecNode, ...]) -> TableSpecGroup:
    if not children:
        raise ValueError("TableSpec groups must contain at least one child")
    return TableSpecGroup(key=key, children=children)


BASHO_RESULTS_TABLE_SPEC: tuple[TableSpecNode, ...] = (
    group(
        "reference",
        (
            column("row_number", "Int"),
            column("shikona", "String"),
        ),
    ),
    group(
        "before",
        (
            group(
                "rba",
                (
                    column("bp", "BP"),
                    group(
                        "result",
                        (
                            column("wins", "Int"),
                            column("losses", "Int"),
                            column("absences", "Int"),
                            column("prizes", "PrizeString"),
                            column("division_change", "DivisionChange"),
                        ),
                    ),
                    column("equelo", "Rating"),
                    group(
                        "rbbc",
                        (
                            group(
                                "banzuke_error",
                                (
                                    column("direction", "Direction"),
                                    column("magnitude", "Int"),
                                ),
                            ),
                            column("rbbp", "BP"),
                        ),
                    ),
                ),
            ),
        ),
    ),
    group(
        "state",
        (
            group(
                "rba",
                (
                    column("bp", "BP"),
                    group(
                        "result",
                        (
                            column("wins", "Int"),
                            column("losses", "Int"),
                            column("absences", "Int"),
                            column("prizes", "PrizeString"),
                            column("division_change", "DivisionChange"),
                        ),
                    ),
                    column("equelo", "Rating"),
                    group(
                        "rbbc",
                        (
                            group(
                                "banzuke_error",
                                (
                                    column("direction", "Direction"),
                                    column("magnitude", "Int"),
                                ),
                            ),
                            column("rbbp", "BP"),
                        ),
                    ),
                ),
            ),
        ),
    ),
    group(
        "comparison",
        (
            column("delta_equelo", "RatingDelta"),
        ),
    ),
)


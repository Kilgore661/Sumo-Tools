"""Semantic artifact model for make_site2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ArtifactKind = Literal["indexed_table", "chart"]


@dataclass(frozen=True, kw_only=True)
class IndexedDataSource:
    id: str
    label: str
    index_path: str
    payload_path_field: str
    payload_media_type: str


@dataclass(frozen=True, kw_only=True)
class DataSource:
    id: str
    label: str
    path: str
    media_type: str


@dataclass(frozen=True, kw_only=True)
class DataBinding:
    kind: str
    sources: tuple[str, ...]


@dataclass(frozen=True, kw_only=True)
class ColumnGroup:
    id: str
    heading: str
    columns: tuple[str, ...]
    always_visible: bool = False
    controlling_filter_id: str | None = None


@dataclass(frozen=True, kw_only=True)
class TableColumn:
    id: str
    heading: str
    source_field: str | None = None
    group: str | None = None
    always_visible: bool = False
    sort_key: str | None = None
    sort_kind: str = "text"
    align: str | None = None
    note_id: str | None = None


@dataclass(frozen=True, kw_only=True)
class Note:
    id: str
    applies_to: tuple[str, ...]
    text: str


@dataclass(frozen=True, kw_only=True)
class IndexedTableArtifact:
    id: str
    heading: str
    kind: ArtifactKind
    renderer: str
    indexed_source: IndexedDataSource
    selector_filter_id: str
    column_groups: tuple[ColumnGroup, ...]
    columns: tuple[TableColumn, ...]
    default_sort_column: str
    default_sort_descending: bool = False
    notes: tuple[Note, ...] = ()


@dataclass(frozen=True, kw_only=True)
class ChartArtifact:
    id: str
    heading: str
    kind: ArtifactKind
    renderer: str
    data_binding: DataBinding
    data_sources: tuple[DataSource, ...]
    notes: tuple[Note, ...] = ()

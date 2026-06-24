"""Semantic artifact model for make_site2."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from typing import Literal


ArtifactKind = Literal[
    "indexed_table",
    "sectioned_table",
    "table",
    "chart",
    "prose",
    "banzuke_changes",
    "standings",
]
SortDirection = Literal["ascending", "descending"]


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
class ChartTrace:
    id: str
    label: str
    kind: str
    x: str
    y: str
    group_by: str | None = None
    error_y: tuple[str, str] | None = None


@dataclass(frozen=True, kw_only=True)
class ChartAxis:
    id: str
    source_field: str
    label: str
    help: str = ""
    order_values: tuple[str, ...] = ()
    minimum: float | None = None
    maximum: float | None = None
    tickformat: str | None = None


@dataclass(frozen=True, kw_only=True)
class ColumnGroup:
    id: str
    heading: str
    columns: tuple[str, ...]
    help: str = ""
    always_visible: bool = False
    controlling_filter_id: str | None = None


@dataclass(frozen=True, kw_only=True)
class TableColumn:
    id: str
    heading: str
    source_field: str | None = None
    group: str | None = None
    help: str = ""
    always_visible: bool = False
    sort_key: str | None = None
    sort_kind: str = "text"
    sort_default_direction: SortDirection | None = None
    align: str | None = None
    note_id: str | None = None


@dataclass(frozen=True, kw_only=True)
class TableSection:
    id: str
    heading: str
    source_field: str
    source_value: str
    order_by: str


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
class SectionedTableArtifact:
    id: str
    heading: str
    kind: ArtifactKind
    renderer: str
    primary_source: str
    data_sources: tuple[DataSource, ...]
    sections: tuple[TableSection, ...]
    columns: tuple[TableColumn, ...]
    notes: tuple[Note, ...] = ()


@dataclass(frozen=True, kw_only=True)
class TableArtifact:
    id: str
    heading: str
    kind: ArtifactKind
    renderer: str
    rows_source: DataSource
    columns: tuple[TableColumn, ...]
    default_sort_column: str
    default_sort_descending: bool = False
    notes: tuple[Note, ...] = ()


@dataclass(frozen=True, kw_only=True)
class BanzukeChangesArtifact:
    id: str
    heading: str
    kind: ArtifactKind
    renderer: str
    config_source: DataSource
    rows_source: DataSource
    notes: tuple[Note, ...] = ()


@dataclass(frozen=True, kw_only=True)
class SelectedTableDataSource:
    id: str
    label: str
    filter_value: str
    path: str
    metadata_path: str
    media_type: str


@dataclass(frozen=True, kw_only=True)
class StandingsArtifact:
    id: str
    heading: str
    kind: ArtifactKind
    renderer: str
    selector_filter_id: str
    config_source: DataSource
    data_sources: tuple[SelectedTableDataSource, ...]
    column_groups: tuple[ColumnGroup, ...]
    columns: tuple[TableColumn, ...]
    notes: tuple[Note, ...] = ()


@dataclass(frozen=True, kw_only=True)
class ChartArtifact:
    id: str
    heading: str
    kind: ArtifactKind
    renderer: str
    data_binding: DataBinding
    data_sources: tuple[DataSource, ...]
    traces: tuple[ChartTrace, ...] = ()
    x_axis: ChartAxis | None = None
    y_axis: ChartAxis | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    notes: tuple[Note, ...] = ()


@dataclass(frozen=True, kw_only=True)
class ProseArtifact:
    id: str
    heading: str
    kind: ArtifactKind
    renderer: str
    path: str
    notes: tuple[Note, ...] = ()

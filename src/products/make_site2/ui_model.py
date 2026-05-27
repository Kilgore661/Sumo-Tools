"""Semantic UI model for make_site2.

This is the layer make_site2 exists to make explicit. Renderers consume these
objects; they do not decide what public pages, filters, panels, or artifacts are.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .publication_model import NavigationItem


ControlKind = Literal["select", "checkbox"]


@dataclass(frozen=True, kw_only=True)
class NavigationCollapseControl:
    enabled: bool
    storage_key: str


@dataclass(frozen=True, kw_only=True)
class NavigationQuickLink:
    label: str
    page_id: str
    href: str


@dataclass(frozen=True, kw_only=True)
class NavigationBar:
    heading: str
    quick_links: tuple[NavigationQuickLink, ...]
    navigation_tree: tuple[NavigationItem, ...]
    collapse_control: NavigationCollapseControl


@dataclass(frozen=True, kw_only=True)
class FilterValue:
    value: str
    label: str


@dataclass(frozen=True, kw_only=True)
class FilterValuesSource:
    source: str
    field: str
    label_field: str
    order_field: str
    partition_filter: str | None = None
    partition_field: str | None = None
    partition_normalizer: str | None = None


@dataclass(frozen=True, kw_only=True)
class Filter:
    id: str
    label: str
    control: ControlKind
    default: str | bool
    url_key: str
    values: tuple[FilterValue, ...] = ()
    values_source: FilterValuesSource | None = None


@dataclass(frozen=True, kw_only=True)
class FilterSection:
    filters: tuple[Filter, ...]


@dataclass(frozen=True, kw_only=True)
class PA:
    artifact_id: str


@dataclass(frozen=True, kw_only=True)
class Notes:
    note_ids: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class PAPanel:
    pa: PA
    notes: Notes


@dataclass(frozen=True, kw_only=True)
class Contents:
    filter_section: FilterSection | None
    pa_panel: PAPanel


@dataclass(frozen=True, kw_only=True)
class Heading:
    title: str
    summary: str


@dataclass(frozen=True, kw_only=True)
class ContentPanel:
    page_id: str
    heading: Heading
    contents: Contents


@dataclass(frozen=True, kw_only=True)
class PublicSiteShell:
    navigation_bar: NavigationBar
    content_panels: tuple[ContentPanel, ...]

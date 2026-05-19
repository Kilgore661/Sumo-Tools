"""Semantic UI model for make_site2.

This is the layer make_site2 exists to make explicit. Renderers consume these
objects; they do not decide what public pages, filters, panels, or artifacts are.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .publication_model import NavigationItem


ControlKind = Literal["select", "checkbox", "basho_date_selector"]
ContentGrammar = Literal["G1"]


@dataclass(frozen=True, kw_only=True)
class NavigationCollapseControl:
    enabled: bool
    storage_key: str


@dataclass(frozen=True, kw_only=True)
class NavigationBar:
    heading: str
    navigation_tree: tuple[NavigationItem, ...]
    collapse_control: NavigationCollapseControl


@dataclass(frozen=True, kw_only=True)
class FilterValue:
    value: str
    label: str


@dataclass(frozen=True, kw_only=True)
class Filter:
    id: str
    label: str
    control: ControlKind
    default: str | bool
    url_key: str
    values: tuple[FilterValue, ...] = ()


@dataclass(frozen=True, kw_only=True)
class FilterSection:
    filters: tuple[Filter, ...]


@dataclass(frozen=True, kw_only=True)
class PA:
    artifact_id: str


@dataclass(frozen=True, kw_only=True)
class G1Contents:
    filter_section: FilterSection
    pa: PA
    note_ids: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class Heading:
    title: str
    summary: str


@dataclass(frozen=True, kw_only=True)
class ContentPanel:
    page_id: str
    heading: Heading
    grammar: ContentGrammar
    contents: G1Contents


@dataclass(frozen=True, kw_only=True)
class PublicSiteShell:
    navigation_bar: NavigationBar
    content_panels: tuple[ContentPanel, ...]

"""Top-level public site model sorts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .file_refs import AssetRef, DataRef
from .page_parts import OptionsModel, ViewSpec


@dataclass(frozen=True, kw_only=True)
class SiteBuildConfig:
    """Build/deploy context for a generated site."""

    base_route: str
    output_root: Path


@dataclass(frozen=True)
class NavigationTree:
    """Recursive subject-led navigation tree."""

    id: str
    label: str
    slug: str
    children: tuple["NavigationTree", ...] = ()
    page_id: str | None = None


@dataclass(frozen=True, kw_only=True)
class Page:
    """Renderable page known to the public site."""

    id: str
    title: str
    slug: str
    summary: str
    view: ViewSpec
    options: OptionsModel | None = None
    assets: tuple[AssetRef, ...] = ()
    data: tuple[DataRef, ...] = ()


@dataclass(frozen=True, kw_only=True)
class PageRegistry:
    """Finite mapping from page ids to pages."""

    pages: Mapping[str, Page]


@dataclass(frozen=True, kw_only=True)
class Site:
    """Conceptual public site definition."""

    id: str
    title: str
    navigation: NavigationTree
    pages: PageRegistry
    global_assets: tuple[AssetRef, ...] = ()

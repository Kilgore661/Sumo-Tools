"""BRB-first static shell builder for make_site2."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, is_dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from src.products.make_site.pa_manifest.chart_instances import division_stability
from src.products.make_site.pa_manifest.table_instances import (
    basho_results_browser,
    standings_by_wins,
)
from src.products.make_site.site_config import (
    BASHO_RESULTS_OUTPUT_ROOT,
    DIVISION_STABILITY_SITE_BUNDLE,
    OUTPUT_ROOT,
    STANDINGS_PUBLISHER_DATA,
)


DEFAULT_OUTPUT_ROOT = OUTPUT_ROOT / "make_site2"
PACKAGE_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = PACKAGE_ROOT / "runtime"


def build_brb_shell(output_root: Path = DEFAULT_OUTPUT_ROOT) -> None:
    """Build the first make_site2 vertical slice: BRB in a direct shell."""

    clear_dir(output_root)
    write_index(output_root)
    write_manifests(output_root)
    copy_brb_data(output_root)
    copy_division_stability_data(output_root)
    copy_standings_data(output_root)
    copy_career_length_data(output_root)
    copy_finish_by_chii_data(output_root)
    copy_runtime(output_root)


def write_index(output_root: Path) -> None:
    build_stamp = datetime.now().strftime("Generated %Y-%m-%d %H:%M")
    html = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<link rel="stylesheet" href="runtime/make_site2.css">',
            "<title>Gaspode-san's Sumo Lab: make_site2</title>",
            "</head>",
            "<body>",
            '<div class="site-shell">',
            '<aside class="site-nav" aria-label="Site navigation">',
            '<header class="site-brand">',
            "<h1>Gaspode-san's Sumo Lab</h1>",
            f'<p>{escape(build_stamp)}</p>',
            "</header>",
            '<ol class="nav-tree">',
            '<li><span>Sumo History</span>',
            "<ol>",
            (
                '<li><a href="#page=basho_results_browser" class="nav-link" '
                'data-page-id="basho_results_browser">7.1 Basho Results</a></li>'
            ),
            (
                '<li><a href="#page=division_stability" class="nav-link" '
                'data-page-id="division_stability">Division Stability</a></li>'
            ),
            (
                '<li><a href="#page=standings_by_wins" class="nav-link" '
                'data-page-id="standings_by_wins">Standings by Wins</a></li>'
            ),
            (
                '<li><a href="#page=career_length" class="nav-link" '
                'data-page-id="career_length">Career Length</a></li>'
            ),
            (
                '<li><a href="#page=finish_by_chii" class="nav-link" '
                'data-page-id="finish_by_chii">Finish by Chii</a></li>'
            ),
            "</ol>",
            "</li>",
            "</ol>",
            "</aside>",
            '<main class="content-panel" id="content-panel">',
            '<header class="content-heading">',
            '<p class="eyebrow">make_site2</p>',
            '<h2 id="page-title">Select a page</h2>',
            '<p id="page-summary">Choose a navigation item to render it directly in this panel.</p>',
            "</header>",
            '<section id="filter-section" class="filter-section" aria-label="Filters"></section>',
            '<section id="pa-section" class="pa-section" aria-live="polite"></section>',
            '<section id="notes-section" class="notes-section" aria-label="Notes"></section>',
            "</main>",
            "</div>",
            '<script src="runtime/make_site2.js"></script>',
            "</body>",
            "</html>",
            "",
        )
    )
    (output_root / "index.html").write_text(html, encoding="utf-8")


def write_manifests(output_root: Path) -> None:
    manifest_dir = output_root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / "basho_results_browser.json").write_text(
        json.dumps(brb_envelope(), indent=2),
        encoding="utf-8",
    )
    (manifest_dir / "division_stability.json").write_text(
        json.dumps(division_stability_envelope(), indent=2),
        encoding="utf-8",
    )
    (manifest_dir / "standings_by_wins.json").write_text(
        json.dumps(standings_by_wins_envelope(), indent=2),
        encoding="utf-8",
    )
    (manifest_dir / "career_length.json").write_text(
        json.dumps(career_length_envelope(), indent=2),
        encoding="utf-8",
    )
    (manifest_dir / "finish_by_chii.json").write_text(
        json.dumps(finish_by_chii_envelope(), indent=2),
        encoding="utf-8",
    )
    (output_root / "manifest-index.json").write_text(
        json.dumps(
            {
                "basho_results_browser": "manifests/basho_results_browser.json",
                "division_stability": "manifests/division_stability.json",
                "standings_by_wins": "manifests/standings_by_wins.json",
                "career_length": "manifests/career_length.json",
                "finish_by_chii": "manifests/finish_by_chii.json",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def brb_envelope() -> dict[str, Any]:
    return {
        "page": {
            "id": "basho_results_browser",
            "title": "Basho Results",
            "summary": "Historical and current basho results by division.",
            "status": "promoted",
        },
        "contentPanel": {
            "heading": {
                "title": "Basho Results",
                "summary": "Historical and current basho results by division.",
            },
            "contents": {
                "grammar": "G1",
                "filters": manifest_filters(),
                "pas": [
                    {
                        "id": "basho_results_table",
                        "title": "Basho Results table",
                        "artifact": {
                            "kind": "indexed_table",
                            "renderer": basho_results_browser.renderer,
                            "indexedSource": plain(
                                basho_results_browser.indexed_source
                            ),
                            "selectorFilter": basho_results_browser.selector_option,
                            "columnGroups": plain(
                                basho_results_browser.column_groups
                            ),
                            "columns": plain(basho_results_browser.columns),
                            "defaultSort": plain(
                                basho_results_browser.default_sort
                            ),
                        },
                    }
                ],
                "notes": plain(basho_results_browser.notes),
            },
        },
    }


def division_stability_envelope() -> dict[str, Any]:
    return {
        "page": {
            "id": "division_stability",
            "title": "Division Stability",
            "summary": "Historical continuity within divisions.",
            "status": "prototype",
        },
        "contentPanel": {
            "heading": {
                "title": "Division Stability",
                "summary": "Historical continuity within divisions.",
            },
            "contents": {
                "grammar": "G1",
                "filters": manifest_filters_for(division_stability.options),
                "pas": [
                    {
                        "id": "division_stability_chart",
                        "title": "Division Stability chart",
                        "artifact": {
                            "kind": "chart",
                            "renderer": division_stability.renderer,
                            "dataSources": [
                                {
                                    **plain(division_stability.data_sources[0]),
                                    "path": "data/division-stability/persistence.csv",
                                }
                            ],
                            "primarySource": division_stability.primary_source,
                            "traces": plain(division_stability.traces),
                            "xAxis": plain(division_stability.x_axis),
                            "yAxis": plain(division_stability.y_axis),
                            "defaultTrace": division_stability.default_trace,
                            "provenance": plain(division_stability.provenance),
                        },
                    }
                ],
                "notes": [],
            },
        },
    }


def standings_by_wins_envelope() -> dict[str, Any]:
    return {
        "page": {
            "id": "standings_by_wins",
            "title": "Standings by Wins",
            "summary": "Rolling recent-performance standings by wins.",
            "status": "prototype",
        },
        "contentPanel": {
            "heading": {
                "title": "Standings by Wins",
                "summary": "Rolling recent-performance standings by wins.",
            },
            "contents": {
                "grammar": "G1",
                "filters": manifest_filters_for(standings_by_wins.options),
                "pas": [
                    {
                        "id": "standings_by_wins_table",
                        "title": "Standings by Wins table",
                        "artifact": {
                            "kind": "table",
                            "renderer": standings_by_wins.renderer,
                            "dataSources": standings_data_sources(),
                            "primarySource": standings_by_wins.primary_source,
                            "columnGroups": plain(standings_by_wins.column_groups),
                            "columns": plain(standings_by_wins.columns),
                            "groupVisibilityPresets": plain(
                                standings_by_wins.group_visibility_presets
                            ),
                            "defaultSort": plain(standings_by_wins.default_sort),
                        },
                    }
                ],
                "notes": plain(standings_by_wins.notes),
            },
        },
    }


def standings_data_sources() -> list[dict[str, Any]]:
    result = []
    for source in standings_by_wins.data_sources:
        item = plain(source)
        item["path"] = f"data/standings/{Path(source.path).name}"
        if source.metadata_path is not None:
            item["metadata_path"] = f"data/standings/{Path(source.metadata_path).name}"
        result.append(item)
    return result


def career_length_envelope() -> dict[str, Any]:
    return {
        "page": {
            "id": "career_length",
            "title": "Career Length",
            "summary": "Observed rikishi career lengths from banzuke appearances.",
            "status": "prototype",
        },
        "contentPanel": {
            "heading": {
                "title": "Career Length",
                "summary": "Observed rikishi career lengths from banzuke appearances.",
            },
            "contents": {
                "grammar": "G2b",
                "branchSelector": {
                    "id": "branch",
                    "label": "Show",
                    "kind": "enum",
                    "control": "radio_group",
                    "default": "chart",
                    "url_key": "branch",
                    "model": "branchSelector",
                    "values": [
                        {"value": "chart", "label": "Chart"},
                        {"value": "table", "label": "Table"},
                    ],
                },
                "branches": [
                    {
                        "id": "chart",
                        "tag": "Chart",
                        "filters": [
                            {
                                "id": "chart",
                                "label": "Chart",
                                "kind": "enum",
                                "control": "radio_group",
                                "default": "distribution",
                                "url_key": "chart",
                                "model": "filter",
                                "values": [
                                    {"value": "distribution", "label": "Distribution"},
                                    {"value": "pmf", "label": "PMF"},
                                    {"value": "cdf", "label": "CDF"},
                                    {"value": "survival", "label": "Survival"},
                                ],
                            }
                        ],
                        "pa": {
                            "id": "career_length_chart",
                            "title": "Charts",
                            "artifact": {
                                "kind": "career_length_chart",
                                "renderer": "career_length_chart",
                                "dataSources": [
                                    career_length_source("distribution", "Distribution", "distribution.csv"),
                                    career_length_source("pmf", "PMF", "pmf.csv"),
                                    career_length_source("cdf", "CDF", "cdf.csv"),
                                    career_length_source("survival", "Survival", "survival.csv"),
                                ],
                            },
                        },
                    },
                    {
                        "id": "table",
                        "tag": "Table",
                        "filters": [
                            {
                                "id": "active",
                                "label": "Rikishi",
                                "kind": "enum",
                                "control": "radio_group",
                                "default": "all",
                                "url_key": "active",
                                "model": "filter",
                                "values": [
                                    {"value": "all", "label": "All rikishi"},
                                    {"value": "active", "label": "Active only"},
                                ],
                            }
                        ],
                        "pa": {
                            "id": "longest_careers",
                            "title": "Longest Careers",
                            "artifact": {
                                "kind": "table",
                                "renderer": "career_length_longest_table",
                                "dataSources": [
                                    career_length_source("longest", "Longest", "longest.csv"),
                                ],
                                "primarySource": "longest",
                                "columns": [
                                    table_column("rank", "#", "rank", align="right", sortable=False),
                                    table_column("shikona", "Shikona", "shikona", link="rikishi"),
                                    table_column("first_appearance", "First", "first_appearance"),
                                    table_column("last_appearance", "Last", "last_appearance"),
                                    table_column(
                                        "participation_years",
                                        "Years",
                                        "participation_years",
                                        formatter="decimal_2",
                                        sort_kind="numeric",
                                        align="right",
                                    ),
                                    table_column(
                                        "gap_basho_count",
                                        "Bg",
                                        "gap_basho_count",
                                        sort_kind="numeric",
                                        align="right",
                                        note="bg_count",
                                    ),
                                ],
                                "defaultSort": {
                                    "column": "participation_years",
                                    "descending": True,
                                    "role": None,
                                },
                            },
                        },
                    },
                ],
                "notes": [
                    {
                        "id": "bg_count",
                        "text": "<strong>Bg.</strong> The number of basho for which the rikishi was absent.",
                        "placement": "below_table",
                        "applies_to": ["branch:table"],
                        "format": "html",
                    }
                ],
            },
        },
    }


def career_length_source(id: str, label: str, filename: str) -> dict[str, str]:
    return {
        "id": id,
        "label": label,
        "path": f"data/career-length/{filename}",
        "media_type": "text/csv",
    }


def finish_by_chii_envelope() -> dict[str, Any]:
    return {
        "page": {
            "id": "finish_by_chii",
            "title": "Finish by Chii",
            "summary": "Finishing-position probabilities by starting Chii.",
            "status": "prototype",
        },
        "contentPanel": {
            "heading": {
                "title": "Finish by Chii",
                "summary": "Finishing-position probabilities by starting Chii.",
            },
            "contents": {
                "grammar": "G1",
                "filters": [
                    {
                        "id": "division",
                        "label": "Division",
                        "kind": "enum",
                        "control": "select",
                        "default": "makuuchi",
                        "url_key": "division",
                        "model": "filter",
                        "values": [
                            {"value": "makuuchi", "label": "Makuuchi"},
                            {"value": "juryo", "label": "Juryo"},
                        ],
                    },
                    {
                        "id": "direction",
                        "label": "Direction",
                        "kind": "enum",
                        "control": "radio_group",
                        "default": "top",
                        "url_key": "direction",
                        "model": "filter",
                        "values": [
                            {"value": "top", "label": "Top finish"},
                            {"value": "bottom", "label": "Bottom finish"},
                        ],
                    },
                    {
                        "id": "chii",
                        "label": "Chii",
                        "kind": "enum",
                        "control": "select",
                        "default": "Y1e",
                        "url_key": "chii",
                        "model": "filter",
                        "values": [{"value": "Y1e", "label": "Y1e"}],
                    },
                ],
                "pas": [
                    {
                        "id": "finish_by_chii_chart",
                        "title": "Finish by Chii chart",
                        "artifact": {
                            "kind": "chart",
                            "renderer": "finish_by_chii_chart",
                            "dataSources": [
                                finish_by_chii_source(
                                    "top",
                                    "Top finish",
                                    "finish_by_chii_1958_2026_top_thresholds.csv",
                                ),
                                finish_by_chii_source(
                                    "bottom",
                                    "Bottom finish",
                                    "finish_by_chii_1958_2026_bottom_thresholds.csv",
                                ),
                            ],
                            "primarySource": "top",
                            "directionFilter": "direction",
                            "divisionFilter": "division",
                            "chiiFilter": "chii",
                        },
                    }
                ],
                "notes": [
                    {
                        "id": "finish_by_chii_scope",
                        "text": "This make_site2 slice covers the current item 5.1 standalone chart: threshold probabilities by division, direction, and Chii. The separate average-finish chart is not part of this first PA.",
                        "placement": "below_chart",
                        "applies_to": ["all"],
                        "format": "text",
                    }
                ],
            },
        },
    }


def finish_by_chii_source(id: str, label: str, filename: str) -> dict[str, str]:
    return {
        "id": id,
        "label": label,
        "path": f"data/finish-by-chii/{filename}",
        "media_type": "text/csv",
    }


def table_column(
    id: str,
    heading: str,
    source_field: str,
    *,
    align: str = "left",
    formatter: str | None = None,
    sort_kind: str = "auto",
    sortable: bool = True,
    note: str | None = None,
    link: str | None = None,
) -> dict[str, Any]:
    return {
        "id": id,
        "heading": heading,
        "source_field": source_field,
        "group": None,
        "sortable": sortable,
        "sort_key": None,
        "sort_kind": sort_kind,
        "formatter": formatter,
        "align": align,
        "always_visible": True,
        "note": note,
        "link": link,
    }


def manifest_filters() -> list[dict[str, Any]]:
    return manifest_filters_for(basho_results_browser.options)


def manifest_filters_for(options: Any) -> list[dict[str, Any]]:
    filters = []
    for option in options:
        item = plain(option)
        item["model"] = "filter"
        filters.append(item)
    return filters


def copy_brb_data(output_root: Path) -> None:
    data_root = output_root / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        BASHO_RESULTS_OUTPUT_ROOT / "basho_results_index.json",
        data_root / "basho_results_index.json",
    )
    source_payloads = BASHO_RESULTS_OUTPUT_ROOT / "by-basho"
    target_payloads = data_root / "by-basho"
    target_payloads.mkdir(parents=True, exist_ok=True)
    for source in source_payloads.glob("*.csv"):
        shutil.copy2(source, target_payloads / source.name)


def copy_division_stability_data(output_root: Path) -> None:
    data_root = output_root / "data" / "division-stability"
    data_root.mkdir(parents=True, exist_ok=True)
    for name in ("persistence.csv", "metadata.json", "page.json"):
        shutil.copy2(DIVISION_STABILITY_SITE_BUNDLE / name, data_root / name)


def copy_standings_data(output_root: Path) -> None:
    data_root = output_root / "data" / "standings"
    data_root.mkdir(parents=True, exist_ok=True)
    for source in STANDINGS_PUBLISHER_DATA.iterdir():
        if source.is_file():
            shutil.copy2(source, data_root / source.name)


def copy_career_length_data(output_root: Path) -> None:
    source_root = OUTPUT_ROOT / "career_length" / "site" / "career_length"
    data_root = output_root / "data" / "career-length"
    data_root.mkdir(parents=True, exist_ok=True)
    for name in (
        "distribution.csv",
        "pmf.csv",
        "cdf.csv",
        "survival.csv",
        "longest.csv",
        "metadata.json",
        "page.json",
    ):
        shutil.copy2(source_root / name, data_root / name)


def copy_finish_by_chii_data(output_root: Path) -> None:
    source_root = OUTPUT_ROOT / "misc"
    data_root = output_root / "data" / "finish-by-chii"
    data_root.mkdir(parents=True, exist_ok=True)
    for name in (
        "finish_by_chii_1958_2026_top_thresholds.csv",
        "finish_by_chii_1958_2026_bottom_thresholds.csv",
        "finish_by_chii_1958_2026_summary.csv",
    ):
        shutil.copy2(source_root / name, data_root / name)


def copy_runtime(output_root: Path) -> None:
    target = output_root / "runtime"
    target.mkdir(parents=True, exist_ok=True)
    for source in RUNTIME_ROOT.iterdir():
        if source.is_file():
            shutil.copy2(source, target / source.name)


def clear_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def plain(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, tuple):
        return [plain(item) for item in value]
    if isinstance(value, list):
        return [plain(item) for item in value]
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    return value

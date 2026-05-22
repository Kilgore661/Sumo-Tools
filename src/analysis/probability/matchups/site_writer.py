from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from src.analysis.equelo.fixed_v2 import model as fixed_v2_model
from src.analysis.probability.matchups.traces import (
    EqueloTracePoint,
    ObservedTracePoint,
    SidelessRating,
)


SITE_BUNDLE_DIR = "site/win_probability_by_standing"
PAGE_JSON = "page.json"
OBSERVED_TRACE_CSV = "observed_trace_points.csv"
EQUELO_TRACE_CSV = "equelo_trace_points.csv"
METADATA_JSON = "metadata.json"


def write_win_probability_by_standing_bundle(
    *,
    output_dir: Path,
    observed_points: tuple[ObservedTracePoint, ...],
    equelo_points: tuple[EqueloTracePoint, ...],
    sideless_ratings: tuple[SidelessRating, ...],
    fixed_v2_output_root: Path,
    q: float,
    default_trace: str,
) -> dict[str, Path]:
    bundle_dir = output_dir / SITE_BUNDLE_DIR
    bundle_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "page_json": bundle_dir / PAGE_JSON,
        "observed_trace_csv": bundle_dir / OBSERVED_TRACE_CSV,
        "equelo_trace_csv": bundle_dir / EQUELO_TRACE_CSV,
        "metadata_json": bundle_dir / METADATA_JSON,
    }
    _write_page_json(paths["page_json"], default_trace)
    _write_dataclass_csv(observed_points, paths["observed_trace_csv"])
    _write_dataclass_csv(equelo_points, paths["equelo_trace_csv"])
    _write_metadata(
        output_path=paths["metadata_json"],
        observed_points=observed_points,
        equelo_points=equelo_points,
        sideless_ratings=sideless_ratings,
        fixed_v2_output_root=fixed_v2_output_root,
        q=q,
    )
    return paths


def _write_page_json(output_path: Path, default_trace: str) -> None:
    payload = {
        "id": "win_probability_by_standing",
        "title": "Win Probability by Standing",
        "layout": "chart_with_options",
        "default_source": "observed",
        "default_trace": default_trace,
        "default_division": "Makuuchi",
        "controls": [
            {
                "id": "source",
                "label": "Source",
                "kind": "enum",
                "default": "observed",
                "values": [
                    {
                        "value": "observed",
                        "label": "Observed",
                    },
                    {
                        "value": "equelo",
                        "label": "Equelo",
                    },
                ],
            },
            {
                "id": "division",
                "label": "Division",
                "kind": "enum",
                "default": "Makuuchi",
                "values": [
                    {"value": "Makuuchi", "label": "Makuuchi"},
                    {"value": "Juryo", "label": "Juryo"},
                    {"value": "Makushita", "label": "Makushita"},
                    {"value": "Sandanme", "label": "Sandanme"},
                    {"value": "Jonidan", "label": "Jonidan"},
                    {"value": "Jonokuchi", "label": "Jonokuchi"},
                    {"value": "All", "label": "All"},
                ],
            },
            {
                "id": "error_bars",
                "label": "Error bars",
                "kind": "boolean",
                "default": True,
                "applies_to": ["observed"],
            },
        ],
        "data_sources": [
            {
                "id": "observed",
                "label": "Observed",
                "data": OBSERVED_TRACE_CSV,
                "has_error_bars": True,
            },
            {
                "id": "equelo",
                "label": "Equelo",
                "data": EQUELO_TRACE_CSV,
                "has_error_bars": False,
            },
        ],
        "chart": {
            "kind": "plotly_trace_csv",
            "x": "opponent_chii",
            "y": "p_selected_wins",
            "trace": "selected_chii",
            "x_order": "opponent_ordinal",
        },
        "display": {
            "sanyaku": ["Y1", "O1", "S1", "K1"],
            "division_order": [
                "Makuuchi",
                "Juryo",
                "Makushita",
                "Sandanme",
                "Jonidan",
                "Jonokuchi",
                "All",
            ],
        },
        "y_axis": {
            "label": "P(selected standing wins)",
            "min": 0,
            "max": 1,
            "tickformat": ".0%",
        },
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_dataclass_csv(rows, output_path: Path) -> None:
    rows = tuple(rows)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tuple(rows[0].__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _write_metadata(
    *,
    output_path: Path,
    observed_points: tuple[ObservedTracePoint, ...],
    equelo_points: tuple[EqueloTracePoint, ...],
    sideless_ratings: tuple[SidelessRating, ...],
    fixed_v2_output_root: Path,
    q: float,
) -> None:
    observed_keys = {(row.selected_chii, row.opponent_chii) for row in observed_points}
    equelo_keys = {(row.selected_chii, row.opponent_chii) for row in equelo_points}
    payload = {
        "observed_trace_points": len(observed_points),
        "equelo_trace_points": len(equelo_points),
        "missing_equelo_trace_points": len(observed_keys - equelo_keys),
        "sideless_rating_count": len(sideless_ratings),
        "rating_source": (
            "latest fixed_v2 process ratings averaged by current sideless chii"
        ),
        "fixed_v2_rating_source": str(
            fixed_v2_output_root / fixed_v2_model.DAY_END_RATINGS_FILE_NAME
        ),
        "q": q,
        "domain_policy": (
            "Observed and Equelo trace points are restricted to sideless chii "
            "represented in the latest fixed_v2 process-rating snapshot."
        ),
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

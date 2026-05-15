import csv
import json
from dataclasses import dataclass
from pathlib import Path

from src.analysis.persistence.classes import PersistenceResults
from src.sumo_core.BasicEnums import Division


@dataclass(frozen=True)
class PersistenceSiteBundle:
    bundle_dir: Path
    page_json: Path
    persistence_csv: Path
    metadata_json: Path


def _division_label(division: Division) -> str:
    return division.name.capitalize()


def write_persistence_csv(
    results: PersistenceResults,
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "date",
                "division",
                "num_basho",
                "frequency",
                "mean_persistence",
                "stdev_persistence",
            ]
        )

        for row in results.rows:
            writer.writerow(
                [
                    str(row.date),
                    _division_label(row.division),
                    row.num_basho,
                    row.frequency,
                    row.mean_persistence,
                    row.stdev_persistence,
                ]
            )

    return output_path


def write_persistence_site_bundle(
    results: PersistenceResults,
    bundle_dir: Path,
    *,
    start: int,
    end: int,
    source_csv: Path,
) -> PersistenceSiteBundle:
    bundle_dir.mkdir(parents=True, exist_ok=True)

    bundle = PersistenceSiteBundle(
        bundle_dir=bundle_dir,
        page_json=bundle_dir / "page.json",
        persistence_csv=bundle_dir / "persistence.csv",
        metadata_json=bundle_dir / "metadata.json",
    )

    write_persistence_csv(results, bundle.persistence_csv)
    _write_page_json(
        output_path=bundle.page_json,
        start=start,
        end=end,
        num_basho=results.num_basho,
    )
    _write_metadata_json(
        output_path=bundle.metadata_json,
        results=results,
        start=start,
        end=end,
        source_csv=source_csv,
    )

    return bundle


def _write_page_json(
    output_path: Path,
    *,
    start: int,
    end: int,
    num_basho: int,
) -> None:
    page = {
        "title": "Division Stability",
        "summary": "Historical continuity within divisions.",
        "subtitle": f"Division persistence over previous {num_basho} basho ({start}-{end}).",
        "data_sources": [
            {
                "id": "persistence",
                "label": f"Previous {num_basho} basho",
                "data": "persistence.csv",
                "media_type": "text/csv",
            }
        ],
        "division_order": [_division_label(division) for division in Division],
        "default_visible": ["Makuuchi"],
        "chart": {
            "x_field": "date",
            "y_field": "mean_persistence",
            "group_field": "division",
            "x_label": "Basho",
            "x_type": "category",
            "x_tickangle": -45,
            "y_label": "Mean persistence",
            "y_min": 0,
            "y_max": 1,
            "y_tickformat": ".0%",
            "legend_title": "Division",
            "hover_fields": [
                "num_basho",
                "frequency",
                "stdev_persistence",
            ],
        },
    }
    output_path.write_text(json.dumps(page, indent=2) + "\n", encoding="utf-8")


def _write_metadata_json(
    output_path: Path,
    *,
    results: PersistenceResults,
    start: int,
    end: int,
    source_csv: Path,
) -> None:
    metadata = {
        "analysis": "division_persistence",
        "bundle": "division_stability",
        "start": start,
        "end": end,
        "num_basho": results.num_basho,
        "row_count": len(results.rows),
        "source_csv": source_csv.as_posix(),
        "value_policy": "Persistence values are probabilities in [0, 1].",
    }
    output_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

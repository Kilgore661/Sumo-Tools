"""Publish rating-annotated future torikumi for make_site89."""

from __future__ import annotations

import json
import shutil
from math import isfinite
from pathlib import Path

from src.analysis.elo89.api import Elo89Artifacts
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.torikumi import Future
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.History import History

from .common import write_csv, write_json


FIELDS = (
    "order",
    "division_id",
    "east_id",
    "east_shikona",
    "east_elo89",
    "east_probability",
    "west_probability",
    "west_elo89",
    "west_shikona",
    "west_id",
)
SITE_RELATIVE_ROOT = Path("current-sumo/torikumi/data")
DIVISIONS = (
    ("makuuchi", "Makuuchi"),
    ("juryo", "Juryo"),
    ("makushita", "Makushita"),
    ("sandanme", "Sandanme"),
    ("jonidan", "Jonidan"),
    ("jonokuchi", "Jonokuchi"),
)


def produce_torikumi(
    *,
    history: History,
    future: Future,
    ratings: Elo89Artifacts,
    output_root: Path,
    names: FullShikonaStore | None = None,
) -> tuple[Path, ...]:
    """Write an index and one annotated CSV for each published torikumi day."""

    date_key = str(future.date)
    history_date = next(
        (candidate for candidate in history if str(candidate) == date_key),
        None,
    )
    if history_date is None:
        raise ValueError(f"Future basho {date_key} is not present in History")
    q = float(ratings.manifest.get("q", 0))
    if not isfinite(q) or q <= 0:
        raise ValueError(f"Elo-89 manifest contains an invalid q: {q!r}")

    names = names if names is not None else FullShikonaStore.from_sources(history)
    banzuke = history[history_date].banzuke
    paths: list[Path] = []
    entries = []
    for future_day in future.days:
        rating_values, rating_cutoff = _rating_snapshot_before_day(
            ratings, date_key, int(future_day.day)
        )
        rows = []
        for bout in future_day.bouts:
            east_key, west_key = str(int(bout.east)), str(int(bout.west))
            east_chii = banzuke.rikchii.get(bout.east)
            west_chii = banzuke.rikchii.get(bout.west)
            east_rating = _rating_or_none(
                rating_values, east_key, east_chii, rating_cutoff, date_key, future_day.day
            )
            west_rating = _rating_or_none(
                rating_values, west_key, west_chii, rating_cutoff, date_key, future_day.day
            )
            if east_rating is None or west_rating is None:
                east_probability = west_probability = "-"
            else:
                east_chance = 1.0 / (
                    1.0 + 10.0 ** ((west_rating - east_rating) / q)
                )
                east_percent = round(east_chance * 100)
                east_probability = f"{east_percent}%"
                west_probability = f"{100 - east_percent}%"
            rows.append(
                {
                    "order": bout.order,
                    "division_id": _bout_division_id(east_chii, west_chii),
                    "east_id": int(bout.east),
                    "east_shikona": _shikona(
                        names, bout.east, bout.east_shikona, date_key, future_day.day
                    ),
                    "east_elo89": "-" if east_rating is None else f"{east_rating:.0f}",
                    "east_probability": east_probability,
                    "west_probability": west_probability,
                    "west_elo89": "-" if west_rating is None else f"{west_rating:.0f}",
                    "west_shikona": _shikona(
                        names, bout.west, bout.west_shikona, date_key, future_day.day
                    ),
                    "west_id": int(bout.west),
                }
            )
        filename = f"{date_key.replace('/', '-')}-day-{int(future_day.day):02d}.csv"
        paths.append(write_csv(output_root / filename, rows, FIELDS))
        entries.append(
            {
                "day": str(int(future_day.day)),
                "label": f"Day {int(future_day.day)}",
                "payload_path": f"data/{filename}",
                "source_url": future_day.source_url,
                "ratings_cutoff": rating_cutoff,
                "disabled": False,
            }
        )

    entries_by_day = {int(entry["day"]): entry for entry in entries}
    entries = [
        entries_by_day.get(
            day,
            {
                "day": str(day),
                "label": f"Day {day}",
                "disabled": True,
            },
        )
        for day in range(1, 16)
    ]
    available_days = [entry for entry in entries if not entry["disabled"]]

    index = write_json(
        output_root / "torikumi_index.json",
        {
            "schema_version": 1,
            "basho": date_key,
            "completed_through": (
                None
                if future.completed_through is None
                else int(future.completed_through)
            ),
            "generated_at": future.generated_at.isoformat(),
            "default_day": available_days[-1]["day"] if available_days else None,
            "default_division": "makuuchi",
            "divisions": [
                {"id": division_id, "label": label}
                for division_id, label in DIVISIONS
            ],
            "entries": entries,
        },
    )
    return (index, *paths)


def update_existing_bundle(
    *, history: History, future: Future, bundle_root: Path
) -> tuple[Path, ...]:
    """Add or replace Torikumi in an already-produced site89 data bundle."""

    manifest_path = bundle_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rating_manifest = bundle_root / manifest["rating_run"]
    ratings = Elo89Artifacts.load(rating_manifest.parent)
    site_root = bundle_root / "site"
    output_root = site_root / SITE_RELATIVE_ROOT
    if output_root.exists():
        shutil.rmtree(output_root)
    paths = produce_torikumi(
        history=history,
        future=future,
        ratings=ratings,
        output_root=output_root,
    )
    artifact = {
        "id": "torikumi",
        "producer": "src.analysis.site89.torikumi",
        "files": [path.relative_to(site_root).as_posix() for path in paths],
    }
    artifacts = [item for item in manifest["artifacts"] if item.get("id") != "torikumi"]
    artifacts.append(artifact)
    manifest["artifacts"] = sorted(artifacts, key=lambda item: item["id"])
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return paths


def _rating_snapshot_before_day(
    ratings: Elo89Artifacts, date_key: str, day: int
) -> tuple[dict[str, float], str]:
    day_values = ratings.day_end_ratings.get(date_key, {})
    preceding_days = [value for value in day_values if int(value) < day]
    if preceding_days:
        preceding_day = max(preceding_days, key=lambda value: int(value))
        return day_values[preceding_day], f"end of Day {int(preceding_day)}"
    try:
        return ratings.basho_start_ratings[date_key], "start of basho"
    except KeyError as error:
        raise ValueError(f"No Elo-89 ratings are available for {date_key}") from error


def _rating_or_none(values, rikishi, chii, cutoff, date_key, day):
    if chii is None:
        return None
    try:
        return float(values[rikishi])
    except KeyError as error:
        raise ValueError(
            f"Missing required {cutoff} Elo-89 rating for banzuke rikishi "
            f"{rikishi} in {date_key} Day {int(day)}"
        ) from error


def _shikona(names, rikishi, source_shikona, date_key, day):
    known = names.labels_by_rikid.get(rikishi)
    if known:
        return known
    if source_shikona:
        return source_shikona
    raise ValueError(
        f"Missing shikona for rikishi {int(rikishi)} in {date_key} Day {int(day)}"
    )


def _bout_division_id(east_chii, west_chii) -> str:
    """Classify a cross-division bout with its higher-ranked division."""

    east = "jonokuchi" if east_chii is None else _division(east_chii)
    west = "jonokuchi" if west_chii is None else _division(west_chii)
    divisions = [division_id for division_id, _label in DIVISIONS]
    return min((east, west), key=divisions.index)


def _division(chii) -> str:
    division = Division.MAKUUCHI if isinstance(chii.level, MSD) else chii.level
    return {
        Division.MAKUUCHI: "makuuchi",
        Division.JURYO: "juryo",
        Division.MAKUSHITA: "makushita",
        Division.SANDANME: "sandanme",
        Division.JONIDAN: "jonidan",
        Division.JONOKUCHI: "jonokuchi",
    }[division]



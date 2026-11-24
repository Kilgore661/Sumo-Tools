"""Publish historical and current Elo89-annotated torikumi for make_site89."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path

from src.analysis.elo89.api import Elo89Artifacts
from src.analysis.elo89.projection import project_basho_start_ratings
from src.analysis.sumo_history.basho_results.dates import basho_label, payload_file_name
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.torikumi import Future
from src.sumo_core.Banzuke import Banzuke
from src.sumo_core.BasicEnums import Division, MSD, Outcome
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.History import History

from .common import write_csv, write_json


FIELDS = (
    "day", "order", "division_id", "east_id", "east_shikona",
    "east_elo89", "east_odds", "prediction_side", "prediction_result",
    "result_type", "west_odds", "west_elo89", "west_shikona", "west_id",
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


@dataclass(frozen=True, slots=True)
class _ScheduledBout:
    order: int
    east: RikId
    west: RikId
    east_source_shikona: str | None
    west_source_shikona: str | None
    result: object | None


def produce_torikumi(
    *,
    history: History,
    future: Future,
    ratings: Elo89Artifacts,
    output_root: Path,
    names: FullShikonaStore | None = None,
    upcoming_banzuke: Banzuke | None = None,
) -> tuple[Path, ...]:
    """Write a basho index and one annotated CSV for every represented basho."""

    q = float(ratings.manifest.get("q", 0))
    if not isfinite(q) or q <= 0:
        raise ValueError(f"Elo-89 manifest contains an invalid q: {q!r}")
    if not history:
        raise ValueError("Cannot produce Torikumi from an empty History")

    names = names if names is not None else FullShikonaStore.from_sources(history)
    dates = sorted(history)
    if future.date not in history:
        if upcoming_banzuke is None:
            raise ValueError(
                f"Future basho {future.date} is absent from History and has no "
                "matching upcoming banzuke"
            )
        dates.append(future.date)
        dates.sort()

    future_days = {int(day.day): day for day in future.days}
    paths: list[Path] = []
    entries: list[dict[str, object]] = []
    generated_at = datetime.now(timezone.utc).isoformat()

    for date in dates:
        date_key = str(date)
        if date in history:
            state = history[date]
            banzuke = state.banzuke
            summary = getattr(state, "summary", {})
            if not hasattr(summary, "get"):
                summary = {}
            projected_start = None
        else:
            banzuke = upcoming_banzuke
            summary = {}
            projected_start = project_basho_start_ratings(
                ratings=ratings,
                banzuke=banzuke,
            )

        rows: list[dict[str, object]] = []
        day_entries: list[dict[str, object]] = []
        for day_number in range(1, 16):
            scheduled = _scheduled_bouts(
                date=date,
                day_number=day_number,
                summary=summary,
                future=future,
                future_days=future_days,
            )
            if not scheduled:
                day_entries.append(
                    {"day": str(day_number), "label": f"Day {day_number}", "disabled": True}
                )
                continue

            rating_values, rating_cutoff = _rating_snapshot_before_day(
                ratings,
                date_key,
                day_number,
                projected_start=projected_start,
            )
            day_rows = [
                _torikumi_row(
                    bout=bout,
                    day_number=day_number,
                    date_key=date_key,
                    banzuke=banzuke,
                    names=names,
                    rating_values=rating_values,
                    rating_cutoff=rating_cutoff,
                    q=q,
                )
                for bout in scheduled
            ]
            rows.extend(day_rows)
            day_entries.append(
                {
                    "day": str(day_number),
                    "label": f"Day {day_number}",
                    "disabled": False,
                    "ratings_cutoff": rating_cutoff,
                    "summaries": _day_summaries(day_rows),
                }
            )

        filename = payload_file_name(date)
        paths.append(
            write_csv(
                output_root / "by-basho" / filename,
                (_public_row(row) for row in rows),
                FIELDS,
            )
        )
        latest_day = max(
            (int(day["day"]) for day in day_entries if not day["disabled"]),
            default=None,
        )
        entries.append(
            {
                "basho": date_key,
                "year": int(date.year),
                "month": int(date.month),
                "label": basho_label(date),
                "latest_day": latest_day,
                "payload_path": f"data/by-basho/{filename}",
                "days": day_entries,
            }
        )

    index = write_json(
        output_root / "torikumi_index.json",
        {
            "schema": "sumo-tools.torikumi.index.v2",
            "generated_at": generated_at,
            "default_basho": entries[-1]["basho"],
            "default_day": None,
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
    *, history: History, future: Future, bundle_root: Path,
    upcoming_banzuke: Banzuke | None = None,
) -> tuple[Path, ...]:
    """Add or replace Torikumi in an already-produced site89 bundle."""

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
        upcoming_banzuke=upcoming_banzuke,
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


def _scheduled_bouts(*, date, day_number, summary, future, future_days):
    daily = summary.get(Day(day_number)) if summary else None
    results = {} if daily is None else daily.results_lookup
    results_by_participants = {
        frozenset((result.rikishi1, result.rikishi2)): result
        for result in results.values()
    }
    future_day = future_days.get(day_number) if date == future.date else None
    if future_day is not None:
        return tuple(
            _ScheduledBout(
                order=int(bout.order),
                east=bout.east,
                west=bout.west,
                east_source_shikona=bout.east_shikona,
                west_source_shikona=bout.west_shikona,
                result=results_by_participants.get(frozenset((bout.east, bout.west))),
            )
            for bout in sorted(future_day.bouts, key=lambda value: value.order)
        )
    if daily is None:
        return ()

    scheduled: list[_ScheduledBout] = []
    represented_pairs: set[frozenset[RikId]] = set()
    for order, result in enumerate(results.values(), start=1):
        represented_pairs.add(frozenset((result.rikishi1, result.rikishi2)))
        scheduled.append(
            _ScheduledBout(
                order=order,
                east=result.rikishi1,
                west=result.rikishi2,
                east_source_shikona=None,
                west_source_shikona=None,
                result=result,
            )
        )
    for pair in sorted(
        pair
        for pair in daily.torikumi
        if frozenset(pair) not in represented_pairs
    ):
        scheduled.append(
            _ScheduledBout(
                order=len(scheduled) + 1,
                east=pair[0],
                west=pair[1],
                east_source_shikona=None,
                west_source_shikona=None,
                result=None,
            )
        )
    return tuple(scheduled)


def _torikumi_row(
    *, bout, day_number, date_key, banzuke, names, rating_values, rating_cutoff, q
):
    east_key, west_key = str(int(bout.east)), str(int(bout.west))
    east_chii = banzuke.rikchii.get(bout.east)
    west_chii = banzuke.rikchii.get(bout.west)
    east_rating = _rating_or_none(
        rating_values, east_key, east_chii, rating_cutoff, date_key, Day(day_number)
    )
    west_rating = _rating_or_none(
        rating_values, west_key, west_chii, rating_cutoff, date_key, Day(day_number)
    )

    east_odds_value = west_odds_value = None
    prediction_side = ""
    exclusion = "missing_rating"
    if east_rating is not None and west_rating is not None:
        east_chance = 1.0 / (1.0 + 10.0 ** ((west_rating - east_rating) / q))
        east_odds_value = 1.0 / east_chance
        west_odds_value = 1.0 / (1.0 - east_chance)
        if east_rating > west_rating:
            prediction_side = "east"
            exclusion = ""
        elif west_rating > east_rating:
            prediction_side = "west"
            exclusion = ""
        else:
            exclusion = "equal_rating"

    result_type, winner_side = _result_for_sides(bout.result, bout.east, bout.west)
    prediction_result = "pending"
    favourite_profit = winner_profit = chii_profit = None
    if result_type in {"fusen", "draw", "excluded"}:
        prediction_result = "excluded"
    elif result_type == "normal" and not prediction_side:
        prediction_result = "excluded"
    elif result_type == "normal":
        prediction_result = "correct" if prediction_side == winner_side else "incorrect"
        favourite_odds = east_odds_value if prediction_side == "east" else west_odds_value
        winner_odds = east_odds_value if winner_side == "east" else west_odds_value
        favourite_profit = favourite_odds - 1.0 if prediction_result == "correct" else -1.0
        winner_profit = winner_odds - 1.0
    if (
        result_type == "normal"
        and east_chii is not None
        and west_chii is not None
        and east_odds_value is not None
        and west_odds_value is not None
        and east_chii.ordinal() != west_chii.ordinal()
    ):
        chii_side = (
            "east"
            if east_chii.ordinal() < west_chii.ordinal()
            else "west"
        )
        chii_odds = east_odds_value if chii_side == "east" else west_odds_value
        chii_profit = chii_odds - 1.0 if chii_side == winner_side else -1.0

    return {
        "day": day_number,
        "order": bout.order,
        "division_id": _bout_division_id(east_chii, west_chii),
        "east_id": int(bout.east),
        "east_shikona": _shikona(
            names, bout.east, bout.east_source_shikona, date_key, Day(day_number)
        ),
        "east_elo89": "-" if east_rating is None else f"{east_rating:.1f}",
        "east_odds": "-" if east_odds_value is None else f"{east_odds_value:.2f}",
        "prediction_side": prediction_side,
        "prediction_result": prediction_result,
        "prediction_exclusion": exclusion,
        "result_type": result_type,
        "west_odds": "-" if west_odds_value is None else f"{west_odds_value:.2f}",
        "west_elo89": "-" if west_rating is None else f"{west_rating:.1f}",
        "west_shikona": _shikona(
            names, bout.west, bout.west_source_shikona, date_key, Day(day_number)
        ),
        "west_id": int(bout.west),
        "_favourite_profit": favourite_profit,
        "_winner_profit": winner_profit,
        "_chii_profit": chii_profit,
    }


def _result_for_sides(result, east, west) -> tuple[str, str]:
    if result is None:
        return "pending", ""
    outcomes = {result.rikishi1: result.outcome1, result.rikishi2: result.outcome2}
    if set(outcomes) != {east, west}:
        raise ValueError(f"Torikumi/result participants disagree: {(east, west)}")
    pair = set(outcomes.values())
    if pair == {Outcome.FS, Outcome.FP}:
        return "fusen", ""
    if pair == {Outcome.DRAW}:
        return "draw", ""
    if pair != {Outcome.W, Outcome.L}:
        return "excluded", ""
    return "normal", "east" if outcomes[east] == Outcome.W else "west"


def _day_summaries(rows) -> dict[str, dict[str, object]]:
    summaries = {}
    for division_id, _label in DIVISIONS:
        selected = [row for row in rows if row["division_id"] == division_id]
        scored = [
            row for row in selected
            if row["prediction_result"] in {"correct", "incorrect"}
        ]
        chii_scored = [row for row in selected if row["_chii_profit"] is not None]
        summaries[division_id] = {
            "bouts": len(selected),
            "correct": sum(row["prediction_result"] == "correct" for row in scored),
            "scored": len(scored),
            "favourite_profit": round(sum(row["_favourite_profit"] for row in scored), 6),
            "winner_profit": round(sum(row["_winner_profit"] for row in scored), 6),
            "chii_scored": len(chii_scored),
            "chii_profit": round(sum(row["_chii_profit"] for row in chii_scored), 6),
            "fusen_excluded": sum(row["result_type"] == "fusen" for row in selected),
            "draw_excluded": sum(row["result_type"] == "draw" for row in selected),
            "equal_rating_excluded": sum(
                row["prediction_exclusion"] == "equal_rating" for row in selected
            ),
            "missing_rating_excluded": sum(
                row["prediction_exclusion"] == "missing_rating" for row in selected
            ),
            "pending": sum(row["result_type"] == "pending" for row in selected),
        }
    return summaries


def _public_row(row):
    return {field: row[field] for field in FIELDS}


def _rating_snapshot_before_day(
    ratings: Elo89Artifacts, date_key: str, day: int, *,
    projected_start: dict[str, float] | None = None,
) -> tuple[dict[str, float], str]:
    day_values = ratings.day_end_ratings.get(date_key, {})
    preceding_days = [value for value in day_values if int(value) < day]
    if preceding_days:
        preceding_day = max(preceding_days, key=lambda value: int(value))
        return day_values[preceding_day], f"end of Day {int(preceding_day)}"
    if projected_start is not None:
        return projected_start, "projected start of basho"
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
        Division.MAKUUCHI: "makuuchi", Division.JURYO: "juryo",
        Division.MAKUSHITA: "makushita", Division.SANDANME: "sandanme",
        Division.JONIDAN: "jonidan", Division.JONOKUCHI: "jonokuchi",
    }[division]

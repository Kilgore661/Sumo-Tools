"""Produce indexed Elo-89 rating-change tables."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from src.analysis.elo89.api import Elo89Artifacts
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History

from .common import write_csv, write_json


WINDOWS = (1, 2, 3, 4, 5, 6, 12)
FIELDS = (
    "rikishi_id", "shikona", "division_id", "chii_at_start",
    "chii_ordinal_at_start", "chii_at_end", "chii_ordinal_at_end",
    "rating_at_start", "rating_at_end", "delta", "expected_bouts",
    "delta_per_expected_bout", "normalised_delta_per_expected_bout",
    "actual_bouts", "delta_per_actual_bout", "normalised_delta_per_actual_bout",
)


def produce_rating_changes(
    *, history: History, ratings: Elo89Artifacts, output_root: Path,
    windows: tuple[int, ...] = WINDOWS,
) -> tuple[Path, ...]:
    dates = sorted(history)
    names = FullShikonaStore.from_sources(history)
    metrics = _bout_metrics(ratings)
    target_index = len(dates) - 1
    entries = []
    paths = []
    for window in sorted(set(windows)):
        if window <= 0:
            raise ValueError(f"Window must be positive: {window}")
        if target_index - window < 0:
            continue
        start, target = dates[target_index - window], dates[target_index]
        rows = _rows(history, ratings, names, metrics, dates, start, target)
        name = f"{str(target).replace('/', '-')} {window}-change.csv"
        paths.append(write_csv(output_root / name, rows, FIELDS))
        entries.append(
            {
                "n": str(window),
                "label": f"{window} basho",
                "target_date": str(target),
                "start_date": str(start),
                "payload_path": f"data/{name}",
            }
        )
    index = write_json(
        output_root / "rating_changes_index.json",
        {"default_n": "6", "entries": entries},
    )
    return (index, *paths)


def _bout_metrics(ratings: Elo89Artifacts):
    result = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))
    for row in ratings.bout_ledger:
        date = row["date"]
        for side in ("a", "b"):
            rid = RikId(int(row[f"rikishi_{side}"]))
            result[rid][date][0] += 1
            k = float(row[f"k_{side}"])
            result[rid][date][1] += float(row[f"delta_{side}"]) / k if k else 0.0
    return result


def _rows(history, ratings, names, metrics, dates, start, target):
    start_values = ratings.basho_end_ratings[str(start)]
    end_values = ratings.basho_end_ratings[str(target)]
    rikishi_ids = sorted(set(start_values) & set(end_values), key=int)
    rows = []
    window_dates = dates[dates.index(start) + 1 : dates.index(target) + 1]
    for rid_text in rikishi_ids:
        rid = RikId(int(rid_text))
        start_chii = history(start).banzuke.rikchii.get(rid)
        end_chii = history(target).banzuke.rikchii.get(rid)
        start_rating = float(start_values[rid_text])
        end_rating = float(end_values[rid_text])
        delta = end_rating - start_rating
        expected = sum(
            _possible_bouts(chii)
            for date in window_dates
            for chii in (history(date).banzuke.rikchii.get(rid),)
            if chii is not None
        )
        actual = sum(metrics[rid][str(date)][0] for date in window_dates)
        normalised = sum(metrics[rid][str(date)][1] for date in window_dates)
        rows.append(
            {
                "rikishi_id": int(rid),
                "shikona": names.full_shikona(rid),
                "division_id": _division_id(end_chii),
                "chii_at_start": "" if start_chii is None else str(start_chii),
                "chii_ordinal_at_start": "" if start_chii is None else start_chii.ordinal(),
                "chii_at_end": "" if end_chii is None else str(end_chii),
                "chii_ordinal_at_end": "" if end_chii is None else end_chii.ordinal(),
                "rating_at_start": f"{start_rating:.3f}",
                "rating_at_end": f"{end_rating:.3f}",
                "delta": f"{delta:.3f}",
                "expected_bouts": expected,
                "delta_per_expected_bout": f"{delta / expected if expected else 0:.3f}",
                "normalised_delta_per_expected_bout": f"{normalised / expected if expected else 0:.3f}",
                "actual_bouts": actual,
                "delta_per_actual_bout": f"{delta / actual if actual else 0:.3f}",
                "normalised_delta_per_actual_bout": f"{normalised / actual if actual else 0:.3f}",
            }
        )
    return sorted(rows, key=lambda row: (-float(row["delta"]), row["chii_ordinal_at_end"] or 10**9, row["shikona"]))


def _possible_bouts(chii) -> int:
    return 15 if isinstance(chii.level, MSD) or chii.level == Division.JURYO else 7


def _division_id(chii) -> str:
    if chii is None:
        return ""
    division = Division.MAKUUCHI if isinstance(chii.level, MSD) else chii.level
    return {
        Division.MAKUUCHI: "makuuchi", Division.JURYO: "juryo",
        Division.MAKUSHITA: "makushita", Division.SANDANME: "sandanme",
        Division.JONIDAN: "jonidan", Division.JONOKUCHI: "jonokuchi",
    }[division]

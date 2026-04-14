import csv
from pathlib import Path

from ....sumo_core.BasicPrimitives import Day, RikId
from ....sumo_core.History import Date, History
from ....sumo_core.Chii import Chii

from .types import ObservationCounts, Ratings, TimelineKey, TimelineToRatingMap


def _timeline_key(date: Date, day: Day) -> TimelineKey:
    return f"{date.year:04d}/{date.month:02d}/{int(day):02d}"


def project_day_end_ratings(
    history: History,
    day_end_ratings: dict[Date, dict[Day, dict[RikId, float]]],
) -> TimelineToRatingMap:
    projected: TimelineToRatingMap = {}

    for date, basho_ratings in day_end_ratings.items():
        banzuke = history[date].banzuke

        for day, ratings_by_rikishi in basho_ratings.items():
            ratings: Ratings = {}
            for rikid in banzuke.riks:
                chii = banzuke.rikchii[rikid]
                ratings[chii] = ratings_by_rikishi[rikid]

            projected[_timeline_key(date, day)] = ratings

    return projected


def count_observations(timeline_to_ratings: TimelineToRatingMap) -> ObservationCounts:
    counts: ObservationCounts = {}

    for ratings in timeline_to_ratings.values():
        for chii in ratings:
            if chii not in counts:
                counts[chii] = 0
            counts[chii] += 1

    return counts


def write_probe_rating_dump(
    output_path: Path,
    timeline_to_ratings: TimelineToRatingMap,
    probes: list[Chii],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ordered_times = list(timeline_to_ratings.keys())

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["competition_day", *[str(chii) for chii in probes]])

        for key in ordered_times:
            ratings = timeline_to_ratings[key]
            row = [key]
            for chii in probes:
                row.append(ratings[chii] if chii in ratings else "")
            writer.writerow(row)

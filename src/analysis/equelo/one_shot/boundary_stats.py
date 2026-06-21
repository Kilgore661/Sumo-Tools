import csv
import math
from dataclasses import dataclass
from pathlib import Path

from ....sumo_core.Banzuke import Banzuke
from ....sumo_core.BasicPrimitives import Day, RikId
from ....sumo_core.History import Date
from ....sumo_core.Summary import BoutResult


@dataclass(frozen=True)
class AdjustmentRow:
    date: Date
    rikid: RikId
    rating: float
    n: int
    delta: float
    delta_per_rikishi: float
    abs_delta_per_rikishi: float


@dataclass(frozen=True)
class AdjustmentSummary:
    count: int
    mean_abs: float
    stdev_abs: float
    max_abs: float
    max_date: Date | None
    max_rikid: RikId | None
    max_rating: float | None
    max_n: int | None


class BoundaryAdjustmentCollector:
    def __init__(self) -> None:
        self._rows: list[AdjustmentRow] = []

    def on_basho_start(self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke) -> None:
        del date, ratings, banzuke

    def on_entry(self, date: Date, rikid: RikId, rating: float, ratings: dict[RikId, float]) -> None:
        del date, rikid, rating, ratings

    def on_retirement(
        self,
        date: Date,
        rikid: RikId,
        rating: float,
        n: int,
        delta: float,
        delta_per_rikishi: float,
        abs_delta_per_rikishi: float,
        closed: bool,
    ) -> None:
        del closed
        self._rows.append(
            AdjustmentRow(
                date=date,
                rikid=rikid,
                rating=rating,
                n=n,
                delta=delta,
                delta_per_rikishi=delta_per_rikishi,
                abs_delta_per_rikishi=abs_delta_per_rikishi,
            )
        )

    def on_day_start(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None:
        del date, day, ratings

    def on_bout(
        self,
        date: Date,
        day: Day,
        bout: BoutResult,
        delta1: float,
        delta2: float,
        r1_before: float,
        r2_before: float,
        r1_after: float,
        r2_after: float,
        rating_mass_before: float,
        rating_mass_after: float,
    ) -> None:
        del date, day, bout, delta1, delta2, r1_before, r2_before, r1_after, r2_after, rating_mass_before, rating_mass_after

    def on_ignored_bout(self, date: Date, day: Day, bout: BoutResult) -> None:
        del date, day, bout

    def on_day_end(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None:
        del date, day, ratings

    def on_basho_end(self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke) -> None:
        del date, ratings, banzuke

    def summarise(self) -> AdjustmentSummary:
        count = len(self._rows)
        if count == 0:
            return AdjustmentSummary(
                count=0,
                mean_abs=0.0,
                stdev_abs=0.0,
                max_abs=0.0,
                max_date=None,
                max_rikid=None,
                max_rating=None,
                max_n=None,
            )

        values = [row.abs_delta_per_rikishi for row in self._rows]
        mean_abs = sum(values) / count
        variance = sum((value - mean_abs) ** 2 for value in values) / count
        stdev_abs = math.sqrt(variance)

        max_row = max(self._rows, key=lambda row: row.abs_delta_per_rikishi)

        return AdjustmentSummary(
            count=count,
            mean_abs=mean_abs,
            stdev_abs=stdev_abs,
            max_abs=max_row.abs_delta_per_rikishi,
            max_date=max_row.date,
            max_rikid=max_row.rikid,
            max_rating=max_row.rating,
            max_n=max_row.n,
        )

    def write_detail_csv(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date",
                "rikid",
                "rating",
                "n",
                "delta",
                "delta_per_rikishi",
                "abs_delta_per_rikishi",
            ])
            for row in self._rows:
                writer.writerow([
                    str(row.date),
                    int(row.rikid),
                    row.rating,
                    row.n,
                    row.delta,
                    row.delta_per_rikishi,
                    row.abs_delta_per_rikishi,
                ])
        return path

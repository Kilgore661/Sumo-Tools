import json
import math
from dataclasses import dataclass

from src.analysis.equelo.expt1.params import DEFAULT_K_CONFIG_PATH
from src.infra.connect import connect

from .classes import Ratings
from .helpers import load_ratings


OUTPUT_PATH = "./files/output/fide_stdevs.json"


@dataclass
class RunningStats:
    count: int = 0
    total: float = 0.0
    total_sq: float = 0.0
    min_val: float = float("inf")
    max_val: float = float("-inf")

    def add(self, value: float) -> None:
        self.count += 1
        self.total += value
        self.total_sq += value * value

        if value < self.min_val:
            self.min_val = value
        if value > self.max_val:
            self.max_val = value

    @property
    def mean(self) -> float:
        return self.total / self.count if self.count else 0.0

    @property
    def variance(self) -> float:
        if self.count < 2:
            return 0.0
        mean = self.mean
        return max(0.0, (self.total_sq / self.count) - (mean * mean))

    @property
    def stdev(self) -> float:
        return math.sqrt(self.variance)

    @property
    def min(self) -> float:
        return self.min_val if self.count else 0.0

    @property
    def max(self) -> float:
        return self.max_val if self.count else 0.0


def load_bucket_config() -> dict:
    with open(DEFAULT_K_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def bucket_from_division_number(division_number: int) -> str:
    """
    Collapse the Chii ordinal bucket into the broad groups:

        <= 3 -> "3"   (sanyaku)
         4   -> "4"   (maegashira)
         5   -> "5"   (juryo)
        >= 6 -> "max" (below juryo)
    """
    if division_number <= 3:
        return "3"
    if division_number == 4:
        return "4"
    if division_number == 5:
        return "5"
    return "max"


def calculate_stdevs(start_year: int = 1958, end_year: int | None = None, use_zip: bool = False) -> dict:
    history = connect(start_year, end_year, use_zip=use_zip)
    ratings = load_ratings()
    _config = load_bucket_config()

    stats_by_bucket = {key: RunningStats() for key in ["3", "4", "5", "max"]}

    for basho_date in history.keys():
        basho_state = history[basho_date]
        banzuke = basho_state.banzuke

        basho_start_ratings = ratings.basho_start.get(basho_date)
        day_map = ratings.day_end.get(basho_date, {})

        if basho_start_ratings is None:
            continue

        for rikid in banzuke.riks:
            if rikid not in basho_start_ratings:
                continue

            chii = banzuke.get_chii(rikid)
            division_number = chii.ordinal() // 100000
            bucket = bucket_from_division_number(division_number)

            previous = basho_start_ratings[rikid]

            for day in sorted(day_map.keys()):
                day_ratings = day_map[day]
                if rikid not in day_ratings:
                    continue

                current = day_ratings[rikid]
                delta = current - previous
                if bucket == "3" and abs(delta) > 10.000001:
                    print(basho_date, rikid, chii, day, previous, current, delta)
                    import sys; sys.exit()
                stats_by_bucket[bucket].add(delta)
                previous = current

    summary = {}
    for key in ["3", "4", "5", "max"]:
        summary[key] = {
            "count": stats_by_bucket[key].count,
            "mean": stats_by_bucket[key].mean,
            "stdev": stats_by_bucket[key].stdev,
            "min": stats_by_bucket[key].min,
            "max": stats_by_bucket[key].max,
        }

    output_json = {
        "lims": {
            "3": summary["3"]["stdev"],
            "4": summary["4"]["stdev"],
            "5": summary["5"]["stdev"],
        },
        "max": summary["max"]["stdev"],
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=4)

    return summary


def print_summary(summary: dict) -> None:
    for key in ["3", "4", "5", "max"]:
        row = summary[key]
        print(
            f"{key:>3}  "
            f"count={row['count']:>8}  "
            f"mean={row['mean']:>10.6f}  "
            f"stdev={row['stdev']:>10.6f}  "
            f"min={row['min']:>10.6f}  "
            f"max={row['max']:>10.6f}"
        )


def main() -> None:
    summary = calculate_stdevs()
    print_summary(summary)
    print(f"\nWrote stdev config to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()


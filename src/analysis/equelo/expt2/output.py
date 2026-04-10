from pdb import set_trace

import csv
import math
from collections import defaultdict
from pathlib import Path

from scipy.stats import t as student_t

from ....sumo_core.BasicPrimitives import RikId
from ....sumo_core.Chii import Chii
from ....sumo_core.History import History

from .types import BashoStartRatingsByChii, ChiiRatings


CONFIDENCE_LEVEL = 0.95


def write_final_ratings_csv(mu: ChiiRatings, output_path: Path) -> Path:
    """Write final converged ratings as ``chii, ordinal, rating`` sorted by ordinal."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(mu.items(), key=lambda item: (item[0].ordinal(), str(item[0])))
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["chii", "ordinal", "rating"])
        for chii, rating in rows:
            writer.writerow([str(chii), chii.ordinal(), rating])
    return output_path



def _count_basho_days(basho_state) -> int:
    """Return the number of represented days in one basho state.

    The cleaned history keeps one banzuke per basho, so counting a chii "on any
    day of any basho" means multiplying each banzuke appearance by the basho day
    count. The exact day container name varies a little across project versions,
    so this helper checks the common possibilities and falls back to 1.
    """
    for attr_name in ("summary", "days", "results_by_day", "bouts_by_day", "torikumi_by_day"):
        if not hasattr(basho_state, attr_name):
            continue
        value = getattr(basho_state, attr_name)
        if value is None:
            continue
        if isinstance(value, int):
            return max(1, value)
        try:
            return max(1, len(value))
        except TypeError:
            pass
    return 1



def _collect_chii_observation_stats(history: History) -> tuple[dict[Chii, int], dict[Chii, int]]:
    observation_counts: dict[Chii, int] = defaultdict(int)
    rikishi_by_chii: dict[Chii, set[RikId]] = defaultdict(set)

    for date in sorted(history.keys()):
        basho_state = history[date]
        day_count = _count_basho_days(basho_state)

        for rikid, chii in basho_state.banzuke.rikchii.items():
            observation_counts[chii] += day_count
            rikishi_by_chii[chii].add(rikid)

    distinct_rikishi_counts = {
        chii: len(rikids) for chii, rikids in rikishi_by_chii.items()
    }
    return dict(observation_counts), distinct_rikishi_counts



def _sample_stdev(values: list[float]) -> float:
    n = len(values)
    if n <= 1:
        return 0.0
    mean = sum(values) / n
    sumsq = sum((value - mean) ** 2 for value in values)
    return math.sqrt(sumsq / (n - 1))



def _ci_stats(values: list[float]) -> tuple[int, float | str, float | str, float | str, float | str, float | str]:
    n = len(values)
    if n == 0:
        return 0, "", "", "", "", ""

    mean = sum(values) / n
    if n == 1:
        return 1, mean, 0.0, 0.0, mean, mean

    stdev = _sample_stdev(values)
    se = stdev / math.sqrt(n)
    t_crit = float(student_t.ppf(0.5 + CONFIDENCE_LEVEL / 2.0, n - 1))
    margin = t_crit * se
    return n, mean, stdev, se, mean - margin, mean + margin



def write_final_ratings_stats_csv(
    mu: ChiiRatings,
    history: History,
    output_path: Path,
    basho_start_ratings_by_chii: BashoStartRatingsByChii | None = None,
) -> tuple[Path, int]:
    """Write final ratings together with simple observation stats.

    Output columns are always:
    * ``chii``
    * ``ordinal``
    * ``rating``
    * ``observations`` = number of day-level observations across the history
    * ``distinct_rikishi`` = number of distinct rikishi ever seen with that chii
    * ``strictly_less_than_preceding``
    * ``violation`` = current rating is not strictly less than the preceding one

    If ``basho_start_ratings_by_chii`` is supplied, CI-related columns are also
    added using basho-start observations from a final analysis pass.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    observation_counts, distinct_rikishi_counts = _collect_chii_observation_stats(history)
    rows = sorted(mu.items(), key=lambda item: (item[0].ordinal(), str(item[0])))

    include_ci = basho_start_ratings_by_chii is not None
    violation_count = 0
    previous_rating = None

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = [
            "chii",
            "ordinal",
            "rating",
            "observations",
            "distinct_rikishi",
            "strictly_less_than_preceding",
            "violation",
        ]
        if include_ci:
            header.extend(
                [
                    "n_basho_start",
                    "mean_basho_start",
                    "stdev_basho_start",
                    "se_basho_start",
                    "ci95_lower",
                    "ci95_upper",
                ]
            )
        writer.writerow(header)

        for chii, rating in rows:
            if previous_rating is None:
                strictly_less = ""
                violation = False
            else:
                strictly_less = rating < previous_rating
                violation = not strictly_less
                if violation:
                    violation_count += 1

            row = [
                str(chii),
                chii.ordinal(),
                rating,
                observation_counts.get(chii, 0),
                distinct_rikishi_counts.get(chii, 0),
                strictly_less,
                violation,
            ]
            if include_ci:
                values = basho_start_ratings_by_chii.get(chii, [])
                row.extend(_ci_stats(values))

            writer.writerow(row)
            previous_rating = rating

    return output_path, violation_count

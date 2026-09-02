"""Run post-1988 publication analyses which do not depend on a rating model."""

from __future__ import annotations

import shutil
from pathlib import Path
from collections import defaultdict

from src.analysis.persistence.division_persistence import compute_division_persistence
from src.analysis.persistence.reports import write_persistence_csv
from src.analysis.sumo_history.career_lifecycle.career_length import build_career_length_outputs
from src.analysis.sumo_history.career_lifecycle.rank_at_retirement import build_rank_at_retirement_outputs
from src.analysis.sumo_history.records.career_losses import build_career_losses_outputs
from src.analysis.sumo_history.records.career_wins import build_career_wins_outputs
from src.analysis.sumo_history.records.consecutive_bouts import build_consecutive_bouts_outputs
from src.misc.banzuke_by_era import build_banzuke_division_by_era_outputs
from src.misc.finish_by_chii import (
    DEFAULT_DIVISIONS,
    build_threshold_rows,
    collect_finish_rows,
    write_csv,
)
from src.misc.first_appearance import build_first_chii_appearance_outputs
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.History import History

from .longest_careers import produce_longest_careers


def produce_model_independent(
    *, history: History, work_root: Path, site_root: Path
) -> dict[str, tuple[Path, ...]]:
    start = int(min(history).year)
    end = int(max(history).year)
    result = {}

    finish_rows = collect_finish_rows(history, divisions=DEFAULT_DIVISIONS)
    finish_root = site_root / "performance/finish-by-chii/data"
    top = write_csv(build_threshold_rows(finish_rows, threshold_max=10, from_bottom=False), finish_root / "top_thresholds.csv")
    bottom = write_csv(build_threshold_rows(finish_rows, threshold_max=10, from_bottom=True), finish_root / "bottom_thresholds.csv")
    result["finish_by_chii"] = (top, bottom)

    banzuke = build_banzuke_division_by_era_outputs(history, output_root=work_root / "banzuke-era", start=start, end=end, print_summary=False)
    result["banzuke_division_by_era"] = (_copy(banzuke.divisions_csv, site_root / "banzuke-rank/banzuke-structure-over-time/banzuke-division-by-era/data/divisions.csv"),)
    result["makuuchi_rank_by_era"] = (
        _write_makuuchi_rank_by_era(
            history,
            site_root / "banzuke-rank/banzuke-structure-over-time/makuuchi-rank-by-era/data/ranks.csv",
        ),
    )
    first = build_first_chii_appearance_outputs(history, output_root=work_root / "first", start=start, end=end, print_summary=False)
    result["first_chii_appearance"] = (_copy(first.appearances_csv, site_root / "banzuke-rank/rank-history/first-chii-appearance/data/appearances.csv"),)

    persistence = compute_division_persistence(history=history, num_basho=10)
    persistence_path = write_persistence_csv(persistence, site_root / "banzuke-rank/division-stability/data/persistence.csv")
    result["division_stability"] = (persistence_path,)

    career = build_career_length_outputs(history, output_root=work_root / "career-length", print_summary=False)
    career_paths = tuple(
        _copy(getattr(career, f"{name}_csv"), site_root / f"sumo-history/career-lifecycle/career-length/data/{name}.csv")
        for name in ("distribution", "pmf", "cdf", "survival")
    )
    result["career_length"] = career_paths
    result["longest_careers"] = (
        produce_longest_careers(
            career_rikishi_csv=career.rikishi_csv,
            output_root=site_root / "sumo-history/records/longest-careers/data",
        ),
    )

    retirement = build_rank_at_retirement_outputs(history, output_root=work_root / "retirement", print_summary=False)
    result["rank_at_retirement"] = (_copy(retirement.distribution_csv, site_root / "sumo-history/career-lifecycle/rank-at-retirement/data/distribution.csv"),)
    consecutive = build_consecutive_bouts_outputs(history, output_root=work_root / "consecutive")
    result["most_consecutive_bouts"] = (_copy(consecutive.longest_streak_candidates_csv, site_root / "sumo-history/records/most-consecutive-bouts/data/longest_streak_candidates.csv"),)
    wins = build_career_wins_outputs(history, output_root=work_root / "wins")
    result["most_career_wins"] = (_copy(wins.career_wins_csv, site_root / "sumo-history/records/most-career-wins/data/career_wins.csv"),)
    losses = build_career_losses_outputs(history, output_root=work_root / "losses")
    result["most_career_losses"] = (_copy(losses.career_losses_csv, site_root / "sumo-history/records/most-career-losses/data/career_losses.csv"),)
    return result


def _copy(source: Path, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def _write_makuuchi_rank_by_era(history: History, target: Path) -> Path:
    first, last = int(min(history).year), int(max(history).year)
    eras = tuple(
        (year, min(year + 9, last)) for year in range(first, last + 1, 10)
    )
    counts = {f"{start}-{end}": defaultdict(int) for start, end in eras}
    for date, state in history.items():
        era = next(label for (start, end), label in zip(eras, counts) if start <= int(date.year) <= end)
        for rid in state.banzuke.riks:
            chii = state.banzuke.rikchii[rid]
            if isinstance(chii.level, Division):
                continue
            label = chii.level.as_abbreviation() if chii.level != MSD.MAEGASHIRA else f"M{chii.number}"
            counts[era][label] += 1
    labels = [name for name in ("Y", "O", "S", "K") if any(name in values for values in counts.values())]
    labels.extend(
        f"M{number}"
        for number in sorted({int(name[1:]) for values in counts.values() for name in values if name.startswith("M")})
    )
    rows = [
        {
            "rank": label,
            "era": era,
            "count": counts[era].get(label, 0),
            "total": sum(values.get(label, 0) for values in counts.values()),
        }
        for label in labels
        for era in counts
    ]
    from .common import write_csv as write_site_csv
    return write_site_csv(target, rows)

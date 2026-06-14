"""Produce career-win record candidates from History."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from src.analysis.sumo_history.constants import TOP_N_LIMIT
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.History import Date, History


OUTPUT_ROOT = Path("files/output/analysis/sumo_history/records/career_wins")


@dataclass(frozen=True)
class AppearancePoint:
    date: Date
    day: Day

    def label(self) -> str:
        return f"{self.date}/{int(self.day):02d}"


@dataclass
class CareerWinStats:
    rikishi_id: RikId
    wins_all: int = 0
    losses_all: int = 0
    wins_actual: int = 0
    losses_actual: int = 0
    start_all: AppearancePoint | None = None
    end_all: AppearancePoint | None = None
    start_actual: AppearancePoint | None = None
    end_actual: AppearancePoint | None = None


@dataclass(frozen=True)
class CareerWinsRow:
    rikishi_id: int
    shikona: str
    active: bool
    position_all: int | str
    position_actual: int | str
    active_position_all: int | str
    active_position_actual: int | str
    wins_all: int
    losses_all: int
    bouts_all: int
    win_rate_all: str
    start_all: str
    end_all: str
    wins_actual: int
    losses_actual: int
    bouts_actual: int
    win_rate_actual: str
    start_actual: str
    end_actual: str


@dataclass(frozen=True)
class CareerWinsOutputs:
    output_root: Path
    career_wins_csv: Path


def build_career_wins_outputs(
    history: History,
    output_root: Path = OUTPUT_ROOT,
    *,
    limit: int = TOP_N_LIMIT,
) -> CareerWinsOutputs:
    """Write the site-facing career-wins candidate CSV."""

    full_shikona_store = FullShikonaStore.from_sources(history)
    rows = career_wins_rows(
        history=history,
        full_shikona_store=full_shikona_store,
        limit=limit,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    outputs = CareerWinsOutputs(
        output_root=output_root,
        career_wins_csv=output_root / "career_wins.csv",
    )
    write_dataclass_csv(rows, outputs.career_wins_csv)
    return outputs


def career_wins_rows(
    *,
    history: History,
    full_shikona_store: FullShikonaStore,
    limit: int,
) -> list[CareerWinsRow]:
    """Return the union of rows needed by all top-N career-wins views."""

    stats = compute_career_win_stats(history)
    latest_date = max(history)
    active_rikishi = set(history(latest_date).banzuke.riks)

    position_all = ranked_positions(
        stats.values(),
        wins_field="wins_all",
        active_rikishi=None,
        limit=limit,
    )
    position_actual = ranked_positions(
        stats.values(),
        wins_field="wins_actual",
        active_rikishi=None,
        limit=limit,
    )
    active_position_all = ranked_positions(
        stats.values(),
        wins_field="wins_all",
        active_rikishi=active_rikishi,
        limit=limit,
    )
    active_position_actual = ranked_positions(
        stats.values(),
        wins_field="wins_actual",
        active_rikishi=active_rikishi,
        limit=limit,
    )

    included = set().union(
        position_all,
        position_actual,
        active_position_all,
        active_position_actual,
    )

    return [
        career_wins_row(
            stat=stats[rikishi_id],
            shikona=full_shikona_store.full_shikona(rikishi_id),
            active=rikishi_id in active_rikishi,
            position_all=position_all.get(rikishi_id, ""),
            position_actual=position_actual.get(rikishi_id, ""),
            active_position_all=active_position_all.get(rikishi_id, ""),
            active_position_actual=active_position_actual.get(rikishi_id, ""),
        )
        for rikishi_id in sorted(
            included,
            key=lambda item: (
                position_all.get(item, limit + 1),
                position_actual.get(item, limit + 1),
                active_position_all.get(item, limit + 1),
                active_position_actual.get(item, limit + 1),
                int(item),
            ),
        )
    ]


def compute_career_win_stats(history: History) -> dict[RikId, CareerWinStats]:
    """Count career wins/losses with and without fusen results."""

    stats: dict[RikId, CareerWinStats] = {}
    for date in sorted(history):
        state = history(date)
        for day in sorted(state.summary):
            daily_results = state.summary(day)
            for bout in daily_results.results_lookup.values():
                apply_outcome(
                    stats.setdefault(bout.rikishi1, CareerWinStats(bout.rikishi1)),
                    bout.outcome1,
                    AppearancePoint(date=date, day=day),
                )
                apply_outcome(
                    stats.setdefault(bout.rikishi2, CareerWinStats(bout.rikishi2)),
                    bout.outcome2,
                    AppearancePoint(date=date, day=day),
                )
    return stats


def apply_outcome(
    stat: CareerWinStats,
    outcome: Outcome,
    point: AppearancePoint,
) -> None:
    """Apply one rikishi outcome to all and actual-only career totals."""

    if outcome == Outcome.W:
        stat.wins_all += 1
        stat.wins_actual += 1
        mark_all_decision(stat, point)
        mark_actual_decision(stat, point)
    elif outcome == Outcome.L:
        stat.losses_all += 1
        stat.losses_actual += 1
        mark_all_decision(stat, point)
        mark_actual_decision(stat, point)
    elif outcome == Outcome.FS:
        stat.wins_all += 1
        mark_all_decision(stat, point)
    elif outcome == Outcome.FP:
        stat.losses_all += 1
        mark_all_decision(stat, point)


def mark_all_decision(stat: CareerWinStats, point: AppearancePoint) -> None:
    if stat.start_all is None:
        stat.start_all = point
    stat.end_all = point


def mark_actual_decision(stat: CareerWinStats, point: AppearancePoint) -> None:
    if stat.start_actual is None:
        stat.start_actual = point
    stat.end_actual = point


def ranked_positions(
    stats: Iterable[CareerWinStats],
    *,
    wins_field: str,
    active_rikishi: set[RikId] | None,
    limit: int,
) -> dict[RikId, int]:
    """Return top-N positions for one career-wins view."""

    candidates = [
        stat for stat in stats
        if getattr(stat, wins_field) > 0
        and (active_rikishi is None or stat.rikishi_id in active_rikishi)
    ]
    ranked = sorted(
        candidates,
        key=lambda stat: (
            -getattr(stat, wins_field),
            int(stat.rikishi_id),
        ),
    )[:limit]
    return {
        stat.rikishi_id: index
        for index, stat in enumerate(ranked, start=1)
    }


def career_wins_row(
    *,
    stat: CareerWinStats,
    shikona: str,
    active: bool,
    position_all: int | str,
    position_actual: int | str,
    active_position_all: int | str,
    active_position_actual: int | str,
) -> CareerWinsRow:
    bouts_all = stat.wins_all + stat.losses_all
    bouts_actual = stat.wins_actual + stat.losses_actual
    return CareerWinsRow(
        rikishi_id=int(stat.rikishi_id),
        shikona=shikona,
        active=active,
        position_all=position_all,
        position_actual=position_actual,
        active_position_all=active_position_all,
        active_position_actual=active_position_actual,
        wins_all=stat.wins_all,
        losses_all=stat.losses_all,
        bouts_all=bouts_all,
        win_rate_all=win_rate_percent(stat.wins_all, bouts_all),
        start_all=point_label(stat.start_all),
        end_all="-" if active else point_label(stat.end_all),
        wins_actual=stat.wins_actual,
        losses_actual=stat.losses_actual,
        bouts_actual=bouts_actual,
        win_rate_actual=win_rate_percent(stat.wins_actual, bouts_actual),
        start_actual=point_label(stat.start_actual),
        end_actual="-" if active else point_label(stat.end_actual),
    )


def win_rate_percent(wins: int, bouts: int) -> str:
    if bouts == 0:
        return ""
    return f"{100 * wins / bouts:.1f}"


def point_label(point: AppearancePoint | None) -> str:
    if point is None:
        return ""
    return point.label()


def write_dataclass_csv(rows: Iterable[object], output_path: Path) -> None:
    """Write dataclass rows to CSV."""

    rows = tuple(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tuple(rows[0].__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def load_history_from_zip(path: Path) -> History:
    """Load a History from a zip-backed annotated serialisation."""

    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(
        description="Produce most career-wins record candidates."
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Load History from a zip path instead of the live store.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=TOP_N_LIMIT,
        help="Number of rows to publish for each career-wins view.",
    )
    return parser


def main() -> None:
    """Run the producer."""

    args = build_parser().parse_args()
    history = load_history_from_zip(args.history_zip) if args.history_zip else get_history()
    outputs = build_career_wins_outputs(history, limit=args.limit)
    print("Wrote:")
    print(f"  Career wins: {outputs.career_wins_csv}")


if __name__ == "__main__":
    main()

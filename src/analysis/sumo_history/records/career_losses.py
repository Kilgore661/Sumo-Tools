"""Produce career-loss record candidates from History."""

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


OUTPUT_ROOT = Path("files/output/analysis/sumo_history/records/career_losses")


@dataclass(frozen=True)
class AppearancePoint:
    date: Date
    day: Day

    def label(self) -> str:
        return f"{self.date}/{int(self.day):02d}"


@dataclass
class CareerLossStats:
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
class CareerLossesRow:
    rikishi_id: int
    shikona: str
    active: bool
    position_all: int | str
    position_actual: int | str
    active_position_all: int | str
    active_position_actual: int | str
    losses_all: int
    wins_all: int
    bouts_all: int
    win_rate_all: str
    start_all: str
    end_all: str
    losses_actual: int
    wins_actual: int
    bouts_actual: int
    win_rate_actual: str
    start_actual: str
    end_actual: str


@dataclass(frozen=True)
class CareerLossesOutputs:
    output_root: Path
    career_losses_csv: Path


def build_career_losses_outputs(
    history: History,
    output_root: Path = OUTPUT_ROOT,
    *,
    limit: int = TOP_N_LIMIT,
) -> CareerLossesOutputs:
    """Write the site-facing career-losses candidate CSV."""

    full_shikona_store = FullShikonaStore.from_sources(history)
    rows = career_losses_rows(
        history=history,
        full_shikona_store=full_shikona_store,
        limit=limit,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    outputs = CareerLossesOutputs(
        output_root=output_root,
        career_losses_csv=output_root / "career_losses.csv",
    )
    write_dataclass_csv(rows, outputs.career_losses_csv)
    return outputs


def career_losses_rows(
    *,
    history: History,
    full_shikona_store: FullShikonaStore,
    limit: int,
) -> list[CareerLossesRow]:
    """Return the union of rows needed by all top-N career-losses views."""

    stats = compute_career_loss_stats(history)
    latest_date = max(history)
    active_rikishi = set(history(latest_date).banzuke.riks)

    position_all = ranked_positions(
        stats.values(),
        losses_field="losses_all",
        active_rikishi=None,
        limit=limit,
    )
    position_actual = ranked_positions(
        stats.values(),
        losses_field="losses_actual",
        active_rikishi=None,
        limit=limit,
    )
    active_position_all = ranked_positions(
        stats.values(),
        losses_field="losses_all",
        active_rikishi=active_rikishi,
        limit=limit,
    )
    active_position_actual = ranked_positions(
        stats.values(),
        losses_field="losses_actual",
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
        career_losses_row(
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


def compute_career_loss_stats(history: History) -> dict[RikId, CareerLossStats]:
    """Count career wins/losses with and without fusen results."""

    stats: dict[RikId, CareerLossStats] = {}
    for date in sorted(history):
        state = history(date)
        for day in sorted(state.summary):
            daily_results = state.summary(day)
            for bout in daily_results.results_lookup.values():
                apply_outcome(
                    stats.setdefault(bout.rikishi1, CareerLossStats(bout.rikishi1)),
                    bout.outcome1,
                    AppearancePoint(date=date, day=day),
                )
                apply_outcome(
                    stats.setdefault(bout.rikishi2, CareerLossStats(bout.rikishi2)),
                    bout.outcome2,
                    AppearancePoint(date=date, day=day),
                )
    return stats


def apply_outcome(
    stat: CareerLossStats,
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


def mark_all_decision(stat: CareerLossStats, point: AppearancePoint) -> None:
    if stat.start_all is None:
        stat.start_all = point
    stat.end_all = point


def mark_actual_decision(stat: CareerLossStats, point: AppearancePoint) -> None:
    if stat.start_actual is None:
        stat.start_actual = point
    stat.end_actual = point


def ranked_positions(
    stats: Iterable[CareerLossStats],
    *,
    losses_field: str,
    active_rikishi: set[RikId] | None,
    limit: int,
) -> dict[RikId, int]:
    """Return top-N positions for one career-losses view."""

    candidates = [
        stat for stat in stats
        if getattr(stat, losses_field) > 0
        and (active_rikishi is None or stat.rikishi_id in active_rikishi)
    ]
    ranked = sorted(
        candidates,
        key=lambda stat: (
            -getattr(stat, losses_field),
            int(stat.rikishi_id),
        ),
    )[:limit]
    return {
        stat.rikishi_id: index
        for index, stat in enumerate(ranked, start=1)
    }


def career_losses_row(
    *,
    stat: CareerLossStats,
    shikona: str,
    active: bool,
    position_all: int | str,
    position_actual: int | str,
    active_position_all: int | str,
    active_position_actual: int | str,
) -> CareerLossesRow:
    bouts_all = stat.wins_all + stat.losses_all
    bouts_actual = stat.wins_actual + stat.losses_actual
    return CareerLossesRow(
        rikishi_id=int(stat.rikishi_id),
        shikona=shikona,
        active=active,
        position_all=position_all,
        position_actual=position_actual,
        active_position_all=active_position_all,
        active_position_actual=active_position_actual,
        losses_all=stat.losses_all,
        wins_all=stat.wins_all,
        bouts_all=bouts_all,
        win_rate_all=win_rate_percent(stat.wins_all, bouts_all),
        start_all=point_label(stat.start_all),
        end_all="-" if active else point_label(stat.end_all),
        losses_actual=stat.losses_actual,
        wins_actual=stat.wins_actual,
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
        description="Produce most career-losses record candidates."
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
        help="Number of rows to publish for each career-losses view.",
    )
    return parser


def main() -> None:
    """Run the producer."""

    args = build_parser().parse_args()
    history = load_history_from_zip(args.history_zip) if args.history_zip else get_history()
    outputs = build_career_losses_outputs(history, limit=args.limit)
    print("Wrote:")
    print(f"  Career losses: {outputs.career_losses_csv}")


if __name__ == "__main__":
    main()

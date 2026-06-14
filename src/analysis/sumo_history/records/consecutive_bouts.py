"""Explore consecutive-bout record candidates from History.

This module is exploratory. It separates daily evidence from basho-level
adjudication so the eventual record-page contract can be inspected before the
final implementation is designed.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

from src.analysis.sumo_history.constants import TOP_N_LIMIT
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Division, MSD, Outcome
from src.sumo_core.BasicPrimitives import Day, Month, RikId, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import DailyResults


OUTPUT_ROOT = Path("files/output/analysis/sumo_history/records/consecutive_bouts")


class DailyAppearanceKind(Enum):
    """Classifies what the daily result record proves for one rikishi."""

    CONFIRMED_APPEARANCE = "confirmed_appearance"
    EXPLICIT_NO_SHOW = "explicit_no_show"
    NO_OBSERVABLE_FACT = "no_observable_fact"


@dataclass(frozen=True)
class AppearancePoint:
    """One confirmed appearance in History order."""

    sequence_index: int
    date: Date
    day: Day

    def label(self) -> str:
        return f"{self.date}/{int(self.day):02d}"


@dataclass(frozen=True)
class DailyAppearanceFact:
    """The daily evidence available for one banzuke-listed rikishi."""

    rikishi_id: RikId
    date: Date
    day: Day
    chii: Chii
    kind: DailyAppearanceKind


@dataclass(frozen=True)
class SanctionedAbsence:
    """A missed-day interval that does not break a consecutive-bout streak."""

    rikishi_id: RikId
    date: Date
    start_day: Day
    end_day: Day
    reason: str

    def includes(self, rikishi_id: RikId, date: Date, day: Day) -> bool:
        return (
            self.rikishi_id == rikishi_id
            and self.date == date
            and self.start_day <= day <= self.end_day
        )


SANCTIONED_ABSENCES = (
    SanctionedAbsence(
        rikishi_id=RikId(5944),
        date=Date(Year(2022), Month(7)),
        start_day=Day(13),
        end_day=Day(15),
        reason="Heya Covid quarantine withdrawal.",
    ),
)


@dataclass(frozen=True)
class RikishiBashoAppearance:
    """Basho-level diagnostic summary used to inspect streak semantics."""

    rikishi_id: int
    shikona: str
    basho: str
    chii: str
    rank_class: str
    represented_days: int
    expected_bouts: int | str
    confirmed_appearances: int
    explicit_no_shows: int
    no_observable_days: int
    sanctioned_absence_days: int
    sanctioned_absence_reason: str
    first_confirmed: str
    last_confirmed: str
    streak_survives_basho: bool
    break_precision: str


@dataclass(frozen=True)
class CompletedStreak:
    """One completed or open confirmed-appearance streak."""

    rikishi_id: RikId
    start: AppearancePoint
    end: AppearancePoint
    bouts: int
    missed_days: int
    open: bool = False


@dataclass
class RikishiStreakState:
    """Mutable streak accumulator for one rikishi during the History pass."""

    current_start: AppearancePoint | None = None
    current_end: AppearancePoint | None = None
    current_bouts: int = 0
    current_missed_days: int = 0


@dataclass(frozen=True)
class LongestStreakRow:
    """Public-table-shaped candidate row for longest consecutive bouts."""

    position: int
    rikishi_id: int
    shikona: str
    bouts: int
    clean: bool
    start: str
    end: str


@dataclass(frozen=True)
class ConsecutiveBoutsOutputs:
    """Filesystem outputs written by the exploratory producer."""

    output_root: Path
    rikishi_basho_appearance_csv: Path
    longest_streak_candidates_csv: Path


def build_consecutive_bouts_outputs(
    history: History,
    output_root: Path = OUTPUT_ROOT,
    *,
    limit: int = TOP_N_LIMIT,
    rikishi_id_filter: RikId | None = None,
) -> ConsecutiveBoutsOutputs:
    """Write diagnostic and leaderboard CSVs for consecutive-bout exploration."""

    full_shikona_store = FullShikonaStore.from_sources(history)
    diagnostics, streaks = compute_consecutive_bout_records(
        history=history,
        full_shikona_store=full_shikona_store,
        rikishi_id_filter=rikishi_id_filter,
    )
    longest_rows = longest_streak_rows(
        streaks=streaks,
        full_shikona_store=full_shikona_store,
        limit=limit,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    outputs = ConsecutiveBoutsOutputs(
        output_root=output_root,
        rikishi_basho_appearance_csv=output_root / "rikishi_basho_appearance.csv",
        longest_streak_candidates_csv=output_root / "longest_streak_candidates.csv",
    )
    write_dataclass_csv(diagnostics, outputs.rikishi_basho_appearance_csv)
    write_dataclass_csv(longest_rows, outputs.longest_streak_candidates_csv)
    return outputs


def compute_consecutive_bout_records(
    *,
    history: History,
    full_shikona_store: FullShikonaStore,
    rikishi_id_filter: RikId | None = None,
) -> tuple[list[RikishiBashoAppearance], list[CompletedStreak]]:
    """Derive basho diagnostics and completed streaks from daily facts."""

    states: dict[RikId, RikishiStreakState] = {}
    completed: list[CompletedStreak] = []
    diagnostics: list[RikishiBashoAppearance] = []
    sequence_index = 0

    for date in sorted(history):
        state = history(date)
        current_rikishi = set(state.banzuke.riks)
        if rikishi_id_filter is not None:
            current_rikishi = {rikishi_id_filter} & current_rikishi

        close_absent_rikishi_streaks(
            states=states,
            current_rikishi=current_rikishi,
            completed=completed,
            rikishi_id_filter=rikishi_id_filter,
        )

        basho_facts_by_rikishi: dict[RikId, list[DailyAppearanceFact]] = {
            rikishi_id: []
            for rikishi_id in sorted(current_rikishi, key=int)
        }

        for day in sorted(state.summary):
            sequence_index += 1
            daily_results = state.summary(day)
            facts_by_rikishi = daily_facts_for_banzuke(
                date=date,
                day=day,
                daily_results=daily_results,
                chii_by_rikishi={
                    rikishi_id: state.banzuke.get_chii(rikishi_id)
                    for rikishi_id in current_rikishi
                },
            )
            for rikishi_id, fact in facts_by_rikishi.items():
                basho_facts_by_rikishi[rikishi_id].append(fact)
                apply_daily_fact(
                    fact=fact,
                    sequence_index=sequence_index,
                    states=states,
                    completed=completed,
                )

        for rikishi_id, facts in basho_facts_by_rikishi.items():
            summary = summarize_basho_facts(
                facts=facts,
                shikona=full_shikona_store.full_shikona(rikishi_id),
            )
            diagnostics.append(summary)
            apply_basho_adjudication(
                summary=summary,
                rikishi_id=rikishi_id,
                states=states,
                completed=completed,
            )

    close_all_streaks(states, completed)
    return diagnostics, completed


def daily_facts_for_banzuke(
    *,
    date: Date,
    day: Day,
    daily_results: DailyResults,
    chii_by_rikishi: dict[RikId, Chii],
) -> dict[RikId, DailyAppearanceFact]:
    """Return one daily fact for every inspected banzuke-listed rikishi."""

    kinds_by_rikishi: dict[RikId, DailyAppearanceKind] = {}
    for bout in daily_results.results_lookup.values():
        kinds_by_rikishi[bout.rikishi1] = kind_for_outcome(bout.outcome1)
        kinds_by_rikishi[bout.rikishi2] = kind_for_outcome(bout.outcome2)

    return {
        rikishi_id: DailyAppearanceFact(
            rikishi_id=rikishi_id,
            date=date,
            day=day,
            chii=chii,
            kind=kinds_by_rikishi.get(
                rikishi_id,
                DailyAppearanceKind.NO_OBSERVABLE_FACT,
            ),
        )
        for rikishi_id, chii in chii_by_rikishi.items()
    }


def kind_for_outcome(outcome: Outcome) -> DailyAppearanceKind:
    """Classify one recorded rikishi outcome as appearance evidence."""

    if outcome == Outcome.FP:
        return DailyAppearanceKind.EXPLICIT_NO_SHOW
    return DailyAppearanceKind.CONFIRMED_APPEARANCE


def apply_daily_fact(
    *,
    fact: DailyAppearanceFact,
    sequence_index: int,
    states: dict[RikId, RikishiStreakState],
    completed: list[CompletedStreak],
) -> None:
    """Apply precise daily evidence to the current streak state."""

    state = states.setdefault(fact.rikishi_id, RikishiStreakState())
    if sanctioned_absence_for(fact) is not None:
        if state.current_start is not None:
            state.current_missed_days += 1
        return

    if fact.kind == DailyAppearanceKind.CONFIRMED_APPEARANCE:
        append_appearance(
            state,
            AppearancePoint(sequence_index=sequence_index, date=fact.date, day=fact.day),
        )
        return

    if fact.kind == DailyAppearanceKind.EXPLICIT_NO_SHOW:
        close_streak(fact.rikishi_id, state, completed)
        return

    if is_sekitori(fact.chii):
        close_streak(fact.rikishi_id, state, completed)


def apply_basho_adjudication(
    *,
    summary: RikishiBashoAppearance,
    rikishi_id: RikId,
    states: dict[RikId, RikishiStreakState],
    completed: list[CompletedStreak],
) -> None:
    """Apply basho-end non-sekitori adjudication for unknown missed days."""

    if summary.break_precision != "basho_only":
        return
    state = states.setdefault(rikishi_id, RikishiStreakState())
    close_streak(rikishi_id, state, completed)


def append_appearance(state: RikishiStreakState, point: AppearancePoint) -> None:
    """Extend a rikishi streak with one confirmed appearance."""

    if state.current_start is None:
        state.current_start = point
    state.current_end = point
    state.current_bouts += 1


def close_streak(
    rikishi_id: RikId,
    state: RikishiStreakState,
    completed: list[CompletedStreak],
) -> None:
    """Close the current streak if it contains confirmed appearances."""

    if state.current_start is None or state.current_end is None:
        return
    completed.append(
        CompletedStreak(
            rikishi_id=rikishi_id,
            start=state.current_start,
            end=state.current_end,
            bouts=state.current_bouts,
            missed_days=state.current_missed_days,
            open=False,
        )
    )
    state.current_start = None
    state.current_end = None
    state.current_bouts = 0
    state.current_missed_days = 0


def close_absent_rikishi_streaks(
    *,
    states: dict[RikId, RikishiStreakState],
    current_rikishi: set[RikId],
    completed: list[CompletedStreak],
    rikishi_id_filter: RikId | None,
) -> None:
    """Close active streaks for rikishi absent from the current banzuke."""

    for rikishi_id, state in sorted(states.items(), key=lambda item: int(item[0])):
        if rikishi_id_filter is not None and rikishi_id != rikishi_id_filter:
            continue
        if rikishi_id not in current_rikishi:
            close_streak(rikishi_id, state, completed)


def close_all_streaks(
    states: dict[RikId, RikishiStreakState],
    completed: list[CompletedStreak],
) -> None:
    """Close all remaining open streaks at the end of the supplied History."""

    for rikishi_id, state in sorted(states.items(), key=lambda item: int(item[0])):
        close_open_streak(rikishi_id, state, completed)


def close_open_streak(
    rikishi_id: RikId,
    state: RikishiStreakState,
    completed: list[CompletedStreak],
) -> None:
    """Record a streak that remains open at the end of the supplied History."""

    if state.current_start is None or state.current_end is None:
        return
    completed.append(
        CompletedStreak(
            rikishi_id=rikishi_id,
            start=state.current_start,
            end=state.current_end,
            bouts=state.current_bouts,
            missed_days=state.current_missed_days,
            open=True,
        )
    )
    state.current_start = None
    state.current_end = None
    state.current_bouts = 0
    state.current_missed_days = 0


def summarize_basho_facts(
    *,
    facts: list[DailyAppearanceFact],
    shikona: str,
) -> RikishiBashoAppearance:
    """Summarize one rikishi's basho evidence for inspection."""

    first_fact = facts[0]
    confirmed = [
        fact for fact in facts
        if fact.kind == DailyAppearanceKind.CONFIRMED_APPEARANCE
    ]
    explicit_no_shows = [
        fact for fact in facts
        if fact.kind == DailyAppearanceKind.EXPLICIT_NO_SHOW
    ]
    no_observable = [
        fact for fact in facts
        if fact.kind == DailyAppearanceKind.NO_OBSERVABLE_FACT
    ]
    sanctioned_facts = [
        fact for fact in facts
        if sanctioned_absence_for(fact) is not None
    ]
    unsanctioned_explicit_no_show_count = sum(
        1 for fact in explicit_no_shows
        if sanctioned_absence_for(fact) is None
    )
    expected_bouts = expected_bouts_for(first_fact.chii, represented_days=len(facts))
    survives, break_precision = adjudicate_basho(
        chii=first_fact.chii,
        represented_days=len(facts),
        expected_bouts=expected_bouts,
        confirmed_count=len(confirmed),
        explicit_no_show_count=unsanctioned_explicit_no_show_count,
        sanctioned_absence_count=len(sanctioned_facts),
    )
    return RikishiBashoAppearance(
        rikishi_id=int(first_fact.rikishi_id),
        shikona=shikona,
        basho=str(first_fact.date),
        chii=str(first_fact.chii),
        rank_class=rank_class(first_fact.chii),
        represented_days=len(facts),
        expected_bouts=expected_bouts if expected_bouts is not None else "",
        confirmed_appearances=len(confirmed),
        explicit_no_shows=len(explicit_no_shows),
        no_observable_days=len(no_observable),
        sanctioned_absence_days=len(sanctioned_facts),
        sanctioned_absence_reason=sanctioned_absence_reason(sanctioned_facts),
        first_confirmed=str(confirmed[0].day) if confirmed else "",
        last_confirmed=str(confirmed[-1].day) if confirmed else "",
        streak_survives_basho=survives,
        break_precision=break_precision,
    )


def adjudicate_basho(
    *,
    chii: Chii,
    represented_days: int,
    expected_bouts: int | None,
    confirmed_count: int,
    explicit_no_show_count: int,
    sanctioned_absence_count: int,
) -> tuple[bool, str]:
    """Decide whether unresolved daily gaps break the streak at basho end."""

    if explicit_no_show_count:
        return False, "explicit_day"

    if is_sekitori(chii):
        if confirmed_count + sanctioned_absence_count == represented_days:
            return True, "none"
        return False, "missing_daily_appearance"

    if expected_bouts is None:
        return True, "partial_basho_unadjudicated"

    if confirmed_count >= expected_bouts:
        return True, "none"
    return False, "basho_only"


def is_sekitori(chii: Chii) -> bool:
    """Return whether a chii belongs to makuuchi or juryo."""

    return isinstance(chii.level, MSD) or chii.level == Division.JURYO


def expected_bouts_for(chii: Chii, *, represented_days: int) -> int | None:
    """Return expected appearances for streak adjudication."""

    if is_sekitori(chii):
        return represented_days
    if represented_days < 15:
        return None
    return 7


def rank_class(chii: Chii) -> str:
    """Return the broad participation class for diagnostics."""

    if is_sekitori(chii):
        return "sekitori"
    return "non_sekitori"


def sanctioned_absence_for(fact: DailyAppearanceFact) -> SanctionedAbsence | None:
    """Return the sanctioned absence covering this daily fact, if any."""

    for absence in SANCTIONED_ABSENCES:
        if absence.includes(fact.rikishi_id, fact.date, fact.day):
            return absence
    return None


def sanctioned_absence_reason(facts: list[DailyAppearanceFact]) -> str:
    """Return the distinct sanctioned absence reasons for diagnostic output."""

    reasons = set()
    for fact in facts:
        absence = sanctioned_absence_for(fact)
        if absence is not None:
            reasons.add(absence.reason)
    return "; ".join(sorted(reasons))


def longest_streak_rows(
    *,
    streaks: list[CompletedStreak],
    full_shikona_store: FullShikonaStore,
    limit: int,
) -> list[LongestStreakRow]:
    """Return public-table-shaped rows for longest streak candidates."""

    streak_count_by_rikishi = Counter(streak.rikishi_id for streak in streaks)
    ranked = sorted(
        streaks,
        key=lambda streak: (
            -streak.bouts,
            streak.start.sequence_index,
            int(streak.rikishi_id),
        ),
    )[:limit]
    return [
        LongestStreakRow(
            position=index,
            rikishi_id=int(streak.rikishi_id),
            shikona=full_shikona_store.full_shikona(streak.rikishi_id),
            bouts=streak.bouts,
            clean=streak_count_by_rikishi[streak.rikishi_id] == 1,
            start=streak.start.label(),
            end="-" if streak.open else streak.end.label(),
        )
        for index, streak in enumerate(ranked, start=1)
    ]


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
    """Build the exploratory command-line interface."""

    parser = argparse.ArgumentParser(
        description="Explore longest consecutive-bout record candidates."
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
        help="Number of longest streak candidates to write.",
    )
    parser.add_argument(
        "--rikishi-id",
        type=int,
        help="Restrict diagnostic exploration to one rikishi id.",
    )
    return parser


def main() -> None:
    """Run the exploratory producer."""

    args = build_parser().parse_args()
    history = load_history_from_zip(args.history_zip) if args.history_zip else get_history()
    rikishi_id_filter = RikId(args.rikishi_id) if args.rikishi_id is not None else None
    outputs = build_consecutive_bouts_outputs(
        history,
        limit=args.limit,
        rikishi_id_filter=rikishi_id_filter,
    )
    print("Wrote:")
    print(f"  Diagnostics: {outputs.rikishi_basho_appearance_csv}")
    print(f"  Candidates: {outputs.longest_streak_candidates_csv}")


if __name__ == "__main__":
    main()

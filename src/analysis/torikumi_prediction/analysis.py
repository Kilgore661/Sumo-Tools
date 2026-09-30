"""Extract scheduled endpoints and aggregate opponent-class distributions."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from src.sumo_core.BasicEnums import Division, MSD, Outcome
from src.sumo_core.BasicPrimitives import Day, Pair, RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult

from .model import (
    AnalysisResult,
    BanzukeClass,
    ClassDayRow,
    ClassDayWinsRow,
    ClassRecordRow,
    Diagnostic,
    Observation,
    OverallClassRow,
)


DIVISION_ORDER = {division.name: index for index, division in enumerate(Division)}
@dataclass
class _Record:
    wins: int = 0
    losses: int = 0


def analyse(
    history: History,
    *,
    start: Date | None = None,
    end: Date | None = None,
) -> AnalysisResult:
    """Build directed scheduled-bout observations for every banzuke division."""

    if not history:
        raise ValueError("History is empty")
    if start is not None and end is not None and end < start:
        raise ValueError("End must not precede start")

    dates = sorted(
        date
        for date in history
        if (start is None or date >= start) and (end is None or date <= end)
    )
    if not dates:
        raise ValueError("No basho in the selected date range")
    completed_dates = [date for date in dates if Day(15) in history[date].summary]
    if not completed_dates:
        raise ValueError("No completed basho in the selected date range")

    observations: list[Observation] = []
    diagnostics: list[Diagnostic] = []
    scheduled_bout_count = 0
    class_keys: dict[str, tuple[int, int]] = {"Mz": (10, 0)}

    for basho_date in completed_dates:
        basho = history[basho_date]
        date_label = str(basho_date)
        ranks = basho.banzuke.rikchii
        roster = sorted(ranks, key=lambda rikishi: ranks[rikishi].ordinal())
        positions = {rikishi: index for index, rikishi in enumerate(roster, start=1)}
        for chii in ranks.values():
            rank_class = BanzukeClass.from_chii(chii)
            class_keys[rank_class.label] = rank_class.sort_key

        records: defaultdict[RikId, _Record] = defaultdict(_Record)
        seen_pairs: set[Pair] = set()
        for day in sorted(basho.summary):
            daily = basho.summary[day]
            scheduled_pairs = set(daily.torikumi)
            result_pairs = set(daily.results_lookup)
            scheduled_bout_count += len(scheduled_pairs)

            for pair in sorted(scheduled_pairs - result_pairs):
                diagnostics.append(_pair_diagnostic(
                    "scheduled_without_result", date_label, day, pair,
                    "Scheduled pair has no corresponding result record.",
                ))
            for pair in sorted(result_pairs - scheduled_pairs):
                diagnostics.append(_pair_diagnostic(
                    "result_without_schedule", date_label, day, pair,
                    "Result pair is absent from the day's torikumi.",
                ))

            participation = Counter(rikishi for pair in scheduled_pairs for rikishi in pair)
            for rikishi, count in sorted(participation.items()):
                if count > 1:
                    diagnostics.append(Diagnostic(
                        "duplicate_daily_participation", date_label, int(day),
                        int(rikishi), None,
                        f"Rikishi appears in {count} scheduled pairs.",
                    ))

            for pair in sorted(scheduled_pairs):
                if pair in seen_pairs:
                    diagnostics.append(_pair_diagnostic(
                        "repeated_regular_opponent", date_label, day, pair,
                        "Pair has already appeared earlier in this basho.",
                    ))
                seen_pairs.add(pair)
                result = daily.results_lookup.get(pair)
                fusen = result is not None and _is_fusen(result)
                for focal, opponent in ((pair[0], pair[1]), (pair[1], pair[0])):
                    focal_chii = ranks.get(focal)
                    opponent_chii = ranks.get(opponent)
                    if focal_chii is None:
                        diagnostics.append(Diagnostic(
                            "missing_focal_chii", date_label, int(day), int(focal),
                            int(opponent),
                            "Unranked participant cannot contribute a focal observation.",
                        ))
                        continue

                    focal_class = BanzukeClass.from_chii(focal_chii)
                    focal_division = focal_class.division.name
                    if opponent_chii is None:
                        opponent_class_label = "Mz"
                        opponent_division = ""
                        opponent_chii_label = ""
                        opponent_position = None
                        diagnostics.append(Diagnostic(
                            "missing_opponent_chii", date_label, int(day), int(focal),
                            int(opponent),
                            "Ranked focal observation retains an unranked opponent as Mz.",
                        ))
                    else:
                        opponent_class = BanzukeClass.from_chii(opponent_chii)
                        opponent_class_label = opponent_class.label
                        opponent_division = opponent_class.division.name
                        opponent_chii_label = str(opponent_chii)
                        opponent_position = positions[opponent]

                    record = records[focal]
                    focal_position = positions[focal]
                    observations.append(Observation(
                        basho=date_label,
                        day=int(day),
                        focal_id=int(focal),
                        focal_chii=str(focal_chii),
                        focal_class=focal_class.label,
                        focal_division=focal_division,
                        opponent_id=int(opponent),
                        opponent_chii=opponent_chii_label,
                        opponent_class=opponent_class_label,
                        opponent_division=opponent_division,
                        wins_before=record.wins,
                        losses_before=record.losses,
                        bouts_before=record.wins + record.losses,
                        bout_number=record.wins + record.losses + 1,
                        cross_division=(
                            bool(opponent_division)
                            and focal_division != opponent_division
                        ),
                        fusen=fusen,
                        focal_roster_position=focal_position,
                        opponent_roster_position=opponent_position,
                        roster_position_delta=(
                            None if opponent_position is None
                            else opponent_position - focal_position
                        ),
                    ))

            for result in daily.results_lookup.values():
                _advance_record(records, result, date_label, int(day))

    observation_tuple = tuple(sorted(
        observations,
        key=lambda row: (row.basho, row.day, row.focal_roster_position, row.opponent_id),
    ))
    return AnalysisResult(
        history_first_basho=str(dates[0]),
        history_last_basho=str(dates[-1]),
        history_basho_count=len(dates),
        included_first_basho=str(completed_dates[0]),
        included_last_basho=str(completed_dates[-1]),
        included_basho_count=len(completed_dates),
        excluded_incomplete_basho_count=len(dates) - len(completed_dates),
        scheduled_bout_count=scheduled_bout_count,
        observations=observation_tuple,
        class_by_day=_aggregate_class_day(observation_tuple, class_keys),
        class_by_day_wins=_aggregate_class_day_wins(observation_tuple, class_keys),
        class_by_record=_aggregate_class_record(observation_tuple, class_keys),
        overall_class=_aggregate_overall(observation_tuple, class_keys),
        diagnostics=tuple(sorted(
            diagnostics,
            key=lambda row: (
                row.basho, row.day or 0, row.kind, row.rikishi1 or 0, row.rikishi2 or 0
            ),
        )),
    )


def _advance_record(
    records: defaultdict[RikId, _Record],
    result: BoutResult,
    basho: str,
    day: int,
) -> None:
    for rikishi, outcome in (
        (result.rikishi1, result.outcome1),
        (result.rikishi2, result.outcome2),
    ):
        if outcome in {Outcome.W, Outcome.FS}:
            records[rikishi].wins += 1
        elif outcome in {Outcome.L, Outcome.FP}:
            records[rikishi].losses += 1
        elif outcome == Outcome.DRAW:
            raise ValueError(
                f"Draw result is outside the torikumi-prediction contract: "
                f"{basho} Day {day}, rikishi {int(rikishi)}"
            )
        else:
            raise ValueError(f"Unsupported outcome {outcome!r} in {basho} Day {day}")


def _is_fusen(result: BoutResult) -> bool:
    return result.decision == "fusen" or {
        result.outcome1, result.outcome2
    } == {Outcome.FS, Outcome.FP}


def _pair_diagnostic(kind: str, basho: str, day: Day, pair: Pair, detail: str) -> Diagnostic:
    return Diagnostic(kind, basho, int(day), int(pair[0]), int(pair[1]), detail)


def _sort_prefix(row, class_keys: dict[str, tuple[int, int]]) -> tuple:
    return (
        DIVISION_ORDER[row[0]],
        class_keys[row[1]],
        *row[2:-1],
        class_keys[row[-1]],
    )


def _count_rows(observations: tuple[Observation, ...], attributes: tuple[str, ...]):
    counts = Counter(
        tuple(getattr(observation, attribute) for attribute in attributes)
        + (observation.opponent_class,)
        for observation in observations
    )
    totals = Counter()
    for key, count in counts.items():
        totals[key[:-1]] += count
    return counts, totals


def _aggregate_class_day(
    observations: tuple[Observation, ...], class_keys: dict[str, tuple[int, int]]
) -> tuple[ClassDayRow, ...]:
    counts, totals = _count_rows(observations, ("focal_division", "focal_class", "day"))
    return tuple(
        ClassDayRow(*key[:-1], key[-1], count, totals[key[:-1]], count / totals[key[:-1]])
        for key, count in sorted(counts.items(), key=lambda item: _sort_prefix(item[0], class_keys))
    )


def _aggregate_class_day_wins(
    observations: tuple[Observation, ...], class_keys: dict[str, tuple[int, int]]
) -> tuple[ClassDayWinsRow, ...]:
    counts, totals = _count_rows(
        observations, ("focal_division", "focal_class", "day", "wins_before")
    )
    return tuple(
        ClassDayWinsRow(*key[:-1], key[-1], count, totals[key[:-1]], count / totals[key[:-1]])
        for key, count in sorted(counts.items(), key=lambda item: _sort_prefix(item[0], class_keys))
    )


def _aggregate_class_record(
    observations: tuple[Observation, ...], class_keys: dict[str, tuple[int, int]]
) -> tuple[ClassRecordRow, ...]:
    attributes = (
        "focal_division", "focal_class", "day", "wins_before", "losses_before",
        "bouts_before", "bout_number",
    )
    counts, totals = _count_rows(observations, attributes)
    return tuple(
        ClassRecordRow(*key[:-1], key[-1], count, totals[key[:-1]], count / totals[key[:-1]])
        for key, count in sorted(counts.items(), key=lambda item: _sort_prefix(item[0], class_keys))
    )


def _aggregate_overall(
    observations: tuple[Observation, ...], class_keys: dict[str, tuple[int, int]]
) -> tuple[OverallClassRow, ...]:
    counts, totals = _count_rows(observations, ("focal_division", "focal_class"))
    return tuple(
        OverallClassRow(*key[:-1], key[-1], count, totals[key[:-1]], count / totals[key[:-1]])
        for key, count in sorted(counts.items(), key=lambda item: _sort_prefix(item[0], class_keys))
    )

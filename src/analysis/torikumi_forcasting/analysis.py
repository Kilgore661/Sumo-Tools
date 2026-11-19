"""Build and score historical greedy torikumi forecasts."""

from __future__ import annotations

from collections import Counter, defaultdict

from src.sumo_core.BasicEnums import MSD, Outcome
from src.sumo_core.BasicPrimitives import Day, Pair, RikId
from src.sumo_core.History import Date, History

from .greedy import forecast_greedily
from .heya import HeyaIndex
from .model import AnalysisResult, CaseExclusion, CaseResult, ForecastCase, Standing


HOLDOUT_BASHO_COUNT = 12


class NonMinimalCrossDivisionCase(ValueError):
    def __init__(
        self,
        *,
        basho: Date,
        day: int,
        population_size: int,
        actual_unmatched_count: int,
    ) -> None:
        self.exclusion = CaseExclusion(
            basho=basho,
            day=day,
            population_size=population_size,
            actual_unmatched_count=actual_unmatched_count,
            parity_minimum=population_size % 2,
            reason="cross_division_count_exceeds_parity_minimum",
        )
        super().__init__(
            f"additional cross-division bouts for {basho} Day {day}: "
            f"population={population_size}, unmatched={actual_unmatched_count}"
        )


def analyse_greedy(
    history: History,
    heya_index: HeyaIndex,
    *,
    start: Date | None = None,
    end: Date | None = None,
    first_day: int = 11,
) -> AnalysisResult:
    if not 1 <= first_day <= 15:
        raise ValueError(f"first_day must be from 1 through 15, got {first_day}")
    if start is not None and end is not None and end < start:
        raise ValueError("End must not precede start")

    selected_dates = sorted(
        date
        for date in history
        if (start is None or date >= start) and (end is None or date <= end)
    )
    if not selected_dates:
        raise ValueError("No basho in the selected date range")

    completed_dates = [
        date for date in selected_dates if Day(15) in history[date].summary
    ]
    if not completed_dates:
        raise ValueError("No completed basho in the selected date range")

    holdout_dates = (
        frozenset(completed_dates[-HOLDOUT_BASHO_COUNT:])
        if len(completed_dates) >= HOLDOUT_BASHO_COUNT + 1
        else frozenset()
    )
    holdout_first = min(holdout_dates) if holdout_dates else None
    results: list[CaseResult] = []
    exclusions: list[CaseExclusion] = []

    for basho_date in completed_dates:
        basho = history[basho_date]
        for day in range(first_day, 16):
            try:
                case = build_case(history, heya_index, basho_date, day)
            except NonMinimalCrossDivisionCase as error:
                exclusions.append(error.exclusion)
                continue
            forecast = forecast_greedily(case)
            predicted_pairs = frozenset(pair.pair for pair in forecast.pairs)
            recovered = len(predicted_pairs & case.actual_pairs)
            recovery_rate = recovered / len(case.actual_pairs)
            predicted_unmatched = tuple(row.rikid for row in forecast.unpaired)
            unmatched_correct = (
                predicted_unmatched == case.actual_unmatched
                if case.actual_unmatched
                else None
            )
            results.append(
                CaseResult(
                    case=case,
                    forecast=forecast,
                    split="holdout" if basho_date in holdout_dates else "development",
                    recovered_pairs=recovered,
                    pair_recovery_rate=recovery_rate,
                    unmatched_correct=unmatched_correct,
                    exact=(
                        forecast.success
                        and predicted_pairs == case.actual_pairs
                        and predicted_unmatched == case.actual_unmatched
                    ),
                )
            )

    return AnalysisResult(
        selected_first_basho=selected_dates[0],
        selected_last_basho=selected_dates[-1],
        included_basho_count=len(completed_dates),
        excluded_incomplete_basho_count=len(selected_dates) - len(completed_dates),
        first_day=first_day,
        holdout_first_basho=holdout_first,
        cases=tuple(results),
        exclusions=tuple(exclusions),
    )


def build_case(
    history: History,
    heya_index: HeyaIndex,
    basho_date: Date,
    day: int,
) -> ForecastCase:
    if not 1 <= day <= 15:
        raise ValueError(f"day must be from 1 through 15, got {day}")
    basho = history[basho_date]
    target = basho.summary(Day(day))
    if target is None:
        raise ValueError(f"missing target torikumi for {basho_date} Day {day}")

    ranks = basho.banzuke.rikchii
    population = frozenset(
        rikishi
        for pair in target.torikumi
        for rikishi in pair
        if rikishi in ranks and isinstance(ranks[rikishi].level, MSD)
    )
    if not population:
        raise ValueError(f"empty makuuchi population for {basho_date} Day {day}")

    participation = Counter(
        rikishi
        for pair in target.torikumi
        for rikishi in pair
        if rikishi in population
    )
    duplicates = sorted(rikishi for rikishi, count in participation.items() if count != 1)
    if duplicates:
        raise ValueError(
            f"duplicate target-day participation for {basho_date} Day {day}: "
            + ", ".join(str(int(rikishi)) for rikishi in duplicates)
        )

    actual_pairs = frozenset(
        pair for pair in target.torikumi if pair[0] in population and pair[1] in population
    )
    paired_population = {rikishi for pair in actual_pairs for rikishi in pair}
    actual_unmatched = tuple(sorted(population - paired_population))
    expected_unmatched = len(population) % 2
    if len(actual_unmatched) != expected_unmatched:
        raise NonMinimalCrossDivisionCase(
            basho=basho_date,
            day=day,
            population_size=len(population),
            actual_unmatched_count=len(actual_unmatched),
        )

    wins: defaultdict[RikId, int] = defaultdict(int)
    for earlier_day in range(1, day - 1):
        daily = basho.summary(Day(earlier_day))
        if daily is None:
            raise ValueError(f"missing {basho_date} Day {earlier_day}")
        for result in daily.results_lookup.values():
            for rikishi, outcome in (
                (result.rikishi1, result.outcome1),
                (result.rikishi2, result.outcome2),
            ):
                if rikishi in population and outcome in {Outcome.W, Outcome.FS}:
                    wins[rikishi] += 1

    prior_pairs: set[Pair] = set()
    for earlier_day in range(1, day):
        daily = basho.summary(Day(earlier_day))
        if daily is None:
            raise ValueError(f"missing {basho_date} Day {earlier_day}")
        prior_pairs.update(
            pair
            for pair in daily.torikumi
            if pair[0] in population and pair[1] in population
        )

    unordered: list[tuple[RikId, str, object, int, str, bool]] = []
    for rikishi in population:
        entry = heya_index.get(basho_date, rikishi)
        heya = entry.heya if entry is not None else f"heya{int(rikishi)}"
        unordered.append(
            (
                rikishi,
                str(basho.banzuke.rikshik[rikishi]),
                ranks[rikishi],
                wins[rikishi],
                heya,
                entry is None,
            )
        )

    unordered.sort(key=lambda row: (-row[3], row[2].ordinal()))
    ordinals = [row[2].ordinal() for row in unordered]
    if len(ordinals) != len(set(ordinals)):
        raise ValueError(f"duplicate makuuchi chii for {basho_date} Day {day}")
    standings = tuple(
        Standing(
            rikid=row[0],
            shikona=row[1],
            chii=row[2],
            wins=row[3],
            heya=row[4],
            synthetic_heya=row[5],
            position=position,
        )
        for position, row in enumerate(unordered, start=1)
    )

    standing_by_id = {row.rikid: row for row in standings}
    for pair in actual_pairs:
        if pair in prior_pairs:
            raise ValueError(
                f"actual target repeats a prior pair for {basho_date} Day {day}: {pair}"
            )
        if standing_by_id[pair[0]].heya == standing_by_id[pair[1]].heya:
            raise ValueError(
                f"actual target contains same-heya pair for {basho_date} Day {day}: "
                f"{pair}, heya={standing_by_id[pair[0]].heya}"
            )

    return ForecastCase(
        basho=basho_date,
        day=day,
        standings=standings,
        prior_pairs=frozenset(prior_pairs),
        actual_pairs=actual_pairs,
        actual_unmatched=actual_unmatched,
    )

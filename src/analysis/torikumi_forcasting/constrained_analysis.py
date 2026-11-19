"""Build and score historical constrained-matching forecasts."""

from __future__ import annotations

from collections.abc import Callable

from src.sumo_core.BasicPrimitives import Day
from src.sumo_core.History import Date, History

from .analysis import HOLDOUT_BASHO_COUNT, NonMinimalCrossDivisionCase, build_case
from .constrained import forecast_with_constraints
from .heya import HeyaIndex
from .model import (
    CaseExclusion,
    ConstrainedAnalysisResult,
    ConstrainedCaseResult,
)


def analyse_constrained(
    history: History,
    heya_index: HeyaIndex,
    *,
    start: Date | None = None,
    end: Date | None = None,
    first_day: int = 11,
    progress: Callable[[str], None] | None = None,
) -> ConstrainedAnalysisResult:
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
    results: list[ConstrainedCaseResult] = []
    exclusions: list[CaseExclusion] = []

    for basho_number, basho_date in enumerate(completed_dates, start=1):
        if progress is not None:
            progress(
                f"[constrained] basho {basho_number:,}/{len(completed_dates):,}: "
                f"{basho_date}"
            )
        for day in range(first_day, 16):
            try:
                case = build_case(history, heya_index, basho_date, day)
            except NonMinimalCrossDivisionCase as error:
                exclusions.append(error.exclusion)
                continue
            forecast = forecast_with_constraints(case)
            if forecast.status == "INFEASIBLE":
                results.append(
                    ConstrainedCaseResult(
                        case=case,
                        forecast=forecast,
                        split=(
                            "holdout"
                            if basho_date in holdout_dates
                            else "development"
                        ),
                        recovered_pairs=0,
                        pair_recovery_rate=0.0,
                        unmatched_correct=(False if case.actual_unmatched else None),
                        exact=False,
                    )
                )
                continue
            predicted_pairs = frozenset(pair.pair for pair in forecast.pairs)
            recovered = len(predicted_pairs & case.actual_pairs)
            predicted_unmatched = tuple(row.rikid for row in forecast.unpaired)
            unmatched_correct = (
                predicted_unmatched == case.actual_unmatched
                if case.actual_unmatched
                else None
            )
            results.append(
                ConstrainedCaseResult(
                    case=case,
                    forecast=forecast,
                    split="holdout" if basho_date in holdout_dates else "development",
                    recovered_pairs=recovered,
                    pair_recovery_rate=recovered / len(case.actual_pairs),
                    unmatched_correct=unmatched_correct,
                    exact=(
                        predicted_pairs == case.actual_pairs
                        and predicted_unmatched == case.actual_unmatched
                    ),
                )
            )

    return ConstrainedAnalysisResult(
        selected_first_basho=selected_dates[0],
        selected_last_basho=selected_dates[-1],
        included_basho_count=len(completed_dates),
        excluded_incomplete_basho_count=len(selected_dates) - len(completed_dates),
        first_day=first_day,
        holdout_first_basho=min(holdout_dates) if holdout_dates else None,
        cases=tuple(results),
        exclusions=tuple(exclusions),
    )

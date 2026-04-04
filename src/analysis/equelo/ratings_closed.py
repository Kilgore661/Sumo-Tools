from dataclasses import dataclass
from typing import Any, TypeAlias

from ...sumo_core.History import History, Date
from ...sumo_core.BashoState import BashoState
from ...sumo_core.Banzuke import Banzuke
from ...sumo_core.Summary import Summary, DailyResults, BoutResult
from ...sumo_core.BasicPrimitives import RikId, Day

from .EloParams import EloParams
from .diagnostics_closed import RatingsDiagnostics, DiagnosticsCollector


Bios = dict[RikId, dict[str, Any]]

DailyRatings: TypeAlias = dict[RikId, float]
BashoRatings: TypeAlias = dict[Day, DailyRatings]
Ratings: TypeAlias = dict[Date, BashoRatings]


@dataclass
class RatingsResults:
    ratings: Ratings
    diagnostics: RatingsDiagnostics


def expect(ra: float, rb: float, q: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((rb - ra) / q))


def _is_retired_before_date(
    rikid: RikId,
    current_date: Date,
    bios: Bios,
) -> bool:
    if rikid not in bios:
        return False

    intai_date = bios[rikid].get("intai_date")
    if intai_date is None:
        return False

    intai_year, intai_month = map(int, intai_date[:7].split("-"))
    return (
        intai_year < current_date.year
        or (intai_year == current_date.year and intai_month < current_date.month)
    )


def _handle_retirements(
    current_ratings: DailyRatings,
    bios: Bios,
    date: Date,
    diagnostics: DiagnosticsCollector,
    closed: bool,
) -> None:
    retirees = [
        rikid
        for rikid in list(current_ratings.keys())
        if _is_retired_before_date(rikid, date, bios)
    ]

    for rikid in sorted(retirees):
        rating = current_ratings[rikid]
        mean_before = sum(current_ratings.values()) / len(current_ratings)
        n = len(current_ratings) - 1

        delta = mean_before - rating
        delta_per_rikishi = (delta / n) if n > 0 else 0.0

        del current_ratings[rikid]

        if closed and n > 0:
            for survivor in current_ratings:
                current_ratings[survivor] -= delta_per_rikishi

        diagnostics.on_retirement(
            date=date,
            rikid=rikid,
            rating=rating,
            n=n,
            delta=delta,
            delta_per_rikishi=delta_per_rikishi if closed and n > 0 else 0.0,
            abs_delta_per_rikishi=abs(delta_per_rikishi) if closed and n > 0 else 0.0,
            closed=closed,
        )


def _initialise_basho_rikishi(
    current_ratings: DailyRatings,
    banzuke: Banzuke,
    params: EloParams,
    diagnostics: DiagnosticsCollector,
    date: Date,
) -> None:
    for rid in banzuke.riks:
        if rid not in current_ratings:
            current_ratings[rid] = params.b
            diagnostics.on_entry(
                date=date,
                rikid=rid,
                rating=params.b,
                ratings=current_ratings,
            )


def _apply_bout_result(
    current_ratings: DailyRatings,
    banzuke: Banzuke,
    bout: BoutResult,
    params: EloParams,
    diagnostics: DiagnosticsCollector,
    date: Date,
    day: Day,
) -> None:
    if bout.decision in ("fusen", "blank"):
        diagnostics.on_ignored_bout(date=date, day=day, bout=bout)
        return

    r1 = bout.rikishi1
    r2 = bout.rikishi2

    ra_before = current_ratings[r1]
    rb_before = current_ratings[r2]
    rating_mass_before = sum(current_ratings.values())

    actual_a = 1.0 if bout.outcome1.name == "W" else 0.0
    expected_a = expect(ra_before, rb_before, params.q)

    ordinal_a = banzuke.rikchii[r1].ordinal()
    k = params.k(ordinal_a)

    delta = k * (actual_a - expected_a)

    current_ratings[r1] += delta
    current_ratings[r2] -= delta

    diagnostics.on_bout(
        date=date,
        day=day,
        bout=bout,
        delta=delta,
        r1_before=ra_before,
        r2_before=rb_before,
        r1_after=current_ratings[r1],
        r2_after=current_ratings[r2],
        rating_mass_before=rating_mass_before,
        rating_mass_after=sum(current_ratings.values()),
    )


def _process_day(
    current_ratings: DailyRatings,
    banzuke: Banzuke,
    daily_results: DailyResults,
    params: EloParams,
    diagnostics: DiagnosticsCollector,
    date: Date,
    day: Day,
) -> DailyRatings:
    updated = current_ratings.copy()

    diagnostics.on_day_start(date=date, day=day, ratings=updated)

    for bout in daily_results.results_lookup.values():
        _apply_bout_result(
            current_ratings=updated,
            banzuke=banzuke,
            bout=bout,
            params=params,
            diagnostics=diagnostics,
            date=date,
            day=day,
        )

    diagnostics.on_day_end(date=date, day=day, ratings=updated)
    return updated


def get_ratings_and_diagnostics(
    history: History,
    params: EloParams,
    bios: Bios | None = None,
    closed: bool = False,
) -> RatingsResults:
    ratings: Ratings = {}
    current_ratings: DailyRatings = {}
    diagnostics = DiagnosticsCollector(params, closed=closed)
    bios = {} if bios is None else bios

    for date in sorted(history.keys()):
        basho_state: BashoState = history[date]
        banzuke: Banzuke = basho_state.banzuke
        summary: Summary = basho_state.summary

        diagnostics.on_basho_start(date=date, ratings=current_ratings, banzuke=banzuke)

        _handle_retirements(
            current_ratings=current_ratings,
            bios=bios,
            date=date,
            diagnostics=diagnostics,
            closed=closed,
        )

        _initialise_basho_rikishi(
            current_ratings=current_ratings,
            banzuke=banzuke,
            params=params,
            diagnostics=diagnostics,
            date=date,
        )

        basho_ratings: BashoRatings = {}

        for day in sorted(summary.keys()):
            current_ratings = _process_day(
                current_ratings=current_ratings,
                banzuke=banzuke,
                daily_results=summary[day],
                params=params,
                diagnostics=diagnostics,
                date=date,
                day=day,
            )
            basho_ratings[day] = current_ratings.copy()

        diagnostics.on_basho_end(date=date, ratings=current_ratings, banzuke=banzuke)
        ratings[date] = basho_ratings

    return RatingsResults(ratings=ratings, diagnostics=diagnostics.finalise())

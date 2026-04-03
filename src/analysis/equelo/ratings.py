# src/analysis/equelo/ratings.py

from dataclasses import dataclass
from typing import TypeAlias

from ...sumo_core.History import History, Date
from ...sumo_core.BashoState import BashoState
from ...sumo_core.Banzuke import Banzuke
from ...sumo_core.Summary import Summary, DailyResults, BoutResult
from ...sumo_core.BasicPrimitives import RikId, Day

from .EloParams import EloParams
from .diagnostics import RatingsDiagnostics, DiagnosticsCollector


################################################################################
# Types
################################################################################

DailyRatings: TypeAlias = dict[RikId, float]
BashoRatings: TypeAlias = dict[Day, DailyRatings]
Ratings: TypeAlias = dict[Date, BashoRatings]


################################################################################
# Results
################################################################################

@dataclass
class RatingsResults:
    ratings: Ratings
    diagnostics: RatingsDiagnostics


################################################################################
# Elo helpers
################################################################################

def expect(ra: float, rb: float, q: float) -> float:
    """
    Expected score for A against B under Elo(q).
    """
    return 1.0 / (1.0 + 10.0 ** ((rb - ra) / q))


def _initialise_basho_rikishi(
    current_ratings: DailyRatings,
    banzuke: Banzuke,
    params: EloParams,
    diagnostics: DiagnosticsCollector,
    date: Date,
) -> None:
    """
    Ensure every rikishi on the current banzuke has a rating.

    Policy:
    - a rikishi first seen on a banzuke enters at params.b
    """
    for rid in banzuke.riks:
        if rid not in current_ratings:
            current_ratings[rid] = params.b
            diagnostics.on_entry(date=date, rikid=rid, rating=params.b, ratings=current_ratings)


def _apply_bout_result(
    current_ratings: DailyRatings,
    banzuke: Banzuke,
    bout: BoutResult,
    params: EloParams,
    diagnostics: DiagnosticsCollector,
    date: Date,
    day: Day,
) -> None:
    """
    Apply one Elo update in place.

    Preconditions established by the oracle:
    - every bout participant is on the banzuke
    - every banzuke rikishi already has a rating

    Policy:
    - "fusen" is ignored as a rating event
    - "blank" is ignored as a rating event
    """
    if bout.decision in ("fusen", "blank"):
        diagnostics.on_ignored_bout(date=date, day=day, bout=bout)
        return

    r1 = bout.rikishi1
    r2 = bout.rikishi2

    ra_before = current_ratings[r1]
    rb_before = current_ratings[r2]

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
    """
    Process one real day and return end-of-day ratings.
    """
    updated = current_ratings.copy()

    diagnostics.on_day_start(
        date=date,
        day=day,
        ratings=updated,
    )

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

    diagnostics.on_day_end(
        date=date,
        day=day,
        ratings=updated,
    )

    return updated


################################################################################
# Main API
################################################################################

def get_ratings_and_diagnostics(
    history: History,
    params: EloParams,
) -> RatingsResults:
    """
    Single-pass Elo calculation over oracle-quality history.

    Output convention:
        ratings[date][day][rik_id]

    means the rating of rik_id after processing that real day.
    """
    ratings: Ratings = {}
    current_ratings: DailyRatings = {}
    diagnostics = DiagnosticsCollector(params)

    for date in sorted(history.keys()):
        basho_state: BashoState = history[date]
        banzuke: Banzuke = basho_state.banzuke
        summary: Summary = basho_state.summary

        diagnostics.on_basho_start(
            date=date,
            ratings=current_ratings,
            banzuke=banzuke,
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
            daily_results: DailyResults = summary[day]

            current_ratings = _process_day(
                current_ratings=current_ratings,
                banzuke=banzuke,
                daily_results=daily_results,
                params=params,
                diagnostics=diagnostics,
                date=date,
                day=day,
            )

            basho_ratings[day] = current_ratings.copy()

        diagnostics.on_basho_end(
            date=date,
            ratings=current_ratings,
        )

        ratings[date] = basho_ratings

    return RatingsResults(
        ratings=ratings,
        diagnostics=diagnostics.finalise(),
    )

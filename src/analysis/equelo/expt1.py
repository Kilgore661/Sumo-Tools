# src/analysis/equelo/expt1.py

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Any, TypeAlias

from ...infra.connect import connect

from ...sumo_core.History import History, Date
from ...sumo_core.BashoState import BashoState
from ...sumo_core.Banzuke import Banzuke
from ...sumo_core.Summary import Summary, DailyResults, BoutResult
from ...sumo_core.BasicPrimitives import RikId, Day, Year, Month

from .EloParams import EloParams
from .Oracle import Oracle, make_oracle


################################################################################
# Types
################################################################################

Bios: TypeAlias = dict[RikId, dict[str, Any]]

DailyRatings: TypeAlias = dict[RikId, float]
BashoRatings: TypeAlias = dict[Day, DailyRatings]
Ratings: TypeAlias = dict[Date, BashoRatings]


################################################################################
# Results
################################################################################

@dataclass
class RatingsDiagnostics:
    """
    Placeholder for Expt 1 diagnostics.

    We are keeping this light until the ratings calculation and oracle
    pipeline are stable.
    """
    notes: list[str] = field(default_factory=list)


@dataclass
class RatingsResults:
    ratings: Ratings
    diagnostics: RatingsDiagnostics


################################################################################
# Bios
################################################################################

def load_bios(path: Path) -> Bios:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {RikId(int(k)): v for k, v in raw.items()}


################################################################################
# Elo helpers
################################################################################

def expect(ra: float, rb: float, q: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((rb - ra) / q))


def _initialise_basho_rikishi(
    current_ratings: DailyRatings,
    banzuke: Banzuke,
    params: EloParams,
) -> None:
    """
    Ensure that every rikishi on the current banzuke has a rating.

    Policy:
    - a rikishi first seen on a banzuke enters at params.b
    """
    for rid in banzuke.riks:
        if rid not in current_ratings:
            current_ratings[rid] = params.b


def _apply_bout_result(
    current_ratings: DailyRatings,
    banzuke: Banzuke,
    bout: BoutResult,
    params: EloParams,
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
        return

    r1 = bout.rikishi1
    r2 = bout.rikishi2

    ra = current_ratings[r1]
    rb = current_ratings[r2]

    actual_a = 1.0 if bout.outcome1.name == "W" else 0.0
    expected_a = expect(ra, rb, params.q)

    ordinal_a = banzuke.rikchii[r1].ordinal()
    k = params.k(ordinal_a)

    delta = k * (actual_a - expected_a)

    current_ratings[r1] += delta
    current_ratings[r2] -= delta


def _process_day(
    start_of_day_ratings: DailyRatings,
    banzuke: Banzuke,
    daily_results: DailyResults,
    params: EloParams,
) -> DailyRatings:
    """
    Process one real day and return end-of-day ratings.
    """
    updated = start_of_day_ratings.copy()

    for bout in daily_results.results_lookup.values():
        _apply_bout_result(updated, banzuke, bout, params)

    return updated


################################################################################
# Main API
################################################################################

def get_ratings(history: History, params: EloParams) -> RatingsResults:
    """
    Single-pass Elo calculation over oracle-quality history.

    Output convention:
        ratings[date][day][rik_id]

    means the rating of rik_id after processing that real day.

    Notes:
    - only real days are stored
    - the implicit initial state before the first recorded bouts is not stored
    - retirement handling is not yet implemented
    """
    ratings: Ratings = {}
    diagnostics = RatingsDiagnostics()
    current_ratings: DailyRatings = {}

    for date in sorted(history.keys()):
        basho_state: BashoState = history[date]
        banzuke: Banzuke = basho_state.banzuke
        summary: Summary = basho_state.summary

        basho_ratings: BashoRatings = {}

        _initialise_basho_rikishi(current_ratings, banzuke, params)

        for day in sorted(summary.keys()):
            daily_results: DailyResults = summary[day]

            current_ratings = _process_day(
                start_of_day_ratings=current_ratings,
                banzuke=banzuke,
                daily_results=daily_results,
                params=params,
            )

            basho_ratings[day] = current_ratings.copy()

        ratings[date] = basho_ratings

    diagnostics.notes.append("Only real days are stored.")
    diagnostics.notes.append("A rikishi first seen on a banzuke enters at params.b.")
    diagnostics.notes.append('"fusen" is ignored as a rating event.')
    diagnostics.notes.append('"blank" is ignored as a rating event.')
    diagnostics.notes.append("Retirement handling is not yet implemented.")

    return RatingsResults(ratings=ratings, diagnostics=diagnostics)


################################################################################
# Module entry point
################################################################################

def main() -> None:
    raw_history = connect()
    bios = load_bios(Path(__file__).with_name("bios.json"))
    oracle: Oracle = make_oracle(raw_history, bios)

    params = EloParams()
    results = get_ratings(oracle.history, params)

    dates = sorted(results.ratings.keys())
    if not dates:
        print("No ratings produced.")
        return

    first_date = dates[0]
    last_date = dates[-1]

    print(f"Computed ratings for {len(dates)} basho: {first_date} to {last_date}")

    last_basho = results.ratings[last_date]
    last_day = max(last_basho.keys())
    n = len(last_basho[last_day])
    print(f"Rikishi rated at end of {last_date} day {last_day}: {n}")

    test_date = Date(Year(2026), Month(3))
    test_day = Day(3)
    test_rikishi = RikId(12451)

    print()
    print("Test query:")
    print(f"  Date:    {test_date}")
    print(f"  Day:     {test_day}")
    print(f"  Rikishi: {test_rikishi}")

    if test_date not in results.ratings:
        print("  Result:  test date not present in ratings")
    elif test_day not in results.ratings[test_date]:
        print("  Result:  test day not present in ratings")
    elif test_rikishi not in results.ratings[test_date][test_day]:
        print("  Result:  rikishi not present in ratings for that date/day")
    else:
        rating = results.ratings[test_date][test_day][test_rikishi]
        print(f"  Rating:  {rating}")

    print()
    print("Diagnostics:")
    for note in results.diagnostics.notes:
        print(f"  - {note}")


if __name__ == "__main__":
    main()

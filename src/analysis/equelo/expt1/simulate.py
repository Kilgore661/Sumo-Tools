from pdb import set_trace

"""Historical Elo simulation for Expt1 and Expt2.

The public entry point is :func:`simulate`.

Design notes:
    * The simulator accepts an already-sliced ``History``. It performs no date
      filtering or data loading itself.
    * Entrant initialisation is externalised as a callable over
      ``(rikid, chii, date)``.
    * Conservation is defined on the active basho universe rather than on all
      ratings ever stored in memory.
    * Diagnostics are optional observers and are not part of the return value.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, TypeAlias

from ....sumo_core.BasicPrimitives import RikId, Day
from ....sumo_core.Banzuke import Banzuke
from ....sumo_core.BashoState import BashoState
from ....sumo_core.History import History, Date
from ....sumo_core.Summary import DailyResults, BoutResult

from .initialisation import EntrantInitialiser
from .params import EloParams


DailyRatings: TypeAlias = dict[RikId, float]
BashoRatings: TypeAlias = dict[Day, DailyRatings]
RatingsByDate: TypeAlias = dict[Date, BashoRatings]
BashoStartRatings: TypeAlias = dict[Date, DailyRatings]


class SimulationMode(str, Enum):
    """Public simulation mode.

    ``OPEN``
        Departures simply leave the active universe. This is the conventional
        open-population Elo interpretation.

    ``CLOSED``
        Departures are redistributed uniformly over the active survivors so that
        the mean on the active basho universe is preserved at basho boundaries.
    """

    OPEN = "open"
    CLOSED = "closed"


@dataclass(frozen=True)
class SimulationResult:
    """Rating observations produced by one simulation run.

    Attributes:
        basho_start_ratings:
            Rating snapshots taken after departures and entrant initialisation,
            but before the first scored bout of the basho.
        day_end_ratings:
            End-of-day snapshots after each day's scored bouts.
    """

    basho_start_ratings: BashoStartRatings = field(default_factory=dict)
    day_end_ratings: RatingsByDate = field(default_factory=dict)


class SimulationObserver(Protocol):
    """Optional observer interface for diagnostics and logging."""

    def on_basho_start(self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke) -> None: ...
    def on_entry(self, date: Date, rikid: RikId, rating: float, ratings: dict[RikId, float]) -> None: ...
    def on_retirement(
        self,
        date: Date,
        rikid: RikId,
        rating: float,
        n: int,
        delta: float,
        delta_per_rikishi: float,
        abs_delta_per_rikishi: float,
        closed: bool,
    ) -> None: ...
    def on_day_start(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None: ...
    def on_bout(
        self,
        date: Date,
        day: Day,
        bout: BoutResult,
        delta: float,
        r1_before: float,
        r2_before: float,
        r1_after: float,
        r2_after: float,
        rating_mass_before: float,
        rating_mass_after: float,
    ) -> None: ...
    def on_ignored_bout(self, date: Date, day: Day, bout: BoutResult) -> None: ...
    def on_day_end(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None: ...
    def on_basho_end(self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke) -> None: ...


def expect(ra: float, rb: float, q: float) -> float:
    """Return player A's expected score against player B."""
    return 1.0 / (1.0 + 10.0 ** ((rb - ra) / q))


def _handle_departures(
    current_ratings: DailyRatings,
    previous_active_rikishi: set[RikId],
    current_active_rikishi: set[RikId],
    date: Date,
    observer: SimulationObserver | None,
    mode: SimulationMode,
) -> None:
    """Apply the basho-boundary departure rule.

    The simulator may keep ratings for convenience while processing, but the
    conservation contract is defined on the active set only.

    Departures are rikishi who were active in the previous basho and are absent
    from the current one. Redistribution, when enabled, is computed over the
    previous active set only, not over every rating currently stored.
    """
    departures = sorted(previous_active_rikishi - current_active_rikishi)

    if mode == SimulationMode.CLOSED:
        for rikid in departures:
            active_before = [rid for rid in previous_active_rikishi if rid in current_ratings]
            if rikid not in current_ratings or rikid not in active_before:
                continue

            rating = current_ratings[rikid]
            mean_before = sum(current_ratings[rid] for rid in active_before) / len(active_before)
            survivors = [rid for rid in active_before if rid != rikid]
            n = len(survivors)

            delta = mean_before - rating
            delta_per_rikishi = (delta / n) if n > 0 else 0.0

            if n > 0:
                for survivor in survivors:
                    current_ratings[survivor] -= delta_per_rikishi

            del current_ratings[rikid]

            if observer is not None:
                observer.on_retirement(
                    date=date,
                    rikid=rikid,
                    rating=rating,
                    n=n,
                    delta=delta,
                    delta_per_rikishi=delta_per_rikishi if n > 0 else 0.0,
                    abs_delta_per_rikishi=abs(delta_per_rikishi) if n > 0 else 0.0,
                    closed=True,
                )
    else:
        for rikid in departures:
            if rikid not in current_ratings:
                continue
            rating = current_ratings[rikid]
            del current_ratings[rikid]
            if observer is not None:
                observer.on_retirement(
                    date=date,
                    rikid=rikid,
                    rating=rating,
                    n=len(current_active_rikishi),
                    delta=0.0,
                    delta_per_rikishi=0.0,
                    abs_delta_per_rikishi=0.0,
                    closed=False,
                )


def _initialise_basho_rikishi(
    current_ratings: DailyRatings,
    banzuke: Banzuke,
    entrant_initialiser: EntrantInitialiser,
    date: Date,
    observer: SimulationObserver | None,
) -> None:
    """Initialise previously unseen rikishi for the current basho.

    The initialisation boundary is intentionally rank-based. The caller decides
    how a basho-start ``Chii`` should map to an initial rating.
    """
    for rid in banzuke.riks:
        if rid not in current_ratings:
            rating = entrant_initialiser(rid, banzuke.rikchii[rid], date)
            current_ratings[rid] = rating
            if observer is not None:
                observer.on_entry(
                    date=date,
                    rikid=rid,
                    rating=rating,
                    ratings=current_ratings,
                )


def _apply_bout_result(
    current_ratings: DailyRatings,
    banzuke: Banzuke,
    bout: BoutResult,
    params: EloParams,
    observer: SimulationObserver | None,
    date: Date,
    day: Day,
) -> None:
    """Apply one scored bout.

    ``fusen`` and ``blank`` are treated as non-rating events.

    For every scored bout, rating mass is conserved exactly up to numerical
    precision because one competitor gains ``delta`` and the other loses the
    same ``delta``.
    """
    if bout.decision in ("fusen", "blank"):
        if observer is not None:
            observer.on_ignored_bout(date=date, day=day, bout=bout)
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

    if observer is not None:
        observer.on_bout(
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
    observer: SimulationObserver | None,
    date: Date,
    day: Day,
) -> DailyRatings:
    updated = current_ratings.copy()

    if observer is not None:
        observer.on_day_start(date=date, day=day, ratings=updated)

    for bout in daily_results.results_lookup.values():
        _apply_bout_result(
            current_ratings=updated,
            banzuke=banzuke,
            bout=bout,
            params=params,
            observer=observer,
            date=date,
            day=day,
        )

    if observer is not None:
        observer.on_day_end(date=date, day=day, ratings=updated)
    return updated


def simulate(
    history: History,
    params: EloParams,
    entrant_initialiser: EntrantInitialiser,
    mode: SimulationMode = SimulationMode.OPEN,
    observer: SimulationObserver | None = None,
) -> SimulationResult:
    """Simulate Elo over an already-prepared history slice.

    Args:
        history:
            The history to simulate. This is assumed to be the exact history
            slice the caller wants to process.
        params:
            Resolved Elo parameters.
        entrant_initialiser:
            Callable used to initialise rikishi with no prior visible rating.
        mode:
            Open or closed active-universe semantics.
        observer:
            Optional diagnostics/logging observer.

    Returns:
        A :class:`SimulationResult` containing basho-start and day-end rating
        observations.
    """
    basho_start_ratings: BashoStartRatings = {}
    day_end_ratings: RatingsByDate = {}
    current_ratings: DailyRatings = {}
    previous_active_rikishi: set[RikId] = set()

    for date in sorted(history.keys()):
        basho_state: BashoState = history[date]
        banzuke: Banzuke = basho_state.banzuke
        summary = basho_state.summary
        current_active_rikishi = set(banzuke.riks)

        if observer is not None:
            observer.on_basho_start(date=date, ratings=current_ratings, banzuke=banzuke)

        _handle_departures(
            current_ratings=current_ratings,
            previous_active_rikishi=previous_active_rikishi,
            current_active_rikishi=current_active_rikishi,
            date=date,
            observer=observer,
            mode=mode,
        )

        _initialise_basho_rikishi(
            current_ratings=current_ratings,
            banzuke=banzuke,
            entrant_initialiser=entrant_initialiser,
            date=date,
            observer=observer,
        )

        basho_start_ratings[date] = current_ratings.copy()
        basho_ratings: BashoRatings = {}

        for day in sorted(summary.keys()):
            current_ratings = _process_day(
                current_ratings=current_ratings,
                banzuke=banzuke,
                daily_results=summary[day],
                params=params,
                observer=observer,
                date=date,
                day=day,
            )
            basho_ratings[day] = current_ratings.copy()

        if observer is not None:
            observer.on_basho_end(date=date, ratings=current_ratings, banzuke=banzuke)
        day_end_ratings[date] = basho_ratings
        previous_active_rikishi = current_active_rikishi

    return SimulationResult(
        basho_start_ratings=basho_start_ratings,
        day_end_ratings=day_end_ratings,
    )

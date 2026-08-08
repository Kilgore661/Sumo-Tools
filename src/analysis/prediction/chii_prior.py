"""Derive a retrospective start-of-basho rating surface over Chii."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass

from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .experiment import ForecastRecord
from .run import Proposal1Result


@dataclass(frozen=True)
class ChiiRatingObservation:
    """One normalized carried rating observed at an exact pre-basho Chii."""

    date: Date
    chii: Chii
    normalized_rating: float


@dataclass(frozen=True)
class ChiiPriorRow:
    """One exact or interpolated point in the initialization surface."""

    chii: Chii
    initial_rating: float
    source: str
    observation_count: int
    first_observation_date: Date | None
    last_observation_date: Date | None


@dataclass(frozen=True)
class ChiiPrior:
    """Retrospective Chii surface and the per-RikId values it initializes."""

    trailing_observations: int
    common_mean: float
    rows: tuple[ChiiPriorRow, ...]
    observations: tuple[ChiiRatingObservation, ...]
    initial_rating_by_rikishi: dict[RikId, float]
    unranked_initial_rikishi: tuple[RikId, ...]
    unranked_fallback_rating: float


def build_chii_prior(
    history: History,
    baseline: Proposal1Result,
    *,
    trailing_observations: int = 10,
    common_mean: float = 1500.0,
) -> ChiiPrior:
    """Average recent normalized start ratings and interpolate absent Chii."""

    observations_by_chii: dict[Chii, deque[ChiiRatingObservation]] = defaultdict(
        lambda: deque(maxlen=trailing_observations)
    )
    ratings: dict[RikId, float] = {}
    forecasts_by_date = _forecasts_by_date(baseline)
    for date in sorted(
        value for value in history
        if baseline.definition.start_date <= value <= baseline.definition.end_date
    ):
        banzuke = history[date].banzuke
        rated_banzuke = tuple(
            rikishi_id for rikishi_id in banzuke.riks
            if rikishi_id in ratings
        )
        if rated_banzuke:
            mean_rating = sum(ratings[rid] for rid in rated_banzuke) / len(rated_banzuke)
            for rikishi_id in rated_banzuke:
                chii = banzuke.rikchii[rikishi_id]
                observations_by_chii[chii].append(
                    ChiiRatingObservation(
                        date=date,
                        chii=chii,
                        normalized_rating=(
                            ratings[rikishi_id] - mean_rating + common_mean
                        ),
                    )
                )
        for forecast in forecasts_by_date.get(date, ()):
            ratings[RikId(forecast.rikishi_a)] = forecast.rating_a_after
            ratings[RikId(forecast.rikishi_b)] = forecast.rating_b_after

    required_chii_by_rikishi, unranked_rikishi = _first_chii_by_rikishi(
        history,
        baseline,
    )
    exact_ratings = {
        chii: sum(row.normalized_rating for row in rows) / len(rows)
        for chii, rows in observations_by_chii.items()
    }
    domain = tuple(sorted(set(exact_ratings) | set(required_chii_by_rikishi.values())))
    position = {chii: index for index, chii in enumerate(domain)}
    observed_positions = tuple(
        index for index, chii in enumerate(domain)
        if chii in exact_ratings
    )
    rows: list[ChiiPriorRow] = []
    rating_by_chii: dict[Chii, float] = {}
    for chii in domain:
        if chii in exact_ratings:
            retained = tuple(observations_by_chii[chii])
            rating = exact_ratings[chii]
            row = ChiiPriorRow(
                chii=chii,
                initial_rating=rating,
                source="observed trailing mean",
                observation_count=len(retained),
                first_observation_date=retained[0].date,
                last_observation_date=retained[-1].date,
            )
        else:
            rating, source = _interpolate(
                position[chii],
                domain,
                observed_positions,
                exact_ratings,
            )
            row = ChiiPriorRow(
                chii=chii,
                initial_rating=rating,
                source=source,
                observation_count=0,
                first_observation_date=None,
                last_observation_date=None,
            )
        rating_by_chii[chii] = rating
        rows.append(row)

    unranked_fallback_rating = rating_by_chii[domain[-1]]
    initial_rating_by_rikishi = {
        rikishi_id: rating_by_chii[chii]
        for rikishi_id, chii in required_chii_by_rikishi.items()
    }
    initial_rating_by_rikishi.update({
        rikishi_id: unranked_fallback_rating
        for rikishi_id in unranked_rikishi
    })
    return ChiiPrior(
        trailing_observations=trailing_observations,
        common_mean=common_mean,
        rows=tuple(rows),
        observations=tuple(
            row
            for chii in sorted(observations_by_chii)
            for row in observations_by_chii[chii]
        ),
        initial_rating_by_rikishi=initial_rating_by_rikishi,
        unranked_initial_rikishi=tuple(sorted(unranked_rikishi)),
        unranked_fallback_rating=unranked_fallback_rating,
    )


def _forecasts_by_date(
    baseline: Proposal1Result,
) -> dict[Date, tuple[ForecastRecord, ...]]:
    grouped: dict[Date, list[ForecastRecord]] = defaultdict(list)
    for forecast in baseline.forecasts:
        grouped[forecast.bout_id.date].append(forecast)
    return {date: tuple(rows) for date, rows in grouped.items()}


def _first_chii_by_rikishi(
    history: History,
    baseline: Proposal1Result,
) -> tuple[dict[RikId, Chii], set[RikId]]:
    result: dict[RikId, Chii] = {}
    unranked: set[RikId] = set()
    for bout in baseline.selection.bouts:
        banzuke = history[bout.contest.id.date].banzuke
        for rikishi_id in (
            bout.contest.rikishi_a,
            bout.contest.rikishi_b,
        ):
            if rikishi_id not in result and rikishi_id not in unranked:
                if rikishi_id in banzuke:
                    result[rikishi_id] = banzuke.rikchii[rikishi_id]
                else:
                    unranked.add(rikishi_id)
    return result, unranked


def _interpolate(
    target_position: int,
    domain: tuple[Chii, ...],
    observed_positions: tuple[int, ...],
    exact_ratings: dict[Chii, float],
) -> tuple[float, str]:
    lower = tuple(value for value in observed_positions if value < target_position)
    upper = tuple(value for value in observed_positions if value > target_position)
    if not lower:
        return (
            exact_ratings[domain[upper[0]]],
            "nearest weaker observed Chii (upper-edge extrapolation)",
        )
    if not upper:
        return (
            exact_ratings[domain[lower[-1]]],
            "nearest stronger observed Chii (lower-edge extrapolation)",
        )
    lower_position = lower[-1]
    upper_position = upper[0]
    lower_rating = exact_ratings[domain[lower_position]]
    upper_rating = exact_ratings[domain[upper_position]]
    fraction = (
        (target_position - lower_position)
        / (upper_position - lower_position)
    )
    return (
        lower_rating + fraction * (upper_rating - lower_rating),
        "linear interpolation by ordered Chii position",
    )

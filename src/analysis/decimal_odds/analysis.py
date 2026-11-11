"""Pure analysis for external prices and pre-bout Elo-89 ratings."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from src.analysis.elo89 import Elo89Artifacts
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


@dataclass(frozen=True, slots=True)
class CompetitorComparison:
    name: str
    rikishi_id: RikId
    rating: float
    elo_probability: float
    elo_decimal_odds: float
    market_decimal_odds: float
    market_raw_implied_probability: float
    market_normalized_probability: float


@dataclass(frozen=True, slots=True)
class BoutComparison:
    event_name: str
    event_url: str
    first: CompetitorComparison
    second: CompetitorComparison
    market_overround: float


def normalise_name(value: str) -> str:
    """Return the conservative key used to join external and banzuke names."""

    return " ".join(value.split()).casefold()


def build_banzuke_name_index(history: History, basho: Date) -> dict[str, RikId]:
    """Index one banzuke by normalized current shikona, rejecting ambiguity."""

    try:
        banzuke = history[basho].banzuke
    except KeyError as error:
        raise ValueError(f"History has no banzuke for {basho}") from error

    result: dict[str, RikId] = {}
    for rikishi_id in banzuke.riks:
        label = str(banzuke.rikshik[rikishi_id])
        key = normalise_name(label)
        if key in result and result[key] != rikishi_id:
            raise ValueError(
                f"Banzuke shikona is ambiguous after normalization: {label!r} "
                f"identifies {int(result[key])} and {int(rikishi_id)}"
            )
        result[key] = rikishi_id
    return result


def decimal_price(value: object) -> float:
    """Parse one positive decimal price, accepting the conventional EVS label."""

    if isinstance(value, str) and value.strip().casefold() == "evs":
        return 2.0
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Invalid decimal price: {value!r}") from error
    if not isfinite(result) or result <= 1.0:
        raise ValueError(f"Decimal price must be finite and greater than 1: {value!r}")
    return result


def elo_probability(first_rating: float, second_rating: float, q: float) -> float:
    """Return Elo-89's probability that the first competitor wins."""

    if not isfinite(q) or q <= 0:
        raise ValueError(f"Elo-89 q must be finite and positive, got {q!r}")
    return 1.0 / (1.0 + 10.0 ** ((second_rating - first_rating) / q))


def rating_snapshot_before_day(
    ratings: Elo89Artifacts,
    basho: Date,
    day: int,
) -> tuple[Mapping[str, float], str]:
    """Return ratings known immediately before the requested basho day."""

    if not 1 <= day <= 15:
        raise ValueError(f"Basho day must be from 1 to 15, got {day}")
    date_key = str(basho)
    if day == 1:
        try:
            return ratings.basho_start_ratings[date_key], "start of basho"
        except KeyError as error:
            raise ValueError(f"No Elo-89 start ratings are available for {basho}") from error
    try:
        return ratings.day_end_ratings[date_key][str(day - 1)], f"end of Day {day - 1}"
    except KeyError as error:
        raise ValueError(
            f"No Elo-89 ratings are available for {basho} immediately before Day {day}"
        ) from error


def analyse_odds_payload(
    payload: Mapping[str, object],
    *,
    name_index: Mapping[str, RikId],
    ratings: Elo89Artifacts,
    basho: Date,
    day: int,
) -> tuple[BoutComparison, ...]:
    """Join external two-way prices to pre-day Elo-89 ratings."""

    rating_values, _cutoff = rating_snapshot_before_day(ratings, basho, day)
    q = float(ratings.manifest.get("q", 0))
    raw_events = payload.get("events")
    if not isinstance(raw_events, list):
        raise ValueError("Odds payload has no events list")

    comparisons: list[BoutComparison] = []
    for raw_event in raw_events:
        if not isinstance(raw_event, dict):
            raise ValueError("Odds payload contains a non-object event")
        first_name = _required_text(raw_event, "competitor_1")
        second_name = _required_text(raw_event, "competitor_2")
        first_id = _resolve_name(first_name, name_index)
        second_id = _resolve_name(second_name, name_index)
        first_rating = _rating(rating_values, first_id, first_name, basho, day)
        second_rating = _rating(rating_values, second_id, second_name, basho, day)
        market_prices = _two_way_prices(raw_event, first_name, second_name)
        first_market = market_prices[normalise_name(first_name)]
        second_market = market_prices[normalise_name(second_name)]
        first_raw = 1.0 / first_market
        second_raw = 1.0 / second_market
        implied_sum = first_raw + second_raw
        first_probability = elo_probability(first_rating, second_rating, q)
        second_probability = 1.0 - first_probability
        comparisons.append(
            BoutComparison(
                event_name=str(raw_event.get("name") or f"{first_name} vs {second_name}"),
                event_url=str(raw_event.get("url") or ""),
                first=CompetitorComparison(
                    name=first_name,
                    rikishi_id=first_id,
                    rating=first_rating,
                    elo_probability=first_probability,
                    elo_decimal_odds=1.0 / first_probability,
                    market_decimal_odds=first_market,
                    market_raw_implied_probability=first_raw,
                    market_normalized_probability=first_raw / implied_sum,
                ),
                second=CompetitorComparison(
                    name=second_name,
                    rikishi_id=second_id,
                    rating=second_rating,
                    elo_probability=second_probability,
                    elo_decimal_odds=1.0 / second_probability,
                    market_decimal_odds=second_market,
                    market_raw_implied_probability=second_raw,
                    market_normalized_probability=second_raw / implied_sum,
                ),
                market_overround=implied_sum - 1.0,
            )
        )
    return tuple(comparisons)


def _required_text(record: Mapping[str, object], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Odds event has no {key!r}")
    return value.strip()


def _resolve_name(name: str, name_index: Mapping[str, RikId]) -> RikId:
    try:
        return name_index[normalise_name(name)]
    except KeyError as error:
        raise ValueError(f"External competitor is absent from the selected banzuke: {name!r}") from error


def _rating(
    values: Mapping[str, float],
    rikishi_id: RikId,
    name: str,
    basho: Date,
    day: int,
) -> float:
    try:
        return float(values[str(int(rikishi_id))])
    except KeyError as error:
        raise ValueError(
            f"No pre-Day {day} Elo-89 rating for {name} ({int(rikishi_id)}) in {basho}"
        ) from error


def _two_way_prices(
    event: Mapping[str, object],
    first_name: str,
    second_name: str,
) -> dict[str, float]:
    raw_odds = event.get("odds")
    if not isinstance(raw_odds, list):
        raise ValueError(f"Odds event {event.get('name')!r} has no odds list")
    wanted = {normalise_name(first_name), normalise_name(second_name)}
    prices: dict[str, float] = {}
    for raw_odd in raw_odds:
        if not isinstance(raw_odd, dict):
            continue
        market = str(raw_odd.get("market") or "")
        if market and "2-way" not in market.casefold():
            continue
        outcome = raw_odd.get("outcome")
        if not isinstance(outcome, str):
            continue
        key = normalise_name(outcome)
        if key not in wanted:
            continue
        if key in prices:
            raise ValueError(f"Duplicate two-way price for {outcome!r}")
        prices[key] = decimal_price(raw_odd.get("price"))
    missing = wanted - prices.keys()
    if missing:
        raise ValueError(
            f"Odds event {event.get('name')!r} lacks two-way prices for: "
            + ", ".join(sorted(missing))
        )
    return prices

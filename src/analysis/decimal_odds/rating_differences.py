"""Compare bookmaker-implied and pre-bout Elo-89 rating differences."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log10
from typing import Iterable, Mapping

from src.analysis.elo89 import Elo89Artifacts
from src.infra.torikumi.model import Future
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.History import Date, History

from .analysis import decimal_price, normalise_name, rating_snapshot_before_day


MARKET_Q = 400.0


class OddsEloComparisonError(ValueError):
    """The odds row cannot be compared without guessing or stale data."""


@dataclass(frozen=True, slots=True)
class ResolvedIdentity:
    bookmaker_shikona: str
    history_shikona: str
    rikishi_id: RikId
    method: str


@dataclass(frozen=True, slots=True)
class RatingDifferenceComparison:
    date: str
    day: int
    site: str
    first: ResolvedIdentity
    second: ResolvedIdentity
    first_market_decimal_odds: float
    second_market_decimal_odds: float
    market_overround: float
    first_market_probability: float
    second_market_probability: float
    first_market_fair_odds: float
    second_market_fair_odds: float
    market_q: float
    market_rating_difference: float
    first_elo89_rating: float
    second_elo89_rating: float
    elo89_rating_difference: float
    market_minus_elo89_difference: float
    rating_cutoff: str
    identity_warning: str
    source_file: str


def market_rating_difference(probability: float, q: float = MARKET_Q) -> float:
    """Return first-minus-second rating difference implied by one probability."""

    if not isfinite(q) or q <= 0:
        raise ValueError(f"Elo q must be finite and positive, got {q!r}")
    if not isfinite(probability) or not 0.0 < probability < 1.0:
        raise ValueError(
            f"Win probability must be strictly between zero and one, got {probability!r}"
        )
    return q * log10(probability / (1.0 - probability))


def normalise_market_prices(first: object, second: object) -> tuple[float, float, float]:
    """Return overround and proportional no-overround probabilities."""

    first_price = decimal_price(first)
    second_price = decimal_price(second)
    first_raw = 1.0 / first_price
    second_raw = 1.0 / second_price
    implied_sum = first_raw + second_raw
    return implied_sum - 1.0, first_raw / implied_sum, second_raw / implied_sum


def build_canonical_opponent_index(
    history: History,
    basho: Date,
    future: Future | None = None,
) -> dict[tuple[int, RikId], tuple[RikId, ...]]:
    """Index each known day/rikishi to canonical opponents for safe inference."""

    opponents: dict[tuple[int, RikId], set[RikId]] = {}
    state = history.get(basho)
    completed_days: set[int] = set()
    if state is not None:
        for day, daily in state.summary.items():
            day_number = int(day)
            completed_days.add(day_number)
            for pair in daily.torikumi:
                first, second = RikId(int(pair[0])), RikId(int(pair[1]))
                opponents.setdefault((day_number, first), set()).add(second)
                opponents.setdefault((day_number, second), set()).add(first)

    if future is not None and future.date == basho:
        for future_day in future.days:
            day_number = int(future_day.day)
            if day_number in completed_days:
                continue
            for bout in future_day.bouts:
                opponents.setdefault((day_number, bout.east), set()).add(bout.west)
                opponents.setdefault((day_number, bout.west), set()).add(bout.east)

    return {
        key: tuple(sorted(values, key=int))
        for key, values in opponents.items()
    }


def compare_odds_rows(
    rows: Iterable[Mapping[str, object]],
    *,
    name_index: Mapping[str, RikId],
    history_names: Mapping[RikId, str],
    canonical_opponents: Mapping[tuple[int, RikId], tuple[RikId, ...]],
    ratings: Elo89Artifacts,
    basho: Date,
    market_q: float = MARKET_Q,
) -> tuple[RatingDifferenceComparison, ...]:
    """Convert consolidated bookmaker rows to market-versus-Elo differences."""

    try:
        elo89_q = float(ratings.manifest["q"])
    except (KeyError, TypeError, ValueError) as error:
        raise OddsEloComparisonError("Elo-89 artifacts have no valid q") from error
    if not isfinite(elo89_q) or elo89_q != market_q:
        raise OddsEloComparisonError(
            f"Market rating differences use q={market_q:g}, but Elo-89 uses "
            f"q={elo89_q:g}; their raw rating differences are not comparable"
        )

    comparisons: list[RatingDifferenceComparison] = []
    for row_number, row in enumerate(rows, start=2):
        day = _required_day(row, row_number)
        date = _required_text(row, "date", row_number)
        site = _required_text(row, "site", row_number)
        first_name = _required_text(row, "rikishi_1", row_number)
        second_name = _required_text(row, "rikishi_2", row_number)
        first, second, warning = _resolve_identities(
            first_name,
            second_name,
            day=day,
            site=site,
            date=date,
            name_index=name_index,
            history_names=history_names,
            canonical_opponents=canonical_opponents,
        )
        first_price = decimal_price(row.get("rikishi_1_decimal_odds"))
        second_price = decimal_price(row.get("rikishi_2_decimal_odds"))
        overround, first_probability, second_probability = normalise_market_prices(
            first_price, second_price
        )
        rating_values, cutoff = rating_snapshot_before_day(ratings, basho, day)
        first_rating = _rating(rating_values, first, basho, day)
        second_rating = _rating(rating_values, second, basho, day)
        market_difference = market_rating_difference(first_probability, market_q)
        elo89_difference = first_rating - second_rating
        comparisons.append(
            RatingDifferenceComparison(
                date=date,
                day=day,
                site=site,
                first=first,
                second=second,
                first_market_decimal_odds=first_price,
                second_market_decimal_odds=second_price,
                market_overround=overround,
                first_market_probability=first_probability,
                second_market_probability=second_probability,
                first_market_fair_odds=1.0 / first_probability,
                second_market_fair_odds=1.0 / second_probability,
                market_q=market_q,
                market_rating_difference=market_difference,
                first_elo89_rating=first_rating,
                second_elo89_rating=second_rating,
                elo89_rating_difference=elo89_difference,
                market_minus_elo89_difference=market_difference - elo89_difference,
                rating_cutoff=cutoff,
                identity_warning=warning,
                source_file=str(row.get("source_file") or ""),
            )
        )
    return tuple(comparisons)


def _resolve_identities(
    first_name: str,
    second_name: str,
    *,
    day: int,
    site: str,
    date: str,
    name_index: Mapping[str, RikId],
    history_names: Mapping[RikId, str],
    canonical_opponents: Mapping[tuple[int, RikId], tuple[RikId, ...]],
) -> tuple[ResolvedIdentity, ResolvedIdentity, str]:
    first_id = name_index.get(normalise_name(first_name))
    second_id = name_index.get(normalise_name(second_name))
    context = f"{site} {date} Day {day}: {first_name} vs {second_name}"

    if first_id is None and second_id is None:
        raise OddsEloComparisonError(
            f"{context} has two shikona absent from the selected banzuke; "
            "opponent inference is unsafe"
        )
    if first_id is not None and second_id is not None:
        if first_id == second_id:
            raise OddsEloComparisonError(f"{context} resolves both sides to {int(first_id)}")
        return (
            _direct_identity(first_name, first_id, history_names),
            _direct_identity(second_name, second_id, history_names),
            "",
        )

    known_name = second_name if first_id is None else first_name
    unknown_name = first_name if first_id is None else second_name
    known_id = second_id if first_id is None else first_id
    assert known_id is not None
    candidates = canonical_opponents.get((day, known_id), ())
    if len(candidates) != 1:
        detail = "no canonical opponent" if not candidates else (
            "multiple canonical opponents: " + ", ".join(str(int(value)) for value in candidates)
        )
        raise OddsEloComparisonError(
            f"{context} cannot infer unknown shikona {unknown_name!r} from "
            f"known opponent {known_name} ({int(known_id)}): {detail}"
        )
    inferred_id = candidates[0]
    try:
        inferred_name = history_names[inferred_id]
    except KeyError as error:
        raise OddsEloComparisonError(
            f"{context} inferred History ID {int(inferred_id)} for {unknown_name!r}, "
            "but that ID is absent from the selected banzuke"
        ) from error
    warning = (
        f"inferred {site} shikona {unknown_name!r} as {inferred_name} "
        f"({int(inferred_id)}) from its Day {day} bout against "
        f"{history_names[known_id]} ({int(known_id)})"
    )
    inferred = ResolvedIdentity(
        bookmaker_shikona=unknown_name,
        history_shikona=inferred_name,
        rikishi_id=inferred_id,
        method="opponent_inferred",
    )
    known = _direct_identity(known_name, known_id, history_names)
    return (inferred, known, warning) if first_id is None else (known, inferred, warning)


def _direct_identity(
    bookmaker_name: str,
    rikishi_id: RikId,
    history_names: Mapping[RikId, str],
) -> ResolvedIdentity:
    return ResolvedIdentity(
        bookmaker_shikona=bookmaker_name,
        history_shikona=history_names[rikishi_id],
        rikishi_id=rikishi_id,
        method="banzuke",
    )


def _rating(
    values: Mapping[str, float],
    identity: ResolvedIdentity,
    basho: Date,
    day: int,
) -> float:
    try:
        return float(values[str(int(identity.rikishi_id))])
    except KeyError as error:
        raise OddsEloComparisonError(
            f"No pre-Day {day} Elo-89 rating for {identity.history_shikona} "
            f"({int(identity.rikishi_id)}) in {basho}"
        ) from error


def _required_text(row: Mapping[str, object], key: str, row_number: int) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise OddsEloComparisonError(f"Odds CSV row {row_number} has no {key!r}")
    return value.strip()


def _required_day(row: Mapping[str, object], row_number: int) -> int:
    try:
        return int(Day(int(row["day"])))
    except (KeyError, TypeError, ValueError) as error:
        raise OddsEloComparisonError(
            f"Odds CSV row {row_number} has an invalid basho day: {row.get('day')!r}"
        ) from error

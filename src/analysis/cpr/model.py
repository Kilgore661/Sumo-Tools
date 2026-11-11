"""Core calculations for Cumulative Performance Rating (CPR)."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class RatedBout:
    """One rated, non-fusen, non-draw bout from the Elo-89 ledger."""

    day: int
    opponent_rating: float
    won: bool


@dataclass(frozen=True, slots=True)
class CPRMetrics:
    """Cumulative CPR metrics through one day."""

    rated_bouts: int
    rated_wins: int
    rated_losses: int
    expected_wins: float | None
    win_variance: float | None
    cpr: float | None
    cpr_minus_start: float | None
    z_score: float | None
    tail_direction: str
    tail_probability: float | None
    cpr_standard_error: float | None


@dataclass(frozen=True, slots=True)
class CPRRow:
    """Published CPR row for one rikishi at the end of one basho day."""

    basho: str
    division: str
    day: int
    rikishi_id: int
    shikona: str
    chii: str
    chii_ordinal: int
    basho_start_rating: float
    day_end_rating: float
    rated_bouts: int
    rated_wins: int
    rated_losses: int
    expected_wins: float | None
    win_variance: float | None
    cpr: float | None
    cpr_minus_start: float | None
    z_score: float | None
    tail_direction: str
    tail_probability: float | None
    cpr_standard_error: float | None


def win_probability(rating: float, opponent_rating: float, *, q: float) -> float:
    """Return the Elo probability that ``rating`` beats ``opponent_rating``."""

    if not math.isfinite(rating) or not math.isfinite(opponent_rating):
        raise ValueError("Ratings must be finite")
    if not math.isfinite(q) or q <= 0:
        raise ValueError("q must be positive and finite")
    exponent = (opponent_rating - rating) / q
    if exponent >= 308:
        return 0.0
    if exponent <= -308:
        return 1.0
    return 1.0 / (1.0 + 10.0**exponent)


def calculate_metrics(
    bouts: Sequence[RatedBout],
    *,
    start_rating: float,
    q: float,
) -> CPRMetrics:
    """Calculate every cumulative metric for one sequence of rated bouts."""

    if not bouts:
        return CPRMetrics(
            rated_bouts=0,
            rated_wins=0,
            rated_losses=0,
            expected_wins=None,
            win_variance=None,
            cpr=None,
            cpr_minus_start=None,
            z_score=None,
            tail_direction="N/A",
            tail_probability=None,
            cpr_standard_error=None,
        )

    probabilities = tuple(
        win_probability(start_rating, bout.opponent_rating, q=q) for bout in bouts
    )
    wins = sum(bout.won for bout in bouts)
    count = len(bouts)
    expected = sum(probabilities)
    variance = sum(probability * (1.0 - probability) for probability in probabilities)
    cpr = solve_cpr(
        tuple(bout.opponent_rating for bout in bouts), wins=wins, q=q
    )
    cpr_probabilities = tuple(
        win_probability(cpr, bout.opponent_rating, q=q) for bout in bouts
    ) if math.isfinite(cpr) else ()
    cpr_variance = sum(
        probability * (1.0 - probability) for probability in cpr_probabilities
    )
    cpr_se = (
        q / math.log(10.0) / math.sqrt(cpr_variance)
        if cpr_variance > 0.0
        else math.inf
    )
    difference = wins - expected
    if difference > 0.0:
        direction = "upper"
    elif difference < 0.0:
        direction = "lower"
    else:
        direction = "equal"
    return CPRMetrics(
        rated_bouts=count,
        rated_wins=wins,
        rated_losses=count - wins,
        expected_wins=expected,
        win_variance=variance,
        cpr=cpr,
        cpr_minus_start=cpr - start_rating,
        z_score=difference / math.sqrt(variance),
        tail_direction=direction,
        tail_probability=directional_tail_probability(
            probabilities, wins=wins, direction=direction
        ),
        cpr_standard_error=cpr_se,
    )


def solve_cpr(
    opponent_ratings: Sequence[float],
    *,
    wins: int,
    q: float,
) -> float:
    """Solve the CPR equation in the extended real numbers."""

    count = len(opponent_ratings)
    if count == 0:
        raise ValueError("CPR is undefined when there are no rated bouts")
    if not 0 <= wins <= count:
        raise ValueError(f"wins must be in 0..{count}, got {wins}")
    if wins == 0:
        return -math.inf
    if wins == count:
        return math.inf
    if not all(math.isfinite(rating) for rating in opponent_ratings):
        raise ValueError("Opponent ratings must be finite")

    low = min(opponent_ratings) - 50.0 * q
    high = max(opponent_ratings) + 50.0 * q
    for _ in range(100):
        midpoint = (low + high) / 2.0
        expectation = sum(
            win_probability(midpoint, opponent, q=q)
            for opponent in opponent_ratings
        )
        if expectation < wins:
            low = midpoint
        else:
            high = midpoint
    return (low + high) / 2.0


def directional_tail_probability(
    probabilities: Sequence[float],
    *,
    wins: int,
    direction: str,
) -> float:
    """Return an exact Poisson-binomial tail probability."""

    distribution = [1.0] + [0.0] * len(probabilities)
    used = 0
    for probability in probabilities:
        for successes in range(used + 1, -1, -1):
            stay = (
                distribution[successes] * (1.0 - probability)
                if successes <= used
                else 0.0
            )
            gain = distribution[successes - 1] * probability if successes else 0.0
            distribution[successes] = stay + gain
        used += 1
    if direction == "upper":
        return sum(distribution[wins:])
    if direction == "lower":
        return sum(distribution[: wins + 1])
    if direction == "equal":
        return 1.0
    raise ValueError(f"Unknown tail direction: {direction!r}")


def cumulative_rows(
    *,
    basho: object,
    division: str,
    latest_day: int,
    rikishi: Iterable[object],
    shikona: Mapping[object, object],
    chii: Mapping[object, object],
    start_ratings: Mapping[str, float],
    day_end_ratings: Mapping[str, Mapping[str, float]],
    ledger: Iterable[Mapping[str, str]],
    q: float,
) -> tuple[CPRRow, ...]:
    """Build cumulative daily rows for the supplied division roster."""

    basho_text = str(basho)
    selected = tuple(rikishi)
    selected_ids = {int(rid) for rid in selected}
    bouts: dict[int, list[RatedBout]] = {rid: [] for rid in selected_ids}
    for raw in ledger:
        if raw["date"] != basho_text:
            continue
        a = int(raw["rikishi_a"])
        b = int(raw["rikishi_b"])
        day = int(raw["day"])
        a_won = raw["a_won"].strip().lower() == "true"
        if a in selected_ids:
            bouts[a].append(
                RatedBout(day, float(raw["rating_b_before"]), a_won)
            )
        if b in selected_ids:
            bouts[b].append(
                RatedBout(day, float(raw["rating_a_before"]), not a_won)
            )

    rows: list[CPRRow] = []
    for day in range(1, latest_day + 1):
        day_ratings = day_end_ratings.get(str(day))
        if day_ratings is None:
            raise ValueError(f"Elo-89 artifacts contain no day {day} ratings for {basho}")
        for rid in sorted(selected, key=lambda item: chii[item]):
            key = str(int(rid))
            if key not in start_ratings:
                raise ValueError(f"No basho-start rating for rikishi {key} at {basho}")
            if key not in day_ratings:
                raise ValueError(f"No day-end rating for rikishi {key} on {basho} Day {day}")
            through_day = tuple(bout for bout in bouts[int(rid)] if bout.day <= day)
            metrics = calculate_metrics(
                through_day, start_rating=float(start_ratings[key]), q=q
            )
            rank = chii[rid]
            rows.append(
                CPRRow(
                    basho=basho_text,
                    division=division,
                    day=day,
                    rikishi_id=int(rid),
                    shikona=str(shikona[rid]),
                    chii=str(rank),
                    chii_ordinal=int(rank.ordinal()),
                    basho_start_rating=float(start_ratings[key]),
                    day_end_rating=float(day_ratings[key]),
                    **asdict(metrics),
                )
            )
    return tuple(rows)


def remove_repetitions(rows: Iterable[CPRRow]) -> tuple[CPRRow, ...]:
    """Keep the highest-Z row for each rikishi in each basho.

    The returned rows are ordered by descending Z. Rows with no Z value sort
    after every defined value, matching the product convention that N/A is the
    smallest sortable value.
    """

    ordered = sorted(rows, key=_surprise_sort_key)
    seen: set[tuple[str, int]] = set()
    result: list[CPRRow] = []
    for row in ordered:
        identity = (row.basho, row.rikishi_id)
        if identity in seen:
            continue
        seen.add(identity)
        result.append(row)
    return tuple(result)


def _surprise_sort_key(row: CPRRow) -> tuple[object, ...]:
    if row.z_score is None:
        return (1, 0.0, math.inf, row.basho, row.rikishi_id, -row.day)
    tail = math.inf if row.tail_probability is None else row.tail_probability
    return (0, -row.z_score, tail, row.basho, row.rikishi_id, -row.day)

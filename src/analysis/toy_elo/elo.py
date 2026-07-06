from __future__ import annotations


def expected_score(rating_a: float, rating_b: float, *, q: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / q))


def update_ratings(
    ratings: list[float],
    player_a: int,
    player_b: int,
    *,
    winner: int,
    k: float,
    q: float,
) -> None:
    expected_a = expected_score(ratings[player_a], ratings[player_b], q=q)
    score_a = 1.0 if winner == player_a else 0.0
    delta_a = k * (score_a - expected_a)
    ratings[player_a] += delta_a
    ratings[player_b] -= delta_a

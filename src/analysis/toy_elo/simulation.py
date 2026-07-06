from __future__ import annotations

import random

from .elo import expected_score, update_ratings
from .model import BaselineModel
from .progress import ProgressTimer


type SimulationResult = tuple[list[float], list[list[float]], list[list[float]]]


def round_robin_pairs(player_count: int) -> list[tuple[int, int]]:
    return [
        (player_a, player_b)
        for player_a in range(player_count)
        for player_b in range(player_a + 1, player_count)
    ]


def simulate_one_run(
    *,
    model: BaselineModel,
    skills: list[float],
    events: int,
    rng: random.Random,
) -> list[list[float]]:
    ratings = [model.baseline for _ in skills]
    rows = [ratings.copy()]
    pairs = round_robin_pairs(len(skills))

    for _ in range(events):
        rng.shuffle(pairs)
        for player_a, player_b in pairs:
            p_a_wins = expected_score(skills[player_a], skills[player_b], q=model.q)
            winner = player_a if rng.random() < p_a_wins else player_b
            update_ratings(
                ratings,
                player_a,
                player_b,
                winner=winner,
                k=model.k,
                q=model.q,
            )
        rows.append(ratings.copy())

    return rows


def simulate_ensemble(
    *,
    model: BaselineModel,
    events: int,
    runs: int,
    seed: int,
    progress_every: int,
) -> SimulationResult:
    skills = model.hidden_skills()
    sums = [[0.0 for _ in range(model.player_count)] for _ in range(events + 1)]
    sample_rows: list[list[float]] | None = None
    progress = ProgressTimer(runs, report_every=progress_every)

    for run in range(runs):
        rng = random.Random(seed + run)
        rows = simulate_one_run(
            model=model,
            skills=skills,
            events=events,
            rng=rng,
        )
        if sample_rows is None:
            sample_rows = rows
        for iteration, ratings in enumerate(rows):
            for player, rating in enumerate(ratings):
                sums[iteration][player] += rating
        progress.report(run + 1)

    means = [[rating_sum / runs for rating_sum in row] for row in sums]
    return skills, means, sample_rows or []

from __future__ import annotations

import random

from .elo import expected_score, update_ratings
from .metrics import all_pair_gap_rmse
from .model import BaselineModel
from .progress import ProgressTimer
from .split_division_sweep import (
    cross_gap_rmse,
    division_offset_error,
    first_true_window,
    later_event,
    mean,
    metric_slope,
    round_robin_pairs,
    subset,
)


def division_sizes(players: int) -> tuple[int, int]:
    if players < 2:
        raise ValueError("players must be at least 2")
    top_size = (players + 1) // 2
    return top_size, players - top_size


def bridge_slots(top_size: int, bottom_size: int, bridge_width: int) -> tuple[int, int, int]:
    if bridge_width < 0:
        raise ValueError("bridge width must be non-negative")
    top_slots = int(top_size * bridge_width / 100)
    bottom_slots = int(bottom_size * bridge_width / 100)
    if top_slots > top_size // 2:
        raise ValueError(
            f"bridge width {bridge_width} gives {top_slots} top slots, "
            f"but at most {top_size // 2} are valid"
        )
    if bottom_slots > bottom_size // 2:
        raise ValueError(
            f"bridge width {bridge_width} gives {bottom_slots} bottom slots, "
            f"but at most {bottom_size // 2} are valid"
        )
    return top_slots, bottom_slots, min(top_slots, bottom_slots)


def unordered_pair(player_a: int, player_b: int) -> tuple[int, int]:
    if player_a == player_b:
        raise ValueError(f"self-pair is invalid: {player_a}")
    return (player_a, player_b) if player_a < player_b else (player_b, player_a)


def build_bridge_pairs(
    *,
    top_size: int,
    bottom_size: int,
    slots: int,
) -> list[tuple[int, int]]:
    players = top_size + bottom_size
    top_players = list(range(top_size))
    bottom_players = list(range(top_size, players))
    pairs = {unordered_pair(a, b) for a, b in round_robin_pairs(top_players)}
    pairs.update(unordered_pair(a, b) for a, b in round_robin_pairs(bottom_players))

    for index in range(slots):
        top_low = top_size - index - 1
        top_high = index
        bottom_high = top_size + index
        bottom_low = players - index - 1
        for pair in [
            unordered_pair(top_low, top_high),
            unordered_pair(bottom_high, bottom_low),
        ]:
            if pair not in pairs:
                raise ValueError(f"cannot remove missing bridge source pair {pair}")
            pairs.remove(pair)
        for pair in [
            unordered_pair(top_low, bottom_high),
            unordered_pair(top_high, bottom_low),
        ]:
            if pair in pairs:
                raise ValueError(f"bridge target pair already exists {pair}")
            pairs.add(pair)

    return sorted(pairs)


def validate_match_counts(
    *,
    pairs: list[tuple[int, int]],
    top_size: int,
    bottom_size: int,
) -> None:
    counts = [0 for _ in range(top_size + bottom_size)]
    for player_a, player_b in pairs:
        counts[player_a] += 1
        counts[player_b] += 1
    expected = [top_size - 1 for _ in range(top_size)] + [
        bottom_size - 1 for _ in range(bottom_size)
    ]
    if counts != expected:
        raise ValueError(f"bridge schedule changed match counts: {counts} != {expected}")


def match_count_per_event(top_size: int, bottom_size: int) -> int:
    return top_size * (top_size - 1) // 2 + bottom_size * (bottom_size - 1) // 2


def bridge_match_count(players: int, top_size: int, events: int, runs: int) -> int:
    return runs * events * match_count_per_event(top_size, players - top_size)


class BridgeEnsemble:
    def __init__(
        self,
        *,
        model: BaselineModel,
        pairs: list[tuple[int, int]],
        runs: int,
        seed: int,
    ) -> None:
        self.model = model
        self.pairs = pairs
        self.runs = runs
        self.skills = model.hidden_skills()
        self.ratings = [[model.baseline for _ in self.skills] for _ in range(runs)]
        self.rngs = [random.Random(seed + run) for run in range(runs)]
        self.current_event = 0
        self.means = [[model.baseline for _ in self.skills]]
        self.sample_rows = [self.ratings[0].copy()] if runs else []

    def extend_to(self, events: int, *, progress_every: int) -> None:
        if events < self.current_event:
            raise ValueError(
                f"cannot extend backwards from {self.current_event} to {events}"
            )

        progress = ProgressTimer(events - self.current_event, report_every=progress_every)
        completed = 0
        while self.current_event < events:
            sums = [0.0 for _ in self.skills]
            for run, ratings in enumerate(self.ratings):
                event_pairs = self.pairs.copy()
                self.rngs[run].shuffle(event_pairs)
                for player_a, player_b in event_pairs:
                    p_a_wins = expected_score(
                        self.skills[player_a],
                        self.skills[player_b],
                        q=self.model.q,
                    )
                    winner = player_a if self.rngs[run].random() < p_a_wins else player_b
                    update_ratings(
                        ratings,
                        player_a,
                        player_b,
                        winner=winner,
                        k=self.model.k,
                        q=self.model.q,
                    )
                for player, rating in enumerate(ratings):
                    sums[player] += rating

            self.current_event += 1
            self.means.append([rating_sum / self.runs for rating_sum in sums])
            if self.ratings:
                self.sample_rows.append(self.ratings[0].copy())
            completed += 1
            progress.report(completed)


def simulate_one_bridge_run(
    *,
    model: BaselineModel,
    skills: list[float],
    pairs: list[tuple[int, int]],
    events: int,
    rng: random.Random,
) -> list[list[float]]:
    ratings = [model.baseline for _ in skills]
    rows = [ratings.copy()]
    event_pairs = pairs.copy()

    for _ in range(events):
        rng.shuffle(event_pairs)
        for player_a, player_b in event_pairs:
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


def simulate_bridge_ensemble(
    *,
    model: BaselineModel,
    pairs: list[tuple[int, int]],
    events: int,
    runs: int,
    seed: int,
    progress_every: int,
) -> tuple[list[float], list[list[float]], list[list[float]]]:
    skills = model.hidden_skills()
    sums = [[0.0 for _ in range(model.player_count)] for _ in range(events + 1)]
    sample_rows: list[list[float]] | None = None
    progress = ProgressTimer(runs, report_every=progress_every)

    for run in range(runs):
        rng = random.Random(seed + run)
        rows = simulate_one_bridge_run(
            model=model,
            skills=skills,
            pairs=pairs,
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


def build_bridge_metrics(
    *,
    skills: list[float],
    means: list[list[float]],
    sample_rows: list[list[float]],
    top_players: list[int],
    bottom_players: list[int],
    stable_epsilon: float,
    slope_epsilon: float,
    stable_window: int,
    bridge_offset_epsilon: float,
    bridge_boundary_epsilon: float,
) -> list[dict[str, float | int | bool]]:
    rows: list[dict[str, float | int | bool]] = []

    for event, mean_ratings in enumerate(means):
        top_rmse = all_pair_gap_rmse(subset(mean_ratings, top_players), subset(skills, top_players))
        bottom_rmse = all_pair_gap_rmse(subset(mean_ratings, bottom_players), subset(skills, bottom_players))
        whole_rmse = all_pair_gap_rmse(mean_ratings, skills)
        cross_rmse = cross_gap_rmse(mean_ratings, skills, top_players, bottom_players)
        offset_error = division_offset_error(mean_ratings, skills, top_players, bottom_players)
        sample_whole_rmse = all_pair_gap_rmse(sample_rows[event], skills)
        boundary_rating_gap = mean_ratings[top_players[-1]] - mean_ratings[bottom_players[0]]
        boundary_skill_gap = skills[top_players[-1]] - skills[bottom_players[0]]
        division_mean_rating_gap = mean(subset(mean_ratings, top_players)) - mean(
            subset(mean_ratings, bottom_players)
        )
        division_mean_skill_gap = mean(subset(skills, top_players)) - mean(
            subset(skills, bottom_players)
        )

        row: dict[str, float | int | bool] = {
            "event": event,
            "top_rmse": top_rmse,
            "bottom_rmse": bottom_rmse,
            "whole_rmse": whole_rmse,
            "cross_rmse": cross_rmse,
            "division_offset_error": offset_error,
            "sample_whole_rmse": sample_whole_rmse,
            "boundary_rating_gap": boundary_rating_gap,
            "boundary_skill_gap": boundary_skill_gap,
            "boundary_gap_error": boundary_rating_gap - boundary_skill_gap,
            "division_mean_rating_gap": division_mean_rating_gap,
            "division_mean_skill_gap": division_mean_skill_gap,
            "division_mean_gap_error": division_mean_rating_gap - division_mean_skill_gap,
        }
        row["top_slope"] = metric_slope(rows + [row], "top_rmse", event, stable_window)
        row["bottom_slope"] = metric_slope(rows + [row], "bottom_rmse", event, stable_window)
        row["whole_slope"] = metric_slope(rows + [row], "whole_rmse", event, stable_window)
        row["boundary_gap_error_slope"] = metric_slope(
            rows + [row],
            "boundary_gap_error",
            event,
            stable_window,
        )
        row["division_mean_gap_error_slope"] = metric_slope(
            rows + [row],
            "division_mean_gap_error",
            event,
            stable_window,
        )
        row["top_stable_now"] = (
            top_rmse <= stable_epsilon and abs(float(row["top_slope"])) <= slope_epsilon
        )
        row["bottom_stable_now"] = (
            bottom_rmse <= stable_epsilon and abs(float(row["bottom_slope"])) <= slope_epsilon
        )
        row["internal_stable_now"] = bool(row["top_stable_now"] and row["bottom_stable_now"])
        row["whole_stable_now"] = (
            whole_rmse <= stable_epsilon and abs(float(row["whole_slope"])) <= slope_epsilon
        )
        row["bridge_stable_now"] = (
            abs(float(row["division_mean_gap_error"])) <= bridge_offset_epsilon
            and abs(float(row["boundary_gap_error"])) <= bridge_boundary_epsilon
            and abs(float(row["division_mean_gap_error_slope"])) <= slope_epsilon
        )
        rows.append(row)

    top_first = first_true_window([bool(row["top_stable_now"]) for row in rows], stable_window)
    bottom_first = first_true_window(
        [bool(row["bottom_stable_now"]) for row in rows],
        stable_window,
    )
    internal_first = later_event(top_first, bottom_first)
    whole_first = first_true_window(
        [bool(row["whole_stable_now"]) for row in rows],
        stable_window,
    )
    bridge_first = first_true_window(
        [bool(row["bridge_stable_now"]) for row in rows],
        stable_window,
    )

    for row in rows:
        event = int(row["event"])
        row["top_stable_window_met"] = top_first is not None and event >= top_first
        row["bottom_stable_window_met"] = bottom_first is not None and event >= bottom_first
        row["internal_stable_window_met"] = internal_first is not None and event >= internal_first
        row["whole_stable_window_met"] = whole_first is not None and event >= whole_first
        row["bridge_stable_window_met"] = bridge_first is not None and event >= bridge_first

    return rows

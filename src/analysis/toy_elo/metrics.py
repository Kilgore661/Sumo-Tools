from __future__ import annotations


type MetricsRow = dict[str, float | int | bool]


def all_pair_gap_rmse(ratings: list[float], skills: list[float]) -> float:
    squared_error_sum = 0.0
    pair_count = 0
    for player_a in range(len(ratings)):
        for player_b in range(player_a + 1, len(ratings)):
            rating_gap = ratings[player_a] - ratings[player_b]
            skill_gap = skills[player_a] - skills[player_b]
            squared_error_sum += (rating_gap - skill_gap) ** 2
            pair_count += 1
    return (squared_error_sum / pair_count) ** 0.5 if pair_count else 0.0


def build_metrics(
    *,
    skills: list[float],
    means: list[list[float]],
    sample_rows: list[list[float]],
    stable_epsilon: float,
    slope_epsilon: float,
    stable_window: int,
) -> list[MetricsRow]:
    rows: list[MetricsRow] = []
    stable_flags: list[bool] = []

    for iteration, mean_ratings in enumerate(means):
        mean_rmse = all_pair_gap_rmse(mean_ratings, skills)
        sample_rmse = all_pair_gap_rmse(sample_rows[iteration], skills)
        if iteration >= stable_window:
            old_rmse = float(rows[iteration - stable_window]["mean_gap_rmse"])
            mean_rmse_slope = (mean_rmse - old_rmse) / stable_window
        else:
            mean_rmse_slope = 0.0

        stable_now = mean_rmse <= stable_epsilon and abs(mean_rmse_slope) <= slope_epsilon
        stable_flags.append(stable_now)
        stable_window_met = (
            iteration + 1 >= stable_window
            and all(stable_flags[iteration - stable_window + 1 : iteration + 1])
        )
        rows.append(
            {
                "event": iteration,
                "mean_gap_rmse": mean_rmse,
                "sample_gap_rmse": sample_rmse,
                "mean_gap_rmse_slope": mean_rmse_slope,
                "stable_now": stable_now,
                "stable_window_met": stable_window_met,
            }
        )

    return rows


def first_stable_event(metrics: list[MetricsRow]) -> int | None:
    for row in metrics:
        if row["stable_window_met"]:
            return int(row["event"])
    return None


def persistence_after_first_stable(metrics: list[MetricsRow]) -> float | None:
    first_event = first_stable_event(metrics)
    if first_event is None or first_event >= len(metrics) - 1:
        return None

    later_rows = metrics[first_event + 1 :]
    stable_count = sum(1 for row in later_rows if row["stable_now"])
    return stable_count / len(later_rows)

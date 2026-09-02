"""Produce Elo-89 rank-matchup probability traces."""

from __future__ import annotations

import csv
from pathlib import Path

from src.analysis.elo89.api import Elo89Artifacts
from src.analysis.probability.matchups.empirical import compute_empirical_matchups
from src.sumo_core.History import History

from .common import write_csv


def produce_win_probability_by_standing(
    *, history: History, ratings: Elo89Artifacts, output_root: Path
) -> tuple[Path, Path]:
    dates = sorted(history)
    results = compute_empirical_matchups(
        raw_history=history,
        start_year=int(dates[0].year),
        end_year=int(dates[-1].year),
    )
    observed = tuple(
        point
        for pair in results.sideless_chii_pair_rows
        for point in _observed_points(pair)
    )
    observed_path = write_csv(
        output_root / "observed_trace_points.csv",
        observed,
        tuple(observed[0]) if observed else (),
    )
    q = float(ratings.manifest["q"])
    modelled = []
    for row in observed:
        selected = ratings.prior.get(row["selected_chii"])
        opponent = ratings.prior.get(row["opponent_chii"])
        if selected is None or opponent is None:
            continue
        modelled.append(
            {
                "selected_chii": row["selected_chii"],
                "opponent_chii": row["opponent_chii"],
                "selected_ordinal": row["selected_ordinal"],
                "opponent_ordinal": row["opponent_ordinal"],
                "selected_rating": selected,
                "opponent_rating": opponent,
                "p_selected_wins": 1.0 / (1.0 + 10.0 ** ((opponent - selected) / q)),
            }
        )
    rating_path = write_csv(output_root / "rating_trace_points.csv", modelled)
    return observed_path, rating_path


def _observed_points(pair):
    higher = {
        "selected_chii": pair.higher_or_equal_chii,
        "opponent_chii": pair.other_chii,
        "selected_ordinal": pair.higher_or_equal_ordinal,
        "opponent_ordinal": pair.other_ordinal,
        "n_obs": pair.n_obs,
        "n_selected_wins": pair.n_higher_or_equal_wins,
        "n_opponent_wins": pair.n_other_wins,
        "p_selected_wins": pair.p_higher_or_equal_wins,
        "ci95_lower": pair.ci95_lower,
        "ci95_upper": pair.ci95_upper,
    }
    if pair.same_chii:
        return (higher,)
    return (
        higher,
        {
            "selected_chii": pair.other_chii,
            "opponent_chii": pair.higher_or_equal_chii,
            "selected_ordinal": pair.other_ordinal,
            "opponent_ordinal": pair.higher_or_equal_ordinal,
            "n_obs": pair.n_obs,
            "n_selected_wins": pair.n_other_wins,
            "n_opponent_wins": pair.n_higher_or_equal_wins,
            "p_selected_wins": pair.n_other_wins / pair.n_obs,
            "ci95_lower": 1.0 - pair.ci95_upper,
            "ci95_upper": 1.0 - pair.ci95_lower,
        },
    )

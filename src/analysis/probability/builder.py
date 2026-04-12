import csv
import math
from pathlib import Path
from typing import TypeAlias

from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from .classes import CalibrationBins, CalibrationRow


ChiiRatings: TypeAlias = dict[Chii, float]


def load_ratings_csv(path: Path) -> ChiiRatings:
    """Load Expt2 final ratings from a CSV with columns chii, ordinal, rating."""
    ratings: ChiiRatings = {}

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            chii = Chii.from_str(row["chii"])
            rating = float(row["rating"])
            ratings[chii] = rating

    return ratings


def estimated_probability(r1: float, r2: float, q: float) -> float:
    """Return Elo-implied win probability for rating r1 against r2."""
    return 1.0 / (1.0 + 10.0 ** ((r2 - r1) / q))


def _canonical_order(c1: Chii, c2: Chii) -> tuple[Chii, Chii]:
    """Return the pair ordered by ordinal.

    Contract for this first version: observations use full Chii only.
    """
    return (c1, c2) if c1.ordinal() < c2.ordinal() else (c2, c1)


def build_calibration_rows(
    history: History,
    ratings: ChiiRatings,
    q: float,
    bin_width: float,
) -> list[CalibrationRow]:
    """Build calibration rows from a cleaned history and Expt2 ratings."""
    bins = CalibrationBins(bin_width=bin_width)

    for date in sorted(history.keys()):
        basho_state = history[date]
        banzuke = basho_state.banzuke

        for day in sorted(basho_state.summary.keys()):
            daily_results = basho_state.summary[day]

            for bout in daily_results.results_lookup.values():
                if bout.decision in ("fusen", "blank"):
                    continue

                r1 = bout.rikishi1
                r2 = bout.rikishi2

                if r1 not in banzuke.rikchii or r2 not in banzuke.rikchii:
                    continue

                c_raw_1 = banzuke.rikchii[r1]
                c_raw_2 = banzuke.rikchii[r2]
                c1, c2 = _canonical_order(c_raw_1, c_raw_2)

                winner_rikid = r1 if bout.outcome1.name == "W" else r2
                winner_chii = c_raw_1 if winner_rikid == r1 else c_raw_2

                p = estimated_probability(ratings[c1], ratings[c2], q)
                y = 1 if winner_chii == c1 else 0
                bins.record(predicted_probability=p, outcome=y)

    return bins.to_rows()


def calibration_summary(rows: list[CalibrationRow]) -> dict[str, float | int]:
    """Return weighted calibration summaries over all rows and the trusted core.

    Core region:
    - n_obs > 1000
    - 0.48 < mean_predicted < 0.88
    """
    if not rows:
        raise ValueError("Cannot summarise empty calibration rows")

    total_obs = sum(row.n_obs for row in rows)
    mae_all = sum(row.n_obs * row.abs_error for row in rows) / total_obs
    mse_all = sum(row.n_obs * row.sq_error for row in rows) / total_obs
    rmse_all = math.sqrt(mse_all)

    core_rows = [
        row for row in rows
        if row.n_obs > 1000 and 0.48 < row.mean_predicted < 0.88
    ]
    if not core_rows:
        raise ValueError("No calibration rows fall in the core region")

    core_obs = sum(row.n_obs for row in core_rows)
    mae_core = sum(row.n_obs * row.abs_error for row in core_rows) / core_obs
    mse_core = sum(row.n_obs * row.sq_error for row in core_rows) / core_obs
    rmse_core = math.sqrt(mse_core)

    return {
        "mae_all": mae_all,
        "rmse_all": rmse_all,
        "mae_core": mae_core,
        "rmse_core": rmse_core,
        "n_rows": len(rows),
        "n_core_rows": len(core_rows),
        "total_obs": total_obs,
        "core_obs": core_obs,
    }


def write_calibration_csv(rows: list[CalibrationRow], output_path: Path) -> Path:
    """Write calibration-curve rows to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "p_bin_lo",
                "p_bin_hi",
                "n_obs",
                "n_wins_c1",
                "n_losses_c1",
                "mean_predicted",
                "observed_win_rate",
                "ci95_lower",
                "ci95_upper",
                "abs_error",
                "sq_error",
            ]
        )

        for row in rows:
            writer.writerow(
                [
                    row.p_bin_lo,
                    row.p_bin_hi,
                    row.n_obs,
                    row.n_wins_c1,
                    row.n_losses_c1,
                    row.mean_predicted,
                    row.observed_win_rate,
                    row.ci95_lower,
                    row.ci95_upper,
                    row.abs_error,
                    row.sq_error,
                ]
            )

    return output_path

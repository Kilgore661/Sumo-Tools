import csv
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from ..equelo.expt1.Oracle import make_oracle
from .classes import MatchupStats, ChiiPair


ChiiRatings: TypeAlias = dict[Chii, float]


@dataclass(frozen=True)
class ProbabilityRow:
    c1: Chii
    c2: Chii
    n_obs: int
    n_wins_c1: int
    p_c1_beats_c2: float
    p_ci95_lower: float
    p_ci95_upper: float
    r_c1: float
    r_c2: float
    q_c1_beats_c2: float


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


def _canonical_pair_key(pair: ChiiPair) -> tuple[tuple[int, str], tuple[int, str]]:
    c1, c2 = pair
    return ((c1.ordinal(), str(c1)), (c2.ordinal(), str(c2)))


def build_probability_rows(
    history: History,
    ratings: ChiiRatings,
    q: float,
) -> list[ProbabilityRow]:
    """Build joined observed/model probability rows from a cleaned history.

    Args:
        history:
            The cleaned/oracle history on which probabilities are to be observed.
        ratings:
            Expt2 converged chii ratings loaded from a chosen ratings CSV.
        q:
            Elo logistic scale parameter corresponding to the same Expt2 run that
            produced `ratings`.

    Returns:
        One row per canonical unordered chii pair.
    """
    matchup_stats = MatchupStats.from_history(history)
    rows: list[ProbabilityRow] = []

    for c1, c2 in matchup_stats.pairs():
        stats = matchup_stats.pair_stats(c1, c2)

        if c1 not in ratings or c2 not in ratings:
            continue

        p_lower, p_upper = matchup_stats.ci95(c1, c2)
        p_obs = matchup_stats.p(c1, c2)
        r1 = ratings[c1]
        r2 = ratings[c2]
        q_est = estimated_probability(r1, r2, q)

        rows.append(
            ProbabilityRow(
                c1=c1,
                c2=c2,
                n_obs=stats.n_obs,
                n_wins_c1=stats.n_wins_lo,
                p_c1_beats_c2=p_obs,
                p_ci95_lower=p_lower,
                p_ci95_upper=p_upper,
                r_c1=r1,
                r_c2=r2,
                q_c1_beats_c2=q_est,
            )
        )

    rows.sort(key=lambda row: _canonical_pair_key((row.c1, row.c2)))
    return rows


def write_probability_csv(rows: list[ProbabilityRow], output_path: Path) -> Path:
    """Write joined observed/model probabilities to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "c1",
                "c2",
                "n_obs",
                "n_wins_c1",
                "p_c1_beats_c2",
                "p_ci95_lower",
                "p_ci95_upper",
                "r_c1",
                "r_c2",
                "q_c1_beats_c2",
                "abs_error",
                "sq_error",
            ]
        )

        for row in rows:
            abs_error = abs(row.p_c1_beats_c2 - row.q_c1_beats_c2)
            sq_error = (row.p_c1_beats_c2 - row.q_c1_beats_c2) ** 2

            writer.writerow(
                [
                    str(row.c1),
                    str(row.c2),
                    row.n_obs,
                    row.n_wins_c1,
                    row.p_c1_beats_c2,
                    row.p_ci95_lower,
                    row.p_ci95_upper,
                    row.r_c1,
                    row.r_c2,
                    row.q_c1_beats_c2,
                    abs_error,
                    sq_error,
                ]
            )

    return output_path

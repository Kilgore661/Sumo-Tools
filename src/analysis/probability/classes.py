from dataclasses import dataclass
from math import sqrt
from typing import TypeAlias

from ...sumo_core.BasicPrimitives import RikId
from ...sumo_core.Chii import Chii
from ...sumo_core.History import History


ChiiPair: TypeAlias = tuple[Chii, Chii]

Z95 = 1.959963984540054


@dataclass(frozen=True)
class PairStats:
    """Observed bout statistics for one canonical unordered chii pair.

    The pair is stored in canonical order `(lo, hi)`. `n_wins_lo` counts wins by
    the lower member of that canonical pair.
    """

    n_obs: int = 0
    n_wins_lo: int = 0

    def p_lo(self) -> float:
        """Return the observed win probability for the canonical lower chii."""
        if self.n_obs <= 0:
            raise ValueError("Probability undefined for n_obs=0")
        return self.n_wins_lo / self.n_obs

    def wilson95_lo(self) -> tuple[float, float]:
        """Return the 95% Wilson interval for the canonical lower chii."""
        n = self.n_obs
        if n <= 0:
            raise ValueError("Wilson interval undefined for n_obs=0")

        phat = self.n_wins_lo / n
        z2 = Z95 * Z95
        denom = 1.0 + z2 / n
        centre = (phat + z2 / (2.0 * n)) / denom
        halfwidth = (
            Z95
            * sqrt((phat * (1.0 - phat) / n) + (z2 / (4.0 * n * n)))
            / denom
        )
        return centre - halfwidth, centre + halfwidth


class MatchupStats:
    """Pairwise observed bout statistics indexed by unordered chii pairs.

    Statistics are stored once per unordered pair in canonical order. Public
    query methods accept either direction and return the corresponding
    probability or interval.
    """

    def __init__(self) -> None:
        self._data: dict[ChiiPair, PairStats] = {}

    @staticmethod
    def _canonical_pair(c1: Chii, c2: Chii) -> ChiiPair:
        """Return the canonical ordering for a pair of distinct chiis."""
        #if c1 == c2:
        #    This can happen because annotations are ignored
        #    raise ValueError("Expected distinct chiis")
        key1 = (c1.ordinal(), str(c1))
        key2 = (c2.ordinal(), str(c2))
        return (c1, c2) if key1 < key2 else (c2, c1)

    def pairs(self) -> list[ChiiPair]:
        """Return all stored canonical pairs in sorted order."""
        return sorted(
            self._data.keys(),
            key=lambda pair: ((pair[0].ordinal(), str(pair[0])), (pair[1].ordinal(), str(pair[1]))),
        )

    def has_pair(self, c1: Chii, c2: Chii) -> bool:
        """Return whether the pair has any recorded observations."""
        return self._canonical_pair(c1, c2) in self._data

    def pair_stats(self, c1: Chii, c2: Chii) -> PairStats:
        """Return the stored stats object for the unordered pair."""
        return self._data[self._canonical_pair(c1, c2)]

    def n_obs(self, c1: Chii, c2: Chii) -> int:
        """Return the number of observed bouts for the unordered pair."""
        return self.pair_stats(c1, c2).n_obs

    def record(self, c1: Chii, c2: Chii, winner: Chii) -> None:
        """Record one observed bout.

        Args:
            c1, c2:
                Distinct chii values for the two competitors.
            winner:
                Must be equal to `c1` or `c2`.
        """
        if winner != c1 and winner != c2:
            raise ValueError("winner must be one of c1 or c2")

        lo, hi = self._canonical_pair(c1, c2)
        current = self._data.get((lo, hi), PairStats())

        win_for_lo = int(winner == lo)
        self._data[(lo, hi)] = PairStats(
            n_obs=current.n_obs + 1,
            n_wins_lo=current.n_wins_lo + win_for_lo,
        )

    def p(self, c1: Chii, c2: Chii) -> float:
        """Return the observed probability that c1 beats c2."""
        lo, hi = self._canonical_pair(c1, c2)
        p_lo = self._data[(lo, hi)].p_lo()
        return p_lo if c1 == lo else 1.0 - p_lo

    def ci95(self, c1: Chii, c2: Chii) -> tuple[float, float]:
        """Return the 95% Wilson interval for P(c1 beats c2)."""
        lo, hi = self._canonical_pair(c1, c2)
        lower, upper = self._data[(lo, hi)].wilson95_lo()
        if c1 == lo:
            return lower, upper
        return 1.0 - upper, 1.0 - lower

    @classmethod
    def from_history(cls, history: History) -> "MatchupStats":
        """Build matchup stats from a cleaned history.

        Rules:
        - ignore fusen and blank bouts
        - require both rikishi to be present on the basho banzuke
        - use the chii values from the basho banzuke
        """
        stats = cls()

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

                    c1 = banzuke.rikchii[r1]
                    c2 = banzuke.rikchii[r2]

                    winner = r1 if bout.outcome1.name == "W" else r2
                    winner_chii = c1 if winner == r1 else c2

                    stats.record(c1, c2, winner_chii)

        return stats

    def to_rows(self) -> list[dict[str, object]]:
        """Return a row-oriented view suitable for CSV writing."""
        rows: list[dict[str, object]] = []
        for lo, hi in self.pairs():
            s = self._data[(lo, hi)]
            lo_ci_lower, lo_ci_upper = s.wilson95_lo()
            rows.append(
                {
                    "c1": str(lo),
                    "c2": str(hi),
                    "n_obs": s.n_obs,
                    "n_wins_c1": s.n_wins_lo,
                    "p_c1_beats_c2": s.p_lo(),
                    "ci95_lower_c1": lo_ci_lower,
                    "ci95_upper_c1": lo_ci_upper,
                    "n_wins_c2": s.n_obs - s.n_wins_lo,
                    "p_c2_beats_c1": 1.0 - s.p_lo(),
                    "ci95_lower_c2": 1.0 - lo_ci_upper,
                    "ci95_upper_c2": 1.0 - lo_ci_lower,
                }
            )
        return rows

"""Nonnegative holdings; row = holder, column = original entrant.

Departed rows are frozen, not deleted. Unequal K scales the two sides of a
transfer independently. Scalar Elo is tracked separately to audit row sums.
"""

from __future__ import annotations

import math
import numpy as np


class Holdings:
    def __init__(self, size: int):
        self.matrix = np.zeros((size, size), dtype=np.float64)
        self.ratings = np.zeros(size, dtype=np.float64)
        self.active = np.zeros(size, dtype=bool)
        self.entered = np.zeros(size, dtype=bool)
        self.allocated = np.zeros(size, dtype=np.float64)
        self.created = np.zeros(size, dtype=np.float64)

    def enter(self, i: int, rating: float):
        if self.entered[i] or not math.isfinite(rating) or rating <= 0:
            raise ValueError("Entry must be unique and have a positive finite rating")
        self.entered[i] = self.active[i] = True
        self.matrix[i, i] = self.ratings[i] = self.allocated[i] = rating

    def leave(self, i: int):
        if not self.active[i]:
            raise ValueError("Cannot remove an inactive holder")
        self.active[i] = False

    def resume(self, i: int):
        """Reactivate the exact archived row and rating; allocate no new points."""
        if not self.entered[i] or self.active[i]:
            raise ValueError("Resume requires a previously entered, absent holder")
        self.active[i] = True

    def transfer(self, winner: int, loser: int, gain: float, loss: float):
        if winner == loser or not self.active[winner] or not self.active[loser]:
            raise ValueError("A transfer requires two distinct active holders")
        if not all(math.isfinite(x) and x >= 0 for x in (gain, loss)):
            raise ValueError("Nonfinite or negative transfer")
        if self.ratings[loser] <= 0 or loss >= self.ratings[loser]:
            raise ValueError("Nonpositive rating is outside this provenance model")
        proportions = self.matrix[loser] / self.ratings[loser]
        self.matrix[winner] += gain * proportions
        self.matrix[loser] *= 1 - loss / self.ratings[loser]
        self.created += (gain - loss) * proportions
        self.ratings[winner] += gain
        self.ratings[loser] -= loss

    def bout(self, a: int, b: int, a_won: bool, k_a: float, k_b: float, q=400.0):
        if not all(math.isfinite(x) and x > 0 for x in (k_a, k_b, q)):
            raise ValueError("K and q must be positive and finite")
        # Algebraically identical to Elo-89, with overflow-safe logistic tails.
        z = (self.ratings[b] - self.ratings[a]) * math.log(10) / q
        p = math.exp(-z) / (1 + math.exp(-z)) if z >= 0 else 1 / (1 + math.exp(z))
        residual = float(a_won) - p
        da, db = k_a * residual, -k_b * residual
        if a_won:
            self.transfer(a, b, da, -db)
        else:
            self.transfer(b, a, db, -da)
        return p, da, db

    def audit(self, tolerance=1e-6):
        row_error = float(np.max(np.abs(self.matrix.sum(axis=1) - self.ratings)))
        column_error = float(np.max(np.abs(
            self.matrix.sum(axis=0) - self.allocated - self.created)))
        if not np.isfinite(self.matrix).all() or self.matrix.min() < 0:
            raise ValueError("Invalid holdings")
        if max(row_error, column_error) > tolerance:
            raise ValueError(f"Holdings reconciliation failed: {row_error}, {column_error}")
        return {"max_row_error": row_error, "max_column_error": column_error}


def first_stints(populations):
    """Return included/excluded sets per date; first disappearance closes a stint."""
    seen, closed, previous = set(), set(), set()
    for date, population in populations:
        current = set(population)
        closed.update(previous - current)
        excluded = current & closed
        included = current - closed
        seen.update(current)
        previous = current
        yield date, included, excluded

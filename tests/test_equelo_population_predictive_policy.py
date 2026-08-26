from __future__ import annotations

import pytest

from src.analysis.equelo_population_policy.predict_population_policy import (
    _apply_legacy_departures,
    _shift_to_target,
)
from src.sumo_core.BasicPrimitives import RikId


def test_legacy_departure_redistributes_departing_deviation_to_survivors():
    ratings = {RikId(1): 1700.0, RikId(2): 1300.0, RikId(3): 1100.0}

    _apply_legacy_departures(
        ratings,
        {RikId(1), RikId(2), RikId(3)},
        {RikId(1), RikId(2)},
    )

    assert ratings == {
        RikId(1): pytest.approx(1566.6666666667),
        RikId(2): pytest.approx(1166.6666666667),
    }
    assert sum(ratings.values()) / len(ratings) == pytest.approx(1366.6666666667)


def test_uniform_population_shift_preserves_every_rating_difference():
    ratings = {RikId(1): 1700.0, RikId(2): 1300.0, RikId(3): 1100.0}
    before = ratings[RikId(1)] - ratings[RikId(3)]

    adjustment = _shift_to_target(ratings, set(ratings), 1500.0)

    assert adjustment == pytest.approx(133.3333333333)
    assert sum(ratings.values()) / len(ratings) == pytest.approx(1500.0)
    assert ratings[RikId(1)] - ratings[RikId(3)] == pytest.approx(before)

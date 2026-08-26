from __future__ import annotations

import pytest

from src.analysis.equelo_population_policy.recenter import recenter
from src.sumo_core.Chii import Chii


def test_alpha_zero_is_the_old_uniform_shift_and_preserves_differences():
    a = Chii.from_str("M1e")
    b = Chii.from_str("J1e")
    result = recenter(
        {a: 1600.0, b: 1200.0},
        base=1500.0,
        support={a: 100, b: 1},
        alpha=0.0,
    )

    assert result.ratings == {a: pytest.approx(1700.0), b: pytest.approx(1300.0)}
    assert result.maximum_pairwise_difference_change == pytest.approx(0.0)
    assert result.rms_pairwise_difference_change == pytest.approx(0.0)


def test_support_proportional_shift_preserves_mean_and_reports_distortion():
    a = Chii.from_str("M1e")
    b = Chii.from_str("J1e")
    result = recenter(
        {a: 1600.0, b: 1200.0},
        base=1500.0,
        support={a: 3, b: 1},
        alpha=1.0,
    )

    assert sum(result.ratings.values()) / 2 == pytest.approx(1500.0)
    assert result.ratings[a] == pytest.approx(1750.0)
    assert result.ratings[b] == pytest.approx(1250.0)
    assert result.maximum_pairwise_difference_change == pytest.approx(100.0)
    assert result.rms_pairwise_difference_change == pytest.approx(100.0)

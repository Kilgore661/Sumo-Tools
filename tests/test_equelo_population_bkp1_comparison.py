from __future__ import annotations

import csv

import pytest

from src.analysis.equelo_population_policy.run_bkp1_population import (
    _assert_coverage,
    _load_prior,
    _mean_abs,
    _rms,
)
from src.sumo_core.Chii import Chii


def test_canonical_prior_loader_and_coverage(tmp_path):
    path = tmp_path / "prior.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("chii", "rating"))
        writer.writeheader()
        writer.writerow({"chii": "M1e", "rating": 1700})

    prior = _load_prior(path)

    assert prior == {Chii.from_str("M1e"): pytest.approx(1700)}
    _assert_coverage(prior, {Chii.from_str("M1e"): 1})
    with pytest.raises(ValueError, match="1 missing"):
        _assert_coverage(prior, {Chii.from_str("M1e"): 1, Chii.from_str("J1e"): 1})


def test_distance_helpers():
    assert _mean_abs([-3.0, 4.0]) == pytest.approx(3.5)
    assert _rms([-3.0, 4.0]) == pytest.approx((25.0 / 2.0) ** 0.5)

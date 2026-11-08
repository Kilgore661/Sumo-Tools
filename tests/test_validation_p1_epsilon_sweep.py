from __future__ import annotations

import pytest

from src.validation.p1_epsilon_sweep.runner import (
    DEFAULT_EPSILONS,
    _adopted_prior,
    _parse_epsilons,
    _validate_epsilons,
)
from src.sumo_core.Chii import Chii


def test_default_sweep_has_sensible_extent_and_includes_ten() -> None:
    assert DEFAULT_EPSILONS[0] == 1000.0
    assert DEFAULT_EPSILONS[-1] == 0.1
    assert 10.0 in DEFAULT_EPSILONS
    assert DEFAULT_EPSILONS == tuple(sorted(DEFAULT_EPSILONS, reverse=True))


def test_epsilon_parser_sorts_descending() -> None:
    assert _parse_epsilons("3, 100,10") == (100.0, 10.0, 3.0)


@pytest.mark.parametrize("values", [(), (10.0, 10.0), (0.0,), (-1.0,)])
def test_invalid_epsilon_sets_are_rejected(values) -> None:
    with pytest.raises(ValueError):
        _validate_epsilons(values)


def test_support_weighted_pairing_matches_production_rule(tmp_path) -> None:
    east = Chii.from_str("M1e")
    west = Chii.from_str("M1w")
    source = tmp_path / "prior.csv"
    source.write_text("fixture", encoding="utf-8")

    prior = _adopted_prior(
        {east: 2200.0, west: 1800.0},
        {east: 9, west: 1},
        source,
        pairing_policy="support_weighted",
    )

    assert prior.rating_by_pair["M1"] == pytest.approx(2160.0)


def test_legacy_pairing_remains_default(tmp_path) -> None:
    east = Chii.from_str("M1e")
    west = Chii.from_str("M1w")
    source = tmp_path / "prior.csv"
    source.write_text("fixture", encoding="utf-8")

    prior = _adopted_prior(
        {east: 2200.0, west: 1800.0},
        {east: 9, west: 1},
        source,
    )

    assert prior.rating_by_pair["M1"] == pytest.approx(2000.0)

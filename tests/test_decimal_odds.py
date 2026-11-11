from __future__ import annotations

from pathlib import Path

import pytest

from src.analysis.decimal_odds.analysis import (
    analyse_odds_payload,
    decimal_price,
    elo_probability,
)
from src.analysis.elo89 import Elo89Artifacts
from src.sumo_core.BasicPrimitives import RikId, Month, Year
from src.sumo_core.History import Date


DATE = Date(Year(2026), Month(11))


def ratings() -> Elo89Artifacts:
    return Elo89Artifacts(
        root=Path("."),
        manifest={"model_id": "elo-89", "q": 400.0},
        prior={},
        basho_start_ratings={str(DATE): {"1": 2000.0, "2": 2000.0}},
        day_end_ratings={str(DATE): {"4": {"1": 2200.0, "2": 2000.0}}},
        basho_end_ratings={},
        bout_ledger=(),
    )


def payload() -> dict:
    return {
        "events": [
            {
                "name": "Alpha vs Beta",
                "competitor_1": "Alpha",
                "competitor_2": "Beta",
                "url": "https://example.test/alpha-vs-beta",
                "odds": [
                    {"outcome": "Alpha", "price": "1.50", "market": "Fight Result (2-Way)"},
                    {"outcome": "Beta", "price": "2.50", "market": "Fight Result (2-Way)"},
                ],
            }
        ]
    }


def test_joins_pre_day_ratings_and_converts_probabilities_to_decimal_odds() -> None:
    result = analyse_odds_payload(
        payload(),
        name_index={"alpha": RikId(1), "beta": RikId(2)},
        ratings=ratings(),
        basho=DATE,
        day=5,
    )[0]

    assert result.first.rating == 2200.0
    assert result.second.rating == 2000.0
    assert result.first.elo_probability == pytest.approx(0.7597469)
    assert result.first.elo_decimal_odds == pytest.approx(1.3162278)
    assert result.second.elo_decimal_odds == pytest.approx(4.1622777)
    assert result.market_overround == pytest.approx((1 / 1.5) + (1 / 2.5) - 1)
    assert result.first.market_normalized_probability == pytest.approx(0.625)
    assert result.second.market_normalized_probability == pytest.approx(0.375)


def test_day_one_uses_basho_start_ratings() -> None:
    result = analyse_odds_payload(
        payload(),
        name_index={"alpha": RikId(1), "beta": RikId(2)},
        ratings=ratings(),
        basho=DATE,
        day=1,
    )[0]
    assert result.first.elo_probability == pytest.approx(0.5)
    assert result.second.elo_probability == pytest.approx(0.5)
    assert result.first.elo_decimal_odds == pytest.approx(2.0)


def test_external_name_must_match_selected_banzuke() -> None:
    with pytest.raises(ValueError, match="absent from the selected banzuke"):
        analyse_odds_payload(
            payload(),
            name_index={"alpha": RikId(1)},
            ratings=ratings(),
            basho=DATE,
            day=5,
        )


def test_decimal_price_accepts_evens_and_rejects_invalid_values() -> None:
    assert decimal_price("EVS") == 2.0
    with pytest.raises(ValueError, match="greater than 1"):
        decimal_price("1.0")


def test_elo_probability_is_complementary() -> None:
    first = elo_probability(2200.0, 2000.0, 400.0)
    second = elo_probability(2000.0, 2200.0, 400.0)
    assert first + second == pytest.approx(1.0)

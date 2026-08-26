from __future__ import annotations

import csv

import pytest

from src.analysis.equelo_population_policy.predict_candidate import (
    _bootstrap_blocks,
    load_alpha_prior,
)
from src.analysis.elo_model_selection.model import ComparisonDefinition
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date


def test_load_alpha_prior_pairs_east_and_west_and_keeps_singleton(tmp_path):
    source = tmp_path / "prior.csv"
    with source.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("variant", "chii", "rating"),
        )
        writer.writeheader()
        writer.writerows((
            {"variant": "uniform", "chii": "M1e", "rating": 9999},
            {"variant": "support_1", "chii": "M1e", "rating": 1700},
            {"variant": "support_1", "chii": "M1w", "rating": 1500},
            {"variant": "support_1", "chii": "J1e", "rating": 1300},
        ))

    prior, conversion = load_alpha_prior(source)

    assert prior.rating_by_pair == {"M1": pytest.approx(1600), "J1": pytest.approx(1300)}
    assert prior.fallback_rating == pytest.approx(1300)
    assert conversion.source_row_count == 3
    assert conversion.pair_count == 2
    assert conversion.singleton_pair_count == 1


def test_load_alpha_prior_accepts_canonical_single_variant_schema(tmp_path):
    source = tmp_path / "prior.csv"
    with source.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("chii", "rating"))
        writer.writeheader()
        writer.writerows((
            {"chii": "M1e", "rating": 1700},
            {"chii": "M1w", "rating": 1500},
        ))

    prior, conversion = load_alpha_prior(source)

    assert prior.rating_by_pair == {"M1": pytest.approx(1600)}
    assert conversion.source_row_count == 2


def test_block_bootstrap_is_exact_for_identical_blocks():
    definition = ComparisonDefinition(
        start_date=Date(Year(1989), Month(1)),
        end_date=Date(Year(1989), Month(1)),
        bootstrap_resamples=20,
    )

    interval = _bootstrap_blocks(((2.0, 2), (3.0, 3)), definition, seed_offset=0)

    assert interval == pytest.approx((1.0, 1.0, 1.0))

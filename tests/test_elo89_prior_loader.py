from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.analysis.elo89.config import ACCEPTED_PRIOR_PATH
from src.analysis.elo89.prior_loader import load_paired_prior
from src.sumo_core.Chii import Chii


def _write(path: Path, rows, *, columns=("rank_pair", "ordinal", "rating")) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def test_loads_persisted_p1_prime_wl_without_transformation() -> None:
    prior = load_paired_prior(ACCEPTED_PRIOR_PATH)

    assert len(prior.rating_by_pair) == 484
    assert prior.rating_by_pair["K1"] == pytest.approx(2324.543725202043)
    assert prior.rating_by_pair["M1"] == pytest.approx(2303.0923611064345)
    assert prior.source_path == str(ACCEPTED_PRIOR_PATH.resolve())
    assert prior.sha256 == (
        "31ba2ea5430fb6a117b80290e78570cbbb160875febb6af14664a6c64ec93cdf"
    )


def test_loader_rejects_literal_prior_schema(tmp_path: Path) -> None:
    path = tmp_path / "literal.csv"
    _write(
        path,
        ({"chii": "M1e", "support": 100, "rating": 2200},),
        columns=("chii", "support", "rating"),
    )

    with pytest.raises(ValueError, match="exactly the columns"):
        load_paired_prior(path)


@pytest.mark.parametrize(
    ("row", "message"),
    (
        ({"rank_pair": "M1e", "ordinal": 400100, "rating": 2200}, "side-"),
        ({"rank_pair": "K2", "ordinal": 300202, "rating": 2200}, "slot 1"),
        ({"rank_pair": "M1", "ordinal": 123, "rating": 2200}, "Ordinal mismatch"),
        ({"rank_pair": "M1", "ordinal": 400102, "rating": "nan"}, "Non-finite"),
    ),
)
def test_loader_rejects_invalid_paired_rows(tmp_path: Path, row, message) -> None:
    path = tmp_path / "invalid.csv"
    _write(path, (row,))

    with pytest.raises(ValueError, match=message):
        load_paired_prior(path)


def test_loader_rejects_duplicate_and_unsorted_pairs(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.csv"
    _write(
        duplicate,
        (
            {"rank_pair": "M1", "ordinal": Chii.from_str("M1").ordinal(), "rating": 2200},
            {"rank_pair": "M1", "ordinal": Chii.from_str("M1").ordinal(), "rating": 2100},
        ),
    )
    with pytest.raises(ValueError, match="Duplicate"):
        load_paired_prior(duplicate)

    unsorted = tmp_path / "unsorted.csv"
    _write(
        unsorted,
        (
            {"rank_pair": "M2", "ordinal": Chii.from_str("M2").ordinal(), "rating": 2100},
            {"rank_pair": "M1", "ordinal": Chii.from_str("M1").ordinal(), "rating": 2200},
        ),
    )
    with pytest.raises(ValueError, match="strictly increasing"):
        load_paired_prior(unsorted)

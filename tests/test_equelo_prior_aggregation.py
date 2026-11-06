from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from src.analysis.equelo_prior_aggregation.experiment import (
    LiteralPriorRow,
    aggregate_prior,
    load_literal_prior,
    run_experiment,
)
from src.sumo_core.Chii import Chii


def _row(chii: str, rating: float, support: float) -> LiteralPriorRow:
    return LiteralPriorRow(Chii.from_str(chii), chii, rating, support)


def _write_prior(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=("chii", "ordinal", "support", "rating")
        )
        writer.writeheader()
        for chii, support, rating in rows:
            writer.writerow(
                {
                    "chii": chii,
                    "ordinal": Chii.from_str(chii).ordinal(),
                    "support": support,
                    "rating": rating,
                }
            )


def test_support_weighting_includes_sides_and_unbounded_sanyaku_slots():
    rows = (
        _row("Y1e", 2500, 100),
        _row("Y1w", 2300, 10),
        _row("Y17e", 1900, 2),
        _row("Y17w", 1700, 1),
        _row("M1e", 2200, 90),
        _row("M1w", 1800, 10),
    )

    result = {
        row.rank_pair: row
        for row in aggregate_prior(rows, source="p1", policy="support_weighted")
    }

    assert result["Y1"].rating == pytest.approx(
        (2500 * 100 + 2300 * 10 + 1900 * 2 + 1700) / 113
    )
    assert [row.chii_label for row in result["Y1"].constituents] == [
        "Y1e",
        "Y1w",
        "Y17e",
        "Y17w",
    ]
    assert result["M1"].rating == pytest.approx(2160)


@pytest.mark.parametrize("family", ("Y", "O", "S", "K"))
def test_support_weighting_is_generic_across_sanyaku_families(family):
    rows = (
        _row(f"{family}1e", 2500, 100),
        _row(f"{family}1w", 2300, 10),
        _row(f"{family}17e", 1900, 2),
        _row(f"{family}17w", 1700, 1),
    )

    result = aggregate_prior(rows, source="p1", policy="support_weighted")

    assert len(result) == 1
    assert result[0].rank_pair == f"{family}1"
    assert result[0].rating == pytest.approx(
        (2500 * 100 + 2300 * 10 + 1900 * 2 + 1700) / 113
    )


def test_legacy_and_canonical_sanyaku_policies_remain_distinct():
    rows = (
        _row("K1e", 2400, 100),
        _row("K1w", 2300, 100),
        _row("K2e", 2000, 1),
        _row("K2w", 1900, 1),
        _row("M1e", 2200, 90),
        _row("M1w", 1800, 10),
    )

    legacy = {
        row.rank_pair: row.rating
        for row in aggregate_prior(rows, source="p1", policy="legacy_unweighted")
    }
    canonical = {
        row.rank_pair: row.rating
        for row in aggregate_prior(rows, source="p1", policy="canonical_sanyaku")
    }

    assert legacy == {"K1": pytest.approx(2150), "M1": pytest.approx(2000)}
    assert canonical == {"K1": pytest.approx(2350), "M1": pytest.approx(2000)}


def test_literal_prior_requires_explicit_support(tmp_path):
    source = tmp_path / "prior.csv"
    source.write_text("chii,rating\nM1e,2000\n", encoding="utf-8")

    with pytest.raises(ValueError, match="support"):
        load_literal_prior(source)


def test_run_experiment_writes_hashed_artifacts_and_refuses_overwrite(tmp_path):
    p1 = tmp_path / "p1.csv"
    p1_wl = tmp_path / "p1-wl.csv"
    rows = (
        ("K1e", 100, 2400),
        ("K1w", 90, 2300),
        ("K2e", 5, 2000),
        ("K2w", 5, 1900),
        ("M1e", 100, 2250),
        ("M1w", 100, 2200),
    )
    _write_prior(p1, rows)
    _write_prior(p1_wl, rows)
    output = tmp_path / "output"
    persisted = tmp_path / "results" / "priors.csv"

    run_experiment(
        p1_path=p1,
        p1_wl_path=p1_wl,
        output=output,
        persisted_prior_path=persisted,
    )

    assert {path.name for path in output.iterdir()} == {
        "manifest.json",
        "paired_priors.csv",
        "comparison.csv",
        "findings.md",
    }
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert set(manifest["outputs"]) == {
        "paired_priors.csv",
        "comparison.csv",
        "findings.md",
    }
    assert manifest["persisted_official_prior"]["path"] == str(persisted.resolve())
    with persisted.open(newline="", encoding="utf-8") as stream:
        persisted_rows = list(csv.DictReader(stream))
    assert tuple(persisted_rows[0]) == ("rank_pair", "ordinal", "rating")
    assert [row["rank_pair"] for row in persisted_rows] == ["K1", "M1"]
    assert float(persisted_rows[0]["rating"]) == pytest.approx(2332.5)

    second_output = tmp_path / "second-output"
    run_experiment(
        p1_path=p1,
        p1_wl_path=p1_wl,
        output=second_output,
        persisted_prior_path=persisted,
    )

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        run_experiment(
            p1_path=p1,
            p1_wl_path=p1_wl,
            output=output,
            persisted_prior_path=persisted,
        )


def test_run_experiment_refuses_to_replace_different_persisted_prior(tmp_path):
    p1 = tmp_path / "p1.csv"
    p1_wl = tmp_path / "p1-wl.csv"
    rows = (
        ("K1e", 100, 2400),
        ("K1w", 100, 2300),
        ("M1e", 100, 2250),
        ("M1w", 100, 2200),
    )
    _write_prior(p1, rows)
    _write_prior(p1_wl, rows)
    persisted = tmp_path / "results" / "priors.csv"
    run_experiment(
        p1_path=p1,
        p1_wl_path=p1_wl,
        output=tmp_path / "first-output",
        persisted_prior_path=persisted,
    )
    changed = list(rows)
    changed[0] = ("K1e", 100, 2500)
    _write_prior(tmp_path / "changed.csv", changed)

    with pytest.raises(FileExistsError, match="different persisted official prior"):
        run_experiment(
            p1_path=p1,
            p1_wl_path=tmp_path / "changed.csv",
            output=tmp_path / "rejected-output",
            persisted_prior_path=persisted,
        )

    assert not (tmp_path / "rejected-output").exists()


def test_repository_persists_the_accepted_p1_prime_wl_prior():
    path = Path("src/analysis/equelo_prior_aggregation/results/priors.csv")

    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    assert tuple(rows[0]) == ("rank_pair", "ordinal", "rating")
    assert len(rows) == 484
    indexed = {row["rank_pair"]: float(row["rating"]) for row in rows}
    assert indexed["K1"] == pytest.approx(2323.047888779248)
    assert indexed["M1"] == pytest.approx(2301.520014989377)

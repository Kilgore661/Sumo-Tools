"""Focused checks for the matched Elo-89 versus chii comparison."""

from __future__ import annotations

from dataclasses import replace

import pytest

from src.analysis.chii_prediction.__main__ import parse_date
from src.analysis.chii_prediction.comparison import (
    aggregate_rows,
    compare_forecasts,
    subgroup_rows,
)
from src.analysis.chii_prediction.comparison_output import write_comparison_outputs
from src.analysis.elo89.model import Forecast
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.Chii import Chii


def test_common_domain_discordance_and_exclusions() -> None:
    date = parse_date("1989/01")
    forecasts = (
        _forecast(date, a_won=True, elo_a=True, chii_a=True),   # both correct
        _forecast(date, a_won=True, elo_a=True, chii_a=False),  # Elo only
        _forecast(date, a_won=True, elo_a=False, chii_a=True),  # chii only
        _forecast(date, a_won=True, elo_a=False, chii_a=False), # both wrong
        _forecast(date, a_won=True, elo_a=None, chii_a=True),
        _forecast(date, a_won=True, elo_a=True, chii_a="equal"),
        _forecast(date, a_won=True, elo_a=True, chii_a=None),
    )
    result = compare_forecasts(
        forecasts, evaluation_start=date, evaluation_end=date,
        bootstrap_replicates=20, bootstrap_seed=7,
    )

    assert result.primary_count == 4
    assert (result.both_correct, result.elo_correct_chii_wrong,
            result.elo_wrong_chii_correct, result.both_wrong) == (1, 1, 1, 1)
    assert result.elo_tie_count == result.equal_chii_count == result.missing_chii_count == 1
    assert result.elo_accuracy == result.chii_accuracy == 0.5
    assert result.elo_minus_chii.estimate == 0
    assert result.conclusion == "contradicted"


def test_orientation_does_not_change_rule_correctness() -> None:
    date = parse_date("1989/01")
    original = _forecast(date, a_won=True, elo_a=True, chii_a=True)
    reversed_row = replace(
        original,
        rikishi_a=original.rikishi_b,
        rikishi_b=original.rikishi_a,
        chii_a=original.chii_b,
        chii_b=original.chii_a,
        rating_a_before=original.rating_b_before,
        rating_b_before=original.rating_a_before,
        probability_a_wins=1.0 - original.probability_a_wins,
        a_won=False,
    )
    result = compare_forecasts(
        (original, reversed_row), evaluation_start=date, evaluation_end=date,
        bootstrap_replicates=10,
    )
    assert result.elo_accuracy == result.chii_accuracy == 1


def test_complete_ordering_requires_both_lower_bounds() -> None:
    forecasts = []
    for month in (1, 3, 5, 7, 9, 11):
        date = parse_date(f"1989/{month:02d}")
        # Identical basho blocks: Elo 10/10, chii 6/10, so both lower bounds
        # remain strictly positive under complete-basho resampling.
        forecasts.extend(
            _forecast(date, a_won=True, elo_a=True, chii_a=index < 6)
            for index in range(10)
        )
    result = compare_forecasts(
        forecasts,
        evaluation_start=parse_date("1989/01"),
        evaluation_end=parse_date("1989/11"),
        bootstrap_replicates=100,
        bootstrap_seed=89,
    )
    assert result.elo_minus_chii.one_sided_lower_95 == pytest.approx(0.4)
    assert result.chii_minus_random.one_sided_lower_95 == pytest.approx(0.1)
    assert result.conclusion == "confirmed"


def test_later_evaluation_start_only_filters_scoring() -> None:
    january = parse_date("1989/01")
    march = parse_date("1989/03")
    early = _forecast(january, a_won=False, elo_a=True, chii_a=True)
    later = replace(
        _forecast(march, a_won=True, elo_a=True, chii_a=True),
        rating_a_before=1777.0,
        rated_bouts_a_before=12,
    )
    result = compare_forecasts(
        (early, later), evaluation_start=march, evaluation_end=march,
        bootstrap_replicates=10,
    )
    assert len(result.rows) == 1
    assert result.rows[0].rating_a_before == 1777.0
    assert result.rows[0].rated_bouts_a_before == 12


def test_division_and_maturity_subgroups_partition_primary_total() -> None:
    date = parse_date("1989/01")
    rows = (
        _forecast(date, a_won=True, elo_a=True, chii_a=True, ranks=("M1e", "M2e"), counts=(0, 4)),
        _forecast(date, a_won=True, elo_a=True, chii_a=True, ranks=("J1e", "J2e"), counts=(10, 20)),
        _forecast(date, a_won=True, elo_a=True, chii_a=True, ranks=("Ms1e", "J1e"), counts=(100, 200)),
    )
    result = compare_forecasts(
        rows, evaluation_start=date, evaluation_end=date,
        bootstrap_replicates=10,
    )
    summaries = {row["population"]: row for row in subgroup_rows(result)}
    division_total = sum(summaries[name]["bouts"] for name in (
        "MAKUUCHI", "JURYO", "MAKUSHITA", "SANDANME", "JONIDAN", "JONOKUCHI", "CROSS_DIVISION"
    ))
    maturity_total = sum(summaries[f"MATURITY_{name}"]["bouts"] for name in (
        "0", "1-9", "10-49", "50-99", "100+"
    ))
    assert division_total == maturity_total == result.primary_count == 3
    assert aggregate_rows(result.rows)["paired_difference"] == (
        result.elo_correct_chii_wrong - result.elo_wrong_chii_correct
    ) / result.primary_count


def test_basho_bootstrap_is_deterministic() -> None:
    january = parse_date("1989/01")
    march = parse_date("1989/03")
    forecasts = (
        _forecast(january, a_won=True, elo_a=True, chii_a=False),
        _forecast(march, a_won=True, elo_a=False, chii_a=True),
        _forecast(march, a_won=True, elo_a=True, chii_a=True),
    )
    arguments = dict(
        evaluation_start=january, evaluation_end=march,
        bootstrap_replicates=200, bootstrap_seed=123,
    )
    first = compare_forecasts(forecasts, **arguments)
    second = compare_forecasts(forecasts, **arguments)
    assert first.elo_minus_chii == second.elo_minus_chii


def test_retained_output_smoke(tmp_path) -> None:
    date = parse_date("1989/01")
    result = compare_forecasts(
        (_forecast(date, a_won=True, elo_a=True, chii_a=True),),
        evaluation_start=date, evaluation_end=date,
        bootstrap_replicates=10,
    )
    history = tmp_path / "history.zip"
    prior = tmp_path / "prior.csv"
    k_config = tmp_path / "k.json"
    history.write_bytes(b"fixture")
    prior.write_text("fixture", encoding="utf-8")
    k_config.write_text("{}", encoding="utf-8")
    paths = write_comparison_outputs(
        result=result, output_root=tmp_path / "output",
        history_source=history, history_sha256="history-sha",
        represented_start="1989/01", represented_end="1989/01",
        prior_source=str(prior), prior_sha256="prior-sha",
        k_config_path=k_config, k_config_sha256="k-sha", q=400.0,
    )
    assert paths.manifest.is_file()
    assert paths.bout_comparison.is_file()
    assert "Decision: contradicted" in paths.report.read_text(encoding="utf-8")


def _forecast(
    date,
    *,
    a_won: bool,
    elo_a: bool | None,
    chii_a: bool | None | str,
    ranks: tuple[str, str] | None = None,
    counts: tuple[int, int] = (0, 0),
) -> Forecast:
    probability = 0.7 if elo_a is True else 0.3 if elo_a is False else 0.5
    if ranks is None:
        ranks = ("M1e", "M2e") if chii_a is True else ("M2e", "M1e")
    if chii_a == "equal":
        ranks = ("M1e", "M1e")
    chii_left = None if chii_a is None else Chii.from_str(ranks[0])
    chii_right = None if chii_a is None else Chii.from_str(ranks[1])
    return Forecast(
        date=date, day=Day(1), rikishi_a=RikId(1), rikishi_b=RikId(2),
        chii_a=chii_left, chii_b=chii_right,
        rating_a_before=1600.0 if elo_a is not False else 1400.0,
        rating_b_before=1400.0 if elo_a is not False else 1600.0,
        rated_bouts_a_before=counts[0], rated_bouts_b_before=counts[1],
        probability_a_wins=probability, a_won=a_won,
        k_a=20.0, k_b=20.0, delta_a=0.0, delta_b=0.0,
        rating_a_after=1600.0, rating_b_after=1400.0,
        initialisation_a="fixture", initialisation_b="fixture",
    )

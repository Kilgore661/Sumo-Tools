from __future__ import annotations

import csv
from math import isclose

from src.analysis.elo_model_selection.evaluation import evaluate
from src.analysis.elo_model_selection.model import (
    AdoptedPrior,
    ComparisonDefinition,
    load_adopted_prior,
    rank_pair,
    run_comparison,
)
from src.analysis.elo_model_selection.output import HistorySource, write_outputs
from src.analysis.prediction.definition import Proposal1Definition
from src.analysis.prediction.experiment import build_forecast_ledger
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import (
    Day,
    Month,
    Pair,
    RikId,
    Riks,
    Shikona,
    Torikumi,
    Year,
)
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary


def test_load_adopted_prior_uses_paired_values_without_transformation(tmp_path) -> None:
    path = tmp_path / "prior.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("rank_pair", "pre_smoothing_rating"))
        writer.writeheader()
        writer.writerow({"rank_pair": "M1", "pre_smoothing_rating": "2125.25"})
        writer.writerow({"rank_pair": "J1", "pre_smoothing_rating": "1953.5"})

    prior = load_adopted_prior(path)

    assert prior.rating_for(Chii.from_str("M1e")) == (2125.25, "adopted prior M1")
    assert prior.rating_for(Chii.from_str("M1wTD")) == (2125.25, "adopted prior M1")
    assert prior.fallback_rating == 1953.5
    assert rank_pair(Chii.from_str("J1w")) == "J1"
    assert rank_pair(Chii.from_str("O2eHD")) == "O1"


def test_four_models_share_bouts_and_change_only_declared_factors() -> None:
    first = _date(1989, 1)
    second = _date(1989, 3)
    history = History({
        first: _basho(_result(1, True, 2), {1: "M1e", 2: "J1w"}),
        second: _basho(_result(1, True, 2), {1: "M1e", 2: "J1w"}),
    })
    definition = ComparisonDefinition(
        start_date=first,
        end_date=second,
        bootstrap_resamples=50,
    )
    run = run_comparison(history, definition, prior=_prior())
    models = {model.spec.name: model for model in run.models}

    assert tuple(models) == ("B", "B_k", "B_P", "B_kP")
    assert all(len(model.forecasts) == 2 for model in models.values())
    assert models["B"].forecasts[0].probability_a_wins == 0.5
    assert models["B_k"].forecasts[0].probability_a_wins == 0.5
    assert models["B_P"].forecasts[0].rating_a_before == 1700.0
    assert models["B_P"].forecasts[0].rating_b_before == 1300.0
    assert models["B_kP"].forecasts[0].probability_a_wins == models["B_P"].forecasts[0].probability_a_wins

    divisional = models["B_k"].forecasts[0]
    assert divisional.k_a == 15.0
    assert divisional.k_b == 25.0
    assert divisional.rating_a_after == 1507.5
    assert divisional.rating_b_after == 1487.5
    assert models["B"].forecasts[0].rating_a_after == 1517.5
    assert models["B"].forecasts[0].rating_b_after == 1482.5


def test_b_cell_exactly_reproduces_basic_elo_on_shared_bouts() -> None:
    date = _date(1989, 1)
    history = History({date: _basho(_result(1, True, 2), {1: "M1e", 2: "J1w"})})
    definition = ComparisonDefinition(start_date=date, end_date=date, bootstrap_resamples=20)
    run = run_comparison(history, definition, prior=_prior())
    basic = build_forecast_ledger(
        run.selection.bouts,
        Proposal1Definition(end_date=date, start_date=date),
    )[0]
    selected = run.models[0].forecasts[0]

    assert selected.model == "B"
    assert selected.rating_a_before == basic.rating_a_before
    assert selected.rating_b_before == basic.rating_b_before
    assert selected.probability_a_wins == basic.probability_a_wins
    assert selected.delta_a == basic.delta_a
    assert selected.rating_a_after == basic.rating_a_after
    assert selected.rating_b_after == basic.rating_b_after


def test_unranked_rikishi_uses_declared_prior_and_k_fallback() -> None:
    date = _date(1989, 1)
    history = History({date: _basho(_result(1, True, 2), {1: "M1e"})})
    run = run_comparison(
        history,
        ComparisonDefinition(start_date=date, end_date=date, bootstrap_resamples=20),
        prior=_prior(),
    )
    rows = {model.spec.name: model.forecasts[0] for model in run.models}

    assert rows["B_P"].rating_b_before == 1100.0
    assert rows["B_P"].initialisation_b == "unranked weakest-prior fallback"
    assert rows["B_kP"].k_b == 35.0


def test_evaluation_and_outputs_preserve_all_models(tmp_path) -> None:
    first = _date(1989, 1)
    second = _date(1989, 3)
    history = History({
        first: _basho(_result(1, True, 2), {1: "M1e", 2: "J1w"}),
        second: _basho(_result(1, True, 2), {1: "M1e", 2: "J1w"}),
    })
    run = run_comparison(
        history,
        ComparisonDefinition(start_date=first, end_date=second, bootstrap_resamples=50),
        prior=_prior(),
    )
    result = evaluate(run)

    all_rows = tuple(row for row in result.summaries if row.population == "all")
    assert tuple(row.model for row in all_rows) == ("B", "B_k", "B_P", "B_kP")
    assert all(row.bout_count == 2 for row in all_rows)
    assert next(row for row in all_rows if row.model == "B_P").mean_log_loss < next(
        row for row in all_rows if row.model == "B"
    ).mean_log_loss
    assert {
        row.contrast for row in result.factorial_contrasts if row.population == "all"
    } == {
        "k under constant initialisation",
        "P under constant k",
        "P under divisional k",
        "k under informed initialisation",
        "k-by-P interaction",
    }
    all_calibration = tuple(
        row for row in result.calibration_summaries if row.population == "all"
    )
    assert tuple(row.model for row in all_calibration) == ("B", "B_k", "B_P", "B_kP")
    assert all(row.bout_count == 2 for row in all_calibration)
    assert all(row.participant_count == 4 for row in all_calibration)
    assert all(row.supported_bin_count == 0 for row in all_calibration)
    assert all(row.supported_maximum_calibration_error is None for row in all_calibration)
    assert result.support_pair_calibration
    assert result.coarse_support_pair_calibration
    assert {row.model for row in result.support_pair_calibration} == {
        "B", "B_k", "B_P", "B_kP"
    }
    assert all(row.participant_count == 2 * row.bout_count for row in result.support_pair_calibration)
    b_bins = tuple(
        row for row in result.calibration_bins
        if row.population == "all" and row.model == "B"
    )
    assert sum(row.participant_count for row in b_bins) == 4
    assert sum(row.win_count for row in b_bins) == 2
    assert isclose(
        sum(row.mean_predicted_probability * row.participant_count for row in b_bins) / 4,
        0.5,
    )

    output = tmp_path / "output"
    write_outputs(run, result, output, HistorySource("fixture.zip", "abc"))
    assert (output / "manifest.json").is_file()
    assert (output / "factorial_contrasts.csv").is_file()
    assert (output / "calibration.csv").is_file()
    assert (output / "calibration_summary.csv").is_file()
    assert (output / "calibration_by_support_pair.csv").is_file()
    assert (output / "calibration_by_support_pair_coarse.csv").is_file()
    chart = (output / "calibration_all.html").read_text(encoding="utf-8")
    assert "https://cdn.plot.ly/plotly-3.0.1.min.js" in chart
    assert "displayModeBar: true" in chart
    assert "responsive: true" in chart
    assert 'window.addEventListener("resize"' in chart
    assert "min-height" not in chart
    support_chart = (output / "calibration_by_support.html").read_text(encoding="utf-8")
    assert "B_kP calibration by minimum prior rated bouts: initial range" in support_chart
    assert "support <15" in support_chart
    assert "support 15-19" in support_chart
    assert "support 25-29" in support_chart
    assert "support 30-34" in support_chart
    assert "support 45-49" in support_chart
    assert "support 50+" in support_chart
    assert "bouts)" in support_chart
    assert "displayModeBar: true" in support_chart
    career_chart = (output / "calibration_by_career_support.html").read_text(
        encoding="utf-8"
    )
    assert "B_kP calibration by minimum prior rated bouts: career scale" in career_chart
    assert "prior bouts <30" in career_chart
    assert "prior bouts 480+" in career_chart
    assert "displayModeBar: true" in career_chart
    heatmap = (output / "calibration_ece_heatmap.html").read_text(encoding="utf-8")
    assert "Calibration error by model and rating maturity" in heatmap
    assert '"type": "heatmap"' in heatmap
    assert '"B_kP"' in heatmap
    assert '"480+"' in heatmap
    assert "ECE=%{z:.2f} percentage points" in heatmap
    assert "displayModeBar: true" in heatmap
    assert "responsive: true" in heatmap
    assert 'window.addEventListener("resize"' in heatmap
    distribution = (output / "rating_maturity_distribution.html").read_text(
        encoding="utf-8"
    )
    assert "Distribution of bouts by rating maturity" in distribution
    assert '"type": "bar"' in distribution
    assert '"<30"' in distribution
    assert '"480+"' in distribution
    assert "share=%{customdata:.1%}" in distribution
    assert "displayModeBar: true" in distribution
    assert "responsive: true" in distribution
    pair_heatmap = (output / "calibration_ece_by_support_pair.html").read_text(
        encoding="utf-8"
    )
    assert "Calibration error by paired rating maturity" in pair_heatmap
    assert pair_heatmap.count('"type": "heatmap"') == 4
    assert "lower-support rating=%{y}" in pair_heatmap
    assert "higher-support rating=%{x}" in pair_heatmap
    assert "Prior rated bouts: less-experienced rikishi" in pair_heatmap
    assert "Prior rated bouts: more-experienced rikishi" in pair_heatmap
    assert "ECE (expected calibration error)" in pair_heatmap
    assert "participant-weighted" in pair_heatmap
    assert pair_heatmap.count("<br>") >= 2
    assert "Hover for bout count" in pair_heatmap
    assert '"570-599"' in pair_heatmap
    assert '"600+"' in pair_heatmap
    assert '"active": 3' in pair_heatmap
    assert "displayModeBar: true" in pair_heatmap
    assert "responsive: true" in pair_heatmap
    coarse_pair_heatmap = (
        output / "calibration_ece_by_support_pair_coarse.html"
    ).read_text(encoding="utf-8")
    assert "coarse bands" in coarse_pair_heatmap
    assert '"60-119"' in coarse_pair_heatmap
    assert '"480+"' in coarse_pair_heatmap
    assert '"600+"' not in coarse_pair_heatmap
    assert coarse_pair_heatmap.count('"type": "heatmap"') == 4
    assert "displayModeBar: true" in coarse_pair_heatmap
    assert "future-informed" in (output / "report.md").read_text(encoding="utf-8")
    with (output / "forecast_ledger.csv").open(newline="", encoding="utf-8") as stream:
        assert len(tuple(csv.DictReader(stream))) == 8


def _prior() -> AdoptedPrior:
    return AdoptedPrior(
        source_path="fixture-prior.csv",
        sha256="fixture",
        rating_by_pair={"M1": 1700.0, "J1": 1300.0, "Ms1": 1100.0},
        fallback_rating=1100.0,
    )


def _result(winner: int, winner_won: bool, loser: int) -> BoutResult:
    assert winner_won
    return BoutResult(
        rikishi1=RikId(winner),
        outcome1=Outcome.W,
        rikishi2=RikId(loser),
        outcome2=Outcome.L,
        decision="blank",
        symbol=Symbol.W,
    )


def _basho(result: BoutResult, rank_by_id: dict[int, str]) -> BashoState:
    rikishi_ids = {RikId(value) for value in rank_by_id}
    lookup = ResultLookup({Pair(result.rikishi1, result.rikishi2): result})
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(rikishi_ids),
            rikchii=RikChii({RikId(value): Chii.from_str(rank) for value, rank in rank_by_id.items()}),
            rikshik=RikShikona({rid: Shikona(f"Rikishi {rid}") for rid in rikishi_ids}),
        ),
        summary=Summary({
            Day(1): DailyResults(
                torikumi=Torikumi(set(lookup)),
                results_lookup=lookup,
            )
        }),
    )


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))

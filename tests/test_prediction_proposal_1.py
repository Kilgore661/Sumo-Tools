from math import isclose

from src.analysis.prediction.basic_elo import BasicEloProducer
from src.analysis.prediction.charts import _plot_date
from src.analysis.prediction.chii_prior import build_chii_prior
from src.analysis.prediction.output import _dated_rows
from src.analysis.prediction.bouts import (
    BoutId,
    Contest,
    RatedBout,
    select_rated_bouts,
)
from src.analysis.prediction.definition import Proposal1Definition
from src.analysis.prediction.experiment import build_forecast_ledger
from src.analysis.prediction.scoring import score_forecasts
from src.analysis.prediction.run import run_proposal_1
from src.analysis.prediction.sekitori import (
    evaluate_sekitori_bouts,
    evaluate_sub_sekitori_bouts,
    is_sekitori,
)
from src.analysis.prediction.series import (
    build_basho_loss_rows,
    build_cumulative_loss_rows,
    build_rolling_loss_rows,
)
from src.analysis.prediction.uncertainty import build_uncertainty_rows
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


def test_selection_includes_blank_win_loss_and_excludes_non_contests() -> None:
    date = _date(1989, 1)
    blank_win = _result(1, Outcome.W, 2, Outcome.L, "blank")
    fusen = _result(3, Outcome.FS, 4, Outcome.FP, "fusen")
    draw = _result(5, Outcome.DRAW, 6, Outcome.DRAW, "blank")
    history = History({date: _basho(blank_win, fusen, draw)})

    selection = select_rated_bouts(history, start_date=date, end_date=date)

    assert selection.raw_result_count == 3
    assert selection.rated_bout_count == 1
    assert selection.excluded_fusen_count == 1
    assert selection.excluded_draw_count == 1
    assert selection.bouts[0].contest.id.pair == Pair(RikId(1), RikId(2))


def test_prediction_precedes_update_and_ratings_persist_through_absence() -> None:
    definition = Proposal1Definition(end_date=_date(1989, 5), bootstrap_resamples=20)
    bouts = (
        _rated_bout(1989, 1, 1, 1, 2, True),
        _rated_bout(1989, 3, 1, 3, 4, True),
        _rated_bout(1989, 5, 1, 1, 3, True),
    )

    ledger = build_forecast_ledger(bouts, definition)

    assert ledger[0].probability_a_wins == 0.5
    assert ledger[0].rating_a_before == 1500
    assert ledger[0].rating_a_after == 1517.5
    assert ledger[2].rating_a_before == 1517.5
    assert ledger[2].rated_bouts_a_before == 1


def test_rating_origin_does_not_change_forecasts() -> None:
    bouts = (
        _rated_bout(1989, 1, 1, 1, 2, True),
        _rated_bout(1989, 1, 2, 1, 2, False),
        _rated_bout(1989, 1, 3, 1, 2, True),
    )
    at_1500 = build_forecast_ledger(
        bouts,
        Proposal1Definition(end_date=_date(1989, 1), initial_rating=1500),
    )
    at_2000 = build_forecast_ledger(
        bouts,
        Proposal1Definition(end_date=_date(1989, 1), initial_rating=2000),
    )

    for left, right in zip(at_1500, at_2000):
        assert isclose(left.probability_a_wins, right.probability_a_wins)


def test_explicit_initial_ratings_reach_first_forecast() -> None:
    bout = _rated_bout(1989, 1, 1, 1, 2, True)
    ledger = build_forecast_ledger(
        (bout,),
        Proposal1Definition(end_date=_date(1989, 1)),
        {RikId(1): 1600.0, RikId(2): 1400.0},
    )

    assert ledger[0].rating_a_before == 1600.0
    assert ledger[0].rating_b_before == 1400.0
    assert ledger[0].probability_a_wins > 0.5


def test_later_result_cannot_change_earlier_forecasts() -> None:
    definition = Proposal1Definition(end_date=_date(1989, 1))
    shared = (
        _rated_bout(1989, 1, 1, 1, 2, True),
        _rated_bout(1989, 1, 2, 1, 2, False),
    )
    won_last = build_forecast_ledger(
        shared + (_rated_bout(1989, 1, 3, 1, 2, True),),
        definition,
    )
    lost_last = build_forecast_ledger(
        shared + (_rated_bout(1989, 1, 3, 1, 2, False),),
        definition,
    )

    assert won_last[:2] == lost_last[:2]
    assert won_last[2].probability_a_wins == lost_last[2].probability_a_wins


def test_series_are_bout_weighted_and_uncertainty_is_reproducible() -> None:
    definition = Proposal1Definition(end_date=_date(1989, 3))
    ledger = build_forecast_ledger(
        (
            _rated_bout(1989, 1, 1, 1, 2, True),
            _rated_bout(1989, 1, 2, 1, 2, True),
            _rated_bout(1989, 3, 1, 1, 2, False),
        ),
        definition,
    )
    basho = build_basho_loss_rows(score_forecasts(ledger, reference_probability=0.5))
    rolling = build_rolling_loss_rows(basho, (2,))
    cumulative = build_cumulative_loss_rows(basho)
    first = build_uncertainty_rows(
        basho,
        windows=(2,),
        seed=7,
        resamples=100,
        confidence_level=0.95,
    )
    second = build_uncertainty_rows(
        basho,
        windows=(2,),
        seed=7,
        resamples=100,
        confidence_level=0.95,
    )

    expected = sum(row.log_loss_sum for row in basho) / 3
    assert isclose(rolling[0].mean_log_loss, expected)
    assert isclose(cumulative[-1].mean_log_loss, expected)
    assert first == second


def test_basic_elo_updates_are_symmetric() -> None:
    definition = Proposal1Definition(end_date=_date(1989, 1))
    producer = BasicEloProducer(definition)
    prediction = producer.predict(_rated_bout(1989, 1, 1, 1, 2, True).contest)
    transition = producer.update(prediction, a_won=True)

    assert transition.delta_a == 17.5
    assert transition.rating_a_after + transition.rating_b_after == 3000


def test_plot_dates_are_chronological_values_not_category_labels() -> None:
    assert _plot_date(_date(1989, 3)) == "1989-03-01"


def test_csv_rows_preserve_history_date_format() -> None:
    definition = Proposal1Definition(
        end_date=_date(1989, 1),
        rolling_windows=(1,),
        bootstrap_resamples=10,
    )
    ledger = build_forecast_ledger(
        (_rated_bout(1989, 1, 1, 1, 2, True),),
        definition,
    )
    basho = build_basho_loss_rows(
        score_forecasts(ledger, reference_probability=0.5)
    )

    row = tuple(_dated_rows(basho))[0]

    assert row["date"] == "1989/01"


def test_sekitori_evaluation_requires_both_participants_in_domain() -> None:
    date = _date(1989, 1)
    history = History(
        {
            date: _ranked_basho(
                (
                    _result(1, Outcome.W, 2, Outcome.L, "blank"),
                    _result(3, Outcome.W, 4, Outcome.L, "blank"),
                    _result(5, Outcome.W, 6, Outcome.L, "blank"),
                ),
                {1: "J1e", 2: "M1e", 3: "J2e", 4: "Ms1e", 5: "Ms2e", 6: "Sd1e"},
            )
        }
    )
    baseline = run_proposal_1(
        history,
        Proposal1Definition(
            end_date=date,
            rolling_windows=(1,),
            bootstrap_resamples=10,
        ),
    )

    result = evaluate_sekitori_bouts(history, baseline)

    assert result.selection.evaluated_bout_count == 1
    assert result.selection.excluded_one_sekitori_count == 1
    assert result.selection.excluded_no_sekitori_count == 1
    assert result.forecasts[0].bout_id.pair == Pair(RikId(1), RikId(2))


def test_sub_sekitori_evaluation_requires_both_participants_in_domain() -> None:
    date = _date(1989, 1)
    history = History(
        {
            date: _ranked_basho(
                (
                    _result(1, Outcome.W, 2, Outcome.L, "blank"),
                    _result(3, Outcome.W, 4, Outcome.L, "blank"),
                    _result(5, Outcome.W, 6, Outcome.L, "blank"),
                ),
                {1: "J1e", 2: "M1e", 3: "J2e", 4: "Ms1e", 5: "Ms2e", 6: "Sd1e"},
            )
        }
    )
    baseline = run_proposal_1(
        history,
        Proposal1Definition(
            end_date=date,
            rolling_windows=(1,),
            bootstrap_resamples=10,
        ),
    )

    result = evaluate_sub_sekitori_bouts(history, baseline)

    assert result.selection.evaluated_bout_count == 1
    assert result.selection.excluded_one_sub_sekitori_count == 1
    assert result.selection.excluded_no_sub_sekitori_count == 1
    assert result.forecasts[0].bout_id.pair == Pair(RikId(5), RikId(6))


def test_excluded_cross_boundary_bout_still_updates_later_sekitori_ratings() -> None:
    first_date = _date(1989, 1)
    second_date = _date(1989, 3)
    history = History(
        {
            first_date: _ranked_basho(
                (_result(1, Outcome.W, 2, Outcome.L, "blank"),),
                {1: "J1e", 2: "Ms1e"},
            ),
            second_date: _ranked_basho(
                (_result(1, Outcome.W, 2, Outcome.L, "blank"),),
                {1: "J1e", 2: "J2e"},
            ),
        }
    )
    baseline = run_proposal_1(
        history,
        Proposal1Definition(
            end_date=second_date,
            rolling_windows=(1,),
            bootstrap_resamples=10,
        ),
    )

    result = evaluate_sekitori_bouts(history, baseline)

    assert result.selection.excluded_one_sekitori_count == 1
    assert result.selection.evaluated_bout_count == 1
    assert result.forecasts[0].rating_a_before == 1517.5
    assert result.forecasts[0].rating_b_before == 1482.5


def test_sekitori_membership_uses_chii_value() -> None:
    assert is_sekitori(Chii.from_str("M1e"))
    assert is_sekitori(Chii.from_str("J14w"))
    assert not is_sekitori(Chii.from_str("Ms1e"))


def test_chii_prior_retains_observed_reversal_without_smoothing() -> None:
    first_date = _date(1989, 1)
    second_date = _date(1989, 3)
    history = History(
        {
            first_date: _ranked_basho(
                (_result(1, Outcome.L, 2, Outcome.W, "blank"),),
                {1: "J1e", 2: "Ms1e"},
            ),
            second_date: _ranked_basho(
                (_result(1, Outcome.W, 2, Outcome.L, "blank"),),
                {1: "J1e", 2: "Ms1e"},
            ),
        }
    )
    baseline = run_proposal_1(
        history,
        Proposal1Definition(
            end_date=second_date,
            rolling_windows=(1,),
            bootstrap_resamples=10,
        ),
    )

    prior = build_chii_prior(history, baseline, trailing_observations=10)
    rows = {str(row.chii): row for row in prior.rows}

    assert rows["J1e"].initial_rating == 1482.5
    assert rows["Ms1e"].initial_rating == 1517.5
    assert rows["J1e"].source == "observed trailing mean"
    assert rows["Ms1e"].source == "observed trailing mean"


def _rated_bout(
    year: int,
    month: int,
    day: int,
    rikishi_a: int,
    rikishi_b: int,
    a_won: bool,
) -> RatedBout:
    pair = Pair(RikId(rikishi_a), RikId(rikishi_b))
    return RatedBout(
        contest=Contest(BoutId(_date(year, month), Day(day), pair)),
        a_won=a_won,
    )


def _result(
    rikishi1: int,
    outcome1: Outcome,
    rikishi2: int,
    outcome2: Outcome,
    decision: str,
) -> BoutResult:
    return BoutResult(
        rikishi1=RikId(rikishi1),
        outcome1=outcome1,
        rikishi2=RikId(rikishi2),
        outcome2=outcome2,
        decision=decision,
        symbol=outcome1.to_symbol(),
    )


def _basho(*results: BoutResult) -> BashoState:
    represented = {result.rikishi1 for result in results} | {
        result.rikishi2 for result in results
    }
    banzuke_ids = represented - {RikId(2)}
    banzuke = Banzuke(
        riks=Riks(banzuke_ids),
        rikchii=RikChii({rid: Chii.from_str("J1e") for rid in banzuke_ids}),
        rikshik=RikShikona({rid: Shikona(f"Rikishi {rid}") for rid in banzuke_ids}),
    )
    lookup = ResultLookup({
        Pair(result.rikishi1, result.rikishi2): result for result in results
    })
    return BashoState(
        banzuke=banzuke,
        summary=Summary(
            {
                Day(1): DailyResults(
                    torikumi=Torikumi(set(lookup)),
                    results_lookup=lookup,
                )
            }
        ),
    )


def _ranked_basho(
    results: tuple[BoutResult, ...],
    rank_by_id: dict[int, str],
) -> BashoState:
    rikishi_ids = {RikId(value) for value in rank_by_id}
    lookup = ResultLookup({
        Pair(result.rikishi1, result.rikishi2): result for result in results
    })
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(rikishi_ids),
            rikchii=RikChii({
                RikId(value): Chii.from_str(rank)
                for value, rank in rank_by_id.items()
            }),
            rikshik=RikShikona({
                rikishi_id: Shikona(f"Rikishi {rikishi_id}")
                for rikishi_id in rikishi_ids
            }),
        ),
        summary=Summary(
            {
                Day(1): DailyResults(
                    torikumi=Torikumi(set(lookup)),
                    results_lookup=lookup,
                )
            }
        ),
    )


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))

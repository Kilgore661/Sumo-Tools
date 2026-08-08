from math import isclose

from src.analysis.prediction.bouts import (
    BoutId,
    BoutSelection,
    Contest,
    RatedBout,
)
from src.analysis.prediction.definition import Proposal1Definition
from src.analysis.prediction.experiment import build_forecast_ledger
from src.analysis.prediction.randomised_prior import (
    ALL_BOUTS,
    CumulativeScore,
    GLOBAL_PLACEBO,
    PreparedPlaceboBouts,
    PriorValue,
    RandomisationDefinition,
    RandomisedMapping,
    RandomisedPriorResult,
    SCOPES,
    ScopedBout,
    WITHIN_DIVISION_PLACEBO,
    build_randomised_mappings,
    build_within_division_mappings,
    score_prepared_bouts,
    summarize_ordered,
)
from src.analysis.prediction.randomised_prior_output import (
    _cumulative_envelope_rows,
    _write_chart,
)
from src.analysis.prediction.scoring import score_forecasts
from src.sumo_core.BasicPrimitives import Day, Month, Pair, RikId, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


def test_randomized_mappings_are_reproducible_permutations() -> None:
    prior = tuple(
        PriorValue(Chii.from_str(chii), rating)
        for chii, rating in (
            ("J1e", 1800.0),
            ("Ms1e", 1500.0),
            ("Sd1e", 1200.0),
        )
    )
    definition = RandomisationDefinition(replicate_count=100, seed=20260807)

    first = build_randomised_mappings(prior, definition)
    second = build_randomised_mappings(prior, definition)

    assert first == second
    assert tuple(row.replicate for row in first) == tuple(range(1, 101))
    expected = sorted(row.rating for row in prior)
    assert all(sorted(row.ratings) == expected for row in first)
    assert len({row.ratings for row in first}) > 1


def test_order_statistics_follow_declared_positions() -> None:
    summary = summarize_ordered(tuple(float(value) for value in range(1, 101)))

    assert summary.median == 50.5
    assert summary.percentile_5 == 5.0
    assert summary.percentile_95 == 95.0


def test_within_division_randomization_preserves_each_division_multiset() -> None:
    prior = tuple(sorted(
        (
            PriorValue(Chii.from_str("Y1e"), 2100.0),
            PriorValue(Chii.from_str("M1e"), 1900.0),
            PriorValue(Chii.from_str("J1e"), 1700.0),
            PriorValue(Chii.from_str("J2e"), 1600.0),
            PriorValue(Chii.from_str("Ms1e"), 1400.0),
            PriorValue(Chii.from_str("Ms2e"), 1300.0),
        ),
        key=lambda row: row.chii,
    ))
    mappings = build_within_division_mappings(
        prior,
        RandomisationDefinition(replicate_count=100, seed=20260807),
    )
    genuine_groups = (
        sorted((prior[0].rating, prior[1].rating)),
        sorted((prior[2].rating, prior[3].rating)),
        sorted((prior[4].rating, prior[5].rating)),
    )

    for mapping in mappings:
        assert sorted(mapping.ratings[0:2]) == genuine_groups[0]
        assert sorted(mapping.ratings[2:4]) == genuine_groups[1]
        assert sorted(mapping.ratings[4:6]) == genuine_groups[2]
    assert len({mapping.ratings for mapping in mappings}) > 1


def test_streaming_score_matches_the_forecast_ledger() -> None:
    date = Date(Year(1989), Month(1))
    bouts = (
        _bout(date, 1, 1, 2, True),
        _bout(date, 2, 3, 4, False),
    )
    selection = BoutSelection(
        bouts=bouts,
        raw_result_count=2,
        rated_bout_count=2,
        excluded_fusen_count=0,
        excluded_draw_count=0,
    )
    prepared = PreparedPlaceboBouts(
        selection=selection,
        bouts=(ScopedBout(bouts[0], 3), ScopedBout(bouts[1], 5)),
        first_chii_by_rikishi={},
        unranked_initial_rikishi=(),
    )
    definition = Proposal1Definition(end_date=date)

    streamed = next(
        row for row in score_prepared_bouts(
            prepared,
            definition,
            initial_ratings=None,
        )
        if row.scope == ALL_BOUTS
    )
    ledger = build_forecast_ledger(bouts, definition)
    scored = score_forecasts(ledger, reference_probability=0.5)

    assert streamed.bout_count == 2
    assert isclose(
        streamed.mean_log_loss,
        sum(row.log_loss for row in scored) / 2,
    )
    assert isclose(
        streamed.mean_brier_score,
        sum(row.brier_score for row in scored) / 2,
    )


def test_dual_placebo_envelope_reaches_the_chart(tmp_path) -> None:
    date = Date(Year(1989), Month(1))
    definition = Proposal1Definition(end_date=date)
    prepared = PreparedPlaceboBouts(
        selection=BoutSelection((), 0, 0, 0, 0),
        bouts=(),
        first_chii_by_rikishi={},
        unranked_initial_rikishi=(),
    )

    def scores(log_loss: float, brier: float) -> tuple[CumulativeScore, ...]:
        return tuple(
            CumulativeScore(scope, date, 1, 10, log_loss, brier)
            for scope in SCOPES
        )

    mappings = tuple(
        RandomisedMapping(placebo, replicate, (1500.0,))
        for placebo in (GLOBAL_PLACEBO, WITHIN_DIVISION_PLACEBO)
        for replicate in range(1, 101)
    )
    randomized_scores = tuple(
        scores(
            (0.80 if mapping.placebo == GLOBAL_PLACEBO else 0.72)
            + mapping.replicate / 100000,
            (0.30 if mapping.placebo == GLOBAL_PLACEBO else 0.26)
            + mapping.replicate / 100000,
        )
        for mapping in mappings
    )
    result = RandomisedPriorResult(
        elo_definition=definition,
        randomisation=RandomisationDefinition(),
        prior_values=(PriorValue(Chii.from_str("J1e"), 1500.0),),
        prepared=prepared,
        equal_scores=scores(0.70, 0.25),
        genuine_scores=scores(0.69, 0.24),
        mappings=mappings,
        randomised_scores=randomized_scores,
    )

    rows = tuple(_cumulative_envelope_rows(result))
    assert "global_random_log_median" in rows[0]
    assert "within_division_random_log_median" in rows[0]
    chart = tmp_path / "placebo.html"
    _write_chart(rows, chart)
    document = chart.read_text(encoding="utf-8")
    assert "Global random median" in document
    assert "Within-division random median" in document


def _bout(
    date: Date,
    day: int,
    rikishi_a: int,
    rikishi_b: int,
    a_won: bool,
) -> RatedBout:
    return RatedBout(
        contest=Contest(
            BoutId(
                date=date,
                day=Day(day),
                pair=Pair(RikId(rikishi_a), RikId(rikishi_b)),
            )
        ),
        a_won=a_won,
    )

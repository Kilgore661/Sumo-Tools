from math import isclose
import random

from src.analysis.prediction.bouts import BoutId, BoutSelection, Contest, RatedBout
from src.analysis.prediction.definition import Proposal1Definition
from src.analysis.prediction.fair_coin_null import (
    BettingScore,
    FairCoinDefinition,
    NullReplicate,
    _summaries,
    score_probability_stakes,
)
from src.analysis.prediction.randomised_prior import (
    ALL_BOUTS,
    PreparedPlaceboBouts,
    ScopedBout,
)
from src.sumo_core.BasicPrimitives import Day, Month, Pair, RikId, Year
from src.sumo_core.History import Date


def test_probability_stake_uses_pre_bout_favourite_and_daily_average() -> None:
    date = Date(Year(1989), Month(1))
    bouts = (_bout(date, 1, 1, 2, True), _bout(date, 2, 1, 2, True))
    definition = Proposal1Definition(end_date=date)
    score = next(
        row for row in score_probability_stakes(
            _prepared(bouts), definition, outcomes=(True, True)
        ) if row.scope == ALL_BOUTS
    )
    second_probability = 1.0 / (1.0 + 10.0 ** (-35.0 / 400.0))

    assert score.basho_count == 1
    assert score.day_count == 2
    assert isclose(score.mean_stake_per_basho, second_probability)
    assert isclose(score.mean_profit_per_basho, second_probability)
    assert score.return_on_stake == 1.0


def test_fixed_seed_fair_coin_histories_are_reproducible() -> None:
    first = random.Random(20260807)
    second = random.Random(20260807)
    assert [first.getrandbits(1) for _ in range(100)] == [
        second.getrandbits(1) for _ in range(100)
    ]


def test_summary_uses_declared_order_statistics_and_add_one_p_value() -> None:
    observed = tuple(
        BettingScore(scope, 1, 1, 1.0, 0.75, 0.75)
        for scope in (
            "all eligible bouts",
            "both participants sekitori",
            "both participants sub-sekitori",
        )
    )
    replicates = tuple(
        NullReplicate(
            replicate,
            tuple(
                BettingScore(
                    score.scope,
                    1,
                    1,
                    1.0,
                    replicate / 100.0,
                    replicate / 100.0,
                )
                for score in observed
            ),
        )
        for replicate in range(1, 101)
    )
    summaries = _summaries(
        observed,
        replicates,
        FairCoinDefinition(replicate_count=100),
    )

    for summary in summaries:
        assert summary.null_lower_profit == 0.03
        assert summary.null_upper_profit == 0.98
        assert summary.null_at_least_observed == 26
        assert summary.monte_carlo_p == 27 / 101


def _prepared(bouts: tuple[RatedBout, ...]) -> PreparedPlaceboBouts:
    return PreparedPlaceboBouts(
        selection=BoutSelection(bouts, len(bouts), len(bouts), 0, 0),
        bouts=tuple(ScopedBout(bout, 7) for bout in bouts),
        first_chii_by_rikishi={},
        unranked_initial_rikishi=(),
    )


def _bout(date, day: int, rikishi_a: int, rikishi_b: int, a_won: bool) -> RatedBout:
    return RatedBout(
        Contest(BoutId(date, Day(day), Pair(RikId(rikishi_a), RikId(rikishi_b)))),
        a_won,
    )

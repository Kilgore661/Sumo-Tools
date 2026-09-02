from __future__ import annotations

import pytest

from src.analysis.elo_model_selection.model import (
    AdoptedPrior,
    ComparisonDefinition,
    _context,
)
from src.analysis.elo89.replay import replay_elo89
from src.analysis.equelo_population_policy.predict_population_policy import (
    run_whole_population_model,
)
from src.analysis.prediction.bouts import select_rated_bouts
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


def test_production_replay_matches_accepted_elo89_forecasts() -> None:
    january = _date(1989, 1)
    march = _date(1989, 3)
    may = _date(1989, 5)
    history = History(
        {
            january: _basho(
                {1: "M1e", 2: "J1w"},
                [_bout(1, Outcome.W, 2, Outcome.L)],
            ),
            march: _basho({2: "J1w"}, []),
            may: _basho(
                {1: "M1e", 2: "J1w"},
                [_bout(2, Outcome.W, 1, Outcome.L)],
            ),
        }
    )
    prior = AdoptedPrior(
        source_path="fixture.csv",
        sha256="fixture",
        rating_by_pair={"M1": 1600.0, "J1": 1400.0},
        fallback_rating=1400.0,
    )
    actual = replay_elo89(
        history=history,
        start_date=january,
        end_date=may,
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
    )
    selection = select_rated_bouts(history, start_date=january, end_date=may)
    contexts = tuple(_context(history, bout) for bout in selection.bouts)
    expected = run_whole_population_model(
        history,
        contexts,
        ComparisonDefinition(start_date=january, end_date=may),
        prior,
        lambda _ordinal: 20.0,
    )

    assert len(actual.forecasts) == len(expected) == 2
    for actual_row, expected_row in zip(actual.forecasts, expected, strict=True):
        assert actual_row.probability_a_wins == pytest.approx(
            expected_row.probability_a_wins
        )
        assert actual_row.delta_a == pytest.approx(expected_row.delta_a)
        assert actual_row.delta_b == pytest.approx(expected_row.delta_b)
    assert actual.basho_start_ratings[may][RikId(1)] == pytest.approx(1550.0)


def test_production_replay_exposes_daily_and_normalised_end_snapshots() -> None:
    date = _date(1989, 1)
    history = History(
        {
            date: _basho(
                {1: "M1e", 2: "J1w", 3: "J2e"},
                [_bout(1, Outcome.W, 2, Outcome.L)],
            )
        }
    )
    prior = AdoptedPrior(
        source_path="fixture.csv",
        sha256="fixture",
        rating_by_pair={"M1": 1600.0, "J1": 1400.0, "J2": 1300.0},
        fallback_rating=1300.0,
    )
    run = replay_elo89(
        history=history,
        start_date=date,
        end_date=date,
        prior=prior,
        divisional_k=lambda ordinal: (
            30.0 if ordinal == Chii.from_str("M1e").ordinal() else 20.0
        ),
    )

    assert set(run.day_end_ratings[date][Day(1)]) == {RikId(1), RikId(2), RikId(3)}
    assert sum(run.basho_end_ratings[date].values()) / 3 == pytest.approx(
        run.target_mean
    )
    assert run.day_end_ratings[date][Day(1)] != run.basho_end_ratings[date]


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))


def _basho(ranks: dict[int, str], bouts: list[BoutResult]) -> BashoState:
    rikishi_ids = {RikId(value) for value in ranks}
    lookup = ResultLookup({Pair(bout.rikishi1, bout.rikishi2): bout for bout in bouts})
    summary = Summary({})
    if bouts:
        summary[Day(1)] = DailyResults(
            torikumi=Torikumi(set(lookup)),
            results_lookup=lookup,
        )
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(rikishi_ids),
            rikchii=RikChii(
                {RikId(value): Chii.from_str(rank) for value, rank in ranks.items()}
            ),
            rikshik=RikShikona(
                {
                    rikishi: Shikona(f"Rikishi {int(rikishi)}")
                    for rikishi in rikishi_ids
                }
            ),
        ),
        summary=summary,
    )


def _bout(
    rikishi_1: int,
    outcome_1: Outcome,
    rikishi_2: int,
    outcome_2: Outcome,
) -> BoutResult:
    return BoutResult(
        rikishi1=RikId(rikishi_1),
        outcome1=outcome_1,
        rikishi2=RikId(rikishi_2),
        outcome2=outcome_2,
        decision="blank",
        symbol=Symbol[outcome_1.name],
    )

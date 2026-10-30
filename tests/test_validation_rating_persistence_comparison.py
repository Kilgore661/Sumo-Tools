from __future__ import annotations

import pytest

from src.analysis.elo_model_selection.model import AdoptedPrior
from src.analysis.elo89.replay import replay_elo89
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import (
    Day,
    Pair,
    RikId,
    Riks,
    Shikona,
    Torikumi,
)
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary
from src.validation.rating_persistence_comparison.replay import replay_policy


def test_frozen_policy_exactly_matches_canonical_elo89() -> None:
    history, prior = _gap_history()
    start, end = min(history), max(history)

    canonical = replay_elo89(
        history=history,
        start_date=start,
        end_date=end,
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
    )
    candidate = replay_policy(
        history=history,
        start_date=start,
        end_date=end,
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
        policy="frozen",
    )

    assert candidate.run == canonical


def test_frozen_policy_restores_unchanged_archive_and_retains_support() -> None:
    history, prior = _gap_history()
    dates = sorted(history)
    candidate = replay_policy(
        history=history,
        start_date=dates[0],
        end_date=dates[-1],
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
        policy="frozen",
    )

    assert len(candidate.returns) == 2
    first, second = candidate.returns
    assert first.rated_bouts_before_return == 1
    assert second.rated_bouts_before_return == 2
    assert first.archived_rating == pytest.approx(
        candidate.run.basho_end_ratings[dates[0]][RikId(1)]
    )
    assert first.rating_before_start_adjustment == first.archived_rating
    assert second.archived_rating == pytest.approx(
        candidate.run.basho_end_ratings[dates[2]][RikId(1)]
    )
    assert second.rating_before_start_adjustment == second.archived_rating


def test_inactive_archive_does_not_affect_active_population_until_return() -> None:
    history, prior = _gap_history()
    dates = sorted(history)
    control = replay_policy(
        history=history,
        start_date=dates[0],
        end_date=dates[-1],
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
        policy="reset",
    )
    candidate = replay_policy(
        history=history,
        start_date=dates[0],
        end_date=dates[-1],
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
        policy="frozen",
    )

    # Before the first restoration, merely holding the archive has no effect.
    assert control.run.basho_end_ratings[dates[1]] == candidate.run.basho_end_ratings[dates[1]]

    # The rikishi is excluded from active snapshots during either absence.
    # After his first return, legitimate effects from that active spell may
    # remain in opponents' ratings during the second absence.
    for absent_date in (dates[1], dates[3]):
        assert RikId(1) not in candidate.run.basho_end_ratings[absent_date]


def test_first_entrant_still_uses_prior_under_frozen_policy() -> None:
    history, prior = _gap_history()
    dates = sorted(history)
    candidate = replay_policy(
        history=history,
        start_date=dates[0],
        end_date=dates[-1],
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
        policy="frozen",
    )

    assert not any(event.rikishi == RikId(3) for event in candidate.returns)
    first_forecast_with_three = next(
        row
        for row in candidate.run.forecasts
        if RikId(3) in (row.rikishi_a, row.rikishi_b)
    )
    source = (
        first_forecast_with_three.initialisation_a
        if first_forecast_with_three.rikishi_a == RikId(3)
        else first_forecast_with_three.initialisation_b
    )
    assert source == "adopted prior J2"


def test_frozen_policy_rejects_rated_participant_absent_from_banzuke() -> None:
    date = Date.from_ints(1989, 1)
    history = History(
        {date: _basho({1: "Jk1e"}, [_bout(1, Outcome.W, 2, Outcome.L)])}
    )
    prior = AdoptedPrior(
        source_path="fixture.csv",
        sha256="fixture",
        rating_by_pair={"Jk1": 1000.0},
        fallback_rating=1000.0,
    )

    with pytest.raises(ValueError, match="participant absent from the same-basho banzuke"):
        replay_policy(
            history=history,
            start_date=date,
            end_date=date,
            prior=prior,
            divisional_k=lambda _ordinal: 20.0,
            policy="frozen",
        )


def _gap_history() -> tuple[History, AdoptedPrior]:
    january = Date.from_ints(1989, 1)
    march = Date.from_ints(1989, 3)
    may = Date.from_ints(1989, 5)
    july = Date.from_ints(1989, 7)
    september = Date.from_ints(1989, 9)
    history = History(
        {
            january: _basho(
                {1: "Jk1e", 2: "Jk1w"},
                [_bout(1, Outcome.W, 2, Outcome.L)],
            ),
            march: _basho({2: "Jk1e"}, []),
            may: _basho(
                {1: "Jk2e", 2: "Jk1e", 3: "J2e"},
                [_bout(1, Outcome.L, 2, Outcome.W), _bout(3, Outcome.W, 2, Outcome.L)],
            ),
            july: _basho({2: "Jk1e", 3: "J2e"}, []),
            september: _basho(
                {1: "Jk3e", 2: "Jk1e", 3: "J2e"},
                [_bout(1, Outcome.W, 2, Outcome.L)],
            ),
        }
    )
    prior = AdoptedPrior(
        source_path="fixture.csv",
        sha256="fixture",
        rating_by_pair={"Jk1": 1000.0, "Jk2": 900.0, "Jk3": 800.0, "J2": 1500.0},
        fallback_rating=800.0,
    )
    return history, prior


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

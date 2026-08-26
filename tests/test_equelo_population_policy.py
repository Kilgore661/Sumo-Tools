from __future__ import annotations

import pytest

from src.analysis.equelo.expt1.params import EloParams
from src.analysis.equelo.expt1.simulate import SimulationMode, simulate as legacy_simulate
from src.analysis.equelo_population_policy import PopulationPolicy, replay
from src.analysis.equelo_population_policy.solve import aggregate_by_chii
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import Day, Month, Pair, RikId, Riks, Shikona, Torikumi, Year
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Kimarite import Kimarite
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary


def test_post_basho_policy_restores_target_after_population_and_dual_k_changes():
    first = _date(2000, 1)
    second = _date(2000, 3)
    history = History()
    history[first] = _basho(
        {1: "M1e", 2: "J1e"},
        [_bout(1, 2)],
    )
    history[second] = _basho(
        {1: "M1e", 3: "Ms1e"},
        [_bout(1, 3)],
    )
    priors = {
        Chii.from_str("M1e"): 1600.0,
        Chii.from_str("J1e"): 1400.0,
        Chii.from_str("Ms1e"): 1200.0,
    }
    makuuchi_ordinal = Chii.from_str("M1e").ordinal()
    params = EloParams(
        b=1500.0,
        q=400.0,
        k=lambda ordinal: 10.0 if ordinal == makuuchi_ordinal else 30.0,
    )

    result = replay(history, params, priors, PopulationPolicy.POST_BASHO_MEAN)

    assert result.target_mean == pytest.approx(1500.0)
    assert all(row.adjusted_start_mean == pytest.approx(1500.0) for row in result.adjustments)
    assert all(row.adjusted_end_mean == pytest.approx(1500.0) for row in result.adjustments)
    assert any(abs(row.bout_mass_change) > 0.0 for row in result.adjustments)


def test_controls_separate_turnover_and_dual_k_corrections():
    first = _date(2000, 1)
    second = _date(2000, 3)
    history = History()
    history[first] = _basho({1: "M1e", 2: "J1e"}, [_bout(1, 2)])
    history[second] = _basho({1: "M1e", 3: "Ms1e"}, [_bout(1, 3)])
    priors = {
        Chii.from_str("M1e"): 1600.0,
        Chii.from_str("J1e"): 1400.0,
        Chii.from_str("Ms1e"): 1200.0,
    }
    makuuchi_ordinal = Chii.from_str("M1e").ordinal()
    params = EloParams(
        b=1500.0,
        q=400.0,
        k=lambda ordinal: 10.0 if ordinal == makuuchi_ordinal else 30.0,
    )

    start_only = replay(
        history, params, priors, PopulationPolicy.POST_BASHO_MEAN_START_ONLY
    )
    dual_k_only = replay(
        history, params, priors, PopulationPolicy.LEGACY_DEPARTURE_BOUT_MASS
    )
    legacy = replay(history, params, priors, PopulationPolicy.LEGACY_DEPARTURE)

    assert all(row.adjusted_start_mean == pytest.approx(1500.0) for row in start_only.adjustments)
    assert any(row.adjusted_end_mean != pytest.approx(1500.0) for row in start_only.adjustments)
    assert dual_k_only.adjustments[0].adjusted_start_mean == pytest.approx(
        legacy.adjustments[0].adjusted_start_mean
    )
    assert all(
        row.adjusted_end_mean == pytest.approx(row.adjusted_start_mean)
        for row in dual_k_only.adjustments
    )


def test_legacy_policy_matches_departure_specific_not_whole_population_rule():
    first = _date(2000, 1)
    second = _date(2000, 3)
    history = History()
    history[first] = _basho({1: "M1e", 2: "J1e"}, [])
    history[second] = _basho({1: "M1e", 3: "Ms1e"}, [])
    priors = {
        Chii.from_str("M1e"): 1600.0,
        Chii.from_str("J1e"): 1400.0,
        Chii.from_str("Ms1e"): 1200.0,
    }
    params = EloParams.constant(b=1500.0, q=400.0, k_value=20.0)

    legacy = replay(history, params, priors, PopulationPolicy.LEGACY_DEPARTURE)
    proposed = replay(history, params, priors, PopulationPolicy.POST_BASHO_MEAN)

    assert legacy.adjustments[1].adjusted_start_mean == pytest.approx(1350.0)
    assert proposed.adjustments[1].adjusted_start_mean == pytest.approx(1500.0)


def test_chii_aggregation_preserves_observation_weighted_not_unweighted_mean():
    date = _date(2000, 1)
    history = History()
    history[date] = _basho({1: "M1e", 2: "M1e", 3: "J1e"}, [])
    priors = {Chii.from_str("M1e"): 1600.0, Chii.from_str("J1e"): 1300.0}
    result = replay(
        history,
        EloParams.constant(),
        priors,
        PopulationPolicy.POST_BASHO_MEAN,
    )

    aggregated = aggregate_by_chii(history, result)

    assert result.target_mean == pytest.approx(1500.0)
    assert sum(aggregated.values()) / len(aggregated) == pytest.approx(1450.0)
    assert (2 * aggregated[Chii.from_str("M1e")] + aggregated[Chii.from_str("J1e")]) / 3 == pytest.approx(1500.0)


def test_shared_legacy_policy_reproduces_current_expt2_simulator():
    first = _date(2000, 1)
    second = _date(2000, 3)
    history = History()
    history[first] = _basho({1: "M1e", 2: "J1e"}, [_bout(1, 2)])
    history[second] = _basho({1: "M1e", 3: "Ms1e"}, [_bout(1, 3)])
    priors = {
        Chii.from_str("M1e"): 1600.0,
        Chii.from_str("J1e"): 1400.0,
        Chii.from_str("Ms1e"): 1200.0,
    }
    params = EloParams.constant(b=1500.0, q=400.0, k_value=20.0)

    controlled = replay(history, params, priors, PopulationPolicy.LEGACY_DEPARTURE)
    existing = legacy_simulate(
        history,
        params,
        lambda context: priors[context.chii],
        mode=SimulationMode.CLOSED,
    )

    assert controlled.basho_start_ratings == existing.basho_start_ratings
    for date in history:
        if history[date].summary:
            final_day = max(history[date].summary)
            assert controlled.basho_end_ratings[date] == existing.day_end_ratings[date][final_day]


def test_support_weighting_preserves_mean_but_may_change_differences():
    first = _date(2000, 1)
    second = _date(2000, 3)
    history = History()
    history[first] = _basho({1: "M1e", 2: "J1e"}, [])
    history[second] = _basho({1: "M1e", 3: "Ms1e"}, [])
    m = Chii.from_str("M1e")
    j = Chii.from_str("J1e")
    ms = Chii.from_str("Ms1e")
    priors = {m: 1600.0, j: 1400.0, ms: 1200.0}
    params = EloParams.constant()

    equal = replay(history, params, priors, PopulationPolicy.POST_BASHO_MEAN)
    weighted = replay(
        history,
        params,
        priors,
        PopulationPolicy.POST_BASHO_MEAN,
        normalisation_support={m: 100, j: 10, ms: 1},
        normalisation_alpha=1.0,
    )

    equal_second = equal.basho_start_ratings[second]
    weighted_second = weighted.basho_start_ratings[second]
    assert sum(weighted_second.values()) / len(weighted_second) == pytest.approx(1500.0)
    assert weighted_second[RikId(1)] - weighted_second[RikId(3)] != pytest.approx(
        equal_second[RikId(1)] - equal_second[RikId(3)]
    )


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))


def _basho(ranks: dict[int, str], bouts: list[BoutResult]) -> BashoState:
    rikids = {RikId(value) for value in ranks}
    lookup = ResultLookup({Pair(bout.rikishi1, bout.rikishi2): bout for bout in bouts})
    summary = Summary({})
    if bouts:
        summary[Day(1)] = DailyResults(torikumi=Torikumi(set(lookup)), results_lookup=lookup)
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(rikids),
            rikchii=RikChii({RikId(value): Chii.from_str(rank) for value, rank in ranks.items()}),
            rikshik=RikShikona({rikid: Shikona(f"Rikishi {rikid}") for rikid in rikids}),
        ),
        summary=summary,
    )


def _bout(winner: int, loser: int) -> BoutResult:
    return BoutResult(
        rikishi1=RikId(winner),
        outcome1=Outcome.W,
        rikishi2=RikId(loser),
        outcome2=Outcome.L,
        decision=Kimarite.OSHIDASHI,
        symbol=Symbol.W,
    )

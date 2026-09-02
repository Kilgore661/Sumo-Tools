from __future__ import annotations

import csv
from statistics import fmean

import pytest

from src.analysis.divisional_averages.division import division_name
from src.analysis.divisional_averages.full_history import (
    PriorValue,
    _date_slice,
    complete_historical_p2,
    run_full_history,
)
from src.analysis.divisional_averages.prior import divisional_targets
from src.analysis.divisional_averages.recenter import recenter_by_division
from src.analysis.divisional_averages.replay import replay
from src.analysis.divisional_averages.run import _year_slice
from src.analysis.divisional_averages.solve import solve
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
from src.sumo_core.Kimarite import Kimarite
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary
from src.infra.parser.parser2_IntDate import IntDate


def test_p1_targets_are_unweighted_literal_chii_means_by_division() -> None:
    p1 = {
        Chii.from_str("Y1e"): 2400.0,
        Chii.from_str("M1e"): 2200.0,
        Chii.from_str("J1e"): 2000.0,
        Chii.from_str("Ms1e"): 1800.0,
        Chii.from_str("Sd1e"): 1600.0,
        Chii.from_str("Jd1e"): 1400.0,
        Chii.from_str("Jk1e"): 1300.0,
    }

    targets = divisional_targets(p1)

    assert targets == {
        "Makuuchi": 2300.0,
        "Juryo": 2000.0,
        "Makushita": 1800.0,
        "Sandanme": 1600.0,
        "Jonidan": 1400.0,
        "Jonokuchi": 1300.0,
    }


def test_map_recentering_restores_each_target_independently() -> None:
    m1 = Chii.from_str("M1e")
    m2 = Chii.from_str("M2e")
    j1 = Chii.from_str("J1e")
    result = recenter_by_division(
        {m1: 2300.0, m2: 2100.0, j1: 1900.0},
        targets={"Makuuchi": 2250.0, "Juryo": 2000.0},
        support={m1: 3, m2: 1, j1: 2},
    )

    assert fmean(
        rating
        for chii, rating in result.ratings.items()
        if division_name(chii) == "Makuuchi"
    ) == pytest.approx(2250.0)
    assert result.ratings[j1] == pytest.approx(2000.0)
    assert result.ratings[m1] - 2300.0 == pytest.approx(75.0)
    assert result.ratings[m2] - 2100.0 == pytest.approx(25.0)


def test_replay_persists_each_active_divisional_mean_at_start_and_end() -> None:
    first = _date(2000, 1)
    second = _date(2000, 3)
    history = History()
    history[first] = _basho(
        {1: "M1e", 2: "M2e", 3: "J1e", 4: "J2e"},
        [_bout(1, 3)],
    )
    history[second] = _basho(
        {1: "M1e", 2: "M2e", 3: "J1e", 5: "J2e"},
        [_bout(3, 2)],
    )
    priors = {
        Chii.from_str("M1e"): 2300.0,
        Chii.from_str("M2e"): 2100.0,
        Chii.from_str("J1e"): 2050.0,
        Chii.from_str("J2e"): 1950.0,
    }
    targets = {"Makuuchi": 2200.0, "Juryo": 2000.0}

    result = replay(history, priors, lambda _ordinal: 20.0, targets)

    for date in history:
        chii = history[date].banzuke.rikchii
        for ratings in (
            result.basho_start_ratings[date],
            result.basho_end_ratings[date],
        ):
            assert fmean(
                rating
                for rikishi, rating in ratings.items()
                if division_name(chii[rikishi]) == "Makuuchi"
            ) == pytest.approx(2200.0)
            assert fmean(
                rating
                for rikishi, rating in ratings.items()
                if division_name(chii[rikishi]) == "Juryo"
            ) == pytest.approx(2000.0)


def test_replay_rates_binary_bout_when_kimarite_is_blank() -> None:
    date = _date(2000, 1)
    history = History()
    history[date] = _basho(
        {1: "M1e", 2: "M1w"},
        [_bout_with_decision(1, 2, "blank")],
    )
    m1e = Chii.from_str("M1e")
    m1w = Chii.from_str("M1w")

    result = replay(
        history,
        {m1e: 1500.0, m1w: 1500.0},
        lambda _ordinal: 20.0,
        {"Makuuchi": 1500.0},
    )

    assert result.rated_bout_count == 1
    assert result.basho_end_ratings[date][RikId(1)] == pytest.approx(1510.0)
    assert result.basho_end_ratings[date][RikId(2)] == pytest.approx(1490.0)


def test_replay_excludes_non_binary_result_even_when_decision_is_not_fusen() -> None:
    date = _date(2000, 1)
    history = History()
    bout = _bout_with_decision(1, 2, Kimarite.HANSOKU)
    object.__setattr__(bout, "outcome1", Outcome.FP)
    object.__setattr__(bout, "outcome2", Outcome.FS)
    history[date] = _basho({1: "M1e", 2: "M1w"}, [bout])
    m1e = Chii.from_str("M1e")
    m1w = Chii.from_str("M1w")

    result = replay(
        history,
        {m1e: 1500.0, m1w: 1500.0},
        lambda _ordinal: 20.0,
        {"Makuuchi": 1500.0},
    )

    assert result.rated_bout_count == 0


def test_solver_retains_every_iteration_for_console_and_csv_reporting() -> None:
    date = _date(2000, 1)
    history = History()
    ranks = {
        1: "M1e",
        2: "J1e",
        3: "Ms1e",
        4: "Sd1e",
        5: "Jd1e",
        6: "Jk1e",
    }
    history[date] = _basho(ranks, [_bout(1, 2)])
    p1 = {
        Chii.from_str(rank): rating
        for rank, rating in zip(ranks.values(), (2200, 2000, 1800, 1600, 1400, 1300))
    }
    targets = divisional_targets(p1)
    progress = []

    result = solve(
        history,
        lambda _ordinal: 20.0,
        p1=p1,
        targets=targets,
        epsilon=1e9,
        support_threshold=1,
        progress=lambda row, divisions: progress.append((row, divisions)),
    )

    assert result.converged
    assert result.iterations == 1
    assert len(result.iteration_rows) == 1
    assert len(result.division_iteration_rows) == 6
    assert len(result.prior_iteration_rows) == 6
    assert len(progress) == 1
    assert all(
        row.centred_map_mean == pytest.approx(row.target_mean)
        for row in result.division_iteration_rows
    )


def test_solver_updates_only_supported_chii_and_completes_the_tail() -> None:
    history = History()
    for year in range(2000, 2003):
        ranks = {
            1: "M1e",
            2: "J1e",
            3: "Ms1e",
            4: "Sd1e",
            5: "Jd1e",
            6: "Jk1e",
        }
        if year == 2000:
            ranks[7] = "Jk2e"
        history[_date(year, 1)] = _basho(
            ranks,
            [],
        )
    # Jk2e is present only once and must inherit Jk1e.
    p1 = {
        chii: float(2000 - chii.ordinal())
        for basho in history.values()
        for chii in basho.banzuke.rikchii.values()
    }
    targets = divisional_targets(p1)

    result = solve(
        history,
        lambda _ordinal: 20.0,
        p1=p1,
        targets=targets,
        epsilon=1e9,
        support_threshold=2,
    )

    jk1 = Chii.from_str("Jk1e")
    jk2 = Chii.from_str("Jk2e")
    assert jk1 in result.supported_chii
    assert jk2 not in result.supported_chii
    assert result.completion_sources[jk2] == jk1
    assert result.priors[jk2] == result.priors[jk1]


def test_declared_year_slice_removes_wider_live_store_history() -> None:
    history = History()
    history[_date(1958, 1)] = _basho({1: "M20e"}, [])
    history[_date(1989, 1)] = _basho({2: "M1e"}, [])
    history[_date(2026, 7)] = _basho({3: "M2e"}, [])

    selected = _year_slice(history, 1989, 2026)

    assert [str(date) for date in sorted(selected)] == ["1989/01", "2026/07"]


def test_full_history_date_slice_accepts_live_store_int_dates() -> None:
    history = History()
    history[IntDate(1958, 1)] = _basho({1: "M1e"}, [])

    selected = _date_slice(history, _date(1958, 1), _date(1958, 1))

    assert len(selected) == 1
    assert str(next(iter(selected))) == "1958/01"


def test_historical_p2_completion_uses_supported_chii_above_in_same_division() -> None:
    m18 = Chii.from_str("M18w")
    m20 = Chii.from_str("M20e")
    j1 = Chii.from_str("J1e")
    p2 = {
        m18: PriorValue(1800.0, m18, "p2_supported"),
        j1: PriorValue(1700.0, j1, "p2_supported"),
    }

    completed = complete_historical_p2(p2, {m18, m20, j1})

    assert completed[m20].rating == 1800.0
    assert completed[m20].source_chii == m18
    assert completed[m20].provenance == "historical_nearest_supported_above"


def test_full_history_experiment_writes_map_scores_and_latest_ratings(tmp_path) -> None:
    date = _date(2000, 1)
    history = History()
    ranks = {
        1: "M1e",
        2: "J1e",
        3: "Ms1e",
        4: "Sd1e",
        5: "Jd1e",
        6: "Jk1e",
    }
    history[date] = _basho(ranks, [_bout(1, 2)])
    ratings = {
        Chii.from_str(rank): float(value)
        for rank, value in zip(
            ranks.values(), (2200, 2000, 1800, 1600, 1400, 1300), strict=True
        )
    }
    p2 = {
        chii: PriorValue(rating, chii, "p2_supported")
        for chii, rating in ratings.items()
    }
    output = tmp_path / "full_history"

    result = run_full_history(
        history,
        prior=p2,
        p2=p2,
        targets=divisional_targets(ratings),
        divisional_k=lambda _ordinal: 20.0,
        support_threshold=1,
        reference_start=date,
        output=output,
    )

    assert result["scores"]["all"].bouts == 1
    assert (output / "p2_final_map_comparison.csv").is_file()
    assert (output / "latest_ratings.csv").is_file()
    assert (output / "division_adjustment_summary.csv").is_file()
    summary = list(csv.DictReader((output / "division_map_summary.csv").open()))
    assert {row["division"] for row in summary} == {
        "Makuuchi",
        "Juryo",
        "Makushita",
        "Sandanme",
        "Jonidan",
        "Jonokuchi",
        "All",
    }


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))


def _basho(ranks: dict[int, str], bouts: list[BoutResult]) -> BashoState:
    rikids = {RikId(value) for value in ranks}
    lookup = ResultLookup(
        {Pair(bout.rikishi1, bout.rikishi2): bout for bout in bouts}
    )
    summary = Summary({})
    if bouts:
        summary[Day(1)] = DailyResults(
            torikumi=Torikumi(set(lookup)), results_lookup=lookup
        )
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(rikids),
            rikchii=RikChii(
                {
                    RikId(value): Chii.from_str(rank)
                    for value, rank in ranks.items()
                }
            ),
            rikshik=RikShikona(
                {rikishi: Shikona(f"Rikishi {rikishi}") for rikishi in rikids}
            ),
        ),
        summary=summary,
    )


def _bout(winner: int, loser: int) -> BoutResult:
    return _bout_with_decision(winner, loser, Kimarite.OSHIDASHI)


def _bout_with_decision(winner: int, loser: int, decision) -> BoutResult:
    return BoutResult(
        rikishi1=RikId(winner),
        outcome1=Outcome.W,
        rikishi2=RikId(loser),
        outcome2=Outcome.L,
        decision=decision,
        symbol=Symbol.W,
    )

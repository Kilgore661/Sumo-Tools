"""Contract tests for the isolated Elo89a viability experiment."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.analysis.absences.jsa_check.model import FinalRecord
from src.analysis.elo_penalties.ledger import build_nonappearance_ledger
from src.analysis.elo_penalties.model import ExperimentArm
from src.analysis.elo_penalties.replay import prepare_replay_evidence, replay
from src.analysis.elo_penalties.solve import solve
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


def test_replay_rates_blank_wl_and_penalises_fp_and_published_absences() -> None:
    date = _date(1989, 1)
    history = History(
        {
            date: _basho(
                {1: "M1e", 2: "M1w", 3: "J1e"},
                {
                    1: [_bout(1, Outcome.W, 3, Outcome.L, decision="blank")],
                    2: [_bout(2, Outcome.FS, 3, Outcome.FP, decision="fusen")],
                },
            )
        }
    )
    final_records = {
        date: {
            RikId(1): _record(1, 0, 0),
            RikId(2): _record(1, 0, 0),
            RikId(3): _record(0, 2, 2),
        }
    }
    evidence = prepare_replay_evidence(history, (date,), final_records)
    priors = {chii: 1500.0 for chii in history[date].banzuke.rikchii.values()}

    control = replay(
        history,
        evidence,
        priors,
        lambda _ordinal: 20.0,
        ExperimentArm.CONTROL,
        base=1500.0,
    )
    elo89a = replay(
        history,
        evidence,
        priors,
        lambda _ordinal: 20.0,
        ExperimentArm.ELO89A,
        base=1500.0,
    )

    assert evidence.rated_bout_count == 1
    assert evidence.excluded_fusen_count == 1
    count = evidence.non_appearances[date][RikId(3)]
    assert (count.fusen_pai, count.absences, count.total) == (1, 2, 3)
    assert control.basho_end_ratings[date] == pytest.approx(
        {RikId(1): 1510.0, RikId(2): 1500.0, RikId(3): 1490.0}
    )
    assert elo89a.basho_end_ratings[date] == pytest.approx(
        {RikId(1): 1520.0, RikId(2): 1510.0, RikId(3): 1470.0}
    )
    row = elo89a.adjustments[0]
    assert (row.fusen_pai_count, row.absence_count) == (1, 2)
    assert row.penalised_rikishi_count == 1
    assert row.total_deducted_mass == pytest.approx(30.0)
    assert row.end_adjustment == pytest.approx(10.0)
    assert row.normalised_end_mean == pytest.approx(1500.0)
    assert control.adjustments[0].penalised_rikishi_count == 0
    assert control.adjustments[0].total_deducted_mass == 0.0

    # The FS rikishi receives only the common normalisation shift. Its rating
    # distance from the contested-bout winner is unchanged between arms.
    control_distance = (
        control.basho_end_ratings[date][RikId(2)]
        - control.basho_end_ratings[date][RikId(1)]
    )
    elo89a_distance = (
        elo89a.basho_end_ratings[date][RikId(2)]
        - elo89a.basho_end_ratings[date][RikId(1)]
    )
    assert elo89a_distance == pytest.approx(control_distance)


def test_multiple_nonappearances_accumulate_and_are_applied_after_bouts() -> None:
    date = _date(1989, 1)
    history = History(
        {
            date: _basho(
                {1: "M1e", 2: "M1w"},
                {
                    1: [_bout(1, Outcome.W, 2, Outcome.L, decision="blank")],
                    2: [_bout(1, Outcome.FS, 2, Outcome.FP, decision="fusen")],
                    3: [_bout(1, Outcome.FS, 2, Outcome.FP, decision="fusen")],
                },
            )
        }
    )
    final_records = {
        date: {
            RikId(1): _record(3, 0, 0),
            RikId(2): _record(0, 3, 1),
        }
    }
    evidence = prepare_replay_evidence(history, (date,), final_records)
    priors = {chii: 1500.0 for chii in history[date].banzuke.rikchii.values()}

    result = replay(
        history,
        evidence,
        priors,
        lambda _ordinal: 40.0,
        ExperimentArm.ELO89A,
        base=1500.0,
    )

    assert evidence.non_appearances[date][RikId(2)].total == 3
    assert result.adjustments[0].total_deducted_mass == pytest.approx(60.0)
    # Contested bout first: 1520/1480; deduction: 1520/1420;
    # normalisation +30: 1550/1450.
    assert result.basho_end_ratings[date] == pytest.approx(
        {RikId(1): 1550.0, RikId(2): 1450.0}
    )


def test_control_and_elo89a_are_identical_without_nonappearances() -> None:
    date = _date(1989, 1)
    history = History(
        {
            date: _basho(
                {1: "M1e", 2: "J1e"},
                {1: [_bout(1, Outcome.W, 2, Outcome.L, decision="blank")]},
            )
        }
    )
    final_records = {
        date: {RikId(1): _record(1, 0, 0), RikId(2): _record(0, 1, 0)}
    }
    evidence = prepare_replay_evidence(history, (date,), final_records)
    priors = {chii: 1500.0 for chii in history[date].banzuke.rikchii.values()}

    control = replay(
        history,
        evidence,
        priors,
        lambda _ordinal: 20.0,
        ExperimentArm.CONTROL,
        base=1500.0,
    )
    elo89a = replay(
        history,
        evidence,
        priors,
        lambda _ordinal: 20.0,
        ExperimentArm.ELO89A,
        base=1500.0,
    )

    assert control.basho_start_ratings == elo89a.basho_start_ratings
    assert control.basho_end_ratings == elo89a.basho_end_ratings


def test_solver_iteration_one_consumes_the_constant_prior_and_is_retained() -> None:
    date = _date(1989, 1)
    history = History(
        {
            date: _basho(
                {1: "M1e", 2: "J1e"},
                {1: [_bout(1, Outcome.W, 2, Outcome.L, decision="blank")]},
            )
        }
    )
    final_records = {
        date: {RikId(1): _record(1, 0, 0), RikId(2): _record(0, 1, 0)}
    }
    evidence = prepare_replay_evidence(history, (date,), final_records)

    from src.analysis.elo_penalties.replay import replay as actual_replay

    with patch(
        "src.analysis.elo_penalties.solve.replay",
        wraps=actual_replay,
    ) as wrapped:
        result = solve(
            history,
            evidence,
            lambda _ordinal: 20.0,
            ExperimentArm.CONTROL,
            base=1517.0,
            epsilon=0.0,
            max_iterations=1,
        )

    first_priors = wrapped.call_args_list[0].args[2]
    assert set(first_priors.values()) == {1517.0}
    assert result.iterations == 1
    assert {row.iteration for row in result.iteration_priors} == {1}
    assert len(result.iteration_priors) == len(result.priors)


def test_missing_published_record_fails_loudly() -> None:
    date = _date(1989, 1)
    history = History({date: _basho({1: "M1e", 2: "J1e"}, {})})
    final_records = {date: {RikId(1): _record(0, 0, 0)}}

    with pytest.raises(KeyError, match="omit 1 ranked rikishi"):
        build_nonappearance_ledger(history, (date,), final_records)


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))


def _basho(
    ranks: dict[int, str],
    bouts_by_day: dict[int, list[BoutResult]],
) -> BashoState:
    rikishi_ids = {RikId(value) for value in ranks}
    summary = Summary(
        {
            Day(day): DailyResults(
                torikumi=Torikumi(
                    {Pair(bout.rikishi1, bout.rikishi2) for bout in bouts}
                ),
                results_lookup=ResultLookup(
                    {
                        Pair(bout.rikishi1, bout.rikishi2): bout
                        for bout in bouts
                    }
                ),
            )
            for day, bouts in bouts_by_day.items()
        }
    )
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(rikishi_ids),
            rikchii=RikChii(
                {
                    RikId(value): Chii.from_str(rank)
                    for value, rank in ranks.items()
                }
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
    *,
    decision: str,
) -> BoutResult:
    return BoutResult(
        rikishi1=RikId(rikishi_1),
        outcome1=outcome_1,
        rikishi2=RikId(rikishi_2),
        outcome2=outcome_2,
        decision=decision,
        symbol=Symbol[outcome_1.name],
    )


def _record(wins: int, losses: int, absences: int) -> FinalRecord:
    source = f"{wins}-{losses}-{absences}"
    return FinalRecord(
        source_text=source,
        wins=wins,
        losses=losses,
        absences=absences,
        draws=0,
    )

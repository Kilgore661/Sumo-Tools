"""Contracts for the first Equelo2 full-history baseline."""

from __future__ import annotations

import csv

import pytest

from src.analysis.elo_model_selection.model import (
    AdoptedPrior,
    ComparisonDefinition,
    _context,
)
from src.analysis.equelo2_baseline.analysis import (
    ExperimentDefinition,
    elo89_target_mean,
    run_experiment,
)
from src.analysis.equelo2_baseline.prior import (
    complete_historical_prior,
    load_and_complete_prior,
)
from src.analysis.equelo2_baseline.replay import ReplayEngine
from src.analysis.equelo2_baseline.selection import select_basho_bouts
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


def test_historical_prior_uses_nearest_available_rank_above_within_division() -> None:
    completed = complete_historical_prior(
        _base_prior({"M18": 1800.0, "J1": 1700.0, "J14": 1500.0}),
        (Chii.from_str("M20w"), Chii.from_str("J24eHD")),
    )

    assert completed.entries["M20"].rating == pytest.approx(1800.0)
    assert completed.entries["M20"].source_rank_pair == "M18"
    assert completed.entries["J24"].rating == pytest.approx(1500.0)
    assert completed.entries["J24"].source_rank_pair == "J14"
    assert completed.entries["M20"].provenance == "historical_nearest_higher"


def test_historical_prior_never_crosses_a_division_boundary() -> None:
    with pytest.raises(ValueError, match="no Elo-89 chii above it in the same division"):
        complete_historical_prior(
            _base_prior({"M18": 1800.0}),
            (Chii.from_str("J15e"),),
        )


def test_selection_includes_blank_kimarite_wl_and_excludes_fusen() -> None:
    basho = _basho(
        {1: "M1e", 2: "M1w", 3: "J1e", 4: "J1w"},
        [
            _bout(1, Outcome.W, 2, Outcome.L, decision="blank"),
            _bout(3, Outcome.FS, 4, Outcome.FP, decision="fusen"),
        ],
    )

    selection = select_basho_bouts(_date(1989, 1), basho)

    assert selection.raw_result_count == 2
    assert selection.rated_bout_count == 1
    assert selection.bouts[0].a_won is True
    assert selection.excluded_fusen_count == 1


def test_selection_reports_wl_with_off_banzuke_participant() -> None:
    basho = _basho(
        {1: "M1e"},
        [_bout(1, Outcome.W, 2, Outcome.L, decision="blank")],
    )

    selection = select_basho_bouts(_date(1958, 1), basho)

    assert selection.rated_bout_count == 0
    assert selection.excluded_off_banzuke_count == 1
    assert selection.excluded[0].reason == "participant_not_on_banzuke"


def test_replay_uses_full_banzuke_and_persists_across_result_gaps() -> None:
    prior = complete_historical_prior(
        _base_prior({"M1": 1500.0}),
        (Chii.from_str("M1e"),),
    )
    engine = ReplayEngine(
        name="candidate",
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
        target_mean=1500.0,
    )
    first_basho = _basho(
        {1: "M1e", 2: "M1w", 3: "M1e"},
        [_bout(1, Outcome.W, 2, Outcome.L, decision="blank")],
    )
    first_selection = select_basho_bouts(_date(1958, 1), first_basho)

    first = engine.process_basho(_date(1958, 1), first_basho, first_selection)
    second_basho = _basho({1: "M1e", 2: "M1w", 3: "M1e"}, [])
    second = engine.process_basho(
        _date(1958, 3),
        second_basho,
        select_basho_bouts(_date(1958, 3), second_basho),
    )

    assert len(first.start_ratings) == 3
    assert first.rated_bouts_after[RikId(3)] == 0
    assert second.start_ratings == pytest.approx(first.end_ratings)
    assert second.rated_bouts_before[RikId(1)] == 1


def test_replay_archives_and_restores_same_rikishi_rating() -> None:
    prior = complete_historical_prior(
        _base_prior({"M1": 1500.0}),
        (Chii.from_str("M1e"),),
    )
    engine = ReplayEngine(
        name="candidate",
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
        target_mean=1500.0,
    )
    first_basho = _basho(
        {1: "M1e", 2: "M1w"},
        [_bout(1, Outcome.W, 2, Outcome.L, decision="blank")],
    )
    first = engine.process_basho(
        _date(1958, 1),
        first_basho,
        select_basho_bouts(_date(1958, 1), first_basho),
    )
    absent_basho = _basho({2: "M1w"}, [])
    engine.process_basho(
        _date(1958, 3),
        absent_basho,
        select_basho_bouts(_date(1958, 3), absent_basho),
    )
    return_basho = _basho({1: "M1e", 2: "M1w"}, [])
    returned = engine.process_basho(
        _date(1958, 5),
        return_basho,
        select_basho_bouts(_date(1958, 5), return_basho),
    )

    assert first.end_ratings[RikId(1)] == pytest.approx(1510.0)
    assert returned.adjustment.returning_rikishi_count == 1
    assert returned.rated_bouts_before[RikId(1)] == 1
    assert returned.start_ratings[RikId(1)] > returned.start_ratings[RikId(2)]


def test_target_mean_is_exact_january_1989_prior_population_mean() -> None:
    january = _date(1989, 1)
    history = History({january: _basho({1: "M1e", 2: "J1w"}, [])})
    prior = complete_historical_prior(
        _base_prior({"M1": 1600.0, "J1": 1400.0}),
        history[january].banzuke.rikchii.values(),
    )

    assert elo89_target_mean(history, january, prior) == pytest.approx(1500.0)


def test_canonical_p1_literal_sides_are_paired_before_completion(tmp_path) -> None:
    prior_path = tmp_path / "prior.csv"
    with prior_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("chii", "rating"))
        writer.writeheader()
        writer.writerows((
            {"chii": "M18e", "rating": 1600},
            {"chii": "M18w", "rating": 1400},
        ))

    completed = load_and_complete_prior(
        prior_path,
        (Chii.from_str("M18e"), Chii.from_str("M20w")),
    )

    assert completed.entries["M18"].rating == pytest.approx(1500.0)
    assert completed.entries["M20"].rating == pytest.approx(1500.0)
    assert completed.entries["M20"].source_rank_pair == "M18"


def test_reference_engine_matches_retained_elo89_whole_population_contract() -> None:
    january = _date(1989, 1)
    march = _date(1989, 3)
    may = _date(1989, 5)
    history = History({
        january: _basho(
            {1: "M1e", 2: "J1w"},
            [_bout(1, Outcome.W, 2, Outcome.L, decision="blank")],
        ),
        march: _basho({2: "J1w"}, []),
        may: _basho(
            {1: "M1e", 2: "J1w"},
            [_bout(2, Outcome.W, 1, Outcome.L, decision="blank")],
        ),
    })
    base = _base_prior({"M1": 1600.0, "J1": 1400.0})
    completed = complete_historical_prior(
        base, history[january].banzuke.rikchii.values()
    )
    target = elo89_target_mean(history, january, completed)
    selection = select_basho_bouts(january, history[january])
    engine = ReplayEngine(
        name="elo89_reference",
        prior=completed,
        divisional_k=lambda _ordinal: 20.0,
        target_mean=target,
        persist_inactive_ratings=False,
    )

    actual = list(engine.process_basho(january, history[january], selection).forecasts)
    for date in (march, may):
        actual.extend(
            engine.process_basho(
                date,
                history[date],
                select_basho_bouts(date, history[date]),
            ).forecasts
        )
    canonical = select_rated_bouts(history, start_date=january, end_date=may)
    contexts = tuple(_context(history, bout) for bout in canonical.bouts)
    expected = run_whole_population_model(
        history,
        contexts,
        ComparisonDefinition(start_date=january, end_date=may),
        base,
        lambda _ordinal: 20.0,
    )

    assert len(actual) == len(expected) == 2
    for actual_row, expected_row in zip(actual, expected, strict=True):
        assert actual_row.probability_a_wins == pytest.approx(
            expected_row.probability_a_wins
        )
        assert actual_row.delta_a == pytest.approx(expected_row.delta_a)
        assert actual_row.delta_b == pytest.approx(expected_row.delta_b)


def test_small_experiment_writes_boundary_and_completion_artifacts(tmp_path) -> None:
    first = _date(1958, 1)
    boundary = _date(1988, 11)
    reference = _date(1989, 1)
    history = History({
        first: _basho(
            {1: "M20e", 2: "M20w"},
            [_bout(1, Outcome.W, 2, Outcome.L, decision="blank")],
        ),
        boundary: _basho({1: "M18e", 2: "M18w"}, []),
        reference: _basho(
            {1: "M18e", 2: "M18w"},
            [_bout(2, Outcome.W, 1, Outcome.L, decision="blank")],
        ),
    })
    prior_path = tmp_path / "prior.csv"
    with prior_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("chii", "rating"))
        writer.writeheader()
        writer.writerows((
            {"chii": "M18e", "rating": 1500},
            {"chii": "M18w", "rating": 1500},
        ))
    k_path = tmp_path / "k.json"
    k_path.write_text("{}", encoding="utf-8")

    outputs = run_experiment(
        history,
        ExperimentDefinition(first, reference, reference, boundary),
        prior_path=prior_path,
        k_config_path=k_path,
        divisional_k=lambda _ordinal: 20.0,
        output_root=tmp_path / "output",
        history_source={"kind": "fixture"},
    )

    completed = list(csv.DictReader((outputs.output_root / "completed_prior.csv").open()))
    handover = list(csv.DictReader((outputs.output_root / "1989_01_handover.csv").open()))
    forecasts = list(csv.DictReader((outputs.output_root / "forecast_ledger.csv").open()))
    rating_rows = list(csv.DictReader((outputs.output_root / "rating_ledger.csv").open()))
    assert next(row for row in completed if row["rank_pair"] == "M20")["source_rank_pair"] == "M18"
    assert len(handover) == 2
    assert {row["run"] for row in forecasts} == {
        "equelo2_full_history",
        "elo89_reference",
    }
    assert rating_rows
    assert all(row["chii_ordinal"] for row in rating_rows)
    assert {
        int(row["chii_ordinal"])
        for row in rating_rows
        if row["chii"] == "M18e"
    } == {Chii.from_str("M18e").ordinal()}
    assert outputs.findings.is_file()


def _base_prior(values: dict[str, float]) -> AdoptedPrior:
    return AdoptedPrior("fixture.csv", "digest", values, min(values.values()))


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
            rikchii=RikChii({
                RikId(value): Chii.from_str(rank) for value, rank in ranks.items()
            }),
            rikshik=RikShikona({
                rikishi: Shikona(f"Rikishi {int(rikishi)}")
                for rikishi in rikishi_ids
            }),
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

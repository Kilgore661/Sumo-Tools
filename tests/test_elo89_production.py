from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from src.analysis.elo_model_selection.model import (
    AdoptedPrior,
    ComparisonDefinition,
    _context,
)
from src.analysis.elo89.replay import replay_elo89
from src.analysis.elo89.api import Elo89Artifacts
from src.analysis.elo89.projection import project_basho_start_ratings
from src.analysis.elo89.output import _write_prior, write_elo89_outputs
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
            march: _basho({1: "M1e", 2: "J1w"}, []),
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
    assert actual.basho_start_ratings[may][RikId(1)] == pytest.approx(
        actual.basho_end_ratings[march][RikId(1)]
    )


def test_production_replay_freezes_rating_across_absence() -> None:
    january = _date(1989, 1)
    march = _date(1989, 3)
    may = _date(1989, 5)
    history = History(
        {
            january: _basho({1: "M1e", 2: "J1w"}, []),
            march: _basho({2: "J1w"}, []),
            may: _basho({1: "J2e", 2: "J1w"}, []),
        }
    )
    prior = AdoptedPrior(
        source_path="fixture.csv",
        sha256="fixture",
        rating_by_pair={"M1": 1600.0, "J1": 1400.0, "J2": 1000.0},
        fallback_rating=1000.0,
    )

    run = replay_elo89(
        history=history,
        start_date=january,
        end_date=may,
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
    )

    assert run.target_mean == pytest.approx(1500.0)
    assert run.basho_start_ratings[march][RikId(2)] == pytest.approx(1500.0)
    assert run.basho_start_ratings[may][RikId(1)] == pytest.approx(1550.0)
    assert run.basho_start_ratings[may][RikId(2)] == pytest.approx(1450.0)
    assert run.adjustments[1].departing_rikishi_count == 1
    assert run.adjustments[2].new_rikishi_count == 0


def test_projected_upcoming_start_matches_replay_with_returnee_and_newcomer() -> None:
    january = _date(1989, 1)
    march = _date(1989, 3)
    may = _date(1989, 5)
    prior = AdoptedPrior(
        source_path="fixture.csv",
        sha256="fixture",
        rating_by_pair={"M1": 1600.0, "J1": 1400.0, "J2": 1200.0},
        fallback_rating=1200.0,
    )
    represented = History(
        {
            january: _basho({1: "M1e", 2: "J1w"}, []),
            march: _basho({2: "J1w"}, []),
        }
    )
    represented_run = replay_elo89(
        history=represented,
        start_date=january,
        end_date=march,
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
    )
    artifacts = Elo89Artifacts(
        root=Path("unused"),
        manifest={"target_mean": represented_run.target_mean},
        prior=prior.rating_by_pair,
        basho_start_ratings={},
        day_end_ratings={},
        basho_end_ratings={
            str(date): {
                str(int(rikishi)): rating
                for rikishi, rating in values.items()
            }
            for date, values in represented_run.basho_end_ratings.items()
        },
        bout_ledger=(),
    )
    upcoming = _basho({1: "J2e", 2: "J1w", 3: "J2w"}, []).banzuke

    projected = project_basho_start_ratings(
        ratings=artifacts,
        banzuke=upcoming,
    )
    extended = History({**represented, may: _basho({1: "J2e", 2: "J1w", 3: "J2w"}, [])})
    extended_run = replay_elo89(
        history=extended,
        start_date=january,
        end_date=may,
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
    )
    expected = {
        str(int(rikishi)): rating
        for rikishi, rating in extended_run.basho_start_ratings[may].items()
    }

    assert projected == pytest.approx(expected)


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


def test_production_replay_rejects_rated_participant_absent_from_banzuke() -> None:
    date = _date(1989, 1)
    history = History(
        {date: _basho({1: "M1e"}, [_bout(1, Outcome.W, 2, Outcome.L)])}
    )
    prior = AdoptedPrior(
        source_path="fixture.csv",
        sha256="fixture",
        rating_by_pair={"M1": 1600.0},
        fallback_rating=1600.0,
    )

    with pytest.raises(
        ValueError,
        match="participant absent from the same-basho banzuke.*unresolved Mz data",
    ):
        replay_elo89(
            history=history,
            start_date=date,
            end_date=date,
            prior=prior,
            divisional_k=lambda _ordinal: 20.0,
        )


def test_saved_paired_prior_includes_chii_ordinal(tmp_path) -> None:
    prior = AdoptedPrior(
        source_path="fixture.csv",
        sha256="fixture",
        rating_by_pair={"Y1": 2500.0, "J1": 1800.0},
        fallback_rating=1800.0,
    )
    output = tmp_path / "prior.csv"

    _write_prior(output, prior)

    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert tuple(rows[0]) == ("rank_pair", "ordinal", "rating")
    assert {row["rank_pair"]: int(row["ordinal"]) for row in rows} == {
        "J1": Chii.from_str("J1").ordinal(),
        "Y1": Chii.from_str("Y1").ordinal(),
    }
    assert [row["rank_pair"] for row in rows] == ["Y1", "J1"]


def test_output_manifest_records_prior_source_hash(tmp_path) -> None:
    date = _date(1989, 1)
    history = History(
        {date: _basho({1: "M1e", 2: "J1w"}, [_bout(1, Outcome.W, 2, Outcome.L)])}
    )
    prior = AdoptedPrior(
        source_path="fixture.csv",
        sha256="fixed-prior-sha256",
        rating_by_pair={"M1": 1600.0, "J1": 1400.0},
        fallback_rating=1400.0,
    )
    run = replay_elo89(
        history=history,
        start_date=date,
        end_date=date,
        prior=prior,
        divisional_k=lambda _ordinal: 20.0,
    )

    paths = write_elo89_outputs(
        run=run,
        prior=prior,
        output_root=tmp_path / "elo89",
        history_source="fixture",
        start_date=date,
        end_date=date,
        k_config_path=tmp_path / "k.json",
        q=400.0,
    )

    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    assert manifest["prior"]["source_sha256"] == "fixed-prior-sha256"
    assert manifest["rating_lifecycle"] == "frozen across absence"


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

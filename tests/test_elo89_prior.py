from __future__ import annotations

import json

import pytest

from src.analysis.elo89.config import (
    ACCEPTED_LITERAL_PRIOR_PATH,
    ACCEPTED_PRIOR_PATH,
    DEFAULT_LAST_PRIOR_BASHO,
    prior_run_directory,
)
from src.analysis.elo89.prior.__main__ import parse_basho
from src.analysis.elo89.prior import producer
from src.analysis.elo89.producer import DEFAULT_PRIOR
from src.analysis.equelo_bkp1.model import FixedPointResult, IterationRow
from src.analysis.equelo_bkp1.simulate import BoutEligibility
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_accepted_prior_paths_separate_paired_input_from_literal_fit() -> None:
    assert DEFAULT_LAST_PRIOR_BASHO == Date.from_ints(2026, 9)
    assert producer.EPSILON == 8.5
    assert ACCEPTED_PRIOR_PATH.as_posix() == (
        "src/analysis/equelo_prior_aggregation/results/priors.csv"
    )
    assert ACCEPTED_LITERAL_PRIOR_PATH.as_posix() == (
        "files/output/analysis/elo89/prior/2026-09/run-002/prior.csv"
    )
    assert prior_run_directory(DEFAULT_LAST_PRIOR_BASHO, 2).name == "run-002"
    assert DEFAULT_PRIOR == ACCEPTED_PRIOR_PATH


@pytest.mark.parametrize("value", ("2026-09", "2026/09"))
def test_parse_basho_accepts_unambiguous_boundary_formats(value: str) -> None:
    assert parse_basho(value) == Date.from_ints(2026, 9)


def test_producer_includes_boundary_excludes_future_and_numbers_runs(
    tmp_path,
    monkeypatch,
) -> None:
    january = Date.from_ints(1989, 1)
    boundary = Date.from_ints(2026, 9)
    future = Date.from_ints(2026, 11)
    history = History(
        {
            january: _basho("J1e"),
            boundary: _basho("M1e"),
            future: _basho("Y1e"),
        }
    )
    observed: list[tuple[tuple[Date, ...], BoutEligibility]] = []

    def fake_solve(selected, _k, *, eligibility, **_kwargs):
        observed.append((tuple(sorted(selected)), eligibility))
        chii = Chii.from_str("M1e")
        row = IterationRow(1, 2.0, "M1e", 1, 0.0, 0.0, 0.0)
        return FixedPointResult(
            priors={chii: 1600.0},
            support={chii: 1},
            converged=True,
            iterations=1,
            final_delta=2.0,
            iteration_rows=(row,),
        )

    monkeypatch.setattr(producer, "solve", fake_solve)
    monkeypatch.setattr(producer, "load_divisional_k", lambda _path: object())

    first = producer.produce_prior(
        history,
        last_prior_basho=boundary,
        output_root=tmp_path,
        history_source="fixture",
    )
    second = producer.produce_prior(
        history,
        last_prior_basho=boundary,
        output_root=tmp_path,
        history_source="fixture",
    )

    assert observed == [
        ((january, boundary), BoutEligibility.P1_WL),
        ((january, boundary), BoutEligibility.P1_WL),
    ]
    assert first.root == tmp_path / "2026-09" / "run-001"
    assert second.root == tmp_path / "2026-09" / "run-002"
    assert first.prior.is_file()
    assert first.iterations.is_file()
    manifest = json.loads(first.manifest.read_text(encoding="utf-8"))
    assert manifest["history"]["last_prior_basho_inclusive"] == "2026/09"
    assert manifest["history"]["end"] == "2026/09"
    assert manifest["bout_eligibility"]["policy"] == "p1-wl"


def test_producer_rejects_boundary_absent_from_history_before_writing(tmp_path) -> None:
    history = History({Date.from_ints(1989, 1): _basho("J1e")})

    with pytest.raises(ValueError, match="basho absent from History"):
        producer.produce_prior(
            history,
            last_prior_basho=Date.from_ints(2026, 9),
            output_root=tmp_path,
        )

    assert list(tmp_path.iterdir()) == []


def _basho(rank: str) -> BashoState:
    rikid = RikId(1)
    return BashoState(
        banzuke=Banzuke(
            riks=Riks({rikid}),
            rikchii=RikChii({rikid: Chii.from_str(rank)}),
            rikshik=RikShikona({rikid: Shikona("Fixture")}),
        ),
        summary=Summary({}),
    )

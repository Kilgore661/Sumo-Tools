from __future__ import annotations

import csv
import json

import pytest

from src.analysis.equelo_bkp1.simulate import BoutEligibility
from src.analysis.equelo_bkp1.solve import solve
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import Day, Pair, RikId, Riks, Shikona, Torikumi
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary
from src.validation.p1_trajectory.runner import _parser, run_trajectory


def test_trajectory_matches_bounded_solver_and_writes_checkpoint(tmp_path) -> None:
    history = _history()
    k_config = tmp_path / "k.json"
    k_config.write_text('{"max": 20, "lims": {}}', encoding="utf-8")
    expected = solve(
        history,
        lambda _ordinal: 20.0,
        epsilon=0.0,
        max_iterations=11,
        eligibility=BoutEligibility.P1_WL,
    )
    assert expected.iterations == 11
    output = tmp_path / "trajectory"

    run_trajectory(
        history,
        output_root=output,
        k_config_path=k_config,
        eligibility=BoutEligibility.P1_WL,
        report_every=10,
        checkpoint_every=11,
        history_source={"kind": "fixture"},
        _iteration_limit=11,
    )

    checkpoint = output / "checkpoints" / "iteration-000011"
    with (checkpoint / "prior.csv").open(newline="", encoding="utf-8") as stream:
        prior_rows = list(csv.DictReader(stream))
    actual = {Chii.from_str(row["chii"]): float(row["rating"]) for row in prior_rows}
    assert actual == pytest.approx(expected.priors)
    assert [int(row["ordinal"]) for row in prior_rows] == sorted(
        chii.ordinal() for chii in expected.priors
    )

    with (output / "iterations.csv").open(newline="", encoding="utf-8") as stream:
        iterations = list(csv.DictReader(stream))
    assert len(iterations) == 11
    assert float(iterations[-1]["gradient_10"]) == pytest.approx(
        (
            float(iterations[-1]["max_prior_change"])
            - float(iterations[0]["max_prior_change"])
        )
        / 10.0
    )
    checkpoint_manifest = json.loads(
        (checkpoint / "manifest.json").read_text(encoding="utf-8")
    )
    assert checkpoint_manifest["iteration"] == 11
    assert checkpoint_manifest["eligibility"] == "p1-wl"
    assert checkpoint_manifest["prior"]["path"] == "prior.csv"


def test_cli_has_no_epsilon_or_iteration_ceiling() -> None:
    required = ["--history-zip", "history.zip", "--eligibility", "p1-wl"]
    with pytest.raises(SystemExit):
        _parser().parse_args([*required, "--epsilon", "3"])
    with pytest.raises(SystemExit):
        _parser().parse_args([*required, "--max-iterations", "400"])


def _history() -> History:
    first, second = RikId(1), RikId(2)
    pair = Pair(first, second)
    bout = BoutResult(
        rikishi1=first,
        outcome1=Outcome.W,
        rikishi2=second,
        outcome2=Outcome.L,
        decision="blank",
        symbol=Symbol.W,
    )
    return History(
        {
            Date.from_ints(1989, 1): BashoState(
                banzuke=Banzuke(
                    riks=Riks({first, second}),
                    rikchii=RikChii(
                        {
                            first: Chii.from_str("Ms1e"),
                            second: Chii.from_str("Ms2e"),
                        }
                    ),
                    rikshik=RikShikona(
                        {first: Shikona("First"), second: Shikona("Second")}
                    ),
                ),
                summary=Summary(
                    {
                        Day(1): DailyResults(
                            torikumi=Torikumi({pair}),
                            results_lookup=ResultLookup({pair: bout}),
                        )
                    }
                ),
            )
        }
    )

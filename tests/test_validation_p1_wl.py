from __future__ import annotations

import csv
import json

import pytest

from src.analysis.equelo_bkp1.simulate import (
    BoutEligibility,
    bout_is_eligible,
    replay,
)
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
from src.sumo_core.Kimarite import Kimarite
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary
from src.validation.kimarite.p1_wl import _selected_history, run_comparison


def test_p1_wl_rates_blank_binary_result_while_p1_control_does_not() -> None:
    history = _two_basho_history(decision="blank")
    priors = {Chii.from_str("Ms1e"): 1500.0, Chii.from_str("Ms1w"): 1500.0}

    control = replay(history, priors, lambda _ordinal: 20.0)
    candidate = replay(
        history,
        priors,
        lambda _ordinal: 20.0,
        eligibility=BoutEligibility.P1_WL,
    )

    later = Date.from_ints(1989, 3)
    assert control.basho_start_ratings[later][RikId(1)] == pytest.approx(1500.0)
    assert candidate.basho_start_ratings[later][RikId(1)] == pytest.approx(1510.0)
    assert candidate.basho_start_ratings[later][RikId(2)] == pytest.approx(1490.0)


def test_p1_wl_gives_named_and_blank_kimarite_identical_rating_semantics() -> None:
    priors = {Chii.from_str("Ms1e"): 1500.0, Chii.from_str("Ms1w"): 1500.0}
    blank = replay(
        _two_basho_history(decision="blank"),
        priors,
        lambda _ordinal: 20.0,
        eligibility=BoutEligibility.P1_WL,
    )
    named = replay(
        _two_basho_history(decision=Kimarite.KATASUKASHI),
        priors,
        lambda _ordinal: 20.0,
        eligibility=BoutEligibility.P1_WL,
    )

    assert blank.basho_start_ratings == named.basho_start_ratings


def test_p1_wl_positively_requires_binary_wl() -> None:
    fusen = _bout(1, Outcome.FS, 2, Outcome.FP, decision="fusen")
    draw = _bout(1, Outcome.DRAW, 2, Outcome.DRAW, decision="blank")

    assert not bout_is_eligible(fusen, BoutEligibility.P1_WL)
    assert not bout_is_eligible(draw, BoutEligibility.P1_WL)


def test_small_p1_wl_comparison_writes_isolated_artifacts(tmp_path) -> None:
    output = tmp_path / "comparison-run"
    k_config = tmp_path / "k.json"
    k_config.write_text('{"max": 20, "lims": {}}', encoding="utf-8")

    run_comparison(
        _two_basho_history(decision="blank"),
        output_root=output,
        k_config_path=k_config,
        epsilon=1_000_000.0,
        max_iterations=2,
        history_source={"kind": "fixture"},
    )

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    p1_manifest = json.loads(
        (output / "p1" / "manifest.json").read_text(encoding="utf-8")
    )
    p1_wl_manifest = json.loads(
        (output / "p1-wl" / "manifest.json").read_text(encoding="utf-8")
    )
    rows = list(
        csv.DictReader(
            (output / "comparison" / "prior_comparison.csv").open(
                encoding="utf-8", newline=""
            )
        )
    )

    assert manifest["model"]["controlled_difference"] == "bout eligibility only"
    assert manifest["runtime"]["total_seconds"] >= 0.0
    assert manifest["variants"]["p1"]["convergence"] == {
        "threshold": 1_000_000.0,
        "maximum_iterations": 2,
        "iterations_taken": 1,
        "final_maximum_change": pytest.approx(
            manifest["variants"]["p1"]["final_delta"]
        ),
        "converged": True,
    }
    assert p1_manifest["convergence"]["threshold"] == 1_000_000.0
    assert p1_manifest["convergence"]["maximum_iterations"] == 2
    assert p1_manifest["convergence"]["iterations_taken"] == 1
    assert p1_manifest["convergence"]["final_maximum_change"] == pytest.approx(
        p1_manifest["final_delta"]
    )
    assert p1_manifest["convergence"]["converged"] is True
    assert p1_manifest["counts"]["excluded_blank_kimarite"] == 1
    assert p1_wl_manifest["counts"]["rated_blank_kimarite"] == 1
    assert {row["chii"] for row in rows} == {"Ms1e", "Ms1w"}
    assert any(float(row["difference"]) != 0.0 for row in rows)


def test_cli_history_preparation_matches_canonical_p1_oracle_contract() -> None:
    history = _two_basho_history(decision="blank", ranks={1: "Y1eYO", 2: "Y1w"})

    selected = _selected_history(
        history,
        Date.from_ints(1989, 1),
        Date.from_ints(1989, 3),
    )

    assert str(selected[Date.from_ints(1989, 1)].banzuke.rikchii[RikId(1)]) == "Y1e"


def _two_basho_history(
    *, decision, ranks: dict[int, str] | None = None
) -> History:
    ranks = ranks or {1: "Ms1e", 2: "Ms1w"}
    return History(
        {
            Date.from_ints(1989, 1): _basho(
                ranks,
                [_bout(1, Outcome.W, 2, Outcome.L, decision=decision)],
            ),
            Date.from_ints(1989, 3): _basho(ranks, []),
        }
    )


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
    *,
    decision,
) -> BoutResult:
    return BoutResult(
        rikishi1=RikId(rikishi_1),
        outcome1=outcome_1,
        rikishi2=RikId(rikishi_2),
        outcome2=outcome_2,
        decision=decision,
        symbol=Symbol[outcome_1.name],
    )

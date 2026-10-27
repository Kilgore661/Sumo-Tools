from __future__ import annotations

import csv
import json

from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import Day, Pair, RikId, Riks, Shikona, Torikumi
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Kimarite import Kimarite
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary
from src.validation.kimarite.p1_wl_evaluation import run_evaluation


def test_complete_p1_wl_evaluation_writes_controlled_artifacts(tmp_path) -> None:
    history = _history()
    published = tmp_path / "published.csv"
    p1 = tmp_path / "p1.csv"
    p1_wl = tmp_path / "p1-wl.csv"
    old = tmp_path / "old.csv"
    k_config = tmp_path / "k.json"
    _side_prior(published, {"Ms1e": 1590.0, "Ms2e": 1410.0})
    _side_prior(p1, {"Ms1e": 1600.0, "Ms2e": 1400.0})
    _side_prior(p1_wl, {"Ms1e": 1620.0, "Ms2e": 1380.0})
    old.write_text(
        "rank_pair,pre_smoothing_rating\nMs1,1550\nMs2,1450\n",
        encoding="utf-8",
    )
    k_config.write_text('{"max": 20, "lims": {}}', encoding="utf-8")
    output = tmp_path / "evaluation"

    run_evaluation(
        history,
        output_root=output,
        published_p1_path=published,
        p1_path=p1,
        p1_wl_path=p1_wl,
        old_prior_path=old,
        k_config_path=k_config,
        bootstrap_resamples=10,
        history_source={"kind": "fixture"},
    )

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    initial = list(csv.DictReader((output / "initialisation" / "summary.csv").open()))
    ratings = list(
        csv.DictReader(
            (output / "elo89" / "rating_difference_summary.csv").open()
        )
    )
    probabilities = list(
        csv.DictReader(
            (output / "elo89" / "probability_difference_summary.csv").open()
        )
    )
    publication = list(
        csv.DictReader((output / "elo89" / "publication_comparison.csv").open())
    )

    assert manifest["history"]["start"] == "1989/01"
    assert manifest["history"]["end"] == "1989/03"
    assert manifest["selection"]["rated_bout_count"] == 2
    assert manifest["priors"]["same_history_p1"]["pair_count"] == 2
    assert {row["model"] for row in initial if row["population"] == "all"} == {
        "B", "B_k", "old_B_kP", "published_B_kP1", "B_kP1", "B_kP1-WL"
    }
    causal = next(
        row for row in ratings
        if row["contrast"] == "kimarite_effect" and row["stage"] == "basho_end"
    )
    assert float(causal["maximum_absolute_difference"]) > 0.0
    assert "aligned_mean_absolute_difference" in causal
    assert {row["population"] for row in probabilities} >= {"all", "new_entrant"}
    assert (output / "elo89" / "rating_difference_by_maturity.csv").is_file()
    assert (output / "elo89" / "rating_difference_by_entry_status.csv").is_file()
    assert {row["kind"] for row in publication} == {"current", "peak"}
    assert (output / "elo89" / "p1-wl" / "manifest.json").is_file()


def _side_prior(path, values) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("chii", "rating"))
        writer.writeheader()
        for chii, rating in values.items():
            writer.writerow({"chii": chii, "rating": rating})


def _history() -> History:
    return History(
        {
            Date.from_ints(1989, 1): _basho(Kimarite.KATASUKASHI),
            Date.from_ints(1989, 3): _basho(Kimarite.OSHIDASHI),
        }
    )


def _basho(decision) -> BashoState:
    first, second = RikId(1), RikId(2)
    bout = BoutResult(
        rikishi1=first,
        outcome1=Outcome.W,
        rikishi2=second,
        outcome2=Outcome.L,
        decision=decision,
        symbol=Symbol.W,
    )
    pair = Pair(first, second)
    return BashoState(
        banzuke=Banzuke(
            riks=Riks({first, second}),
            rikchii=RikChii(
                {first: Chii.from_str("Ms1e"), second: Chii.from_str("Ms2e")}
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

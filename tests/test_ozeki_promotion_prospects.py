import json
from types import SimpleNamespace

from src.analysis.promotion.prospects.ozeki.dataset import build_dataset
from src.analysis.promotion.prospects.ozeki.run import run_analysis
from src.analysis.promotion.prospects.ozeki.statistics import score_rule, wilson_interval
from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


def _state(specification):
    """Build one compact basho: rikishi_id -> (rank, regular wins)."""
    ranks = {
        rikishi_id: Chii.from_str(rank)
        for rikishi_id, (rank, _) in specification.items()
    }
    days = {}
    for day in range(1, 16):
        bouts = {}
        for rikishi_id, (_, wins) in specification.items():
            outcome = Outcome.W if day <= wins else Outcome.L
            bouts[rikishi_id] = SimpleNamespace(
                rikishi1=rikishi_id,
                rikishi2=-rikishi_id,
                outcome1=outcome,
                outcome2=Outcome.L if outcome == Outcome.W else Outcome.W,
            )
        days[day] = SimpleNamespace(results_lookup=bouts)
    return SimpleNamespace(
        banzuke=SimpleNamespace(
            riks=set(specification),
            rikchii=ranks,
            rikshik={rikishi_id: f"Rikishi {rikishi_id}" for rikishi_id in specification},
        ),
        summary=days,
    )


def _history():
    history = History()
    history[Date(2020, 1)] = _state({
        1: ("K1e", 10),
        2: ("M1e", 12),
        3: ("K1w", 11),
    })
    history[Date(2020, 3)] = _state({
        1: ("S1e", 11),
        2: ("K1e", 10),
        3: ("S1w", 11),
    })
    history[Date(2020, 5)] = _state({
        1: ("S1e", 11),
        2: ("S1w", 10),
        3: ("S2eHD", 11),
    })
    history[Date(2020, 7)] = _state({
        1: ("O1e", 0),
        2: ("O1w", 0),
        3: ("S1e", 0),
    })
    return history


def test_dataset_and_rule_scoring_keep_rank_patterns_and_all_promotions():
    dataset = build_dataset(_history())
    assert len(dataset["promotions"]) == 2
    assert len(dataset["opportunities"]) == 4
    assert sum(not row["resolved"] for row in dataset["opportunities"]) == 1
    assert {row["rank_pattern"] for row in dataset["opportunities"]} == {
        "K-S-S", "M-K-S", "S-S-S"
    }
    a32 = score_rule(dataset["opportunities"], dataset["promotions"], "A", 32)
    b32 = score_rule(dataset["opportunities"], dataset["promotions"], "B", 32)
    assert (a32["tp"], a32["fp"], a32["fn"]) == (1, 1, 1)
    assert (b32["tp"], b32["fp"], b32["fn"]) == (2, 1, 0)
    low, high = wilson_interval(2, 3)
    assert 0 < low < 2 / 3 < high < 1


def test_smoke_run_writes_artifacts_and_reports_console_progress(tmp_path):
    messages = []
    report = run_analysis(
        _history(), tmp_path / "run", source={"kind": "synthetic_smoke"},
        bootstrap_samples=25, seed=17, progress=messages.append,
    )
    assert messages[0].startswith("[1/8]")
    assert messages[-2] == "[8/8] Complete."
    assert report.name == "report.md"
    assert report.exists()
    expected = {
        "opportunities.csv", "promotions.csv", "total_wins.csv",
        "rank_patterns.csv", "minimum_wins.csv",
        "weak_result_position.csv", "rules.csv", "period_rules.csv",
        "forward_validation.csv", "report.md", "manifest.json",
    }
    assert {path.name for path in report.parent.iterdir()} == expected
    manifest = json.loads((report.parent / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source"] == {"kind": "synthetic_smoke"}
    assert manifest["bootstrap"]["samples"] == 25
    assert manifest["counts"]["promotions"] == 2
    assert "not a JSA rule" in report.read_text(encoding="utf-8")

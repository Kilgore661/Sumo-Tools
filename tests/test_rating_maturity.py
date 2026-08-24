from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.analysis.career_bout_volume.rating_maturity.analysis import run_probe
from src.analysis.career_bout_volume.rating_maturity.model import ProbeDefinition
from src.analysis.career_bout_volume.rating_maturity import reports
from src.analysis.career_bout_volume.rating_maturity.reports import SourceIdentity
from src.analysis.elo_model_selection.model import (
    AdoptedPrior,
    ComparisonDefinition,
    run_comparison,
)
from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import Day, Month, Pair, RikId, Riks, Shikona, Torikumi, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult, DailyResults, Decision, ResultLookup, Summary


def test_probe_uses_strictly_prior_support_and_preserves_rating_birth_contract() -> None:
    result = run_probe(
        _history(),
        start_date=_date(1989, 1),
        end_date=_date(1989, 5),
        prior=_prior(),
        divisional_k=lambda ordinal: 20.0,
        definition=ProbeDefinition("1989/01", "1989/05", minimum_chii_observations=1),
    )
    rows = {(row.basho, row.rikishi_id): row for row in result.maturity_rows}

    assert rows[("1989/01", 1)].normalized_position == pytest.approx(0.0)
    assert rows[("1989/01", 2)].normalized_position == pytest.approx(1.0)
    assert rows[("1989/01", 1)].prior_rated_bouts == 0
    assert rows[("1989/03", 2)].prior_rated_bouts == 1
    assert rows[("1989/03", 3)].prior_rated_bouts == 0
    assert rows[("1989/03", 3)].model_state_available
    assert rows[("1989/03", 3)].cohort == "observed_entrant"

    absent = rows[("1989/03", 4)]
    assert not absent.model_state_available
    assert absent.rating_bk is None
    assert absent.model_state_exclusion == "no eligible rated bout yet"

    first_eligible = rows[("1989/05", 4)]
    assert first_eligible.model_state_available
    assert first_eligible.prior_rated_bouts == 0
    assert first_eligible.prior_fought_bouts == 1
    assert first_eligible.rating_bk == 1500.0
    assert first_eligible.rating_bkp == 1400.0
    assert result.rated_bout_count == 3
    assert result.excluded_draw_count == 1
    assert result.model_state_exclusion_count == 1


def test_coupled_replay_has_identical_domains_and_complementary_participant_forecasts() -> None:
    result = run_probe(
        _history(), start_date=_date(1989, 1), end_date=_date(1989, 5),
        prior=_prior(), divisional_k=lambda ordinal: 20.0,
        definition=ProbeDefinition("1989/01", "1989/05", minimum_chii_observations=1),
    )

    assert len(result.bout_rows) == result.rated_bout_count
    assert all(0.0 <= row.probability_a_bk <= 1.0 for row in result.bout_rows)
    assert all(0.0 <= row.probability_a_bkp <= 1.0 for row in result.bout_rows)
    assert all(
        row.absolute_probability_disagreement
        == pytest.approx(abs((1 - row.probability_a_bkp) - (1 - row.probability_a_bk)))
        for row in result.bout_rows
    )
    jan = [row for row in result.maturity_rows if row.basho == "1989/01"]
    assert sum(row.centered_rating_bk for row in jan if row.centered_rating_bk is not None) == pytest.approx(0.0)
    assert sum(row.centered_rating_bkp for row in jan if row.centered_rating_bkp is not None) == pytest.approx(0.0)


def test_coupled_replay_matches_selected_model_implementations_bout_for_bout() -> None:
    history = _history()
    definition = ProbeDefinition("1989/01", "1989/05", minimum_chii_observations=1)
    k_path = Path("files/input/elo_fide.json")
    probe = run_probe(
        history, start_date=_date(1989, 1), end_date=_date(1989, 5),
        prior=_prior(), divisional_k=load_divisional_k_fn(k_path), definition=definition,
    )
    comparison = run_comparison(
        history,
        ComparisonDefinition(start_date=_date(1989, 1), end_date=_date(1989, 5)),
        prior=_prior(),
        k_config=k_path,
    )
    by_model = {model.spec.name: model.forecasts for model in comparison.models}

    assert [row.probability_a_bk for row in probe.bout_rows] == pytest.approx(
        [row.probability_a_wins for row in by_model["B_k"]]
    )
    assert [row.probability_a_bkp for row in probe.bout_rows] == pytest.approx(
        [row.probability_a_wins for row in by_model["B_kP"]]
    )
    assert [row.prior_rated_bouts_a for row in probe.bout_rows] == [
        row.rated_bouts_a_before for row in by_model["B_k"]
    ]
    assert [row.prior_rated_bouts_b for row in probe.bout_rows] == [
        row.rated_bouts_b_before for row in by_model["B_k"]
    ]


def test_reports_write_declared_artifacts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    result = run_probe(
        _history(), start_date=_date(1989, 1), end_date=_date(1989, 5),
        prior=_prior(), divisional_k=lambda ordinal: 20.0,
        definition=ProbeDefinition("1989/01", "1989/05", minimum_chii_observations=1),
    )
    monkeypatch.setattr(reports, "_git_state", lambda: ("abc123", True))
    outputs = reports.write_outputs(
        result,
        SourceIdentity("history.zip", "h", "prior.csv", "p", "k.json", "k"),
        output_root=tmp_path,
        generated_at=datetime(2026, 8, 24, 10, 0, tzinfo=timezone.utc),
    )

    manifest = json.loads(outputs.manifest.read_text(encoding="utf-8"))
    assert outputs.run_directory.name == "2026-08-24_10-00-00"
    assert manifest["history"]["start_basho"] == "1989/01"
    assert manifest["counts"]["participant_forecast_rows"] == 6
    assert manifest["git"] == {"commit": "abc123", "dirty": True}
    assert "first eligible rated bout" in manifest["contracts"]["rating_birth"]
    assert "Plotly.newPlot" in outputs.position_support_html.read_text(encoding="utf-8")
    assert "normalized position" in outputs.chii_means_html.read_text(encoding="utf-8")
    assert outputs.position_means_csv.exists()
    assert "Answers to the staged questions" in outputs.findings.read_text(encoding="utf-8")
    assert outputs.forecast_disagreement_csv.read_text(encoding="utf-8-sig").count("\n") == 7


def _history() -> History:
    r1, r2, r3, r4 = (RikId(value) for value in range(1, 5))
    return History({
        _date(1989, 1): _state(
            {r1: ("One", "J1e"), r2: ("Two", "J1w")},
            {Day(1): [_bout(r1, Outcome.W, r2, Outcome.L)]},
        ),
        _date(1989, 3): _state(
            {r1: ("One", "J1e"), r2: ("Two", "J1w"), r3: ("Three", "J2e"), r4: ("Four", "J2w")},
            {
                Day(1): [_bout(r3, Outcome.W, r2, Outcome.L)],
                Day(2): [_bout(r1, Outcome.DRAW, r4, Outcome.DRAW)],
            },
        ),
        _date(1989, 5): _state(
            {r1: ("One", "J1e"), r3: ("Three", "J1w"), r4: ("Four", "J2e")},
            {Day(1): [_bout(r4, Outcome.L, r1, Outcome.W)]},
        ),
    })


def _prior() -> AdoptedPrior:
    return AdoptedPrior("prior.csv", "digest", {"J1": 1600.0, "J2": 1400.0}, 1400.0)


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))


def _state(entries: dict[RikId, tuple[str, str]], bouts_by_day: dict[Day, list[BoutResult]]) -> BashoState:
    daily = {}
    for day, bouts in bouts_by_day.items():
        lookup = ResultLookup({Pair(bout.rikishi1, bout.rikishi2): bout for bout in bouts})
        daily[day] = DailyResults(
            torikumi=Torikumi(Pair(bout.rikishi1, bout.rikishi2) for bout in bouts),
            results_lookup=lookup,
        )
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(entries),
            rikchii=RikChii({rikishi: Chii.from_str(chii) for rikishi, (_, chii) in entries.items()}),
            rikshik=RikShikona({rikishi: Shikona(name) for rikishi, (name, _) in entries.items()}),
        ),
        summary=Summary(daily),
    )


def _bout(r1: RikId, outcome1: Outcome, r2: RikId, outcome2: Outcome) -> BoutResult:
    return BoutResult(
        rikishi1=r1, outcome1=outcome1, rikishi2=r2, outcome2=outcome2,
        decision=Decision("blank"),
        symbol=Symbol.DRAW if outcome1 == Outcome.DRAW else outcome1.to_symbol(),
    )

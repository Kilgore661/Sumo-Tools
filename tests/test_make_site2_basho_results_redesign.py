from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE = (
    Path.home()
    / ".cache"
    / "codex-runtimes"
    / "codex-primary-runtime"
    / "dependencies"
    / "node"
    / "bin"
    / "node.exe"
)
MODULE = ROOT / "src/products/make_site2/runtime/site-refactor/ui/basho-results-table.js"


def render_case(*, latest_day: int, previous_context: bool, rating_context: bool, nu_chii: bool) -> str:
    script = f"""
import {{ buildBashoResultsPresentationModel, renderBashoResultsPresentationTable }} from {json.dumps(MODULE.as_uri())};

const model = buildBashoResultsPresentationModel({{
  rows: [{{
    shikona: "Test Rikishi",
    previous_chii: "M1e",
    previous_result: "10-5 G",
    previous_rank_level_movement: {json.dumps("\u2191")},
    previous_equelo: "1800",
    chii: "S1e",
    score: "8-6-1 Y",
    previous_delta_direction: {json.dumps("\u2193")},
    equelo: "1815",
    delta_equelo: "+15",
    nu_chii: "K1e",
  }}],
  state: {{
    previous_context: {json.dumps(previous_context)},
    rating_context: {json.dumps(rating_context)},
    nu_chii: {json.dumps(nu_chii)},
  }},
  entry: {{ latest_day: {latest_day} }},
  title: "Makuuchi Results, May 2026",
}});
console.log(renderBashoResultsPresentationTable(model));
"""
    result = subprocess.run(
        [str(NODE), "--input-type=module", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    return result.stdout


def test_transitional_basho_results_renderer_shows_projected_context() -> None:
    html = render_case(
        latest_day=15,
        previous_context=True,
        rating_context=True,
        nu_chii=True,
    )

    assert "brb-redesign-table" in html
    assert "Before Basho" in html
    assert "After Basho" in html
    assert "Comparison" in html
    assert "📦" in html
    assert 'data-column-path="before.rba.result.wins">10<' in html
    assert 'data-column-path="before.rba.result.losses">5<' in html
    assert 'data-column-path="before.rba.result.prizes">G<' in html
    assert 'data-column-path="before.rba.result.division_change">↑<' in html
    assert 'data-column-path="state.rba.result.wins">8<' in html
    assert 'data-column-path="state.rba.result.losses">6<' in html
    assert 'data-column-path="state.rba.result.absences">1<' in html
    assert 'data-column-path="state.rba.result.prizes">Y<' in html
    assert 'data-column-path="state.rba.result.division_change">↓<' in html
    assert "Delta Equelo" in html
    assert "K1e" in html


def test_transitional_basho_results_renderer_hides_unprojected_context() -> None:
    html = render_case(
        latest_day=7,
        previous_context=False,
        rating_context=False,
        nu_chii=False,
    )

    assert "Current" in html
    assert "Before Basho" not in html
    assert "Comparison" not in html
    assert "before.rba.result.wins" not in html
    assert "Delta Equelo" not in html
    assert "K1e" not in html


def test_transitional_basho_results_renderer_derives_current_division_change_from_next_bp() -> None:
    script = f"""
import {{ buildBashoResultsPresentationModel, renderBashoResultsPresentationTable }} from {json.dumps(MODULE.as_uri())};

const model = buildBashoResultsPresentationModel({{
  rows: [{{
    shikona: "Demoted Rikishi",
    chii: "M13w",
    score: "5-10",
    nu_chii: "J6e",
  }}],
  state: {{
    previous_context: false,
    rating_context: false,
    nu_chii: true,
  }},
  entry: {{ latest_day: 15 }},
  title: "Makuuchi Results, January 1970",
}});
console.log(renderBashoResultsPresentationTable(model));
"""
    result = subprocess.run(
        [str(NODE), "--input-type=module", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )

    assert 'data-column-path="state.rba.result.division_change">↓<' in result.stdout

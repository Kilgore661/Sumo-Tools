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


def assert_cell(html: str, path: str, value: str) -> None:
    assert f'data-column-path="{path}"' in html
    assert f">{value}<" in html


def render_case(
    *,
    latest_day: int,
    previous_context: bool,
    rating_context: bool,
    nu_chii: bool,
    analysis_context: bool = False,
) -> str:
    script = f"""
import {{ buildBashoResultsPresentationModel, renderBashoResultsPresentationTable }} from {json.dumps(MODULE.as_uri())};

const model = buildBashoResultsPresentationModel({{
  rows: [{{
    shikona: "Test Rikishi",
    previous_chii: "M1e",
    previous_chii_ordinal: "400002",
    previous_result: "10-5 G",
    previous_equelo: "1800",
    chii: "S1e",
    chii_ordinal: "200002",
    score: "8-6-1 Y",
    equelo: "1815",
    delta_equelo: "+15",
    nu_chii: "K1e",
    nu_chii_ordinal: "300002",
  }}],
  state: {{
    previous_context: {json.dumps(previous_context)},
    changes_context: true,
    rating_context: {json.dumps(rating_context)},
    analysis_context: {json.dumps(analysis_context)},
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
    assert "Next Basho" in html
    assert ">reference<" not in html
    assert 'data-column-path="reference.row_number"' in html
    assert 'data-column-path="reference.shikona"' in html
    assert "\U0001f4e6" in html
    assert_cell(html, "before.result.wins", "10")
    assert_cell(html, "before.result.losses", "5")
    assert_cell(html, "before.result.prizes", "G")
    assert_cell(html, "selected.result.wins", "8")
    assert_cell(html, "selected.result.losses", "6")
    assert_cell(html, "selected.result.absences", "1")
    assert_cell(html, "selected.result.prizes", "Y")
    assert_cell(html, "changes.movement.bp", "\u2193")
    assert_cell(html, "changes.movement.division", "\u2193")
    assert "\u0394Eq" in html
    assert "K1e" in html


def test_transitional_basho_results_renderer_labels_analysis_as_ratings_fit() -> None:
    html = render_case(
        latest_day=15,
        previous_context=False,
        rating_context=True,
        nu_chii=False,
        analysis_context=True,
    )

    assert "Ratings Fit" in html
    assert "See TBD" in html


def test_transitional_basho_results_renderer_hides_unprojected_context() -> None:
    html = render_case(
        latest_day=7,
        previous_context=False,
        rating_context=False,
        nu_chii=False,
    )

    assert "Current" in html
    assert "Before Basho" not in html
    assert "before.result.wins" not in html
    assert "\u0394Eq" not in html
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
    changes_context: true,
    rating_context: false,
    analysis_context: false,
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

    assert_cell(result.stdout, "changes.movement.division", "\u2193")

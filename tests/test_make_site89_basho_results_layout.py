from __future__ import annotations

import json
import re
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
MODULE = (
    ROOT
    / "src/products/make_site89/runtime/site-refactor/ui/basho-results-table.js"
)
LAYOUT_MODULE = ROOT / "src/products/make_site89/runtime/site-refactor/ui/layout.js"


def test_basho_result_counts_are_centred_with_hyphen_columns() -> None:
    script = f"""
import {{ buildBashoResultsPresentationModel, renderBashoResultsPresentationTable }} from {json.dumps(MODULE.as_uri())};

const model = buildBashoResultsPresentationModel({{
  rows: [{{
    shikona: "Test Rikishi",
    previous_chii: "M1e",
    previous_result: "10-5",
    chii: "S1e",
    score: "8-6-1",
  }}],
  state: {{
    previous_context: true,
    changes_context: false,
    rating_context: false,
    analysis_context: false,
    nu_chii: false,
  }},
  entry: {{ latest_day: 15 }},
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
    html = result.stdout

    for context in ("before", "selected"):
        for count in ("wins", "losses", "absences"):
            assert re.search(
                rf'data-column-path="{context}\.result\.{count}"[^>]*'
                r'style="text-align: center;"[^>]*'
                r'data-column-role="record-count"',
                html,
            )

        assert (
            f'data-column-path="{context}.result.wins_losses_separator" '
            'style="text-align: center;" '
            'data-column-role="record-separator">-</td>'
        ) in html

    assert (
        'data-column-path="before.result.losses_absences_separator" '
        'style="text-align: center;" '
        'data-column-role="record-separator"></td>'
    ) in html
    assert (
        'data-column-path="selected.result.losses_absences_separator" '
        'style="text-align: center;" '
        'data-column-role="record-separator">-</td>'
    ) in html

    for heading in ("W", "L", "A"):
        assert f'style="text-align: center;"' in html
        assert f'>{heading}<' in html
        assert (
            'class="table-sort-width-reserver" aria-hidden="true" '
            'style="grid-area: 1 / 1; visibility: hidden; white-space: nowrap;">'
            f'{heading}</span>'
        ) in html

    assert html.count("margin: 0; text-align: center;") >= 6


def test_table_width_synchronizer_allows_result_columns_to_use_intrinsic_width() -> None:
    script = f"""
import {{ minimumSyncedColumnWidth }} from {json.dumps(LAYOUT_MODULE.as_uri())};

const widths = [
  minimumSyncedColumnWidth({{ dataset: {{ columnRole: "record-count" }} }}),
  minimumSyncedColumnWidth({{ dataset: {{ columnRole: "record-separator" }} }}),
  minimumSyncedColumnWidth({{ dataset: {{}} }}),
];
console.log(JSON.stringify(widths));
"""
    result = subprocess.run(
        [str(NODE), "--input-type=module", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )

    assert json.loads(result.stdout) == [1, 1, 24]

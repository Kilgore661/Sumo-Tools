from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from src.products.make_site89.manifest.artifacts import FASTEST_RISERS_ARTIFACT
from src.products.make_site89.manifest.builder import build_public_site_shell
from src.products.make_site89.publication_model import build_publication_plan
from src.products.make_site89.site_definition import SITE


ROOT = Path(__file__).resolve().parents[1]
MODEL = (
    ROOT
    / "src/products/make_site89/runtime/site-refactor/ui/fastest-risers/model.js"
)
RENDER = (
    ROOT
    / "src/products/make_site89/runtime/site-refactor/ui/fastest-risers/render.js"
)
NODE = shutil.which("node") or str(
    Path.home()
    / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe"
)


def test_fastest_risers_is_published_after_longest_careers() -> None:
    plan = build_publication_plan(SITE)
    assert plan.pages["fastest_risers"].route.parts == (
        "records",
        "fastest-risers",
    )

    shell = build_public_site_shell(plan)
    records = next(
        item for item in shell.navigation_bar.navigation_tree if item.id == "records"
    )
    ids = [item.id for item in records.children if item.included]
    assert ids.index("fastest_risers") == ids.index("longest_careers") + 1
    fastest = next(item for item in records.children if item.id == "fastest_risers")
    assert fastest.label == "Fastest risers"
    assert fastest.href == (
        "index.html?page=fastest_risers&start=Jk&finish=M&direction=fastest"
        "&range=10&hide_retired=false"
    )


def test_fastest_risers_manifest_declares_specialised_table() -> None:
    shell = build_public_site_shell(build_publication_plan(SITE))
    panel = next(
        panel
        for panel in shell.content_panels
        if panel.page_id == "fastest_risers"
    )
    filters = panel.contents.filter_section.filters

    assert FASTEST_RISERS_ARTIFACT.kind == "table"
    assert FASTEST_RISERS_ARTIFACT.renderer == "fastest_risers_table"
    assert FASTEST_RISERS_ARTIFACT.rows_source.media_type == "application/json"
    assert [filter_.id for filter_ in filters] == [
        "start",
        "finish",
        "direction",
        "ranking_range",
        "hide_retired",
    ]
    assert panel.heading.title == "Fastest and Slowest Risers"
    notes = {note.id: note.text for note in FASTEST_RISERS_ARTIFACT.notes}
    assert "No eligible rikishi first appeared in Jonidan" in notes[
        "fastest_start_choices"
    ]
    assert "destination for Jonokuchi starters" in notes["fastest_start_choices"]


def test_fastest_risers_model_applies_range_before_active_filter() -> None:
    script = f"""
import {{ buildFastestRisersPresentationModel }} from {json.dumps(MODEL.as_uri())};

const record = (id, fastest, slowest, active) => ({{
  rik_id: id,
  shikona: `Rikishi ${{id}}`,
  active,
  fastest_position: fastest,
  slowest_position: slowest,
  elapsed_basho: fastest + 4,
  start_chii: "Jk1e",
  start_chii_ordinal: 900100,
  start_date: "2000/01",
  start_basho_ordinal: 1,
  finish_chii: "M10e",
  finish_chii_ordinal: 401000,
  finish_date: "2001/01",
  finish_basho_ordinal: 7,
}});
const ranked = Array.from({{ length: 11 }}, (_, index) => {{
  const position = index + 1;
  return record(position, position, 12 - position, position === 2 || position === 11);
}});
const data = {{ routes: {{
  "Jk:M": {{ start_group: "Jk", finish_group: "M", starter_count: 20, reached_count: 11, not_reached_count: 9, records: ranked }},
  "Jk:Y": {{ start_group: "Jk", finish_group: "Y", starter_count: 20, reached_count: 0, not_reached_count: 20, records: [] }},
  "Ms:M": {{ start_group: "Ms", finish_group: "M", starter_count: 2, reached_count: 1, not_reached_count: 1, records: [record(4, 1, 1, true)] }},
}} }};
const model = buildFastestRisersPresentationModel(data, {{
  start: "Jk", finish: "M", direction: "fastest", ranking_range: "10", hide_retired: true,
}});
console.log(JSON.stringify(model));
"""
    result = subprocess.run(
        [NODE, "--input-type=module", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    model = json.loads(result.stdout)

    assert model["available_starts"] == ["Jk", "Ms"]
    assert model["available_finishes"] == ["M", "Y"]
    assert [row["rik_id"] for row in model["values"]] == [2]
    assert model["values"][0]["position"] == 2
    assert model["header"]["heading"] == (
        "Fastest promotions from Jonokuchi to Maegashira"
    )
    assert model["header"]["subheading"] == (
        "Showing 1 active rikishi among the first 10 of 11 who reached "
        "Maegashira, from 20 Jonokuchi starters."
    )


def test_fastest_risers_renderer_groups_columns_and_preserves_position() -> None:
    artifact = {
        "id": "fastest_risers",
        "default_sort_column": "position",
        "columns": [
            {"id": "position", "heading": "#", "source_field": "position", "sort_kind": "numeric", "sort_default_direction": "ascending", "align": "right"},
            {"id": "shikona", "heading": "Shikona", "source_field": "shikona", "sort_kind": "text", "align": "left"},
            {"id": "start_chii", "heading": "Chii", "source_field": "start_chii", "sort_key": "start_chii_ordinal", "sort_kind": "chii_ordinal", "align": "left"},
            {"id": "start_date", "heading": "Basho", "source_field": "start_date", "sort_kind": "text", "align": "left"},
            {"id": "finish_chii", "heading": "Chii", "source_field": "finish_chii", "sort_key": "finish_chii_ordinal", "sort_kind": "chii_ordinal", "align": "left"},
            {"id": "finish_date", "heading": "Basho", "source_field": "finish_date", "sort_kind": "text", "align": "left"},
            {"id": "elapsed_basho", "heading": "Elapsed Basho", "source_field": "elapsed_basho", "sort_kind": "numeric", "align": "right"},
        ],
    }
    model = {
        "header": {"heading": "Fastest promotions", "subheading": "Cohort context."},
        "empty_message": "No records.",
        "values": [
            {
                "position": 7,
                "rik_id": 12717,
                "shikona": "Oshoma",
                "start_chii": "Ms15eTD",
                "start_chii_ordinal": 601540,
                "start_date": "2021/11",
                "finish_chii": "M14w",
                "finish_chii_ordinal": 401401,
                "finish_date": "2024/05",
                "elapsed_basho": 15,
            }
        ],
    }
    script = f"""
import {{ renderFastestRisersTable }} from {json.dumps(RENDER.as_uri())};
console.log(renderFastestRisersTable({json.dumps(artifact)}, {json.dumps(model)}));
"""
    result = subprocess.run(
        [NODE, "--input-type=module", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    html = result.stdout

    assert 'class="artifact-table fastest-risers-table"' in html
    assert 'colspan="2" data-group-start="true" data-heading-group="true">Start<' in html
    assert ">Destination<" in html
    assert ">7<" in html
    assert "Oshoma" in html
    assert "Ms15eTD" in html
    assert "15" in html

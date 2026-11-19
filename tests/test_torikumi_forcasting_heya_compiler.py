import csv
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.analysis.torikumi_forcasting.heya import load_heya_index
from src.analysis.torikumi_forcasting.heya_compiler import (
    compile_heya_index,
    write_compilation,
)
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date


def test_compiles_consensus_heya_by_basho_and_loads_typed_index(tmp_path: Path) -> None:
    root = tmp_path / "HTML results"
    _write_day(
        root,
        "1992 11",
        4,
        _link(2, "貴花田, Fujishima, Tokyo, 12.08.1972")
        + _link(2, "貴花田, Fujishima, Tokyo, 12.08.1972")
        + _link(3, "誰か, Stable, U.S.A., Hawaii, Oahu"),
    )
    _write_day(
        root,
        "1992 11",
        5,
        _link(2, "貴花田, Fujishima, Tokyo, 12.08.1972"),
    )
    _write_day(
        root,
        "1993 03",
        5,
        _link(2, "貴ノ花, Futagoyama, Tokyo, 12.08.1972"),
    )

    compilation = compile_heya_index(root)

    assert compilation.source_file_count == 3
    assert compilation.observation_count == 5
    assert compilation.first_basho == "1992/11"
    assert compilation.last_basho == "1993/03"
    assert compilation.diagnostics == ()
    assert [
        (row.basho, row.rikid, row.heya, row.observed_days, row.observation_count)
        for row in compilation.records
    ] == [
        ("1992/11", 2, "Fujishima", (4, 5), 3),
        ("1992/11", 3, "Stable", (4,), 1),
        ("1993/03", 2, "Futagoyama", (5,), 1),
    ]

    output = tmp_path / "heya_index.json"
    diagnostics = tmp_path / "diagnostics.csv"
    write_compilation(
        compilation,
        output_path=output,
        diagnostics_path=diagnostics,
        html_results_root=root,
        generated_at=datetime(2026, 11, 19, tzinfo=timezone.utc),
    )
    index = load_heya_index(output)

    assert index.heya_at(Date.from_ints(1992, 11), RikId(2)) == "Fujishima"
    assert index.heya_at(Date.from_ints(1993, 3), RikId(2)) == "Futagoyama"
    assert index.heya_at(Date.from_ints(1992, 11), RikId(999)) is None
    assert list(csv.DictReader(diagnostics.open(encoding="utf-8"))) == []


def test_reports_malformed_and_blank_heya_without_inventing_records(tmp_path: Path) -> None:
    root = tmp_path / "HTML results"
    _write_day(
        root,
        "2026 11",
        1,
        _link(1, "headword only") + _link(2, "headword, , Tokyo"),
    )

    compilation = compile_heya_index(root)

    assert compilation.records == ()
    assert [row.kind for row in compilation.diagnostics] == [
        "malformed_title",
        "blank_heya",
    ]


def test_within_basho_conflict_writes_diagnostics_and_refuses_index(tmp_path: Path) -> None:
    root = tmp_path / "HTML results"
    _write_day(root, "1992 11", 4, _link(2, "name, Fujishima, Tokyo"))
    _write_day(root, "1992 11", 5, _link(2, "name, Futagoyama, Tokyo"))
    compilation = compile_heya_index(root)
    output = tmp_path / "heya_index.json"
    diagnostics = tmp_path / "diagnostics.csv"

    with pytest.raises(ValueError, match="within-basho conflicts"):
        write_compilation(
            compilation,
            output_path=output,
            diagnostics_path=diagnostics,
            html_results_root=root,
        )

    assert not output.exists()
    rows = list(csv.DictReader(diagnostics.open(encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["kind"] == "conflicting_heya"
    assert rows[0]["values"] == "Fujishima | Futagoyama"


def test_date_range_limits_compilation(tmp_path: Path) -> None:
    root = tmp_path / "HTML results"
    _write_day(root, "1992 11", 1, _link(2, "name, Fujishima, Tokyo"))
    _write_day(root, "1993 03", 1, _link(2, "name, Futagoyama, Tokyo"))

    compilation = compile_heya_index(root, start="1993/03", end="1993/03")

    assert [(row.basho, row.heya) for row in compilation.records] == [
        ("1993/03", "Futagoyama")
    ]


def _write_day(root: Path, basho: str, day: int, body: str) -> None:
    path = root / basho / f"{day:02d}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"<html><body>{body}</body></html>", encoding="utf-8")


def _link(rikid: int, title: str) -> str:
    return f"<a title='{title}' href='Rikishi.aspx?r={rikid}'>rikishi</a>"

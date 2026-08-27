"""Contracts for literal-chii Rikishi.aspx record availability."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.analysis.bout_data_completeness import __main__ as cli
from src.analysis.bout_data_completeness.analysis import analyse_availability
from src.analysis.bout_data_completeness.model import SourceIdentity
from src.analysis.bout_data_completeness.output import write_outputs
from src.analysis.bout_data_completeness.source import parse_hoshi_records
from src.infra.get_bios.api import BioBashoDate
from src.sumo_core.BasicPrimitives import Month, RikId, Riks, Shikona, Year
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_hoshi_parser_distinguishes_empty_from_non_empty_fields() -> None:
    records = parse_hoshi_records(
        page_html(
            {
                "195801": (),
                "195803": complete_symbols(),
            }
        ),
        rikishi_id=4203,
    )

    assert records["1958/01"].recorded is False
    assert records["1958/01"].complete is False
    assert records["1958/01"].known_symbol_count == 0
    assert records["1958/01"].empty_symbol_count == 0
    assert records["1958/03"].recorded is True
    assert records["1958/03"].complete is True
    assert records["1958/03"].known_symbol_count == 15
    assert records["1958/03"].empty_symbol_count == 0


def test_hoshi_parser_treats_hoshi_empty_as_missing_day_records() -> None:
    symbols = (
        "hoshi_shiro",
        "hoshi_kuro",
        "hoshi_kuro",
        *("hoshi_yasumi",) * 4,
        *("hoshi_empty",) * 8,
    )
    record = parse_hoshi_records(
        page_html({"197301": symbols}),
        rikishi_id=8063,
    )["1973/01"]

    assert record.recorded is True
    assert record.complete is False
    assert record.known_symbol_count == 7
    assert record.empty_symbol_count == 8
    assert record.slot_count == 15


def test_hoshi_parser_requires_exactly_fifteen_known_symbols() -> None:
    short = parse_hoshi_records(
        page_html({"197301": ("hoshi_yasumi",) * 7}),
        rikishi_id=8063,
    )["1973/01"]

    assert short.recorded is True
    assert short.complete is False
    assert short.known_symbol_count == 7
    assert short.empty_symbol_count == 0
    assert short.slot_count == 7


def test_hoshi_parser_rejects_more_than_fifteen_slots() -> None:
    with pytest.raises(ValueError, match="16 hoshi slots; expected at most 15"):
        parse_hoshi_records(
            page_html({"197301": ("hoshi_yasumi",) * 16}),
            rikishi_id=8063,
        )


def test_hoshi_parser_ignores_html_retirement_presentation_class() -> None:
    records = parse_hoshi_records(
        page_html({"202305": ()}, retired={"202305"}),
        rikishi_id=12107,
    )

    assert records["2023/05"].recorded is False
    assert not hasattr(records["2023/05"], "retired")


def test_hoshi_parser_rejects_dated_row_without_hoshi_cell() -> None:
    html = "<table><tr><td><a href='Banzuke.aspx?b=195801'>1958.01</a></td></tr></table>"

    with pytest.raises(ValueError, match="has no hoshi cell"):
        parse_hoshi_records(html, rikishi_id=4203)


def test_analysis_uses_actual_literal_chii_and_classifies_division_status(tmp_path) -> None:
    first = date(1958, 1)
    second = date(1958, 3)
    third = date(1958, 5)
    history = History(
        {
            first: basho({1: "Ms1e", 2: "Ms1w"}),
            second: basho({1: "Ms1e", 2: "Ms1w"}),
            third: basho({1: "Ms1e", 3: "Ms2eHD"}),
        }
    )
    bio_dir = tmp_path / "rikishi"
    bio_dir.mkdir()
    write_page(
        bio_dir,
        1,
        {
            "195801": (),
            "195803": complete_symbols("hoshi_shiro"),
            "195805": complete_symbols("hoshi_kuro"),
        },
    )
    write_page(
        bio_dir,
        2,
        {"195801": (), "195803": ()},
    )
    write_page(
        bio_dir,
        3,
        {"195805": complete_symbols("hoshi_yasumi")},
    )

    audit = analyse_availability(
        history,
        history_source=SourceIdentity("fixture.zip", "abc", 1),
        bio_store_source=SourceIdentity("bios.json", "def", 1, "bio_store"),
        intai_by_rikishi={RikId(1): None, RikId(2): None, RikId(3): None},
        bio_dir=bio_dir,
        start=(1958, 1),
        end=(1958, 5),
    )

    assert [(row.basho, row.status) for row in audit.basho_division_rows] == [
        ("1958/01", "none"),
        ("1958/03", "partial"),
        ("1958/05", "complete"),
    ]
    partial = audit.basho_division_rows[1]
    assert partial.expected_day_records == 30
    assert partial.known_day_records == 15
    assert partial.missing_day_records == 15
    assert partial.missing_day_record_percentage == 50.0
    assert partial.known_day_record_percentage == 50.0
    annotated = next(row for row in audit.chii_rows if row.rikishi_id == 3)
    assert annotated.chii == "Ms2eHD"
    assert annotated.recorded is True
    assert annotated.complete is True

    summary = audit.division_summary_rows[0]
    assert summary.first_basho_with_any_recorded_chii == "1958/03"
    assert summary.first_basho_with_complete_records == "1958/05"
    assert summary.last_basho_with_incomplete_records == "1958/03"
    assert summary.continuous_complete_coverage_begins == "1958/05"
    assert summary.basho_with_no_records == 1
    assert summary.basho_with_partial_records == 1
    assert summary.basho_with_complete_records == 1
    assert summary.pre_1989_partial_expected_day_records == 30
    assert summary.pre_1989_partial_missing_day_records == 15
    assert summary.pre_1989_partial_missing_day_record_percentage == 50.0
    assert summary.pre_1989_partial_known_day_record_percentage == 50.0
    assert summary.all_partial_expected_day_records == 30
    assert summary.all_partial_missing_day_records == 15


def test_output_contract_writes_the_three_agreed_csvs(tmp_path) -> None:
    selected_date = date(1958, 1)
    history = History({selected_date: basho({1: "Ms1e"})})
    bio_dir = tmp_path / "rikishi"
    bio_dir.mkdir()
    write_page(bio_dir, 1, {"195801": complete_symbols("hoshi_shiro")})
    audit = analyse_availability(
        history,
        history_source=SourceIdentity("fixture.zip", "abc", 1),
        bio_store_source=SourceIdentity("bios.json", "def", 1, "bio_store"),
        intai_by_rikishi={RikId(1): None},
        bio_dir=bio_dir,
        start=(1958, 1),
        end=(1958, 1),
    )

    outputs = write_outputs(audit, output_root=tmp_path / "output")

    assert outputs.chii_csv.name == "basho_chii_record_availability.csv"
    assert outputs.basho_division_csv.name == "basho_division_record_availability.csv"
    assert outputs.division_summary_csv.name == "division_record_availability_summary.csv"
    with outputs.chii_csv.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["chii"] == "Ms1e"
    assert rows[0]["recorded"] == "True"
    assert rows[0]["complete"] == "True"
    findings = outputs.findings_md.read_text(encoding="utf-8")
    assert (
        "| Division | First any | Last incomplete | First complete | "
        "Continuous complete from |" in findings
    )
    assert "## Density within partial basho" in findings


def test_biostore_intai_empty_row_does_not_make_division_incomplete(
    tmp_path,
) -> None:
    selected_date = date(2023, 5)
    history = History({selected_date: basho({12107: "M13w"})})
    bio_dir = tmp_path / "rikishi"
    bio_dir.mkdir()
    write_page(bio_dir, 12107, {"202305": ()})

    audit = analyse_availability(
        history,
        history_source=SourceIdentity("fixture.zip", "abc", 1),
        bio_store_source=SourceIdentity("bios.json", "def", 1, "bio_store"),
        intai_by_rikishi={RikId(12107): BioBashoDate(2023, 5)},
        bio_dir=bio_dir,
        start=(2023, 5),
        end=(2023, 5),
    )

    atomic = audit.chii_rows[0]
    division = audit.basho_division_rows[0]
    assert atomic.recorded is False
    assert atomic.complete is False
    assert atomic.retired is True
    assert division.chii_with_any_records == 0
    assert division.chii_complete_records == 0
    assert division.chii_without_records == 1
    assert division.chii_retired_incomplete == 1
    assert division.chii_missing == 0
    assert division.expected_day_records == 0
    assert division.missing_day_records == 0
    assert division.status == "complete"


def test_history_loader_prefers_available_live_store(tmp_path, monkeypatch) -> None:
    name_file = tmp_path / "store_name.txt"
    name_file.write_text("history-test", encoding="utf-8")
    expected = History({date(1958, 1): basho({1: "Ms1e"})})
    monkeypatch.setattr(cli, "published_name_file", lambda: name_file)
    monkeypatch.setattr(cli, "get_history", lambda: expected)

    actual, source = cli.load_history(None)

    assert actual is expected
    assert source.kind == "live_store"
    assert source.path == str(name_file.resolve())


def test_history_loader_falls_back_when_published_store_is_stale(
    tmp_path, monkeypatch
) -> None:
    name_file = tmp_path / "store_name.txt"
    name_file.write_text("stale-store", encoding="utf-8")
    fallback = tmp_path / "fallback.zip"
    fallback.write_bytes(b"fixture")
    expected = History({date(1958, 1): basho({1: "Ms1e"})})
    monkeypatch.setattr(cli, "published_name_file", lambda: name_file)
    monkeypatch.setattr(
        cli,
        "get_history",
        lambda: (_ for _ in ()).throw(SystemExit("stale shared memory")),
    )
    monkeypatch.setattr(cli, "load_history_with_annotations", lambda _: expected)
    monkeypatch.setattr(cli, "DEFAULT_HISTORY_ZIP", fallback)

    actual, source = cli.load_history(None)

    assert actual is expected
    assert source.kind == "history_zip"
    assert source.path == str(fallback.resolve())


def date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))


def basho(positions: dict[int, str]) -> BashoState:
    rikchii = RikChii(
        {RikId(rikishi_id): Chii.from_str(chii) for rikishi_id, chii in positions.items()}
    )
    riks = Riks(rikchii)
    return BashoState(
        banzuke=Banzuke(
            riks=riks,
            rikchii=rikchii,
            rikshik=RikShikona(
                {rikishi_id: Shikona(str(int(rikishi_id))) for rikishi_id in riks}
            ),
        ),
        summary=Summary({}),
    )


def write_page(
    directory: Path,
    rikishi_id: int,
    records: dict[str, tuple[str, ...]],
    *,
    retired: set[str] | None = None,
) -> None:
    (directory / f"{rikishi_id:05d}.html").write_text(
        page_html(records, retired=retired),
        encoding="utf-8",
    )


def page_html(
    records: dict[str, tuple[str, ...]],
    *,
    retired: set[str] | None = None,
) -> str:
    retired = retired or set()
    rows = []
    for yyyymm, symbols in records.items():
        images = "".join(f'<img src="img/{symbol}.gif">' for symbol in symbols)
        rank_cell = '<td class="retired">Ms1e</td>' if yyyymm in retired else ""
        rows.append(
            "<tr>"
            f"<td><a href='Banzuke.aspx?b={yyyymm}'>{yyyymm}</a></td>"
            f"{rank_cell}"
            f'<td class="hoshi">{images}</td>'
            "</tr>"
        )
    return "<html><table class=\"rikishi\">" + "".join(rows) + "</table></html>"


def complete_symbols(symbol: str = "hoshi_yasumi") -> tuple[str, ...]:
    return (symbol,) * 15

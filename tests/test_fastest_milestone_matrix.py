from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from types import MappingProxyType

import pytest

from src.analysis.fastest.__main__ import build_parser
from src.analysis.fastest.milestone_matrix import (
    GROUPS,
    matrix_fieldnames,
    produce_milestone_matrix,
    rank_group,
)
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.get_bios.api import BioStore
from src.sumo_core.BasicPrimitives import Month, RikId, Riks, Shikona, Year
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))


def _state(entries: dict[int, tuple[str, str]]) -> BashoState:
    chii = {RikId(rik_id): Chii.from_str(rank) for rik_id, (_, rank) in entries.items()}
    shikona = {
        RikId(rik_id): Shikona(name) for rik_id, (name, _) in entries.items()
    }
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(chii),
            rikchii=RikChii(chii),
            rikshik=RikShikona(shikona),
        ),
        summary=Summary({}),
    )


def _fixture_history() -> History:
    return History(
        {
            _date(1958, 1): _state({1: ("Boundary", "Jd10e")}),
            _date(1958, 3): _state(
                {
                    1: ("Boundary", "Sd90e"),
                    2: ("Climber", "Jk20e"),
                    3: ("NoBio", "Jk21e"),
                    4: ("Peer", "Jk22e"),
                }
            ),
            _date(1958, 5): _state(
                {
                    2: ("Climber", "Jd100e"),
                    3: ("NoBio", "Jd101e"),
                    4: ("Peer", "Jd102e"),
                }
            ),
        }
    )


def test_cli_defaults_to_site89_proof_of_concept_epoch() -> None:
    args = build_parser().parse_args([])
    assert str(args.epoch) == "1989/01"


def test_writes_matrix_rankings_and_runtime_missing_bio_audit(tmp_path: Path) -> None:
    history = _fixture_history()
    bios = BioStore(
        MappingProxyType(
            {RikId(1): object(), RikId(2): object(), RikId(4): object()}
        )
    )
    names = FullShikonaStore(
        MappingProxyType(
            {RikId(1): "Boundary", RikId(2): "Climber", RikId(4): "Peer"}
        )
    )
    warnings = io.StringIO()

    outputs = produce_milestone_matrix(
        history,
        epoch=_date(1958, 1),
        output_root=tmp_path,
        bios=bios,
        shikona_store=names,
        warning_stream=warnings,
    )

    with outputs.matrix_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert reader.fieldnames == matrix_fieldnames()
    assert len(reader.fieldnames) == 38
    assert outputs.row_count == 3
    assert [row["rik_id"] for row in rows] == ["1", "2", "4"]

    boundary, climber, _ = rows
    assert boundary["Jd_chii"] == "Jd10e"
    assert boundary["Jd_chii_ordinal"] == str(Chii.from_str("Jd10e").ordinal())
    assert boundary["Jd_date"] == "1958/01"
    assert boundary["Jd_basho_ordinal"] == "1"
    assert boundary["Sd_date"] == "1958/03"
    assert boundary["Sd_basho_ordinal"] == "2"
    assert climber["Jk_chii"] == "Jk20e"
    assert climber["Jk_chii_ordinal"] == str(Chii.from_str("Jk20e").ordinal())
    assert climber["Jd_chii"] == "Jd100e"
    assert climber["Jd_date"] == "1958/05"
    assert climber["Jd_basho_ordinal"] == "3"
    assert climber["Sd_chii"] == ""
    assert climber["Sd_chii_ordinal"] == ""
    assert climber["Sd_date"] == ""
    assert climber["Sd_basho_ordinal"] == ""

    with outputs.missing_bios_csv.open(newline="", encoding="utf-8") as handle:
        missing = list(csv.DictReader(handle))
    assert missing == [
        {
            "rik_id": "3",
            "shikona": "NoBio",
            "chii": "Jk21e",
            "chii_ordinal": str(Chii.from_str("Jk21e").ordinal()),
            "date": "1958/03",
            "basho_ordinal": "2",
            "reason": "missing_bio",
        }
    ]
    assert outputs.missing_bio_count == 1
    warning = warnings.getvalue()
    assert warning.count("WARNING: missing bio") == 1
    assert "rik_id=3" in warning
    assert "shikona=NoBio" in warning
    assert "chii=Jk21e" in warning
    assert "date=1958/03" in warning
    assert "basho_ordinal=2" in warning

    rankings = json.loads(outputs.rankings_json.read_text(encoding="utf-8"))
    assert rankings["history"] == {
        "start": "1958/01",
        "end": "1958/05",
        "basho_count": 3,
        "basho_ordinal_base": 1,
    }
    route = rankings["routes"]["Jk:Jd"]
    assert route["starter_count"] == 2
    assert route["reached_count"] == 2
    assert route["not_reached_count"] == 0
    assert len(route["records"]) == 2
    assert [row["fastest_position"] for row in route["records"]] == [1, 2]
    assert [row["slowest_position"] for row in route["records"]] == [1, 2]
    assert route["records"][0]["elapsed_basho"] == 1
    assert route["records"][0]["active"] is True
    assert route["records"][0]["start_basho_ordinal"] == 2
    assert route["records"][0]["finish_basho_ordinal"] == 3


def test_ranking_active_means_present_on_latest_banzuke(tmp_path: Path) -> None:
    history = History(
        {
            _date(1958, 1): _state({1: ("Boundary", "Jd10e")}),
            _date(1958, 3): _state(
                {
                    2: ("Current", "Jk20e"),
                    3: ("Retired", "Jk21e"),
                }
            ),
            _date(1958, 5): _state(
                {
                    2: ("Current", "Jd100e"),
                    3: ("Retired", "Jd101e"),
                }
            ),
            _date(1958, 7): _state({2: ("Current", "Sd90e")}),
        }
    )
    bios = BioStore(
        MappingProxyType(
            {RikId(1): object(), RikId(2): object(), RikId(3): object()}
        )
    )
    names = FullShikonaStore(
        MappingProxyType(
            {RikId(1): "Boundary", RikId(2): "Current", RikId(3): "Retired"}
        )
    )

    outputs = produce_milestone_matrix(
        history,
        epoch=_date(1958, 1),
        output_root=tmp_path,
        bios=bios,
        shikona_store=names,
    )

    rankings = json.loads(outputs.rankings_json.read_text(encoding="utf-8"))
    records = rankings["routes"]["Jk:Jd"]["records"]
    assert {row["shikona"]: row["active"] for row in records} == {
        "Current": True,
        "Retired": False,
    }


def test_every_chii_column_is_immediately_followed_by_ordinal() -> None:
    fields = matrix_fieldnames()
    for group in GROUPS:
        chii_index = fields.index(f"{group}_chii")
        assert fields[chii_index + 1] == f"{group}_chii_ordinal"


@pytest.mark.parametrize(
    ("chii", "expected"),
    (
        ("Jk1e", "Jk"),
        ("Jd1e", "Jd"),
        ("Sd1e", "Sd"),
        ("Ms1e", "Ms"),
        ("J1e", "J"),
        ("M1e", "M"),
        ("K1e", "KS"),
        ("S1e", "KS"),
        ("O1e", "O"),
        ("Y1e", "Y"),
    ),
)
def test_rank_group(chii: str, expected: str) -> None:
    assert rank_group(Chii.from_str(chii)) == expected


def test_rejects_history_that_does_not_represent_epoch(tmp_path: Path) -> None:
    history = History({_date(1989, 1): _state({1: ("Late", "Jk1e")})})
    with pytest.raises(ValueError, match="epoch to be a represented banzuke"):
        produce_milestone_matrix(
            history,
            epoch=_date(1958, 1),
            output_root=tmp_path,
        )


def test_epoch_discards_earlier_history_and_excludes_epoch_incumbents(
    tmp_path: Path,
) -> None:
    class AlternateDate(Date):
        pass

    history = History(
        {
            _date(1958, 1): _state({1: ("Old", "Jk1e")}),
            AlternateDate(Year(1989), Month(1)): _state({1: ("Old", "M1e")}),
            _date(1989, 3): _state({2: ("New", "Jk1e")}),
            _date(1989, 5): _state({2: ("New", "Jd1e")}),
        }
    )
    bios = BioStore(MappingProxyType({RikId(1): object(), RikId(2): object()}))
    names = FullShikonaStore(
        MappingProxyType({RikId(1): "Old", RikId(2): "New"})
    )

    outputs = produce_milestone_matrix(
        history,
        epoch=_date(1989, 1),
        output_root=tmp_path,
        bios=bios,
        shikona_store=names,
    )

    rankings = json.loads(outputs.rankings_json.read_text(encoding="utf-8"))
    assert rankings["history"] == {
        "start": "1989/01",
        "end": "1989/05",
        "basho_count": 3,
        "basho_ordinal_base": 1,
    }
    assert rankings["routes"]["Jk:Jd"]["starter_count"] == 1
    assert rankings["routes"]["Jk:Jd"]["records"][0]["shikona"] == "New"

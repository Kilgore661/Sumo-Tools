from __future__ import annotations

import csv
from datetime import date
from types import MappingProxyType

from src.analysis.ages.birth_date_coverage import (
    birth_date_coverage_by_basho,
    write_birth_date_coverage_csv,
)
from src.infra.get_bios.api import BioStore, BirthDate, RikishiBio
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_counts_exact_missing_and_absent_bios_for_every_basho(tmp_path) -> None:
    history = History(
        {
            Date.from_ints(2000, 1): _state({1: "M1e", 2: "J1e", 3: "Jk1e"}),
            Date.from_ints(2000, 3): _state({1: "M1w", 3: "Jk1w", 4: "Jk2e"}),
        }
    )
    bios = BioStore(
        MappingProxyType(
            {
                RikId(1): _bio(1, date(1970, 1, 1)),
                RikId(2): _bio(2, None),
                RikId(4): _bio(4, date(1980, 2, 3)),
            }
        )
    )

    rows = birth_date_coverage_by_basho(history, bios)

    assert [row.basho for row in rows] == ["2000/01", "2000/03"]
    assert rows[0].banzuke_rikishi == 3
    assert rows[0].exact_birth_date == 1
    assert rows[0].missing_exact_birth_date == 2
    assert rows[0].missing_bio == 1
    assert rows[0].bio_without_exact_birth_date == 1
    assert rows[1].banzuke_rikishi == 3
    assert rows[1].exact_birth_date == 2
    assert rows[1].missing_exact_birth_date == 1
    assert rows[1].missing_bio == 1
    assert rows[1].bio_without_exact_birth_date == 0

    output = tmp_path / "coverage.csv"
    write_birth_date_coverage_csv(rows, output)
    with output.open(newline="", encoding="utf-8") as stream:
        written = list(csv.DictReader(stream))
    assert written[0] == {
        "basho": "2000/01",
        "banzuke_rikishi": "3",
        "exact_birth_date": "1",
        "missing_exact_birth_date": "2",
        "missing_bio": "1",
        "bio_without_exact_birth_date": "1",
    }


def test_empty_history_writes_header_only(tmp_path) -> None:
    rows = birth_date_coverage_by_basho(
        History({}),
        BioStore(MappingProxyType({})),
    )
    output = tmp_path / "coverage.csv"
    write_birth_date_coverage_csv(rows, output)

    assert rows == ()
    assert output.read_text(encoding="utf-8").splitlines() == [
        "basho,banzuke_rikishi,exact_birth_date,missing_exact_birth_date,missing_bio,bio_without_exact_birth_date"
    ]


def _state(ranks: dict[int, str]) -> BashoState:
    chii = {
        RikId(rikishi_id): Chii.from_str(rank)
        for rikishi_id, rank in ranks.items()
    }
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(chii),
            rikchii=RikChii(chii),
            rikshik=RikShikona(
                {
                    rikishi_id: Shikona(f"Rikishi {int(rikishi_id)}")
                    for rikishi_id in chii
                }
            ),
        ),
        summary=Summary({}),
    )


def _bio(rikishi_id: int, birth_date: date | None) -> RikishiBio:
    return RikishiBio(
        rikid=RikId(rikishi_id),
        birth_date=None if birth_date is None else BirthDate(birth_date),
        shusshin="",
        heya=(),
        shikona_history=(),
        hatsu_dohyo=None,
        intai=None,
        height_cm=None,
        weight_kg=None,
        height_history=(),
        weight_history=(),
    )

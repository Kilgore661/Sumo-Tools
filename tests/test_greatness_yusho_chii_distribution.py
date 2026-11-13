from __future__ import annotations

import csv

from src.analysis.greatness.yusho_chii_distribution import (
    CHII_GROUPS,
    write_distribution_csv,
    yusho_chii_distribution,
)
from src.sumo_core.BasicEnums import Prize
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Performance import Performance, Performances
from src.sumo_core.Summary import Summary


def test_distribution_groups_makuuchi_yusho_and_includes_zero_rows() -> None:
    history = _history(
        {
            1: ("Y2wHD", True),
            2: ("O1e", True),
            3: ("S1w", False),
            4: ("M3e", True),
            5: ("M3w", True),
            6: ("J1e", True),
        }
    )

    rows = yusho_chii_distribution(history)
    by_group = {row.chii_group: row for row in rows}

    assert tuple(row.chii_group for row in rows[:-1]) == CHII_GROUPS
    assert rows[-1].chii_group == "Total"
    assert rows[-1].yusho == 4
    assert rows[-1].share_percent == 100.0
    assert by_group["Y"].yusho == 1
    assert by_group["O"].share_percent == 25.0
    assert by_group["M3"].yusho == 2
    assert by_group["M3"].share_percent == 50.0
    assert by_group["S"].yusho == 0
    assert by_group["M17"].yusho == 0


def test_write_distribution_csv(tmp_path) -> None:
    rows = yusho_chii_distribution(_history({1: ("K1e", True)}))
    output = tmp_path / "nested" / "distribution.csv"

    write_distribution_csv(rows, output)

    with output.open(newline="", encoding="utf-8") as stream:
        written = list(csv.DictReader(stream))
    assert written[0] == {
        "chii_group": "Y",
        "yusho": "0",
        "share_percent": "0.0",
    }
    assert written[3] == {
        "chii_group": "K",
        "yusho": "1",
        "share_percent": "100.0",
    }
    assert written[-1] == {
        "chii_group": "Total",
        "yusho": "1",
        "share_percent": "100.0",
    }


def _history(entries: dict[int, tuple[str, bool]]) -> History:
    chii = {
        RikId(rikishi_id): Chii.from_str(rank)
        for rikishi_id, (rank, _) in entries.items()
    }
    performances = Performances(
        {
            RikId(rikishi_id): Performance(
                prizes=frozenset({Prize.YUSHO}) if is_yusho else frozenset()
            )
            for rikishi_id, (_, is_yusho) in entries.items()
        }
    )
    return History(
        {
            Date.from_ints(2020, 1): BashoState(
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
                summary=Summary({}, performances),
            )
        }
    )

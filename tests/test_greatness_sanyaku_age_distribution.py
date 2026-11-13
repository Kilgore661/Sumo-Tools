from __future__ import annotations

import csv
from datetime import date
from types import MappingProxyType

from src.analysis.greatness.sanyaku_age_distribution import (
    analyse_sanyaku_ages,
    write_outputs,
)
from src.infra.get_bios.api import (
    BioBashoDate,
    BioStore,
    BirthDate,
    RikishiBio,
    ShikonaUse,
)
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_age_distribution_and_strict_probability_tail() -> None:
    history = History(
        {
            Date.from_ints(2000, 1): _state({1: "Y1e"}),
            Date.from_ints(2000, 3): _state({2: "M1e", 3: "M2e", 4: "M3e"}),
            Date.from_ints(2001, 3): _state({2: "K1e", 3: "M1e", 4: "S1e"}),
            Date.from_ints(2002, 3): _state({3: "O1e"}),
        }
    )
    bios = BioStore(
        MappingProxyType(
            {
                RikId(1): _bio(1, date(1970, 1, 1)),
                RikId(2): _bio(2, date(1981, 3, 1)),
                RikId(3): _bio(3, date(1980, 3, 2)),
                RikId(4): _bio(4, None),
            }
        )
    )

    result = analyse_sanyaku_ages(history, bios)

    assert result.complete_record_rikishi == 3
    assert result.reached_sanyaku == 3
    assert result.sanyaku_missing_birth_date == 1
    assert [row.age for row in result.records] == [20, 21]
    assert [(row.age, row.rikishi) for row in result.distribution] == [(20, 1), (21, 1)]
    assert [
        (
            row.age_threshold,
            row.rikishi_becoming_sanyaku_after_age,
            row.probability,
        )
        for row in result.probability_after_age
    ] == [(19, 2, 1.0), (20, 1, 0.5), (21, 0, 0.0)]


def test_write_outputs(tmp_path) -> None:
    history = History(
        {
            Date.from_ints(2000, 1): _state({1: "M1e"}),
            Date.from_ints(2000, 3): _state({2: "K1e"}),
        }
    )
    analysis = analyse_sanyaku_ages(
        history,
        BioStore(MappingProxyType({RikId(2): _bio(2, date(1980, 1, 1))})),
    )

    write_outputs(analysis, tmp_path)

    with (tmp_path / "probability_after_age.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert rows[-1]["rikishi_becoming_sanyaku_after_age"] == "0"
    assert rows[-1]["probability"] == "0.0"


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


def _bio(rikishi_id: int, birth: date | None) -> RikishiBio:
    return RikishiBio(
        rikid=RikId(rikishi_id),
        birth_date=None if birth is None else BirthDate(birth),
        shusshin="",
        heya=(),
        shikona_history=(
            ShikonaUse(BioBashoDate(2000, 1), Shikona(f"Rikishi {rikishi_id}")),
        ),
        hatsu_dohyo=None,
        intai=None,
        height_cm=None,
        weight_kg=None,
        height_history=(),
        weight_history=(),
    )

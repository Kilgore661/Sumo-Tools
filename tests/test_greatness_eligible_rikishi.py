from __future__ import annotations

from datetime import date
from types import MappingProxyType

import pytest

from src.analysis.greatness.eligible_rikishi import (
    count_eligible_rikishi,
    parse_date,
)
from src.infra.get_bios.api import BioStore, BirthDate, RikishiBio
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_count_excludes_boundary_incumbents_and_counts_sanyaku_birth_dates() -> None:
    history = History(
        {
            Date.from_ints(1958, 1): _state({1: "Y1e", 2: "M1e"}),
            Date.from_ints(1958, 3): _state(
                {1: "Y1e", 3: "Jk1e", 4: "Jk1w", 5: "Jk2e"}
            ),
            Date.from_ints(1958, 5): _state(
                {3: "K1e", 4: "S1e", 5: "M1e", 6: "O1e"}
            ),
        }
    )
    bios = BioStore(
        MappingProxyType(
            {
                RikId(1): _bio(1, date(1930, 1, 1)),
                RikId(3): _bio(3, date(1940, 1, 1)),
                RikId(4): _bio(4, None),
                RikId(5): _bio(5, date(1942, 1, 1)),
            }
        )
    )

    result = count_eligible_rikishi(history, bios)

    assert str(result.epoch) == "1958/01"
    assert result.observed_rikishi == 6
    assert result.boundary_incumbents == 2
    assert result.complete_record_rikishi == 4
    assert result.reached_sanyaku == 3
    assert result.sanyaku_missing_bio == 1
    assert result.sanyaku_missing_birth_date == 1
    assert result.sanyaku_with_birth_date == 1


def test_epoch_changes_the_supporting_boundary() -> None:
    history = History(
        {
            Date.from_ints(1958, 1): _state({1: "Jk1e"}),
            Date.from_ints(1989, 1): _state({2: "M1e"}),
            Date.from_ints(1989, 3): _state({3: "Jk1e"}),
        }
    )
    bios = BioStore(
        MappingProxyType(
            {
                RikId(1): _bio(1, date(1940, 1, 1)),
                RikId(2): _bio(2, date(1960, 1, 1)),
                RikId(3): _bio(3, date(1970, 1, 1)),
            }
        )
    )

    result = count_eligible_rikishi(
        history,
        bios,
        epoch=Date.from_ints(1989, 1),
    )

    assert result.observed_rikishi == 2
    assert result.boundary_incumbents == 1
    assert result.reached_sanyaku == 0
    assert result.sanyaku_with_birth_date == 0


def test_rejects_unrepresented_epoch() -> None:
    history = History({Date.from_ints(1958, 1): _state({1: "Jk1e"})})
    with pytest.raises(ValueError, match="represented banzuke"):
        count_eligible_rikishi(
            history,
            BioStore(MappingProxyType({})),
            epoch=Date.from_ints(1958, 3),
        )


def test_parse_date_accepts_slash_and_hyphen() -> None:
    assert parse_date("1958/01") == Date.from_ints(1958, 1)
    assert parse_date("1989-03") == Date.from_ints(1989, 3)


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

from __future__ import annotations

import csv
import json
from datetime import date
from types import MappingProxyType

from src.analysis.greatness.sanyaku_prospects.producer import produce
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


def test_producer_writes_debut_state_and_audit_bundle(tmp_path) -> None:
    dates = (
        Date.from_ints(2000, 1),
        Date.from_ints(2000, 3),
        Date.from_ints(2000, 5),
    )
    history = History(
        {
            dates[0]: _state({1: "Y1e"}),
            dates[1]: _state({2: "M1e", 3: "M2e", 4: "M3e", 5: "M4e"}),
            dates[2]: _state({2: "K1e", 4: "M2e"}),
        }
    )
    bios = BioStore(
        MappingProxyType(
            {
                RikId(1): _bio(1, date(1970, 1, 1)),
                RikId(2): _bio(2, date(1973, 3, 6)),
                RikId(3): _bio(3, date(1973, 3, 1), intai=BioBashoDate(2000, 5)),
                RikId(4): _bio(4, date(1973, 3, 1)),
                RikId(5): _bio(5, date(1973, 3, 1)),
            }
        )
    )
    results = tmp_path / "results"
    _daily(results, dates[0], "December 26, 1999")
    _daily(results, dates[1], "March 5, 2000")
    _daily(results, dates[2], "April 30, 2000")

    paths = produce(
        history,
        bios,
        results_root=results,
        output_root=tmp_path / "output",
    )

    with paths.debut_probabilities.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    age_26 = next(row for row in rows if row["division"] == "M" and row["age"] == "26")
    age_27 = next(row for row in rows if row["division"] == "M" and row["age"] == "27")
    assert (age_26["success"], age_26["rikishi"]) == ("1", "1")
    assert (age_27["failure"], age_27["right_censored"], age_27["unknown"]) == ("1", "1", "1")

    with paths.population_summary.open(newline="", encoding="utf-8") as stream:
        summary = {row["measure"]: int(row["count"]) for row in csv.DictReader(stream)}
    assert summary["boundary_incumbents"] == 1
    assert summary["complete_record_rikishi"] == 4
    assert summary["complete_records_with_birth_date"] == 4

    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    assert manifest["age_policy"] == "completed years on exact basho Day 1"
    assert paths.cohort_observations.is_file()
    assert paths.basho_date_coverage.is_file()


def _daily(root, basho, day_one: str) -> None:
    directory = root / f"{int(basho.year)} {int(basho.month):02d}"
    directory.mkdir(parents=True)
    (directory / "01.html").write_text(
        f"<h1>Test {int(basho.year)}, Day 1</h1><h2>{day_one}</h2>",
        encoding="utf-8",
    )


def _state(ranks: dict[int, str]) -> BashoState:
    chii = {RikId(rikishi_id): Chii.from_str(rank) for rikishi_id, rank in ranks.items()}
    return BashoState(
        Banzuke(
            Riks(chii),
            RikChii(chii),
            RikShikona({rikishi_id: Shikona(f"Rikishi {int(rikishi_id)}") for rikishi_id in chii}),
        ),
        Summary({}),
    )


def _bio(rikishi_id: int, birth: date, *, intai=None) -> RikishiBio:
    return RikishiBio(
        RikId(rikishi_id),
        BirthDate(birth),
        "",
        (),
        (ShikonaUse(BioBashoDate(2000, 1), Shikona(f"Rikishi {rikishi_id}")),),
        None,
        intai,
        None,
        None,
        (),
        (),
    )

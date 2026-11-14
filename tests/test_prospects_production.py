from __future__ import annotations

import csv
import json
from datetime import date
from types import MappingProxyType

from src.analysis.prospects import produce
from src.analysis.site89.prospects import produce_prospects_site_data
from src.infra.get_bios.api import BioBashoDate, BioStore, BirthDate, RikishiBio, ShikonaUse
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_prospects_produces_all_eligible_trajectories_and_site_payload(tmp_path) -> None:
    dates = tuple(Date.from_ints(1989, month) for month in (1, 3, 5))
    history = History({
        dates[0]: _state({1: "Y1e"}),
        dates[1]: _state({2: "M1e", 3: "M1w"}),
        dates[2]: _state({2: "K1e"}),
    })
    bios = BioStore(MappingProxyType({
        RikId(1): _bio(1, date(1960, 1, 1)),
        RikId(2): _bio(2, date(1963, 3, 6)),
        RikId(3): _bio(3, date(1963, 3, 6), intai=BioBashoDate(1989, 5)),
    }))
    results = tmp_path / "results"
    for basho, day_one in zip(dates, ("January 8, 1989", "March 12, 1989", "May 14, 1989")):
        directory = results / f"{int(basho.year)} {int(basho.month):02d}"
        directory.mkdir(parents=True)
        (directory / "01.html").write_text(
            f"<h1>Test {int(basho.year)}, Day 1</h1><h2>{day_one}</h2>",
            encoding="utf-8",
        )

    paths = produce(
        history,
        bios,
        results_root=results,
        output_root=tmp_path / "prospects",
        source_manifest={"history": "test-history", "bios": "test-bios", "daily_results": str(results)},
    )
    with paths.career_trajectory_points.open(newline="", encoding="utf-8") as stream:
        points = list(csv.DictReader(stream))
    assert {row["rikishi_id"] for row in points} == {"2", "3"}
    assert [row["point_kind"] for row in points if row["rikishi_id"] == "2"] == [
        "cohort_probability", "sanyaku_attainment",
    ]
    assert [row["point_kind"] for row in points if row["rikishi_id"] == "3"] == ["cohort_probability"]
    assert json.loads(paths.manifest.read_text(encoding="utf-8"))["epoch"] == "1989/01"
    assert len(json.loads(paths.manifest.read_text(encoding="utf-8"))["sources"]["represented_history_sha256"]) == 64

    data_path, report_path = produce_prospects_site_data(
        history=history,
        prospects_root=paths.root,
        output_root=tmp_path / "site",
    )
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["source"]["cutoff"] == "1989/05"
    assert set(payload["points_by_rikishi"]) == {"2", "3"}
    assert [row["shikona"] for row in payload["rikishi"]] == ["Rikishi 2", "Rikishi 3"]
    assert report["rikishi_count"] == 2
    assert report["attainment_count"] == 1


def _state(ranks: dict[int, str]) -> BashoState:
    chii = {RikId(rid): Chii.from_str(rank) for rid, rank in ranks.items()}
    return BashoState(
        Banzuke(
            Riks(chii), RikChii(chii),
            RikShikona({rid: Shikona(f"Rikishi {int(rid)}") for rid in chii}),
        ),
        Summary({}),
    )


def _bio(rikishi_id: int, birth: date, *, intai=None) -> RikishiBio:
    return RikishiBio(
        RikId(rikishi_id), BirthDate(birth), "", (),
        (ShikonaUse(BioBashoDate(1989, 1), Shikona(f"Rikishi {rikishi_id}")),),
        None, intai, None, None, (), (),
    )

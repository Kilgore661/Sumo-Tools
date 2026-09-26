from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from types import MappingProxyType

from src.analysis.site89 import rikishi_bio_data
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.get_bios.api import BioStore, BirthDate, RikishiBio
from src.products.make_site89.manifest.artifacts import RIKISHI_BIO_DATA_ARTIFACT
from src.products.make_site89.manifest.builder import build_public_site_shell
from src.products.make_site89.publication_model import build_publication_plan
from src.products.make_site89.site_definition import SITE
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.BasicPrimitives import Month, RikId, Riks, Shikona, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_producer_writes_latest_banzuke_bios_in_banzuke_order(tmp_path, monkeypatch) -> None:
    first = RikId(1)
    second = RikId(2)
    history = History(
        {
            Date(Year(2025), Month(11)): state({first: ("Old Alpha", "M2e")}),
            Date(Year(2026), Month(1)): state(
                {
                    first: ("Alpha", "M1e"),
                    second: ("Beta", "J1w"),
                }
            ),
        }
    )
    bios = BioStore(
        MappingProxyType(
            {
                first: bio(first, birth=date(2000, 1, 1), height="180.5", weight="90.5"),
                second: bio(second, birth=date(2000, 1, 2), height=None, weight=None),
            }
        )
    )
    monkeypatch.setattr(
        rikishi_bio_data.FullShikonaStore,
        "from_sources",
        classmethod(
            lambda cls, history, bios: FullShikonaStore(
                MappingProxyType({first: "Public Alpha", second: "Public Beta"})
            )
        ),
    )

    output = rikishi_bio_data.produce_rikishi_bio_data(
        history=history,
        bios=bios,
        output_root=tmp_path,
    )
    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    assert [row["rikishi_id"] for row in rows] == ["1", "2"]
    assert [row["division"] for row in rows] == ["makuuchi", "juryo"]
    assert [row["shikona"] for row in rows] == ["Public Alpha", "Public Beta"]
    assert rows[0]["age"] == "26"
    assert rows[1]["age"] == "25"
    assert rows[0]["height_cm"] == "181"
    assert rows[0]["weight_kg"] == "91"
    assert rows[0]["bmi"] == "27.8"
    assert rows[1]["height_cm"] == rows[1]["weight_kg"] == rows[1]["bmi"] == ""
    assert {row["snapshot_banzuke"] for row in rows} == {"2026/01"}


def test_page_is_published_on_home_with_makuuchi_default() -> None:
    plan = build_publication_plan(SITE)
    assert plan.pages["rikishi_bio_data"].route.parts == (
        "home",
        "rikishi-bio-data",
    )
    shell = build_public_site_shell(plan)
    home = next(item for item in shell.navigation_bar.navigation_tree if item.id == "home")
    item = next(child for child in home.children if child.id == "rikishi_bio_data")
    assert item.href == "index.html?page=rikishi_bio_data&division=makuuchi"

    panel = next(panel for panel in shell.content_panels if panel.page_id == "rikishi_bio_data")
    division = panel.contents.filter_section.filters[0]
    assert division.default == "makuuchi"
    assert [value.value for value in division.values] == [
        "makuuchi", "juryo", "makushita", "sandanme", "jonidan", "jonokuchi", "all"
    ]
    assert [column.id for column in RIKISHI_BIO_DATA_ARTIFACT.columns] == [
        "row_number", "shikona", "chii", "age", "height_cm", "weight_kg", "bmi"
    ]


def state(entries: dict[RikId, tuple[str, str]]) -> BashoState:
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(entries),
            rikchii=RikChii({rid: Chii.from_str(rank) for rid, (_, rank) in entries.items()}),
            rikshik=RikShikona({rid: Shikona(name) for rid, (name, _) in entries.items()}),
        ),
        summary=Summary({}),
    )


def bio(
    rid: RikId, *, birth: date, height: str | None, weight: str | None
) -> RikishiBio:
    return RikishiBio(
        rikid=rid,
        birth_date=BirthDate(birth),
        shusshin="",
        heya=(),
        shikona_history=(),
        hatsu_dohyo=None,
        intai=None,
        height_cm=None if height is None else Decimal(height),
        weight_kg=None if weight is None else Decimal(weight),
        height_history=(),
        weight_history=(),
    )

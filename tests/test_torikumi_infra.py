from datetime import datetime, timezone
import csv
import json
from pathlib import Path
from types import MappingProxyType
from types import SimpleNamespace

import pytest

from src.analysis.elo89.api import Elo89Artifacts
from src.analysis.site89.torikumi import produce_torikumi
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.torikumi.model import Future, FutureBout, FutureDay
from src.infra.torikumi.parser import parse_torikumi_page
from src.infra.torikumi.persistence import load_future, save_future
from src.infra.torikumi.scraper import refresh_future
from src.infra.parser.parser2_IntDate import IntDate
from src.sumo_core.BasicPrimitives import Day, Month, RikId, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


NOW = datetime(2026, 9, 25, 9, 30, tzinfo=timezone.utc)
DATE = Date(Year(2026), Month(9))


def page(day: int, *, result: bool = False) -> str:
    cells = ["" for _ in range(13)]
    cells[5] = '<a href="Rikishi.aspx?r=1">East</a>'
    cells[7] = "W" if result else ""
    cells[9] = "L" if result else ""
    cells[11] = '<a href="Rikishi.aspx?r=2">West</a>'
    row = "".join(f"<td>{cell}</td>" for cell in cells)
    return (
        f"<h1>Aki 2026, Day {day}</h1><h2>Makuuchi</h2>"
        f"<table><tr>{row}</tr></table>"
        '<a href="Banzuke.aspx?b=202609">Banzuke</a>'
    )


def test_parser_extracts_published_bouts_with_or_without_results() -> None:
    pending = parse_torikumi_page(page(14), expected_date=DATE, expected_day=Day(14))
    completed = parse_torikumi_page(
        page(13, result=True), expected_date=DATE, expected_day=Day(13)
    )

    assert pending.bouts == (
        FutureBout(
            order=1,
            east=RikId(1),
            west=RikId(2),
            east_shikona="East",
            west_shikona="West",
        ),
    )
    assert pending.result_count == 0
    assert completed.result_count == 1


def test_future_json_round_trip(tmp_path: Path) -> None:
    future = Future(
        date=DATE,
        completed_through=Day(13),
        generated_at=NOW,
        days=(
            FutureDay(
                day=Day(14),
                bouts=(FutureBout(order=1, east=RikId(1), west=RikId(2)),),
                source_url="https://example.test/day14",
                downloaded_at=NOW,
            ),
        ),
    )

    assert load_future(save_future(future, tmp_path / "future.json")) == future


def test_scraper_probes_every_day_and_keeps_completed_pairings(tmp_path: Path) -> None:
    history = {DATE: SimpleNamespace(summary=SimpleNamespace(last_defined=lambda: Day(13)))}
    requested = []

    def fetch(url: str) -> str | None:
        requested.append(url)
        if "d=13" in url:
            return page(13, result=True)
        if "d=14" in url:
            return page(14)
        return None

    future = refresh_future(
        history, output_root=tmp_path, fetch_text=fetch, now=NOW
    )

    assert [int(day.day) for day in future.days] == [13, 14]
    assert future.days[0].result_count == 1
    assert [url.rsplit("d=", 1)[1].split("&", 1)[0] for url in requested] == [
        str(day) for day in range(1, 16)
    ]
    assert (tmp_path / "raw" / "2026 09" / "13.html").is_file()
    assert (tmp_path / "raw" / "2026 09" / "14.html").is_file()


def test_annotation_uses_latest_existing_rating_snapshot(tmp_path: Path) -> None:
    future = Future(
        date=DATE,
        completed_through=Day(13),
        generated_at=NOW,
        days=(
            FutureDay(
                day=Day(14),
                bouts=(FutureBout(order=1, east=RikId(1), west=RikId(2)),),
                source_url="https://example.test/day14",
                downloaded_at=NOW,
            ),
        ),
    )
    ratings = Elo89Artifacts(
        root=tmp_path,
        manifest={"q": 400.0},
        prior={},
        basho_start_ratings={str(DATE): {"1": 1400.0, "2": 1400.0}},
        day_end_ratings={str(DATE): {"9": {"1": 1400.0, "2": 1600.0}}},
        basho_end_ratings={},
        bout_ledger=(),
    )
    names = FullShikonaStore(
        MappingProxyType({RikId(1): "Fred", RikId(2): "Bill"})
    )

    paths = produce_torikumi(
        history={
            DATE: SimpleNamespace(
                banzuke=SimpleNamespace(
                    rikchii={
                        RikId(1): Chii.from_str("M1e"),
                        RikId(2): Chii.from_str("J1w"),
                    }
                )
            )
        },
        future=future,
        ratings=ratings,
        output_root=tmp_path,
        names=names,
    )

    index = json.loads(paths[0].read_text(encoding="utf-8"))
    with paths[1].open(newline="", encoding="utf-8") as stream:
        row = next(csv.DictReader(stream))
    day_14 = index["entries"][13]
    assert day_14["day"] == "14"
    assert day_14["disabled"] is False
    assert day_14["ratings_cutoff"] == "end of Day 9"
    assert index["default_day"] == "14"
    assert len(index["entries"]) == 15
    assert index["entries"][14] == {
        "day": "15",
        "label": "Day 15",
        "disabled": True,
    }
    assert row["east_shikona"] == "Fred"
    assert row["division_id"] == "makuuchi"
    assert row["east_probability"] == "24%"
    assert row["west_probability"] == "76%"
    assert "result" not in row


def test_empty_future_produces_no_torikumi_index(tmp_path: Path) -> None:
    ratings = Elo89Artifacts(
        root=tmp_path,
        manifest={"q": 400.0},
        prior={},
        basho_start_ratings={str(DATE): {}},
        day_end_ratings={},
        basho_end_ratings={},
        bout_ledger=(),
    )
    future = Future(
        date=DATE,
        completed_through=Day(15),
        generated_at=NOW,
        days=(),
    )

    paths = produce_torikumi(
        history={DATE: SimpleNamespace(banzuke=SimpleNamespace(rikchii={}))},
        future=future,
        ratings=ratings,
        output_root=tmp_path,
        names=FullShikonaStore(MappingProxyType({})),
    )

    index = json.loads(paths[0].read_text(encoding="utf-8"))
    assert len(index["entries"]) == 15
    assert all(entry["disabled"] for entry in index["entries"])
    assert index["default_day"] is None


def test_annotation_accepts_live_store_int_date_key(tmp_path: Path) -> None:
    ratings = Elo89Artifacts(
        root=tmp_path,
        manifest={"q": 400.0},
        prior={},
        basho_start_ratings={str(DATE): {}},
        day_end_ratings={},
        basho_end_ratings={},
        bout_ledger=(),
    )
    future = Future(
        date=DATE,
        completed_through=Day(15),
        generated_at=NOW,
        days=(),
    )

    paths = produce_torikumi(
        history={
            IntDate(2026, 9): SimpleNamespace(
                banzuke=SimpleNamespace(rikchii={})
            )
        },
        future=future,
        ratings=ratings,
        output_root=tmp_path,
        names=FullShikonaStore(MappingProxyType({})),
    )

    assert paths[0].is_file()


def test_annotation_marks_mz_rating_and_probabilities_as_unknown(tmp_path: Path) -> None:
    future = Future(
        date=DATE,
        completed_through=Day(13),
        generated_at=NOW,
        days=(
            FutureDay(
                day=Day(14),
                bouts=(FutureBout(order=1, east=RikId(1), west=RikId(2)),),
                source_url="https://example.test/day14",
                downloaded_at=NOW,
            ),
        ),
    )
    ratings = Elo89Artifacts(
        root=tmp_path,
        manifest={"q": 400.0},
        prior={},
        basho_start_ratings={str(DATE): {"1": 1400.0, "2": 1600.0}},
        day_end_ratings={},
        basho_end_ratings={},
        bout_ledger=(),
    )

    paths = produce_torikumi(
        history={
            DATE: SimpleNamespace(
                banzuke=SimpleNamespace(rikchii={RikId(2): Chii.from_str("J1w")})
            )
        },
        future=future,
        ratings=ratings,
        output_root=tmp_path,
        names=FullShikonaStore(
            MappingProxyType({RikId(1): "Fred", RikId(2): "Bill"})
        ),
    )

    with paths[1].open(newline="", encoding="utf-8") as stream:
        row = next(csv.DictReader(stream))
    assert row["division_id"] == "juryo"
    assert row["east_elo89"] == "-"
    assert row["west_elo89"] == "1600"
    assert row["east_probability"] == "-"
    assert row["west_probability"] == "-"

    del ratings.basho_start_ratings[str(DATE)]["2"]
    with pytest.raises(ValueError, match="rating for banzuke rikishi 2"):
        produce_torikumi(
            history={
                DATE: SimpleNamespace(
                    banzuke=SimpleNamespace(
                        rikchii={RikId(2): Chii.from_str("J1w")}
                    )
                )
            },
            future=future,
            ratings=ratings,
            output_root=tmp_path / "missing-ranked-rating",
            names=FullShikonaStore(
                MappingProxyType({RikId(1): "Fred", RikId(2): "Bill"})
            ),
        )

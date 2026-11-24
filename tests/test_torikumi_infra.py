import csv
from datetime import datetime, timezone
import importlib
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
from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import Day, Month, RikId, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


torikumi_cli = importlib.import_module("src.infra.torikumi.__main__")


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


def test_torikumi_command_uses_live_store_by_default(
    tmp_path: Path,
    monkeypatch,
) -> None:
    history = object()
    captured = {}
    target = SimpleNamespace(date=DATE, source="test target")
    monkeypatch.setattr(torikumi_cli, "get_history", lambda: history)
    monkeypatch.setattr(
        torikumi_cli,
        "resolve_torikumi_target",
        lambda value, new: target,
    )
    monkeypatch.setattr(
        torikumi_cli,
        "refresh_future",
        lambda value, **kwargs: (
            captured.update(history=value, **kwargs)
            or SimpleNamespace(days=())
        ),
    )

    assert torikumi_cli.main(
        [
            "--output-root",
            str(tmp_path),
            "--new-banzuke",
            str(tmp_path / "absent.json"),
        ]
    ) == 0
    assert captured == {
        "history": history,
        "target": target,
        "output_root": tmp_path,
    }


def test_torikumi_command_accepts_explicit_history_zip(
    tmp_path: Path,
    monkeypatch,
) -> None:
    history = object()
    captured = {}
    history_zip = tmp_path / "history.zip"
    target = SimpleNamespace(date=DATE, source="test target")
    monkeypatch.setattr(
        torikumi_cli,
        "get_history",
        lambda: (_ for _ in ()).throw(AssertionError("live store was accessed")),
    )
    monkeypatch.setattr(
        torikumi_cli,
        "load_history_with_annotations",
        lambda path: captured.update(path=path) or history,
    )
    monkeypatch.setattr(
        torikumi_cli,
        "refresh_future",
        lambda value, **kwargs: (
            captured.update(history=value, **kwargs)
            or SimpleNamespace(days=())
        ),
    )
    monkeypatch.setattr(
        torikumi_cli,
        "resolve_torikumi_target",
        lambda value, new: target,
    )

    assert torikumi_cli.main(
        [
            "--history-zip",
            str(history_zip),
            "--output-root",
            str(tmp_path),
            "--new-banzuke",
            str(tmp_path / "absent.json"),
        ]
    ) == 0
    assert captured == {
        "path": str(history_zip.with_suffix("")),
        "history": history,
        "target": target,
        "output_root": tmp_path,
    }


def test_scraper_probes_published_prefix_and_keeps_completed_pairings(tmp_path: Path) -> None:
    history = {DATE: SimpleNamespace(summary=SimpleNamespace(last_defined=lambda: Day(1)))}
    requested = []

    def fetch(url: str) -> str | None:
        requested.append(url)
        if "d=1&" in url:
            return page(1, result=True)
        if "d=2&" in url:
            return page(2)
        return None

    future = refresh_future(
        history, output_root=tmp_path, fetch_text=fetch, now=NOW
    )

    assert [int(day.day) for day in future.days] == [1, 2]
    assert future.days[0].result_count == 1
    assert [url.rsplit("d=", 1)[1].split("&", 1)[0] for url in requested] == [
        "1",
        "2",
        "3",
    ]
    assert (tmp_path / "raw" / "2026 09" / "01.html").is_file()
    assert (tmp_path / "raw" / "2026 09" / "02.html").is_file()


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
    basho = index["entries"][0]
    day_14 = basho["days"][13]
    assert day_14["day"] == "14"
    assert day_14["disabled"] is False
    assert day_14["ratings_cutoff"] == "end of Day 9"
    assert index["default_day"] is None
    assert index["default_basho"] == "2026/09"
    assert len(basho["days"]) == 15
    assert basho["days"][14] == {
        "day": "15",
        "label": "Day 15",
        "disabled": True,
    }
    assert row["east_shikona"] == "Fred"
    assert row["division_id"] == "makuuchi"
    assert row["east_odds"] == "4.16"
    assert row["west_odds"] == "1.32"
    assert row["prediction_side"] == "west"
    assert row["prediction_result"] == "pending"


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
    assert len(index["entries"]) == 1
    assert all(entry["disabled"] for entry in index["entries"][0]["days"])
    assert index["default_day"] is None


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
    assert row["west_elo89"] == "1600.0"
    assert row["east_odds"] == "-"
    assert row["west_odds"] == "-"

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


def test_historical_results_score_favourites_and_profit_without_fusen(
    tmp_path: Path,
) -> None:
    pairs = [
        (RikId(2), RikId(1), Outcome.W, Outcome.L),
        (RikId(4), RikId(3), Outcome.W, Outcome.L),
        (RikId(6), RikId(5), Outcome.FS, Outcome.FP),
    ]
    results = {
        (east, west): SimpleNamespace(
            rikishi1=east,
            outcome1=east_outcome,
            rikishi2=west,
            outcome2=west_outcome,
        )
        for east, west, east_outcome, west_outcome in pairs
    }
    ranks = {RikId(rid): Chii.from_str(f"M{rid}e") for rid in range(1, 7)}
    ratings = Elo89Artifacts(
        root=tmp_path,
        manifest={"q": 400.0},
        prior={},
        basho_start_ratings={
            str(DATE): {
                "1": 1600.0, "2": 1400.0,
                "3": 1500.0, "4": 1700.0,
                "5": 1550.0, "6": 1450.0,
            }
        },
        day_end_ratings={},
        basho_end_ratings={},
        bout_ledger=(),
    )
    future = Future(
        date=DATE,
        completed_through=Day(1),
        generated_at=NOW,
        days=(),
    )

    paths = produce_torikumi(
        history={
            DATE: SimpleNamespace(
                banzuke=SimpleNamespace(rikchii=ranks),
                summary={
                    Day(1): SimpleNamespace(
                        torikumi=set(results),
                        results_lookup=results,
                    )
                },
            )
        },
        future=future,
        ratings=ratings,
        output_root=tmp_path,
        names=FullShikonaStore(
            MappingProxyType({
                RikId(rid): f"Rikishi {rid}" for rid in range(1, 7)
            })
        ),
    )

    index = json.loads(paths[0].read_text(encoding="utf-8"))
    day = index["entries"][0]["days"][0]
    summary = day["summaries"]["makuuchi"]
    assert summary["correct"] == 1
    assert summary["scored"] == 2
    assert summary["fusen_excluded"] == 1
    assert summary["draw_excluded"] == 0
    assert summary["favourite_profit"] == pytest.approx(-0.683772)
    assert summary["winner_profit"] == pytest.approx(3.478505)
    assert summary["chii_scored"] == 2
    assert summary["chii_profit"] == pytest.approx(-2.0)

    with paths[1].open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert [row["prediction_result"] for row in rows] == [
        "incorrect", "correct", "excluded"
    ]

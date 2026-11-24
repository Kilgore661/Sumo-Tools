import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

import pytest

from src.analysis.elo89.api import Elo89Artifacts
from src.analysis.elo89.projection import project_basho_start_ratings
from src.analysis.site89.torikumi import produce_torikumi
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.new_banzuke.api import NewBanzuke
from src.infra.torikumi.model import Future, FutureBout, FutureDay
from src.infra.torikumi.persistence import load_future, save_future
from src.infra.torikumi.scraper import TorikumiRefreshError, refresh_future
from src.infra.torikumi.target import (
    TorikumiTarget,
    next_basho_date,
    resolve_torikumi_target,
)
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BasicPrimitives import Day, RikId, Riks, Shikona
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


NOW = datetime(2026, 11, 1, tzinfo=timezone.utc)
SEPTEMBER = Date.from_ints(2026, 9)
NOVEMBER = Date.from_ints(2026, 11)


def test_target_uses_active_history_before_published_successor() -> None:
    history = _history(SEPTEMBER, completed=Day(7))
    target = resolve_torikumi_target(
        history,
        _new_banzuke(NOVEMBER, _banzuke({1: "M1e"})),
    )

    assert target.date == SEPTEMBER
    assert target.completed_through == Day(7)
    assert target.source == "active History basho"


def test_target_uses_new_banzuke_after_completed_history() -> None:
    upcoming = _banzuke({1: "M1e", 2: "J1w"})
    target = resolve_torikumi_target(
        _history(SEPTEMBER, completed=Day(15)),
        _new_banzuke(NOVEMBER, upcoming),
    )

    assert target.date == NOVEMBER
    assert target.completed_through is None
    assert target.banzuke == upcoming
    assert target.source == "published New Banzuke"


def test_target_handles_november_to_january_and_rejects_gaps() -> None:
    november = Date.from_ints(2026, 11)
    january = Date.from_ints(2027, 1)
    assert next_basho_date(november) == january
    assert resolve_torikumi_target(
        _history(november, completed=Day(15)),
        _new_banzuke(january, _banzuke({1: "M1e"})),
    ).date == january

    with pytest.raises(ValueError, match="immediate successor"):
        resolve_torikumi_target(
            _history(SEPTEMBER, completed=Day(15)),
            _new_banzuke(january, _banzuke({1: "M1e"})),
        )


def test_unpublished_http_200_shell_produces_empty_upcoming_snapshot(
    tmp_path: Path,
) -> None:
    target = TorikumiTarget(
        date=NOVEMBER,
        banzuke=_banzuke({1: "M1e"}),
        completed_through=None,
        source="test",
    )

    future = refresh_future(
        _history(SEPTEMBER, completed=Day(15)),
        target=target,
        output_root=tmp_path,
        fetch_text=lambda url: _unpublished_shell(url),
        now=NOW,
    )

    assert future.date == NOVEMBER
    assert future.days == ()
    assert load_future(tmp_path / "future.json") == future


def test_failed_refresh_preserves_same_target_snapshot(tmp_path: Path) -> None:
    previous = Future(
        date=NOVEMBER,
        completed_through=None,
        generated_at=NOW,
        days=(
            FutureDay(
                day=Day(1),
                bouts=(FutureBout(order=1, east=RikId(1), west=RikId(2)),),
                source_url="https://example.test/day1",
                downloaded_at=NOW,
            ),
        ),
    )
    path = save_future(previous, tmp_path / "future.json")
    before = path.read_bytes()
    target = TorikumiTarget(
        date=NOVEMBER,
        banzuke=_banzuke({1: "M1e", 2: "M1w"}),
        completed_through=None,
        source="test",
    )

    with pytest.raises(TorikumiRefreshError, match="offline"):
        refresh_future(
            _history(SEPTEMBER, completed=Day(15)),
            target=target,
            output_root=tmp_path,
            fetch_text=lambda _url: (_ for _ in ()).throw(OSError("offline")),
            now=NOW,
        )

    assert path.read_bytes() == before


def test_projection_uses_latest_frozen_rating_and_prior_then_normalizes() -> None:
    ratings = Elo89Artifacts(
        root=Path("unused"),
        manifest={"target_mean": 1400.0},
        prior={"M1": 1100.0, "J1": 1000.0},
        basho_start_ratings={},
        day_end_ratings={},
        basho_end_ratings={
            "2026/07": {"1": 1400.0, "2": 1300.0},
            "2026/09": {"1": 1500.0},
        },
        bout_ledger=(),
    )

    projected = project_basho_start_ratings(
        ratings=ratings,
        banzuke=_banzuke({1: "M1e", 2: "M1w", 3: "J1e"}),
    )

    assert projected == pytest.approx(
        {"1": 1633.333333, "2": 1433.333333, "3": 1133.333333}
    )


def test_upcoming_torikumi_uses_projected_start_ratings(tmp_path: Path) -> None:
    upcoming = _banzuke({1: "M1e", 2: "M1w"})
    future = Future(
        date=NOVEMBER,
        completed_through=None,
        generated_at=NOW,
        days=(
            FutureDay(
                day=Day(1),
                bouts=(FutureBout(order=1, east=RikId(1), west=RikId(2)),),
                source_url="https://example.test/day1",
                downloaded_at=NOW,
            ),
        ),
    )
    ratings = Elo89Artifacts(
        root=tmp_path,
        manifest={"q": 400.0, "target_mean": 1500.0},
        prior={"M1": 1200.0},
        basho_start_ratings={},
        day_end_ratings={},
        basho_end_ratings={"2026/09": {"1": 1600.0, "2": 1400.0}},
        bout_ledger=(),
    )

    paths = produce_torikumi(
        history=_history(SEPTEMBER, completed=Day(15)),
        future=future,
        ratings=ratings,
        output_root=tmp_path,
        upcoming_banzuke=upcoming,
        names=FullShikonaStore(
            MappingProxyType({RikId(1): "East", RikId(2): "West"})
        ),
    )

    index = json.loads(paths[0].read_text(encoding="utf-8"))
    with paths[2].open(newline="", encoding="utf-8") as stream:
        row = next(csv.DictReader(stream))
    november = index["entries"][1]
    assert november["basho"] == "2026/11"
    assert november["days"][0]["ratings_cutoff"] == "projected start of basho"
    assert row["east_elo89"] == "1600.0"
    assert row["west_elo89"] == "1400.0"


def _history(date: Date, *, completed: Day):
    return {
        date: SimpleNamespace(
            banzuke=_banzuke({1: "M2e", 2: "M2w"}),
            summary=SimpleNamespace(last_defined=lambda: completed),
        )
    }


def _banzuke(ranks: dict[int, str]) -> Banzuke:
    chii = {RikId(rid): Chii.from_str(rank) for rid, rank in ranks.items()}
    names = {RikId(rid): Shikona(f"Rikishi {rid}") for rid in ranks}
    return Banzuke(
        riks=Riks(chii),
        rikchii=RikChii(chii),
        rikshik=RikShikona(names),
    )


def _new_banzuke(date: Date, banzuke: Banzuke) -> NewBanzuke:
    return NewBanzuke.from_banzuke(
        date=date,
        banzuke=banzuke,
        source_path=Path("source.html"),
        generated_at=NOW.isoformat(),
    )


def _unpublished_shell(url: str) -> str:
    query = url.split("?", 1)[1].replace("&", "&amp;")
    return (
        "<html><head><title>SumoDB</title></head><body>"
        "Text-only Results "
        f'<a href="Results.aspx?{query}">selected day</a>'
        "</body></html>"
    )

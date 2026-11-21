from __future__ import annotations

import json
from argparse import Namespace
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.misc.Betting.probes.adapters import existing_scraper_adapter
from src.misc.Betting.probes import browser as browser_tools
from src.misc.Betting.probes.connection import ConnectionState, Place
from src.misc.Betting.probes.runner import (
    AcquisitionResult,
    ProbePlan,
    default_target_date,
    normal_start_window,
    run_probe,
)


def london(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 11, 21, hour, minute, tzinfo=ZoneInfo("Europe/London"))


def test_normal_start_window_is_inclusive_from_ten_through_ten_pm() -> None:
    assert not normal_start_window(london(9, 59))
    assert normal_start_window(london(10))
    assert normal_start_window(london(22))
    assert not normal_start_window(london(22, 1))


def test_default_target_date_is_captured_as_tomorrow() -> None:
    assert default_target_date(london(21)) == date(2026, 11, 22)


class FakeController:
    def __init__(self) -> None:
        self.initial = ConnectionState(False, raw="Not connected")
        self.prepared: list[str] = []
        self.restored = False

    def catalogue(self) -> dict[int, str]:
        return {12: "Luxembourg"}

    def status(self) -> ConnectionState:
        return self.initial

    def ensure_place(self, place: Place) -> ConnectionState:
        self.prepared.append(place.key)
        return ConnectionState(place.location_id is not None, place.name, place.name)

    def restore(self, initial, catalogue) -> None:
        assert initial == self.initial
        assert catalogue == {12: "Luxembourg"}
        self.restored = True


def test_runner_advances_then_stops_after_success_and_restores(tmp_path: Path) -> None:
    controller = FakeController()
    outcomes = iter(
        (
            AcquisitionResult("odds_absent"),
            AcquisitionResult("success", files=("odds.json",)),
        )
    )
    plan = ProbePlan(
        "bet365",
        date(2026, 11, 22),
        "Europe/London",
        ("direct", "12"),
        True,
    )

    result = run_probe(
        plan,
        lambda _place, _ip, _run: next(outcomes),
        records_dir=tmp_path / "records",
        lock_path=tmp_path / "vpn.lock",
        controller_factory=lambda: controller,
        exit_ip_observer=lambda: "192.0.2.10",
        now_function=lambda: london(10, 5),
    )

    assert result == 0
    assert controller.prepared == ["direct", "expressvpn:12"]
    assert controller.restored
    rows = [
        json.loads(line)
        for line in (tmp_path / "records" / "bet365_attempts.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert [row["outcome"] for row in rows] == ["odds_absent", "success"]


def test_runner_skips_a_place_with_a_persisted_451(tmp_path: Path) -> None:
    records = tmp_path / "records"
    records.mkdir()
    (records / "bet365_attempts.jsonl").write_text(
        json.dumps(
            {
                "run_id": "earlier",
                "source": "bet365",
                "place": {"key": "direct", "name": "Direct", "location_id": None},
                "outcome": "http_451",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    controller = FakeController()
    plan = ProbePlan(
        "bet365",
        date(2026, 11, 22),
        "Europe/London",
        ("direct", "12"),
        True,
    )

    result = run_probe(
        plan,
        lambda _place, _ip, _run: AcquisitionResult("success"),
        records_dir=records,
        lock_path=tmp_path / "vpn.lock",
        controller_factory=lambda: controller,
        exit_ip_observer=lambda: "192.0.2.11",
        now_function=lambda: london(10, 5),
    )

    assert result == 0
    assert controller.prepared == ["expressvpn:12"]


def test_adapter_requires_a_new_file_for_the_target_date(tmp_path: Path) -> None:
    output = tmp_path / "odds"
    output.mkdir()
    namespace = Namespace(output_dir=output)

    def download(_args, _timezone) -> bool:
        (output / "2026-11-22_05-00.json").write_text(
            json.dumps(
                {
                    "source": "test",
                    "events": [
                        {
                            "start": "2026-11-22T05:00:00+00:00",
                            "competitor_1": "A",
                            "competitor_2": "B",
                            "odds": [
                                {"outcome": "A", "price": "1.5"},
                                {"outcome": "B", "price": "2.5"},
                            ],
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return True

    acquire = existing_scraper_adapter(
        download, namespace, ZoneInfo("Europe/London"), date(2026, 11, 22)
    )
    result = acquire(Place.direct(), "192.0.2.12", "run-1")

    assert result.outcome == "success"
    payload = json.loads(Path(result.files[0]).read_text(encoding="utf-8"))
    assert payload["acquisition"]["target_date"] == "2026-11-22"
    assert payload["acquisition"]["place"] == "Direct"


def test_adapter_reports_target_date_mismatch(tmp_path: Path) -> None:
    output = tmp_path / "odds"
    output.mkdir()
    namespace = Namespace(output_dir=output)

    def download(_args, _timezone) -> bool:
        (output / "2026-11-21_05-00.json").write_text("{}\n", encoding="utf-8")
        return True

    acquire = existing_scraper_adapter(
        download, namespace, ZoneInfo("Europe/London"), date(2026, 11, 22)
    )

    assert acquire(Place.direct(), "192.0.2.13", "run-2").outcome == "target_date_mismatch"


def test_attached_browser_is_closed_through_cdp(monkeypatch) -> None:
    sent: list[str] = []
    stopped: list[object] = []

    class Session:
        def send(self, method: str) -> None:
            sent.append(method)

    class Browser:
        def new_browser_cdp_session(self):
            return Session()

    class Process:
        def poll(self):
            return 0

    process = Process()
    monkeypatch.setattr(browser_tools, "stop_browser", stopped.append)

    browser_tools.close_attached_browser(Browser(), process)

    assert sent == ["Browser.close"]
    assert stopped == [process]

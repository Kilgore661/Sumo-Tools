from __future__ import annotations

from argparse import Namespace
from zoneinfo import ZoneInfo

import src.misc.Betting.download_sumo_odds as scraper
from src.misc.Betting.download_sumo_odds import discover_event_seeds


class EmptyLocator:
    def __init__(self) -> None:
        self.waited = False

    @property
    def first(self):
        return self

    def count(self) -> int:
        return 0

    def is_visible(self) -> bool:
        return False

    def wait_for(self, **_kwargs) -> None:
        self.waited = True


class EmptySumoPage:
    def __init__(self) -> None:
        self.heading = EmptyLocator()

    def get_by_role(self, role: str, **_kwargs):
        if role == "heading":
            return self.heading
        return EmptyLocator()

    def get_by_text(self, _text: str, **_kwargs):
        return EmptyLocator()

    def locator(self, _selector: str):
        return EmptyLocator()


def test_empty_listing_does_not_require_a_japan_group() -> None:
    page = EmptySumoPage()

    seeds = discover_event_seeds(
        page,
        "https://www.marathonbet.com/en/betting/sumo",
        ZoneInfo("Europe/London"),
    )

    assert page.heading.waited
    assert seeds == []


def test_retry_loop_announces_each_attempt_and_stops_on_success(
    monkeypatch, capsys
) -> None:
    outcomes = iter((False, True))
    monkeypatch.setattr(
        scraper, "download_once", lambda _args, _timezone: next(outcomes)
    )
    sleeps = []
    args = Namespace(timezone="Europe/London", retry_minutes=30.0, once=False)

    result = scraper.run_download_loop(args, sleep_function=sleeps.append)

    messages = capsys.readouterr().err
    assert result == 0
    assert "Attempt 1: checking for sumo odds" in messages
    assert "Attempt 2: checking for sumo odds" in messages
    assert "Retrying in 30 minutes" in messages
    assert "Attempt 2 succeeded" in messages
    assert sleeps == [1800.0]


def test_once_does_not_sleep_after_an_empty_listing(monkeypatch) -> None:
    monkeypatch.setattr(
        scraper, "download_once", lambda _args, _timezone: False
    )
    sleeps = []
    args = Namespace(timezone="Europe/London", retry_minutes=30.0, once=True)

    result = scraper.run_download_loop(args, sleep_function=sleeps.append)

    assert result == 1
    assert sleeps == []

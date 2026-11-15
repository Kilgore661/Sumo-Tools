from __future__ import annotations

import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from src.misc.Betting.download_bet365_sumo_odds import (
    decimal_price,
    open_route_fresh,
    parse_args,
    parse_bout_listing,
    parse_candidate_rows,
    wait_for_hash,
)


@pytest.mark.parametrize(
    ("displayed", "expected"),
    [
        ("1.35", "1.35"),
        ("4/11", "1.363636"),
        ("2/1", "3"),
        ("5/6", "1.833333"),
        ("EVS", "2"),
    ],
)
def test_decimal_price_normalizes_bet365_formats(displayed: str, expected: str) -> None:
    assert decimal_price(displayed) == expected


def test_parse_bout_listing_aligns_bouts_with_price_columns() -> None:
    now = datetime(2026, 11, 15, 11, tzinfo=ZoneInfo("Europe/London"))
    page_lines = [
        "Sumo",
        "November Grand Tournament",
        "To Win Bout",
        "Mon 16 Nov",
        "05:00",
        "Aonishiki",
        "Takayasu",
        "05:00",
        "Atamifuji",
        "Hoshoryu",
        "1",
        "4/11",
        "5/6",
        "2",
        "2/1",
        "5/6",
        "Help",
    ]

    sections = parse_bout_listing(page_lines, now)

    assert sections == [
        (
            "Mon 16 Nov",
            [
                {
                    "lines": ["05:00", "Aonishiki", "Takayasu"],
                    "prices": ["4/11", "2/1"],
                },
                {
                    "lines": ["05:00", "Atamifuji", "Hoshoryu"],
                    "prices": ["5/6", "5/6"],
                },
            ],
        )
    ]


def test_parse_candidate_rows_builds_decimal_events() -> None:
    now = datetime(2026, 11, 15, 11, tzinfo=ZoneInfo("Europe/London"))
    events = parse_candidate_rows(
        [
            {
                "lines": ["05:00", "Aonishiki", "Takayasu"],
                "prices": ["4/11", "2/1"],
            },
            {
                "lines": ["05:00", "Atamifuji", "Hoshoryu"],
                "prices": ["1.83", "1.83"],
            },
        ],
        ["Mon 16 Nov", "To Win Bout", "November Grand Tournament"],
        now,
        "https://www.bet365.com/#/AC/B160/C1/D1/E2/F2/",
    )

    assert [event.name for event in events] == [
        "Aonishiki vs Takayasu",
        "Atamifuji vs Hoshoryu",
    ]
    assert events[0].start == "2026-11-16T05:00:00+00:00"
    assert [odd.price for odd in events[0].odds] == ["1.363636", "3"]
    assert [odd.price for odd in events[1].odds] == ["1.83", "1.83"]
    assert all(odd.market == "To Win Bout" for event in events for odd in event.odds)


def test_wait_for_hash_passes_the_route_as_playwright_argument() -> None:
    class Page:
        def __init__(self) -> None:
            self.call = None

        def wait_for_function(self, expression, **kwargs) -> None:
            self.call = (expression, kwargs)

    page = Page()

    assert wait_for_hash(page, "/AS/B160/")
    assert page.call[1] == {"arg": "/AS/B160/", "timeout": 3_000}


def test_open_route_fresh_sets_address_then_reloads() -> None:
    class Page:
        def __init__(self) -> None:
            self.url = "https://www.bet365.com/#/AS/B160/"
            self.visited = None
            self.reloaded = False

        def goto(self, destination: str, **_kwargs) -> None:
            self.visited = destination
            self.url = destination

        def reload(self, **_kwargs) -> None:
            self.reloaded = True

    page = Page()

    open_route_fresh(page, "/AC/B160/C1/D1/E2/F2/")

    assert page.visited == "https://www.bet365.com/#/AC/B160/C1/D1/E2/F2/"
    assert page.reloaded


def test_browser_is_headed_by_default(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["download_bet365_sumo_odds.py"])

    assert parse_args().headed is True


def test_headless_is_an_explicit_option(monkeypatch) -> None:
    monkeypatch.setattr(
        sys, "argv", ["download_bet365_sumo_odds.py", "--headless"]
    )

    assert parse_args().headed is False

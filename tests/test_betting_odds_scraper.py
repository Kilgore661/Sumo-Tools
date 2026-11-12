from __future__ import annotations

from zoneinfo import ZoneInfo

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

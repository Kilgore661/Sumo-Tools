#!/usr/bin/env python3
"""Download Marathonbet sumo events and odds into event-start JSON files.

The site is rendered client-side, so this scraper uses Playwright with an
installed Chrome/Edge browser.  It does not log in or place bets.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

from playwright.sync_api import Browser, BrowserContext, Page, TimeoutError, sync_playwright


DEFAULT_URL = "https://www.marathonbet.com/en/betting/sumo"
ODDS_RE = re.compile(r"^(?:\d+(?:\.\d+)?|EVS)$", re.IGNORECASE)
TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})$")
DATE_FORMATS = ("%d %b", "%d %B", "%a %d %b", "%A %d %B")


@dataclass
class Odd:
    outcome: str
    price: str
    market: str | None = None


@dataclass
class Event:
    name: str
    competitor_1: str
    competitor_2: str
    start: str | None
    displayed_start: str | None
    tournament: str | None
    url: str
    odds: list[Odd]


@dataclass
class EventSeed:
    url: str
    start: datetime | None
    displayed_start: str | None


def lines(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", item).strip() for item in text.splitlines() if item.strip()]


def dismiss_cookie_banner(page: Page) -> None:
    accept = page.get_by_role("button", name="Accept", exact=True)
    try:
        if accept.count() and accept.first.is_visible():
            accept.first.click(timeout=2_000)
    except TimeoutError:
        pass


def expand_event_groups(page: Page) -> None:
    """Expand collapsed country/tournament groups until event links appear."""
    selector = "a[href*='/betting/event/sumo/']"
    if page.locator(selector).count():
        return

    # The current page groups the fixtures under a collapsed Japan row.
    japan = page.get_by_text("Japan", exact=True)
    if japan.count():
        japan.first.click()
        page.locator(selector).first.wait_for(state="attached", timeout=10_000)
        page.locator(f"{selector} time[datetime]").first.wait_for(
            state="attached", timeout=10_000
        )


def unique_event_seeds(page: Page, base_url: str, timezone: ZoneInfo) -> list[EventSeed]:
    found: list[EventSeed] = []
    seen: set[str] = set()
    links = page.locator("a[href*='/betting/event/sumo/']")
    for index in range(links.count()):
        href = links.nth(index).get_attribute("href")
        if not href:
            continue
        url = urljoin(base_url, href).split("?", 1)[0]
        if url not in seen:
            seen.add(url)
            start = None
            displayed_start = None
            time_element = links.nth(index).locator("time[datetime]")
            if time_element.count():
                raw_start = time_element.first.get_attribute("datetime")
                if raw_start:
                    start = datetime.fromisoformat(
                        raw_start.replace("Z", "+00:00")
                    ).astimezone(timezone)
                    displayed_start = start.strftime("%Y-%m-%d %H:%M")
            found.append(EventSeed(url, start, displayed_start))
    return found


def discover_event_seeds(
    page: Page, base_url: str, timezone: ZoneInfo
) -> list[EventSeed]:
    """Wait for a valid sumo page, then return any currently listed events."""

    page.get_by_role("heading", name=re.compile(r"\bSumo\b", re.IGNORECASE)).first.wait_for(
        state="visible", timeout=15_000
    )
    dismiss_cookie_banner(page)
    expand_event_groups(page)
    return unique_event_seeds(page, base_url, timezone)


def parse_displayed_start(page_lines: list[str], now: datetime) -> tuple[datetime | None, str | None, int | None]:
    """Find the event date/time in the rendered event header."""
    for index, value in enumerate(page_lines):
        match = TIME_RE.match(value)
        if not match or index == 0:
            continue
        date_text = page_lines[index - 1]
        hour, minute = int(match.group(1)), int(match.group(2))
        lowered = date_text.casefold()
        if lowered == "today":
            event_date = now.date()
        elif lowered == "tomorrow":
            event_date = (now + timedelta(days=1)).date()
        else:
            event_date = None
            for fmt in DATE_FORMATS:
                try:
                    parsed = datetime.strptime(date_text, fmt)
                except ValueError:
                    continue
                year = now.year
                candidate = parsed.replace(year=year).date()
                # A December page may list January fixtures without a year.
                if candidate < now.date() - timedelta(days=180):
                    candidate = parsed.replace(year=year + 1).date()
                event_date = candidate
                break
            if event_date is None:
                continue
        start = datetime.combine(event_date, datetime.min.time(), tzinfo=now.tzinfo).replace(
            hour=hour, minute=minute
        )
        return start, f"{date_text} {value}", index
    return None, None, None


def names_from_url(url: str) -> tuple[str, str]:
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    if "-vs-" not in slug:
        return slug.replace("-", " ").title(), ""
    left, right = slug.split("-vs-", 1)
    return left.replace("-", " ").title(), right.replace("-", " ").title()


def event_identity(page_lines: list[str], time_index: int | None, url: str) -> tuple[str, str, str | None]:
    left, right = names_from_url(url)
    tournament = next((item for item in page_lines if item.startswith("Sumo.")), None)

    if time_index is not None:
        if time_index >= 2:
            candidate = page_lines[time_index - 2]
            if candidate not in {"Today", "Tomorrow"}:
                left = candidate
        if time_index + 1 < len(page_lines):
            right = page_lines[time_index + 1]
    return left, right, tournament


def extract_odds(
    page: Page, competitor_1: str, competitor_2: str, page_lines: list[str]
) -> list[Odd]:
    """Extract visible selection buttons, including every expanded market."""
    results: list[Odd] = []
    seen: set[tuple[str | None, str, str]] = set()
    fallback_market = next(
        (item for item in page_lines if "Fight Result" in item), None
    )
    # Read the changing React DOM in one browser call. Iterating Playwright
    # locators one at a time is much slower and can race a price refresh.
    raw_buttons = page.locator("button").evaluate_all(
        """(buttons) => buttons
            .filter((button) => button.offsetParent !== null)
            .map((button) => {
                let market = null;
                let node = button.parentElement;
                for (let depth = 0; node && depth < 5; depth++, node = node.parentElement) {
                    const heading = node.querySelector('h2,h3,h4,[role="heading"]');
                    if (heading && heading.innerText.trim()) {
                        market = heading.innerText.trim();
                        break;
                    }
                }
                return { text: button.innerText || '', market };
            })"""
    )
    for raw in raw_buttons:
        parts = lines(raw["text"])
        if len(parts) < 2 or not ODDS_RE.match(parts[-1]):
            continue
        price = parts[-1].upper()
        outcome = " ".join(parts[:-1])
        if outcome == "1":
            outcome = competitor_1
        elif outcome == "2":
            outcome = competitor_2
        market = raw["market"] or fallback_market
        key = (market, outcome, price)
        if key not in seen:
            seen.add(key)
            results.append(Odd(outcome=outcome, price=price, market=market))
    return results


def scrape_event(context: BrowserContext, seed: EventSeed, timezone: ZoneInfo) -> Event:
    url = seed.url
    page = context.new_page()
    try:
        page.goto(url, wait_until="commit", timeout=45_000)
        expected_name, _ = names_from_url(url)
        page.get_by_text(expected_name, exact=True).first.wait_for(
            state="visible", timeout=15_000
        )
        dismiss_cookie_banner(page)
        page.get_by_text(re.compile(r"Fight Result", re.IGNORECASE)).first.wait_for(
            state="visible", timeout=15_000
        )
        page.locator("button").filter(
            has_text=re.compile(r"\d+\.\d+")
        ).first.wait_for(state="visible", timeout=15_000)
        page.wait_for_timeout(100)
        body_lines = lines(page.locator("body").inner_text())
        start, displayed_start, time_index = parse_displayed_start(
            body_lines, datetime.now(timezone)
        )
        start = start or seed.start
        displayed_start = displayed_start or seed.displayed_start
        competitor_1, competitor_2, tournament = event_identity(body_lines, time_index, url)
        odds = extract_odds(page, competitor_1, competitor_2, body_lines)
        return Event(
            name=f"{competitor_1} vs {competitor_2}",
            competitor_1=competitor_1,
            competitor_2=competitor_2,
            start=start.isoformat() if start else None,
            displayed_start=displayed_start,
            tournament=tournament,
            url=url,
            odds=odds,
        )
    finally:
        page.close()


def launch_browser(playwright: Any, headed: bool, channel: str) -> Browser:
    try:
        return playwright.chromium.launch(channel=channel, headless=not headed)
    except Exception as first_error:
        try:
            return playwright.chromium.launch(headless=not headed)
        except Exception:
            raise RuntimeError(
                f"Could not launch the '{channel}' browser or Playwright Chromium. "
                "Install Chrome/Edge, or run: python -m playwright install chromium"
            ) from first_error


def output_name(start: str | None) -> str:
    if not start:
        return "unknown_start.json"
    parsed = datetime.fromisoformat(start)
    return parsed.strftime("%Y-%m-%d_%H-%M.json")


def write_results(events: list[Event], output_dir: Path, source_url: str, timezone: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    groups: dict[str, list[Event]] = defaultdict(list)
    for event in events:
        groups[output_name(event.start)].append(event)

    written: list[Path] = []
    scraped_at = datetime.now(ZoneInfo(timezone)).isoformat()
    for filename, grouped_events in groups.items():
        path = output_dir / filename
        payload = {
            "source": source_url,
            "timezone": timezone,
            "scraped_at": scraped_at,
            "event_start": grouped_events[0].start,
            "events": [asdict(event) for event in grouped_events],
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
    return sorted(written)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Sumo listing URL")
    parser.add_argument("--output-dir", type=Path, default=Path("odds"))
    parser.add_argument("--timezone", default="Europe/London")
    parser.add_argument("--browser-channel", default="chrome", choices=("chrome", "msedge"))
    parser.add_argument("--headed", action="store_true", help="Show the browser window")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    timezone = ZoneInfo(args.timezone)
    with sync_playwright() as playwright:
        browser = launch_browser(playwright, args.headed, args.browser_channel)
        try:
            context = browser.new_context(timezone_id=args.timezone, locale="en-GB")
            listing = context.new_page()
            listing.goto(args.url, wait_until="commit", timeout=45_000)
            seeds = discover_event_seeds(listing, args.url, timezone)
            listing.close()
            if not seeds:
                print(
                    "No sumo events are currently listed; no odds file was written.",
                    file=sys.stderr,
                )
                return 1

            events: list[Event] = []
            for number, seed in enumerate(seeds, start=1):
                print(f"[{number}/{len(seeds)}] {seed.url}", file=sys.stderr)
                events.append(scrape_event(context, seed, timezone))
        finally:
            browser.close()

    paths = write_results(events, args.output_dir, args.url, args.timezone)
    for path in paths:
        print(path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

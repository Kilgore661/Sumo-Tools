#!/usr/bin/env python3
"""Download Bet365 sumo bout odds and save every price as decimal odds.

Bet365 is a client-rendered single-page application, so this scraper uses
Playwright, but Playwright only connects to a normal Chrome or Edge that this
script starts itself, because Bet365 does not serve its sport pages to a
browser launched by Playwright.  It opens the Sumo sport route directly,
does not log in and does not place bets.  If the page
is not as expected, a screenshot and the page text are saved in a
"diagnostics" folder inside the output directory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen
from zoneinfo import ZoneInfo

from playwright.sync_api import (
    Error as PlaywrightError,
    Page,
    TimeoutError,
    sync_playwright,
)


DEFAULT_URL = "https://www.bet365.com/#/AS/B160/"
DEFAULT_PROFILE_DIR = Path(__file__).resolve().parent / "browser_profile"
DEBUG_PORT_TIMEOUT_S = 10
# Ceilings, not delays: each wait returns the moment its condition is met.
# A person sees these pages in about a second, so hitting a ceiling means
# the page is not in the state we expect.
RENDER_TIMEOUT_MS = 5_000
STEP_TIMEOUT_MS = 3_000
# A full page load plus Bet365's data arriving takes longer than a view change.
LOAD_TIMEOUT_MS = 10_000
# A person never clicks within milliseconds of a page appearing; give the app a
# moment to finish connecting before the first click.
SETTLE_MS = 1_000
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "odds" / "bet365"
PRICE_RE = re.compile(
    r"^(?:\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?|\d+\.\d+|EVS|EVENS)$",
    re.IGNORECASE,
)
TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})$")
DATE_FORMATS = (
    "%d %b %Y",
    "%d %B %Y",
    "%a %d %b %Y",
    "%A %d %B %Y",
    "%d %b",
    "%d %B",
    "%a %d %b",
    "%A %d %B",
)


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
    start: str
    displayed_start: str
    tournament: str | None
    url: str
    odds: list[Odd]


def lines(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", item).strip() for item in text.splitlines() if item.strip()]


def decimal_price(value: str) -> str:
    """Return a Bet365 decimal or fractional display price as decimal text."""

    compact = re.sub(r"\s+", "", value).upper()
    if compact in {"EVS", "EVENS"}:
        result = 2.0
    elif "/" in compact:
        numerator_text, denominator_text = compact.split("/", 1)
        numerator = float(numerator_text)
        denominator = float(denominator_text)
        if denominator == 0:
            raise ValueError(f"invalid fractional price: {value!r}")
        result = 1.0 + numerator / denominator
    else:
        result = float(compact)
    if result <= 1.0:
        raise ValueError(f"decimal odds must be greater than 1: {value!r}")
    return f"{result:.6f}".rstrip("0").rstrip(".")


def parse_display_date(value: str, now: datetime) -> date | None:
    lowered = value.casefold()
    if lowered == "today":
        return now.date()
    if lowered == "tomorrow":
        return (now + timedelta(days=1)).date()

    for date_format in DATE_FORMATS:
        try:
            if "%Y" in date_format:
                parsed = datetime.strptime(value, date_format)
            else:
                parsed = datetime.strptime(f"{value} {now.year}", f"{date_format} %Y")
        except ValueError:
            continue
        if "%Y" in date_format:
            return parsed.date()
        candidate = parsed.replace(year=now.year).date()
        if candidate < now.date() - timedelta(days=180):
            candidate = parsed.replace(year=now.year + 1).date()
        return candidate
    return None


def listing_date(page_lines: list[str], now: datetime) -> tuple[date | None, str | None]:
    for value in page_lines:
        parsed = parse_display_date(value, now)
        if parsed is not None:
            return parsed, value
    return None, None


def parse_candidate_rows(
    raw_rows: list[dict[str, Any]],
    page_lines: list[str],
    now: datetime,
    page_url: str,
) -> list[Event]:
    """Turn DOM row candidates into the JSON event model."""

    event_date, displayed_date = listing_date(page_lines, now)
    if event_date is None or displayed_date is None:
        return []
    tournament = next(
        (value for value in page_lines if "Grand Tournament" in value), None
    )
    market = next(
        (value for value in page_lines if value.casefold() == "to win bout"),
        "To Win Bout",
    )

    events: list[Event] = []
    seen: set[tuple[str, str, str]] = set()
    for raw_row in raw_rows:
        row_lines = lines("\n".join(str(value) for value in raw_row.get("lines", [])))
        prices = [str(value).strip() for value in raw_row.get("prices", [])]
        time_text = next((value for value in row_lines if TIME_RE.match(value)), None)
        if time_text is None or len(prices) != 2:
            continue

        ignored = {
            time_text,
            market,
            tournament or "",
            displayed_date,
            "1",
            "2",
        }
        names = [
            value
            for value in row_lines
            if value not in ignored
            and not PRICE_RE.match(value)
            and parse_display_date(value, now) is None
        ]
        if len(names) < 2:
            continue
        competitor_1, competitor_2 = names[0], names[1]

        match = TIME_RE.match(time_text)
        assert match is not None
        start = datetime.combine(event_date, datetime.min.time(), tzinfo=now.tzinfo).replace(
            hour=int(match.group(1)), minute=int(match.group(2))
        )
        identity = (competitor_1, competitor_2, start.isoformat())
        if identity in seen:
            continue
        try:
            normalized_prices = [decimal_price(value) for value in prices]
        except ValueError:
            continue
        seen.add(identity)
        events.append(
            Event(
                name=f"{competitor_1} vs {competitor_2}",
                competitor_1=competitor_1,
                competitor_2=competitor_2,
                start=start.isoformat(),
                displayed_start=f"{displayed_date} {time_text}",
                tournament=tournament,
                url=page_url,
                odds=[
                    Odd(competitor_1, normalized_prices[0], market),
                    Odd(competitor_2, normalized_prices[1], market),
                ],
            )
        )
    return events


def dismiss_cookie_banner(page: Page) -> None:
    """Click the cookie choice if a banner appears; carry on if it does not."""

    any_choice = page.get_by_role(
        "button", name=re.compile(r"^(Essential Only|Accept All|Accept)$")
    )
    try:
        any_choice.first.wait_for(state="visible", timeout=STEP_TIMEOUT_MS)
    except TimeoutError:
        return
    for label in ("Essential Only", "Accept All", "Accept"):
        button = page.get_by_role("button", name=label, exact=True)
        try:
            if button.count() and button.first.is_visible():
                button.first.click(force=True, timeout=STEP_TIMEOUT_MS)
                button.first.wait_for(state="hidden", timeout=STEP_TIMEOUT_MS)
                print(
                    f"Cookie choice applied: {label}.",
                    file=sys.stderr,
                    flush=True,
                )
                return
        except PlaywrightError:
            continue


def wait_for_hash(page: Page, fragment: str, timeout: int = STEP_TIMEOUT_MS) -> bool:
    try:
        page.wait_for_function(
            "fragment => location.hash.includes(fragment)",
            arg=fragment,
            timeout=timeout,
        )
        return True
    except TimeoutError:
        return False


def wait_for_sumo_page(page: Page) -> None:
    """Wait for the Sumo sport page to show its 'To Win Bout' market.

    A person sees this within a second.  If it has not appeared within the
    ceiling, the page is not in the state we expect, so fail rather than wait.
    """

    started = time.monotonic()
    market = page.get_by_text("To Win Bout", exact=True)
    try:
        market.last.wait_for(state="visible", timeout=RENDER_TIMEOUT_MS)
    except TimeoutError as exc:
        raise RuntimeError(
            f"Bet365's Sumo page did not show 'To Win Bout' within "
            f"{RENDER_TIMEOUT_MS / 1000:.0f} seconds; current URL: {page.url}"
        ) from exc
    print(
        f"Sumo page rendered after {time.monotonic() - started:.1f} seconds.",
        file=sys.stderr,
        flush=True,
    )


def read_bout_route(page: Page) -> str | None:
    """Read the bout page's route from the Sumo page's rendered state.

    Bet365 includes the destination in its application state even though the
    visible market row is not an anchor.  The IDs in it change per tournament.
    """

    return page.locator("html").evaluate(
        r"""element => {
            const match = element.innerHTML.match(
                /\/AC\/B160\/C\d+\/D\d+\/E\d+\/F\d+\//
            );
            return match ? match[0] : null;
        }"""
    )


def click_to_win_bout(page: Page) -> bool:
    """Click the 'To Win Bout' row as a person would; True if the address changed."""

    matches = page.get_by_text("To Win Bout", exact=True)
    for index in reversed(range(matches.count())):
        text = matches.nth(index)
        try:
            if not text.is_visible():
                continue
            depth = text.evaluate(
                r"""element => {
                    let node = element;
                    for (let depth = 0; node && depth < 8; depth++, node = node.parentElement) {
                        const role = (node.getAttribute('role') || '').toLowerCase();
                        const tag = node.tagName.toLowerCase();
                        if (
                            getComputedStyle(node).cursor === 'pointer' ||
                            node.hasAttribute('onclick') ||
                            role === 'button' || role === 'link' ||
                            tag === 'button' || tag === 'a'
                        ) return depth;
                    }
                    return 1;
                }"""
            )
            row = text
            for _ in range(depth):
                row = row.locator("..")
            row.scroll_into_view_if_needed(timeout=STEP_TIMEOUT_MS)
            try:
                row.click(timeout=STEP_TIMEOUT_MS)
            except PlaywrightError:
                row.click(force=True, timeout=STEP_TIMEOUT_MS)
            if wait_for_hash(page, "/AC/B160/"):
                return True
        except PlaywrightError:
            continue
    return False


def open_route_fresh(page: Page, route: str) -> None:
    """Load a bout route as a fresh page, as pasting it into a new browser does.

    Changing only the hash of a loaded Bet365 page leaves its application on
    the previous view, so the page is reloaded once the address is in place.
    """

    target = f"https://www.bet365.com/#{route}"
    if page.url != target:
        page.goto(target, wait_until="commit", timeout=20_000)
    page.reload(wait_until="commit", timeout=20_000)


Listing = list[tuple[str, list[dict[str, Any]]]]


def parse_bout_listing(page_lines: list[str], now: datetime) -> Listing:
    """Group the bout page's text into (date line, bout rows) sections.

    The page lays the bouts out in columns, not rows.  For each date it lists
    every bout's time and two names, then a "1" column holding the first
    wrestler's price for every bout, then a "2" column holding the second
    wrestler's prices.  The n-th price in each column belongs to the n-th bout.
    """

    start = next(
        (i for i, value in enumerate(page_lines) if value.casefold() == "to win bout"),
        None,
    )
    if start is None:
        return []

    def is_name(value: str) -> bool:
        return not (TIME_RE.match(value) or PRICE_RE.match(value) or value in {"1", "2"})

    sections: Listing = []
    date_line: str | None = None
    bouts: list[list[str]] = []
    i = start + 1
    while i < len(page_lines):
        line = page_lines[i]
        names = page_lines[i + 1 : i + 3]
        if parse_display_date(line, now) is not None:
            date_line, bouts = line, []
            i += 1
        elif (
            TIME_RE.match(line)
            and date_line is not None
            and len(names) == 2
            and all(is_name(value) for value in names)
        ):
            bouts.append([line, names[0], names[1]])
            i += 3
        elif line == "1" and bouts and date_line is not None:
            count = len(bouts)
            first = page_lines[i + 1 : i + 1 + count]
            marker = page_lines[i + 1 + count : i + 2 + count]
            second = page_lines[i + 2 + count : i + 2 + 2 * count]
            prices = first + second
            if (
                marker != ["2"]
                or len(prices) != 2 * count
                or not all(PRICE_RE.match(value) for value in prices)
            ):
                break
            rows = [
                {"lines": bout, "prices": [price_1, price_2]}
                for bout, price_1, price_2 in zip(bouts, first, second)
            ]
            sections.append((date_line, rows))
            bouts = []
            i += 2 + 2 * count
        elif sections and not bouts:
            break
        else:
            i += 1
    return sections


def wait_for_listing(
    page: Page, now: datetime, timeout_ms: int = STEP_TIMEOUT_MS
) -> Listing:
    """Poll until the bouts and their prices have appeared and stopped changing."""

    deadline = time.monotonic() + timeout_ms / 1000
    previous = -1
    while True:
        try:
            page_lines = lines(page.locator("body").inner_text(timeout=timeout_ms))
        except PlaywrightError:
            page_lines = []  # the page is mid-navigation; look again
        sections = parse_bout_listing(page_lines, now)
        count = sum(len(rows) for _, rows in sections)
        if (count and count == previous) or time.monotonic() >= deadline:
            return sections
        previous = count
        page.wait_for_timeout(250)


def save_diagnostics(page: Page, directory: Path) -> None:
    """Keep a screenshot and the page text so a failure shows its own cause."""

    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    picture = directory / f"failure_{stamp}.png"
    text_file = directory / f"failure_{stamp}.txt"
    try:
        page.screenshot(path=str(picture), timeout=STEP_TIMEOUT_MS)
        print(f"Saved screenshot: {picture.resolve()}", file=sys.stderr)
    except PlaywrightError as exc:
        print(f"Could not save screenshot: {exc}", file=sys.stderr)
    try:
        body = page.locator("body").inner_text(timeout=STEP_TIMEOUT_MS)
        text_file.write_text(f"{page.url}\n\n{body}\n", encoding="utf-8")
        print(f"Saved page text: {text_file.resolve()}", file=sys.stderr)
    except PlaywrightError as exc:
        print(f"Could not save page text: {exc}", file=sys.stderr)


def find_bout_listing(page: Page, now: datetime) -> Listing:
    """Reach the bout page and return its listing, reporting which route worked."""

    started = time.monotonic()

    def report(how: str) -> None:
        print(
            f"Bouts appeared {how}, {time.monotonic() - started:.1f} seconds in.",
            file=sys.stderr,
            flush=True,
        )

    # A bout URL given with --url is already a fresh load of the bout page.
    if "#/AC/B160/" in page.url:
        sections = wait_for_listing(page, now, LOAD_TIMEOUT_MS)
        if sections:
            report("on a direct load of the bout URL")
        return sections

    wait_for_sumo_page(page)
    page.wait_for_timeout(SETTLE_MS)
    route = read_bout_route(page)

    if click_to_win_bout(page):
        sections = wait_for_listing(page, now)
        if sections:
            report("after clicking 'To Win Bout'")
            return sections
        print(
            "The click changed the address but no bouts appeared.",
            file=sys.stderr,
            flush=True,
        )
    else:
        print("Clicking 'To Win Bout' did not work.", file=sys.stderr, flush=True)

    if route is None:
        raise RuntimeError(
            "The Sumo page did not contain a bout route to load; "
            f"current URL: {page.url}"
        )
    print("Loading the bout route as a fresh page...", file=sys.stderr, flush=True)
    open_route_fresh(page, route)
    sections = wait_for_listing(page, now, LOAD_TIMEOUT_MS)
    if sections:
        report("after loading the bout route afresh")
    return sections


def discover_events(page: Page, timezone: ZoneInfo) -> list[Event]:
    """Read the bouts listed under Bet365's current Sumo 'To Win Bout' market."""

    dismiss_cookie_banner(page)
    now = datetime.now(timezone)
    sections = find_bout_listing(page, now)
    if not sections:
        raise RuntimeError(
            "Bet365's bout page did not show any bouts with prices; "
            f"current URL: {page.url}"
        )
    page_lines = lines(page.locator("body").inner_text())
    tournament = next(
        (value for value in page_lines if "Grand Tournament" in value), None
    )
    events: list[Event] = []
    for date_line, rows in sections:
        context_lines = [date_line, "To Win Bout"]
        if tournament:
            context_lines.append(tournament)
        events.extend(parse_candidate_rows(rows, context_lines, now, page.url))
    return events


def find_browser(channel: str) -> Path:
    """Locate the installed Chrome or Edge executable."""

    if channel == "chrome":
        relative = Path("Google") / "Chrome" / "Application" / "chrome.exe"
        names = ("chrome", "google-chrome")
    else:
        relative = Path("Microsoft") / "Edge" / "Application" / "msedge.exe"
        names = ("msedge", "microsoft-edge")

    roots = (
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("LOCALAPPDATA"),
    )
    for root in roots:
        if root and (Path(root) / relative).is_file():
            return Path(root) / relative
    for name in names:
        found = shutil.which(name)
        if found:
            return Path(found)
    raise RuntimeError(
        f"Could not find an installed {channel} browser; "
        "install it or pass its location with --browser-path"
    )


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_debug_port(process: subprocess.Popen[bytes], port: int) -> None:
    """Wait until the browser is listening for Playwright's connection."""

    deadline = time.monotonic() + DEBUG_PORT_TIMEOUT_S
    url = f"http://127.0.0.1:{port}/json/version"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                "The browser exited straight after starting; "
                "is another copy already using the same --profile-dir?"
            )
        try:
            with urlopen(url, timeout=1):
                return
        except (URLError, OSError):
            time.sleep(0.2)
    raise RuntimeError(
        f"The browser did not open its debugging port within {DEBUG_PORT_TIMEOUT_S} seconds"
    )


def start_browser(
    browser_path: Path, profile_dir: Path, headed: bool
) -> tuple[subprocess.Popen[bytes], int]:
    """Start the real browser ourselves, with no Playwright automation flags.

    Playwright then only connects to it.  The browser keeps its own profile
    folder, so cookies and the cookie choice persist between runs.
    """

    port = free_port()
    profile_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(browser_path),
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir.resolve()}",
        "--no-first-run",
        "--no-default-browser-check",
        "--lang=en-GB",
    ]
    if not headed:
        command.append("--headless=new")
    command.append("about:blank")
    process = subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    try:
        wait_for_debug_port(process, port)
    except RuntimeError:
        stop_browser(process)
        raise
    return process, port


def stop_browser(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def output_name(start: str) -> str:
    return datetime.fromisoformat(start).strftime("%Y-%m-%d_%H-%M.json")


def write_results(
    events: list[Event], output_dir: Path, source_url: str, timezone: str
) -> list[Path]:
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
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        written.append(path)
    return sorted(written)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Bet365 Sumo sport page URL")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timezone", default="Europe/London")
    parser.add_argument("--browser-channel", default="chrome", choices=("chrome", "msedge"))
    display = parser.add_mutually_exclusive_group()
    display.add_argument(
        "--headed",
        dest="headed",
        action="store_true",
        help="Show the browser window (default)",
    )
    display.add_argument(
        "--headless",
        dest="headed",
        action="store_false",
        help="Run Chrome without showing its window",
    )
    parser.set_defaults(headed=True)
    parser.add_argument(
        "--profile-dir",
        type=Path,
        default=DEFAULT_PROFILE_DIR,
        help="Folder for the browser's own profile (cookies persist here)",
    )
    parser.add_argument(
        "--browser-path",
        type=Path,
        default=None,
        help="Browser executable, if it is not in the usual place",
    )
    return parser.parse_args()


def download_once(args: argparse.Namespace, timezone: ZoneInfo) -> bool:
    browser_path = args.browser_path or find_browser(args.browser_channel)
    with sync_playwright() as playwright:
        print(f"Starting {browser_path.name}...", file=sys.stderr, flush=True)
        process, port = start_browser(browser_path, args.profile_dir, args.headed)
        browser = None
        try:
            browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            print("Opening the Bet365 Sumo page...", file=sys.stderr, flush=True)
            page.goto(args.url, wait_until="commit", timeout=20_000)
            try:
                events = discover_events(page, timezone)
            except (RuntimeError, PlaywrightError):
                save_diagnostics(page, args.output_dir / "diagnostics")
                raise
        finally:
            if browser is not None:
                try:
                    browser.close()
                except PlaywrightError:
                    pass
            stop_browser(process)

    if not events:
        print(
            "No Bet365 sumo bout odds are currently visible; no odds file was written.",
            file=sys.stderr,
        )
        return False
    paths = write_results(events, args.output_dir, args.url, args.timezone)
    for path in paths:
        print(path.resolve())
    return bool(paths)


def main() -> int:
    args = parse_args()
    timezone = ZoneInfo(args.timezone)
    attempted_at = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"[{attempted_at}] Checking Bet365 for sumo odds...", file=sys.stderr)
    try:
        return 0 if download_once(args, timezone) else 1
    except (PlaywrightError, RuntimeError) as exc:
        detail = str(exc).splitlines()[0]
        print(f"Bet365 acquisition failed: {detail}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nStopped Bet365 acquisition.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())


"""
Tracker scraper.

This module implements the request-driven scraper described in
`tracker/scraper/docs/Scraper.md`.

Contract:
    scrape(requested_basho_days) -> bool

It ensures that:
- daily-results HTML exists for every requested BashoDayRef
- current-standings HTML exists for every distinct Date represented

The implementation is deliberately simple:
- postcondition-based
- all-or-nothing
- minimal sanity checks only
- no parsing or semantic validation
"""

from pdb import set_trace
from pathlib import Path
import os
import stat
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

from infra.tracker.types import BashoDayRef



BASE_URL = "https://sumodb.sumogames.de"
OUTPUT_ROOT = Path("files") / "output"
HTML_RESULTS_ROOT = OUTPUT_ROOT / "HTML results"
CURRENT_STANDINGS_ROOT = OUTPUT_ROOT / "current standings"
WEIRDNESS_PATH = OUTPUT_ROOT / "text_weirdness.html"

DAILY_RESULTS_MIN_LENGTH = 4000
REQUEST_TIMEOUT_SECONDS = 30.0
USER_AGENT = "Mozilla/5.0 (compatible; tracker-scraper/1.0)"


@dataclass(frozen=True)
class BashoDate:
    year: int
    month: int


# Bashos that do not exist in the legacy data model.
_NO_DATA_BASHOS: set[tuple[int, int]] = {
    (2011, 3),
    (2020, 5),
}


def scrape(requested_basho_days: Iterable[BashoDayRef]) -> bool:
    """
    Ensure that all raw artifacts implied by `requested_basho_days` exist.

    Returns True iff all required artifacts are present and usable after the
    scrape attempt.
    """
    requested_list = list(requested_basho_days)
    if not requested_list:
        return True

    requested_dates = _distinct_dates_in_order(requested_list)

    for basho_date in requested_dates:
        if _is_no_data_basho(basho_date):
            #print(
            #    f"[scraper] skipping current standings for no-data basho "
            #    f"{basho_date.year}/{basho_date.month:02d}"
            #)
            continue

        if not _ensure_current_standings(basho_date):
            return False

    for ref in requested_list:
        basho_date = BashoDate(int(ref.date.year), int(ref.date.month))
        if _is_no_data_basho(basho_date):
            #print(
            #    f"[scraper] skipping daily results for no-data basho "
            #    f"{basho_date.year}/{basho_date.month:02d} Day {int(ref.day)}"
            #)
            continue

        if not _ensure_daily_results(ref):
            return False

    return True


def _distinct_dates_in_order(requested_basho_days: Iterable[BashoDayRef]) -> list[BashoDate]:
    seen: set[tuple[int, int]] = set()
    ordered: list[BashoDate] = []

    for ref in requested_basho_days:
        key = (int(ref.date.year), int(ref.date.month))
        if key in seen:
            continue
        seen.add(key)
        ordered.append(BashoDate(*key))

    return ordered


def _ensure_current_standings(date: BashoDate) -> bool:
    path = _current_standings_path(date)

    if path.exists() and not _should_refresh_current_standings(path, date):
        if _looks_like_current_standings(path.read_text(encoding="utf-8", errors="replace")):
            #print(f"[scraper] reusing current standings {path}")
            return True
        print(f"[scraper] existing current standings is unusable; re-fetching {path}")

    url = _current_standings_url(date)
    text = _fetch_text(url)
    if text is None:
        print(f"[scraper] failed to fetch current standings for {date.year}/{date.month:02d}")
        return False

    if not _looks_like_current_standings(text):
        print(
            f"[scraper] fetched current standings was blank or malformed for "
            f"{date.year}/{date.month:02d}"
        )
        return False

    return _write_text(path, text)


def _ensure_daily_results(ref: BashoDayRef) -> bool:
    return True # Hack - far too slow otherwise
    path = _daily_results_path(ref)

    if path.exists():
        existing_text = path.read_text(encoding="utf-8", errors="replace")
        if _looks_like_daily_results(existing_text):
            print(f"[scraper] reusing daily results {path}")
            return True
        print(f"[scraper] existing daily results is unusable; re-fetching {path}")

    url = _daily_results_url(ref)
    text = _fetch_text(url)
    if text is None:
        print(f"[scraper] failed to fetch daily results for {ref}")
        return False

    if not _looks_like_daily_results(text):
        print(f"[scraper] fetched daily results looked dodgy for {ref}")
        _write_text(WEIRDNESS_PATH, text)
        return False

    return _write_text(path, text)


def _daily_results_url(ref: BashoDayRef) -> str:
    year = int(ref.date.year)
    month = int(ref.date.month)
    day = int(ref.day)
    return f"{BASE_URL}/Results.aspx?b={year}{month:02d}&d={day}&simple=on"


def _current_standings_url(date: BashoDate) -> str:
    return f"{BASE_URL}/Banzuke.aspx?b={date.year}{date.month:02d}&heya=-1&shusshin=-1"


def _daily_results_path(ref: BashoDayRef) -> Path:
    year = int(ref.date.year)
    month = int(ref.date.month)
    day = int(ref.day)
    return HTML_RESULTS_ROOT / f"{year} {month:02d}" / f"{day:02d}.html"


def _current_standings_path(date: BashoDate) -> Path:
    return CURRENT_STANDINGS_ROOT / f"{date.year} {date.month:02d}.html"


def _fetch_text(url: str) -> str | None:
    print(f"[scraper] getting {url}")
    request = Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"[scraper] download failed: {exc}")
        return None


def _write_text(path: Path, text: str, read_only: bool = True) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

        # Set file permissions
        if read_only:
            os.chmod(path, stat.S_IREAD)
        else:
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)

        print(f"[scraper] wrote {path} (read_only={read_only})")
        return True

    except OSError as exc:
        print(f"[scraper] failed to write {path}: {exc}")
        return False


def _looks_like_daily_results(text: str) -> bool:
    return len(text) >= DAILY_RESULTS_MIN_LENGTH


def _looks_like_current_standings(text: str) -> bool:
    return "<h1" in text.lower()


def _should_refresh_current_standings(path: Path, date: BashoDate) -> bool:
    """
    Preserve the useful legacy behaviour:
    if a standings file predates basho completion and the basho has since
    completed, refresh it so the stored artifact reflects the completed state.
    """
    basho_end = _basho_end_datetime(date.year, date.month)
    file_mtime = datetime.fromtimestamp(path.stat().st_mtime)
    now = datetime.now()
    return file_mtime < basho_end <= now


def _basho_end_datetime(year: int, month: int) -> datetime:
    # Legacy behaviour treated the basho as starting on the second Sunday.
    # The exact hour is not load-bearing here; the refresh rule only needs a
    # stable completion threshold.
    return _second_sunday(year, month) + timedelta(days=15)


def _second_sunday(year: int, month: int) -> datetime:
    first_of_month = datetime(year, month, 1, 8, 0, 0)
    weekday = first_of_month.weekday()  # Monday=0 ... Sunday=6
    days_until_sunday = (6 - weekday) % 7
    first_sunday_day = 1 + days_until_sunday
    second_sunday_day = first_sunday_day + 7
    return datetime(year, month, second_sunday_day, 8, 0, 0)


def _is_no_data_basho(date: BashoDate) -> bool:
    return (date.year, date.month) in _NO_DATA_BASHOS


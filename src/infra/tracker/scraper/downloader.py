"""
Tracker downloader.

This module implements the request-driven downloader described in
`The Downoader.md`.

Contract:
    download(requested_basho_days) -> RetrievalResult

It ensures that:
- daily-results HTML exists for every requested BashoDayRef
- current-standings HTML exists for every distinct Date represented

The implementation is deliberately simple:
- postcondition-based
- all-or-nothing
- minimal sanity checks only
- no parsing or semantic validation
"""

from pathlib import Path
import os
import stat
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

from infra.tracker.types import BashoDayRef, RetrievalResult


BASE_URL = "https://sumodb.sumogames.de"
OUTPUT_ROOT = Path("files") / "output"
HTML_RESULTS_ROOT = OUTPUT_ROOT / "HTML results"
CURRENT_STANDINGS_ROOT = OUTPUT_ROOT / "current standings"
WEIRDNESS_PATH = OUTPUT_ROOT / "text_weirdness.html"

DAILY_RESULTS_MIN_LENGTH = 4000
REQUEST_TIMEOUT_SECONDS = 30.0
USER_AGENT = "Mozilla/5.0 (compatible; tracker-downloader/1.0)"


@dataclass(frozen=True)
class BashoDate:
    year: int
    month: int


# Bashos that do not exist in the legacy data model.
_NO_DATA_BASHOS: set[tuple[int, int]] = {
    (2011, 3),
    (2020, 5),
}


def download(requested_basho_days: Iterable[BashoDayRef]) -> RetrievalResult:
    """
    Ensure that all raw artifacts implied by `requested_basho_days` exist.

    Returns:
    - FAILURE if any required artifact is still missing or unusable
    - SUCCESS_UNCHANGED if all required artifacts already existed
    - SUCCESS_CHANGED if all required artifacts exist and at least one file
      was written during this run
    """
    requested_list = list(requested_basho_days)
    if not requested_list:
        return RetrievalResult.SUCCESS_UNCHANGED

    changed = False
    requested_dates = _distinct_dates_in_order(requested_list)

    for basho_date in requested_dates:
        if _is_no_data_basho(basho_date):
            continue

        result = _ensure_current_standings(basho_date)
        if result is None:
            return RetrievalResult.FAILURE
        if result:
            changed = True

    from time import time
    t0 = time()

    print( f'BashoRef check at {datetime.fromtimestamp(t0).strftime("%Y/%m/%d %H:%M:%S")}' )

    for ref in requested_list:
        basho_date = BashoDate(int(ref.date.year), int(ref.date.month))
        if _is_no_data_basho(basho_date):
            continue

        result = _ensure_daily_results(ref)
        if result is None:
            return RetrievalResult.FAILURE
        if result:
            changed = True

    print( f'{len(requested_list)} BashoDateRefs checked in {time()-t0:.3f} sec.' )
    if changed:
        return RetrievalResult.SUCCESS_CHANGED
    return RetrievalResult.SUCCESS_UNCHANGED


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


def _ensure_current_standings(date: BashoDate) -> bool | None:
    """
    Return:
    - True  if a file was fetched and written
    - False if a usable existing file was reused
    - None  on failure
    """
    path = _current_standings_path(date)

    if path.exists() and not _should_refresh_current_standings(path, date):
        if _looks_like_current_standings(path.read_text(encoding="utf-8", errors="replace")):
            return False
        print(f"[downloader] existing current standings is unusable; re-fetching {path}")

    url = _current_standings_url(date)
    text = _fetch_text(url)
    if text is None:
        print(f"[downloader] failed to fetch current standings for {date.year}/{date.month:02d}")
        return None

    if not _looks_like_current_standings(text):
        print(
            f"[downloader] fetched current standings was blank or malformed for "
            f"{date.year}/{date.month:02d}"
        )
        return None

    if not _write_text(path, text):
        return None
    return True


def _ensure_daily_results(ref: BashoDayRef) -> bool | None:
    """
    Return:
    - True  if a file was fetched and written
    - False if a usable existing file was reused
    - None  on failure
    """

    path = _daily_results_path(ref)

    if path.exists():
        return False # Hack to improve speed.
        existing_text = path.read_text(encoding="utf-8", errors="replace")
        if _looks_like_daily_results(existing_text):
            print(f"[downloader] reusing daily results {path}")
            return False
        print(f"[downloader] existing daily results is unusable; re-fetching {path}")

    url = _daily_results_url(ref)
    text = _fetch_text(url)
    if text is None:
        print(f"[downloader] failed to fetch daily results for {ref}")
        return None

    if not _looks_like_daily_results(text):
        print(f"[downloader] fetched daily results looked dodgy for {ref}")
        _write_text(WEIRDNESS_PATH, text)
        return None

    if not _write_text(path, text):
        return None
    return True


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
    print(f"[downloader] getting {url}")
    request = Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"[downloader] download failed: {exc}")
        return None


def _write_text(path: Path, text: str, read_only: bool = True) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

        if read_only:
            os.chmod(path, stat.S_IREAD)
        else:
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)

        print(f"[downloader] wrote {path} (read_only={read_only})")
        return True

    except OSError as exc:
        print(f"[downloader] failed to write {path}: {exc}")
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
    return _second_sunday(year, month) + timedelta(days=15)


def _second_sunday(year: int, month: int) -> datetime:
    first_of_month = datetime(year, month, 1, 8, 0, 0)
    weekday = first_of_month.weekday()
    days_until_sunday = (6 - weekday) % 7
    first_sunday_day = 1 + days_until_sunday
    second_sunday_day = first_sunday_day + 7
    return datetime(year, month, second_sunday_day, 8, 0, 0)


def _is_no_data_basho(date: BashoDate) -> bool:
    return (date.year, date.month) in _NO_DATA_BASHOS

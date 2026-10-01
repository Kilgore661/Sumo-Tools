"""
Tracker downloader.

This module implements the request-driven downloader described in
`The Downoader.md`.

Contract:
    download(retrieval_plan) -> RetrievalResult

It ensures that:
- current-standings HTML exists for every requested banzuke date
- daily-results HTML exists for every requested BashoDayRef

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
from datetime import datetime
from time import time, sleep
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

from ..types import BashoDayRef, RetrievalPlan, RetrievalResult


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


def download(retrieval_plan: RetrievalPlan) -> RetrievalResult:
    """
    Ensure that all raw artifacts in `retrieval_plan` exist.

    Returns:
    - FAILURE if any required artifact is still missing or unusable
    - SUCCESS_UNCHANGED if all required artifacts already existed
    - SUCCESS_CHANGED if all required artifacts exist and at least one file
      was written during this run
    """
    requested_list = list(retrieval_plan.daily_results)
    requested_dates = [_to_basho_date(date) for date in retrieval_plan.banzuke_dates]

    if not requested_list and not requested_dates:
        return RetrievalResult.SUCCESS_UNCHANGED

    changed = False
    reused_banzuke_dates: set[BashoDate] = set()
    completed_banzuke_dates: list[BashoDate] = []

    for basho_date in requested_dates:
        if _is_no_data_basho(basho_date):
            continue

        result = _ensure_current_standings(basho_date)
        if result is None:
            return RetrievalResult.FAILURE
        if result:
            changed = True
        else:
            reused_banzuke_dates.add(basho_date)

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
            sleep( 0.5 )
            changed = True

            # SumoDB publishes final scores and prizes on the banzuke page,
            # rather than on the Day 15 results page.  We assume that the
            # banzuke page has been updated by the time Day 15 results become
            # available.  This cannot be verified against a live publication
            # cycle until the November 2026 basho.
            if int(ref.day) == 15:
                basho_date = BashoDate(int(ref.date.year), int(ref.date.month))
                if (
                    basho_date in reused_banzuke_dates
                    and basho_date not in completed_banzuke_dates
                ):
                    completed_banzuke_dates.append(basho_date)

    for basho_date in completed_banzuke_dates:
        print(
            "[downloader] Day 15 downloaded; refreshing current standings for "
            f"{basho_date.year}/{basho_date.month:02d}"
        )
        result = _ensure_current_standings(basho_date, force=True)
        if result is None:
            return RetrievalResult.FAILURE
        if result:
            changed = True

    print( f'{len(requested_list)} BashoDateRefs checked in {time()-t0:.3f} sec.' )
    if changed:
        return RetrievalResult.SUCCESS_CHANGED
    return RetrievalResult.SUCCESS_UNCHANGED


def _to_basho_date(date) -> BashoDate:
    return BashoDate(int(date.year), int(date.month))


def _ensure_current_standings(
    date: BashoDate,
    *,
    force: bool = False,
) -> bool | None:
    """
    Return:
    - True  if a file was fetched and written
    - False if a usable existing file was reused
    - None  on failure
    """
    path = _current_standings_path(date)

    if path.exists() and not force:
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


def _write_text(path: Path, text: str) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        # Read-only was a legacy safeguard for manually managed downloads.
        # Clear it before replacing an old cache entry and leave new downloads
        # writable: tracker-managed files must be refreshable by the tracker.
        if path.exists():
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        path.write_text(text, encoding="utf-8")
        print(f"[downloader] wrote {path}")
        return True

    except OSError as exc:
        print(f"[downloader] failed to write {path}: {exc}")
        return False


def _looks_like_daily_results(text: str) -> bool:
    return len(text) >= DAILY_RESULTS_MIN_LENGTH


def _looks_like_current_standings(text: str) -> bool:
    return "<h1" in text.lower()


def _is_no_data_basho(date: BashoDate) -> bool:
    return (date.year, date.month) in _NO_DATA_BASHOS

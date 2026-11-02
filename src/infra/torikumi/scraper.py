"""Acquire every published torikumi for the current History basho."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.sumo_core.BasicPrimitives import Day
from src.sumo_core.History import History

from .model import Future, FutureDay
from .parser import TorikumiParseError, parse_torikumi_page
from .persistence import DEFAULT_OUTPUT_ROOT, load_future, save_future
from .target import TorikumiTarget


BASE_URL = "https://sumodb.sumogames.de"
USER_AGENT = "Mozilla/5.0 (compatible; torikumi-scraper/1.0)"
REQUEST_TIMEOUT_SECONDS = 30.0


class TorikumiRefreshError(RuntimeError):
    """The selected target could not be refreshed coherently."""


def results_url(date, day: Day) -> str:
    return (
        f"{BASE_URL}/Results.aspx?b={int(date.year)}{int(date.month):02d}"
        f"&d={int(day)}&simple=on"
    )


def refresh_future(
    history: History,
    *,
    target: TorikumiTarget | None = None,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    fetch_text: Callable[[str], str | None] | None = None,
    now: datetime | None = None,
) -> Future:
    if not history:
        raise ValueError("Cannot refresh Future from an empty History")
    fetch = _fetch_text if fetch_text is None else fetch_text
    generated_at = now or datetime.now(timezone.utc)
    if target is None:
        date = max(history)
        latest = history[date].summary.last_defined()
    else:
        date = target.date
        latest = target.completed_through
    existing_path = output_root / "future.json"
    existing = load_future(existing_path) if existing_path.is_file() else None
    if existing is not None and existing.date == date:
        days_by_number = {int(day.day): day for day in existing.days}
        first_probe = max(days_by_number, default=1)
    else:
        days_by_number = {}
        first_probe = 1
    raw_pages: list[tuple[Path, str]] = []
    raw_root = output_root / "raw" / f"{int(date.year)} {int(date.month):02d}"

    for day_number in range(first_probe, 16):
        day = Day(day_number)
        url = results_url(date, day)
        try:
            html = fetch(url)
        except Exception as exc:
            if isinstance(exc, TorikumiRefreshError):
                raise
            raise TorikumiRefreshError(f"Could not download {url}: {exc}") from exc
        if html is None:
            break
        try:
            parsed = parse_torikumi_page(html, expected_date=date, expected_day=day)
        except TorikumiParseError as exc:
            if _looks_like_unpublished_results_shell(html, date=date, day=day):
                break
            raise TorikumiRefreshError(
                f"Unrecognised Results page for {date} Day {day_number}: {exc}"
            ) from exc
        raw_path = raw_root / f"{day_number:02d}.html"
        raw_pages.append((raw_path, html))
        if parsed.result_count:
            print(
                f"[torikumi] warning: Day {day_number} contains results for "
                f"{parsed.result_count}/{len(parsed.bouts)} bouts"
            )
        days_by_number[day_number] = FutureDay(
            day=day,
            bouts=parsed.bouts,
            source_url=url,
            downloaded_at=generated_at,
            result_count=parsed.result_count,
        )
        if fetch_text is None and day_number < 15:
            sleep(0.5)

    future = Future(
        date=date,
        completed_through=latest,
        days=tuple(days_by_number[day] for day in sorted(days_by_number)),
        generated_at=generated_at,
    )
    if existing is not None:
        if existing.date == date:
            existing_days = {int(day.day) for day in existing.days}
            refreshed_days = {int(day.day) for day in future.days}
            if not existing_days <= refreshed_days:
                raise TorikumiRefreshError(
                    f"Refresh for {date} would discard published days "
                    f"{sorted(existing_days - refreshed_days)}"
                )
    for raw_path, html in raw_pages:
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(html, encoding="utf-8")
    save_future(future, output_root / "future.json")
    return future


def _fetch_text(url: str) -> str | None:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise TorikumiRefreshError(f"download failed for {url}: {exc}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise TorikumiRefreshError(f"download failed for {url}: {exc}") from exc


def _looks_like_unpublished_results_shell(html: str, *, date, day: Day) -> bool:
    """Recognise SumoDB's valid HTTP-200 response for an unpublished day."""

    expected = (
        f"Results.aspx?b={int(date.year)}{int(date.month):02d}"
        f"&amp;d={int(day)}"
    )
    lower = html.lower()
    return (
        "sumodb" in lower
        and "text-only results" in lower
        and expected.lower() in lower
        and "<h1>" not in lower
    )


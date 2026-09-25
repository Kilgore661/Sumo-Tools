"""Acquire every published torikumi for the current History basho."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.sumo_core.BasicPrimitives import Day
from src.sumo_core.History import History

from .model import Future, FutureDay
from .parser import TorikumiParseError, parse_torikumi_page
from .persistence import DEFAULT_OUTPUT_ROOT, save_future


BASE_URL = "https://sumodb.sumogames.de"
USER_AGENT = "Mozilla/5.0 (compatible; torikumi-scraper/1.0)"
REQUEST_TIMEOUT_SECONDS = 30.0


def results_url(date, day: Day) -> str:
    return (
        f"{BASE_URL}/Results.aspx?b={int(date.year)}{int(date.month):02d}"
        f"&d={int(day)}&simple=on"
    )


def refresh_future(
    history: History,
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    fetch_text: Callable[[str], str | None] | None = None,
    now: datetime | None = None,
) -> Future:
    if not history:
        raise ValueError("Cannot refresh Future from an empty History")
    fetch = _fetch_text if fetch_text is None else fetch_text
    generated_at = now or datetime.now(timezone.utc)
    date = max(history)
    latest = history[date].summary.last_defined()
    cutoff = 0 if latest is None else int(latest)
    days = []
    raw_root = output_root / "raw" / f"{int(date.year)} {int(date.month):02d}"

    for day_number in range(1, 16):
        day = Day(day_number)
        url = results_url(date, day)
        html = fetch(url)
        if html is None:
            continue
        try:
            parsed = parse_torikumi_page(html, expected_date=date, expected_day=day)
        except TorikumiParseError:
            continue
        raw_path = raw_root / f"{day_number:02d}.html"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(html, encoding="utf-8")
        if parsed.result_count:
            print(
                f"[torikumi] warning: Day {day_number} contains results for "
                f"{parsed.result_count}/{len(parsed.bouts)} bouts"
            )
        days.append(
            FutureDay(
                day=day,
                bouts=parsed.bouts,
                source_url=url,
                downloaded_at=generated_at,
                result_count=parsed.result_count,
            )
        )

    future = Future(
        date=date,
        completed_through=latest,
        days=tuple(days),
        generated_at=generated_at,
    )
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
        print(f"[torikumi] download failed for {url}: {exc}")
        return None
    except (URLError, TimeoutError, OSError) as exc:
        print(f"[torikumi] download failed for {url}: {exc}")
        return None


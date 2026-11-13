"""Extract exact civil dates from downloaded SumoDB daily-result pages."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from src.sumo_core.History import Date

from .parser2_utils import RESULTS_DIR


DAILY_DATE_PATTERN = re.compile(
    r"<h1>\s*.*?, Day (\d+)\s*</h1><h2>\s*"
    r"([A-Za-z]+ \d{1,2}, \d{4})\s*</h2>",
    re.DOTALL,
)


@dataclass(frozen=True)
class BashoDateCoverage:
    basho: Date
    start_date: date | None
    source: str
    daily_dates: int
    consistent: bool
    warning: str


def parse_daily_calendar_date(html: str) -> tuple[int, date] | None:
    """Return the source day number and civil date from one results page."""

    match = DAILY_DATE_PATTERN.search(html)
    if match is None:
        return None
    return (
        int(match.group(1)),
        datetime.strptime(match.group(2), "%B %d, %Y").date(),
    )


def basho_date_coverage(
    basho: Date,
    *,
    results_root: Path = Path(RESULTS_DIR),
) -> BashoDateCoverage:
    """Resolve Day 1 from all available exact dates for one basho."""

    directory = results_root / f"{int(basho.year)} {int(basho.month):02d}"
    implied_starts: list[date] = []
    direct_day_one = False
    for path in sorted(directory.glob("*.html")):
        parsed = parse_daily_calendar_date(path.read_text(encoding="utf-8"))
        if parsed is None:
            continue
        day_number, calendar_date = parsed
        direct_day_one = direct_day_one or day_number == 1
        implied_starts.append(calendar_date - timedelta(days=day_number - 1))

    unique_starts = sorted(set(implied_starts))
    consistent = len(unique_starts) <= 1
    start_date = unique_starts[0] if len(unique_starts) == 1 else None
    if not implied_starts:
        warning = "no exact daily dates"
    elif not consistent:
        warning = "daily dates imply inconsistent Day 1 values"
    else:
        warning = ""
    source = "day_1" if direct_day_one else "reconstructed" if start_date else ""
    return BashoDateCoverage(
        basho=basho,
        start_date=start_date,
        source=source,
        daily_dates=len(implied_starts),
        consistent=consistent,
        warning=warning,
    )

"""Parse the torikumi carried by a SumoDB Results.aspx page."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape

from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.History import Date

from .model import FutureBout


_HEADER_RE = re.compile(
    r"<h1>\s*.*?\s+(?P<year>\d+),\s*Day\s+(?P<day>\d+)</h1>"
    r".*?<h2>.*?</h2>(?P<body>.*)",
    re.DOTALL | re.IGNORECASE,
)
_BANZUKE_RE = re.compile(r"Banzuke\.aspx\?b=(?P<basho>\d{6})", re.IGNORECASE)
_TABLE_RE = re.compile(r"<table(?P<table>.*?)</table>", re.DOTALL | re.IGNORECASE)
_ROW_RE = re.compile(r"<tr>(?P<row>.*?)</tr>", re.DOTALL | re.IGNORECASE)
_CELL_RE = re.compile(r"<td.*?>(?P<cell>.*?)</td>", re.DOTALL | re.IGNORECASE)
_RIKISHI_RE = re.compile(
    r"<a\s+.*?r=(?P<id>\d+).*?>(?P<name>.*?)</a>", re.DOTALL | re.IGNORECASE
)
_RESULT_VALUES = frozenset(Outcome.__members__)


class TorikumiParseError(ValueError):
    """The page did not contain a credible torikumi for the requested day."""


@dataclass(frozen=True, slots=True)
class ParsedTorikumi:
    date: Date
    day: Day
    bouts: tuple[FutureBout, ...]
    result_count: int


def parse_torikumi_page(html: str, *, expected_date: Date, expected_day: Day) -> ParsedTorikumi:
    header = _HEADER_RE.search(html)
    if header is None:
        raise TorikumiParseError("Results page header was not found")
    if int(header.group("year")) != int(expected_date.year):
        raise TorikumiParseError("Results page year does not match the requested basho")
    if int(header.group("day")) != int(expected_day):
        raise TorikumiParseError("Results page day does not match the requested day")

    banzuke = _BANZUKE_RE.search(html)
    expected_token = f"{int(expected_date.year)}{int(expected_date.month):02d}"
    if banzuke is None or banzuke.group("basho") != expected_token:
        raise TorikumiParseError("Results page basho does not match the requested basho")

    table = _TABLE_RE.search(header.group("body"))
    if table is None:
        raise TorikumiParseError("Results page torikumi table was not found")

    bouts: list[FutureBout] = []
    result_count = 0
    for row_match in _ROW_RE.finditer(table.group("table")):
        cells = [match.group("cell") for match in _CELL_RE.finditer(row_match.group("row"))]
        if len(cells) == 12:
            cells.insert(1, "?")
        if len(cells) < 13:
            continue
        east = _RIKISHI_RE.search(cells[5])
        west = _RIKISHI_RE.search(cells[11])
        if east is None or west is None:
            continue
        bouts.append(
            FutureBout(
                order=len(bouts) + 1,
                east=RikId(int(east.group("id"))),
                west=RikId(int(west.group("id"))),
                east_shikona=_plain_text(east.group("name")),
                west_shikona=_plain_text(west.group("name")),
            )
        )
        if cells[7].strip() in _RESULT_VALUES and cells[9].strip() in _RESULT_VALUES:
            result_count += 1

    if not bouts:
        raise TorikumiParseError("Results page contained no recognizable torikumi bouts")
    return ParsedTorikumi(
        date=expected_date,
        day=expected_day,
        bouts=tuple(bouts),
        result_count=result_count,
    )


def _plain_text(value: str) -> str:
    return unescape(re.sub(r"<.*?>", "", value)).strip()


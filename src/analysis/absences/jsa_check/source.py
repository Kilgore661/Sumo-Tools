"""Read independent final records from cached SumoDB banzuke pages."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from src.infra.parser.TableTypes import TableType
from src.infra.parser.parser2_stub import parse_body
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date

from .model import FinalRecord


DEFAULT_STANDINGS_ROOT = Path("files/output/current standings")
DEFAULT_RETIREMENT_ROOT = Path("files/output/rank_at_retirement")
_SOURCE_FILE = re.compile(r"(?P<year>\d{4}) (?P<month>\d{2})\.html")
_DRAW_RESULT = re.compile(r"(?P<count>\d+)d")
_RETIREMENT_FILE = re.compile(
    r"rank_at_retirement_\d{4}_\d{2}_to_"
    r"(?P<year>\d{4})_(?P<month>\d{2})_rikishi\.csv"
)


def load_final_records(
    standings_root: Path = DEFAULT_STANDINGS_ROOT,
    *,
    start: tuple[int, int] = (1989, 1),
    end: tuple[int, int] | None = None,
) -> dict[Date, dict[RikId, FinalRecord]]:
    """Load published final records keyed by basho and rikishi identity."""

    result: dict[Date, dict[RikId, FinalRecord]] = {}
    for path in sorted(standings_root.glob("*.html")):
        match = _SOURCE_FILE.fullmatch(path.name)
        if match is None:
            continue
        year = int(match.group("year"))
        month = int(match.group("month"))
        date_key = (year, month)
        if date_key < start or (end is not None and date_key > end):
            continue

        date = Date.from_ints(year, month)
        body = parse_body(year, month, path.read_text(encoding="utf-8"))
        records: dict[RikId, FinalRecord] = {}
        for division in body.tables[TableType.DIVISION].values():
            for rikishi in division.rikishi_list:
                if rikishi is None:
                    continue
                rikishi_id = rikishi["id"]
                if rikishi_id in records:
                    raise ValueError(
                        f"Duplicate final record for {date} rikishi {rikishi_id}"
                    )
                records[rikishi_id] = parse_final_record(rikishi["result"])
        result[date] = records
    return result


def latest_retirement_csv(
    retirement_root: Path = DEFAULT_RETIREMENT_ROOT,
) -> Path:
    """Return the retirement artifact with the latest ending basho."""

    candidates = []
    for path in retirement_root.glob("rank_at_retirement_*_rikishi.csv"):
        match = _RETIREMENT_FILE.fullmatch(path.name)
        if match is not None:
            candidates.append(
                (
                    int(match.group("year")),
                    int(match.group("month")),
                    path,
                )
            )
    if not candidates:
        raise FileNotFoundError(
            f"No rank-at-retirement rikishi artifact in {retirement_root}"
        )
    return max(candidates, key=lambda item: item[:2])[2]


def load_retirement_last_appearances(path: Path) -> dict[RikId, str]:
    """Load final observed basho by rikishi ID from a retirement artifact."""

    result: dict[RikId, str] = {}
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            rikishi_id = RikId(int(row["rikishi_id"]))
            if rikishi_id in result:
                raise ValueError(
                    f"Duplicate retirement record for rikishi {rikishi_id}"
                )
            result[rikishi_id] = row["last_appearance"]
    return result


def parse_final_record(source_text: str) -> FinalRecord:
    """Parse SumoDB's W-L, W-L-A, W-L-Dd and W-L-A-Dd forms."""

    parts = source_text.split("-")
    if len(parts) not in (2, 3, 4):
        raise ValueError(f"Unsupported final record: {source_text!r}")
    wins = int(parts[0])
    losses = int(parts[1])
    absences = 0
    draws = 0

    if len(parts) >= 3:
        draw = _DRAW_RESULT.fullmatch(parts[2])
        if draw is None:
            absences = int(parts[2])
        else:
            if len(parts) == 4:
                raise ValueError(f"Unsupported final record: {source_text!r}")
            draws = int(draw.group("count"))
    if len(parts) == 4:
        draw = _DRAW_RESULT.fullmatch(parts[3])
        if draw is None:
            raise ValueError(f"Unsupported final record: {source_text!r}")
        draws = int(draw.group("count"))

    return FinalRecord(
        source_text=source_text,
        wins=wins,
        losses=losses,
        absences=absences,
        draws=draws,
    )

"""Shared access to dated rank/status rows in cached SumoDB career pages."""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from pathlib import Path
import re

from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date


DEFAULT_RIKISHI_PAGES = Path("files/output/infra/get_bios/rikishi")
UNRANKED_ACTIVE_STATUSES = frozenset({"Mz", "Bg", "Kg", "Sj"})

ROW_PATTERN = re.compile(r"<tr>\s*(.*?)\s*</tr>", re.DOTALL | re.IGNORECASE)
BASHO_PATTERN = re.compile(r"Banzuke\.aspx\?b=(\d{6})", re.IGNORECASE)
CELL_PATTERN = re.compile(r"<td\b[^>]*>(.*?)</td>", re.DOTALL | re.IGNORECASE)
TAG_PATTERN = re.compile(r"<[^>]+>")


@dataclass(frozen=True, slots=True)
class CareerRow:
    date: Date
    status: str


@dataclass(frozen=True, slots=True)
class CutoffCareerStatus:
    status: str | None
    evidence: str


def parse_career_rows(html: str, *, rikishi_id: int) -> tuple[CareerRow, ...]:
    """Parse the date and rank/status cell from each SumoDB career row."""
    result: list[CareerRow] = []
    seen: set[Date] = set()
    for row_match in ROW_PATTERN.finditer(html):
        row_html = row_match.group(1)
        date_match = BASHO_PATTERN.search(row_html)
        if date_match is None:
            continue
        cells = CELL_PATTERN.findall(row_html)
        if len(cells) < 2:
            raise ValueError(
                f"Rikishi {rikishi_id} career row {date_match.group(1)} "
                "has fewer than two cells"
            )
        raw_date = date_match.group(1)
        basho = Date.from_ints(int(raw_date[:4]), int(raw_date[4:]))
        if basho in seen:
            raise ValueError(f"Rikishi {rikishi_id} has duplicate career row {basho}")
        seen.add(basho)
        status = _cell_text(cells[1]) or "??"
        result.append(CareerRow(date=basho, status=status))
    if not result:
        raise ValueError(f"Rikishi {rikishi_id} page has no dated career rows")
    return tuple(sorted(result, key=lambda item: item.date))


def load_cutoff_career_statuses(
    root: Path,
    rikishi_ids,
    *,
    cutoff: Date,
) -> dict[RikId, CutoffCareerStatus]:
    """Read cutoff status evidence without treating an absent row as unknown."""
    result = {}
    for rikishi_id in sorted(set(rikishi_ids), key=int):
        path = root / f"{int(rikishi_id):05d}.html"
        if not path.is_file():
            result[rikishi_id] = CutoffCareerStatus(None, "missing_career_page")
            continue
        try:
            rows = parse_career_rows(path.read_text(encoding="utf-8"), rikishi_id=int(rikishi_id))
        except (OSError, UnicodeError, ValueError):
            result[rikishi_id] = CutoffCareerStatus(None, "invalid_career_page")
            continue
        status = next((row.status for row in rows if row.date == cutoff), None)
        result[rikishi_id] = CutoffCareerStatus(
            status,
            "cutoff_status_row" if status is not None else "no_cutoff_status_row",
        )
    return result


def _cell_text(value: str) -> str:
    return unescape(TAG_PATTERN.sub("", value)).replace("\xa0", " ").strip()

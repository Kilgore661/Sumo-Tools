"""Read per-basho hoshi availability from cached SumoDB Rikishi pages."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from typing import Mapping

from src.sumo_core.BasicPrimitives import RikId

from .model import SourceIdentity


ROW_PATTERN = re.compile(r"<tr>\s*(.*?)\s*</tr>", re.DOTALL | re.IGNORECASE)
BASHO_PATTERN = re.compile(
    r"Banzuke\.aspx\?b=(\d{6})",
    re.DOTALL | re.IGNORECASE,
)
HOSHI_CELL_PATTERN = re.compile(
    r"<td\b[^>]*\bclass\s*=\s*['\"]hoshi['\"][^>]*>(.*?)</td>",
    re.DOTALL | re.IGNORECASE,
)
HOSHI_SYMBOL_PATTERN = re.compile(r"hoshi_[a-z0-9_]+\.gif", re.IGNORECASE)
EXPECTED_HOSHI_SLOTS = 15


@dataclass(frozen=True, slots=True)
class HoshiRecord:
    """The source symbols in one dated career-table row."""

    known_symbol_count: int
    empty_symbol_count: int

    @property
    def recorded(self) -> bool:
        return self.known_symbol_count > 0

    @property
    def complete(self) -> bool:
        return (
            self.slot_count == EXPECTED_HOSHI_SLOTS
            and self.empty_symbol_count == 0
        )

    @property
    def slot_count(self) -> int:
        return self.known_symbol_count + self.empty_symbol_count


def parse_hoshi_records(html: str, *, rikishi_id: int) -> dict[str, HoshiRecord]:
    """Parse every dated career row, failing on ambiguous source structure."""

    result: dict[str, HoshiRecord] = {}
    for row_match in ROW_PATTERN.finditer(html):
        row = row_match.group(1)
        date_match = BASHO_PATTERN.search(row)
        if date_match is None:
            continue
        yyyymm = date_match.group(1)
        basho = f"{yyyymm[:4]}/{yyyymm[4:]}"
        if basho in result:
            raise ValueError(
                f"Rikishi {rikishi_id} has duplicate career rows for {basho}"
            )
        hoshi_match = HOSHI_CELL_PATTERN.search(row)
        if hoshi_match is None:
            raise ValueError(
                f"Rikishi {rikishi_id} career row {basho} has no hoshi cell"
            )
        symbols = HOSHI_SYMBOL_PATTERN.findall(hoshi_match.group(1))
        if len(symbols) > EXPECTED_HOSHI_SLOTS:
            raise ValueError(
                f"Rikishi {rikishi_id} career row {basho} contains "
                f"{len(symbols)} hoshi slots; expected at most {EXPECTED_HOSHI_SLOTS}"
            )
        empty_symbol_count = sum(
            symbol.lower() == "hoshi_empty.gif" for symbol in symbols
        )
        result[basho] = HoshiRecord(
            known_symbol_count=len(symbols) - empty_symbol_count,
            empty_symbol_count=empty_symbol_count,
        )
    if not result:
        raise ValueError(f"Rikishi {rikishi_id} page has no dated career rows")
    return result


def load_rikishi_pages(
    bio_dir: Path,
    required_bashos: Mapping[RikId, set[str]],
) -> tuple[dict[RikId, dict[str, HoshiRecord]], SourceIdentity]:
    """Load exactly the required cached pages and return aggregate provenance."""

    resolved_dir = bio_dir.resolve()
    if not resolved_dir.is_dir():
        raise FileNotFoundError(f"Rikishi-page directory not found: {resolved_dir}")

    result: dict[RikId, dict[str, HoshiRecord]] = {}
    digest = hashlib.sha256()
    ordered_ids = sorted(required_bashos, key=int)
    work = (
        (
            resolved_dir / f"{int(rikishi_id):05d}.html",
            rikishi_id,
            required_bashos[rikishi_id],
        )
        for rikishi_id in ordered_ids
    )
    with ThreadPoolExecutor(max_workers=16) as executor:
        loaded = executor.map(_load_one_page, work)
        for rikishi_id, path, data, records in loaded:
            result[rikishi_id] = records
            digest.update(path.name.encode("ascii"))
            digest.update(b"\0")
            digest.update(data)
            digest.update(b"\0")

    return result, SourceIdentity(
        path=str(resolved_dir),
        sha256=digest.hexdigest(),
        file_count=len(ordered_ids),
    )


def _load_one_page(
    item: tuple[Path, RikId, set[str]],
) -> tuple[RikId, Path, bytes, dict[str, HoshiRecord]]:
    """Read, parse and reduce one cached page to the required basho."""

    path, rikishi_id, required_bashos = item
    if not path.is_file():
        raise FileNotFoundError(
            f"No cached Rikishi.aspx page for {int(rikishi_id)}: {path}"
        )
    data = path.read_bytes()
    try:
        html = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"Cached rikishi page is not UTF-8: {path}") from error
    all_records = parse_hoshi_records(html, rikishi_id=int(rikishi_id))
    missing = sorted(required_bashos - set(all_records))
    if missing:
        raise ValueError(
            f"Rikishi {int(rikishi_id)} is on banzuke {missing} but the cached "
            "Rikishi.aspx page has no matching career row"
        )
    records = {basho: all_records[basho] for basho in sorted(required_bashos)}
    return rikishi_id, path, data, records

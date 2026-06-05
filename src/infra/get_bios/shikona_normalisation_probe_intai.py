# src/infra/get_bios/shikona_normalisation_probe_intai.py

"""
On-demand Intai repair helpers for the shikona normalisation probe.

This is dirty-boundary prototype code.  It reads cached SumoDB shikona search
pages, downloads a needed page when absent, and parses the search-result row for
the current missing-Intai record.
"""

from __future__ import annotations

import re
import socket
from collections import defaultdict
from dataclasses import replace
from html import unescape
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import urlopen

from src.infra.get_bios.shikona_normalisation_probe_model import (
    BioRecord,
    Finding,
    FixResult,
    empty_if_none,
    normalise_rikid,
)


SEARCH_BASE_URL = "https://sumodb.sumogames.de/Rikishi.aspx"
DOWNLOAD_TIMEOUT_SECONDS = 10
TIMEOUT_RETRY_SECONDS = 30 * 60
REQUEST_PAUSE_SECONDS = 1
MINIMUM_FILE_SIZE_BYTES = 512

RESULT_TABLE_PAT = re.compile(
    r"<thead\b[^>]*>\s*(.*?)\s*</thead>\s*<tbody\b[^>]*>\s*(.*?)\s*</tbody>",
    re.DOTALL | re.IGNORECASE,
)
ROW_PAT = re.compile(r"<tr\b[^>]*>\s*(.*?)\s*</tr>", re.DOTALL | re.IGNORECASE)
CELL_PAT = re.compile(r"<t[dh]\b[^>]*>\s*(.*?)\s*</t[dh]>", re.DOTALL | re.IGNORECASE)
LINK_PAT = re.compile(r"<a\b[^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", re.DOTALL | re.IGNORECASE)
TAG_PAT = re.compile(r"<.*?>", re.DOTALL)
BASHO_DATE_PAT = re.compile(r"(\d{4})\.(\d{2})")

EXPECTED_SEARCH_HEADERS = [
    "Shikona",
    "Heya",
    "Shusshin",
    "Birth Date",
    "Highest Rank",
    "Hatsu Dohyo",
    "Intai",
    "Last Shikona",
]


def search_url(shikona: str) -> str:
    query = urlencode(
        {
            "shikona": shikona,
            "heya": "-1",
            "shusshin": "-1",
            "b": "-1",
            "high": "-1",
            "hd": "-1",
            "entry": "-1",
            "intai": "-1",
            "sort": "1",
        }
    )
    return f"{SEARCH_BASE_URL}?{query}"


def search_page_path(output_dir: Path, shikona: str) -> Path:
    return output_dir / "intai_search_pages" / f"{quote(shikona, safe='')}.html"


def intai_search_shikona(record: BioRecord) -> str:
    if record.sumodb_search_shikona is None:
        raise ValueError(f"Record {record.rikid} has no SumoDB search shikona")
    return record.sumodb_search_shikona


def is_timeout_exception(exc: BaseException) -> bool:
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return True
    if isinstance(exc, URLError):
        reason = getattr(exc, "reason", None)
        return isinstance(reason, (TimeoutError, socket.timeout))
    return False


def download_diagnostic(*, shikona: str, url: str, detail: str) -> str:
    return (
        "Intai fix download failed.\n"
        f"  shikona: {shikona}\n"
        f"  url: {url}\n"
        f"  detail: {detail}"
    )


def download_search_page(shikona: str) -> str:
    url = search_url(shikona)

    while True:
        try:
            with urlopen(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
                data = response.read()
        except (HTTPError, URLError, TimeoutError, socket.timeout, OSError) as exc:
            if is_timeout_exception(exc):
                print(
                    f"{shikona}: Intai fix download timed out; "
                    f"retrying in {TIMEOUT_RETRY_SECONDS // 60} minutes."
                )
                sleep(TIMEOUT_RETRY_SECONDS)
                continue

            raise RuntimeError(
                download_diagnostic(
                    shikona=shikona,
                    url=url,
                    detail=f"{type(exc).__name__}: {exc}",
                )
            ) from exc

        if len(data) < MINIMUM_FILE_SIZE_BYTES:
            raise RuntimeError(
                download_diagnostic(
                    shikona=shikona,
                    url=url,
                    detail=f"response too small: {len(data)} bytes",
                )
            )

        return data.decode("utf-8", errors="replace")


def read_or_download_search_page(record: BioRecord, output_dir: Path) -> str:
    shikona = intai_search_shikona(record)
    path = search_page_path(output_dir, shikona)

    if path.exists():
        return path.read_text(encoding="utf-8")

    print(
        "Intai fix downloading: "
        f"rikid={record.rikid} "
        f"shikona={record.latest_shikona!r} "
        f"sumodb_search_shikona={shikona!r} "
        f"hatsu={empty_if_none(record.hatsu_dohyo)} "
        f"path={path}"
    )
    text = download_search_page(shikona)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    sleep(REQUEST_PAUSE_SECONDS)
    return text


def clean_html_text(text: str) -> str:
    text = TAG_PAT.sub("", text)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    return " ".join(text.split())


def normalize_search_basho_date(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None

    match = BASHO_DATE_PAT.search(value)
    if match is None:
        return None

    return f"{match.group(1)}/{match.group(2)}"


def search_row_rikid(shikona_cell_html: str) -> str | None:
    for link_match in LINK_PAT.finditer(shikona_cell_html):
        href = unescape(link_match.group(1))
        query = parse_qs(urlparse(href).query)
        rikid_values = query.get("r")
        if not rikid_values:
            continue

        try:
            return normalise_rikid(rikid_values[0])
        except ValueError:
            return None

    return None


def row_cells(row_html: str) -> list[str]:
    return [match.group(1) for match in CELL_PAT.finditer(row_html)]


def row_headers(cells: list[str]) -> list[str]:
    return [clean_html_text(cell) for cell in cells]


def search_header_map(headers: list[str]) -> dict[str, int] | None:
    if headers != EXPECTED_SEARCH_HEADERS:
        return None
    return {header: index for index, header in enumerate(headers)}


def parse_intai_from_result_table(
    record: BioRecord,
    header_html: str,
    body_html: str,
    *,
    latest_basho: str,
    latest_basho_rikids_set: set[str],
) -> FixResult | None:
    assert record.latest_shikona is not None

    header_rows = list(ROW_PAT.finditer(header_html))
    if len(header_rows) != 1:
        return None

    header_map = search_header_map(row_headers(row_cells(header_rows[0].group(1))))
    if header_map is None:
        return None

    matching_rows: list[list[str]] = []
    shikona_index = header_map["Shikona"]

    for row_match in ROW_PAT.finditer(body_html):
        cells = row_cells(row_match.group(1))
        if len(cells) != len(header_map):
            continue
        if search_row_rikid(cells[shikona_index]) == record.rikid:
            matching_rows.append(cells)

    if not matching_rows:
        return FixResult(
            intai=None,
            findings=(
                Finding(
                    kind="intai_fix_rikid_not_found",
                    latest_shikona=record.latest_shikona,
                    rikid=record.rikid,
                    detail="Expected shikona search-result table was found, but no row matched this rikid.",
                ),
            ),
        )

    if len(matching_rows) > 1:
        return FixResult(
            intai=None,
            findings=(
                Finding(
                    kind="intai_fix_duplicate_rikid_rows",
                    latest_shikona=record.latest_shikona,
                    rikid=record.rikid,
                    detail=f"Expected one search-result row for this rikid, found {len(matching_rows)}.",
                ),
            ),
        )

    intai_index = header_map["Intai"]
    intai_text = clean_html_text(matching_rows[0][intai_index])
    intai = normalize_search_basho_date(intai_text)

    if intai is None and not intai_text:
        if record.rikid in latest_basho_rikids_set:
            return FixResult(intai=None, findings=())
        return FixResult(
            intai=None,
            findings=(
                Finding(
                    kind="intai_fix_blank_intai_absent_from_latest_basho",
                    latest_shikona=record.latest_shikona,
                    rikid=record.rikid,
                    detail=f"Search-result row has blank Intai, but this rikid is absent from latest represented basho {latest_basho}.",
                ),
            ),
        )

    if intai is None:
        return FixResult(
            intai=None,
            findings=(
                Finding(
                    kind="intai_fix_bad_intai_in_row",
                    latest_shikona=record.latest_shikona,
                    rikid=record.rikid,
                    detail=f"Search-result row matched this rikid, but the Intai cell is not a YYYY.MM basho date: {intai_text!r}.",
                ),
            ),
        )

    return FixResult(intai=intai, findings=())


def parse_intai_from_search_page(
    record: BioRecord,
    text: str,
    *,
    latest_basho: str,
    latest_basho_rikids_set: set[str],
) -> FixResult:
    assert record.latest_shikona is not None

    for table_match in RESULT_TABLE_PAT.finditer(text):
        result = parse_intai_from_result_table(
            record,
            table_match.group(1),
            table_match.group(2),
            latest_basho=latest_basho,
            latest_basho_rikids_set=latest_basho_rikids_set,
        )
        if result is not None:
            return result

    return FixResult(
        intai=None,
        findings=(
            Finding(
                kind="intai_fix_search_header_not_found",
                latest_shikona=record.latest_shikona,
                rikid=record.rikid,
                detail="Cached/downloaded SumoDB search page does not have the expected shikona search-result table.",
            ),
        ),
    )


def fix_intai(
    record: BioRecord,
    output_dir: Path,
    *,
    latest_basho: str,
    latest_basho_rikids_set: set[str],
) -> FixResult:
    assert record.latest_shikona is not None

    text = read_or_download_search_page(record, output_dir)
    return parse_intai_from_search_page(
        record,
        text,
        latest_basho=latest_basho,
        latest_basho_rikids_set=latest_basho_rikids_set,
    )


def try_fix_missing_intai(
    records: list[BioRecord],
    output_dir: Path,
    *,
    latest_basho: str,
    latest_basho_rikids_set: set[str],
) -> tuple[list[BioRecord], list[Finding]]:
    by_latest_shikona: dict[str, list[BioRecord]] = defaultdict(list)

    for record in records:
        if record.latest_shikona is not None:
            by_latest_shikona[record.latest_shikona].append(record)

    fixed_records_by_rikid = {record.rikid: record for record in records}
    findings: list[Finding] = []

    for group in by_latest_shikona.values():
        if len(group) <= 1:
            continue

        for record in group:
            if record.intai is not None:
                continue

            result = fix_intai(
                record,
                output_dir,
                latest_basho=latest_basho,
                latest_basho_rikids_set=latest_basho_rikids_set,
            )
            findings.extend(result.findings)

            if result.intai is not None:
                fixed_records_by_rikid[record.rikid] = replace(record, intai=result.intai)

    return [fixed_records_by_rikid[record.rikid] for record in records], findings

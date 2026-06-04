# src/infra/get_bios/shikona_normalisation_probe.py

"""
Probe the proposed public shikona normalisation rule.

This is exploratory prototype code, not the production normalisation API.

The candidate rule is:

* identify rikishi by latest/current shikona;
* where that shikona is unique, use the bare shikona;
* where that shikona is not unique, give the latest holder the bare shikona;
* give earlier retired holders ``Shikona (IntaiYear)``;
* use ``Shikona (IntaiYear/IntaiMonth)`` only when the year is not enough;
* when Intai is missing, try an on-demand cached SumoDB search-page fix;
* require blank SumoDB Intai rows to be confirmed by latest-basho presence;
* allow first-token or full-recorded-shikona collision probes;
* report data/model pressure rather than inventing fallbacks.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import socket
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from html import unescape
from pathlib import Path
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import urlopen

from src.analysis.sumo_history.basho_results.dates import represented_dates
from src.infra.live_store.api import get_history
from src.products.make_site2.data_output import load_history_from_zip
from src.sumo_core.History import History


OUTPUT_ROOT = Path("files") / "output" / "infra" / "get_bios"
DEFAULT_INPUT_JSON = OUTPUT_ROOT / "rikishi_bios.json"
DEFAULT_OUTPUT_DIR = OUTPUT_ROOT / "shikona_normalisation_probe"

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


@dataclass(frozen=True)
class BioRecord:
    rikid: str
    latest_shikona: str | None
    latest_shikona_first_used: str | None
    hatsu_dohyo: str | None
    intai: str | None

    @property
    def intai_year(self) -> str | None:
        if self.intai is None:
            return None
        if len(self.intai) < 4 or not self.intai[:4].isdigit():
            return None
        return self.intai[:4]

    @property
    def intai_month_label(self) -> str | None:
        if self.intai is None or len(self.intai) < 7:
            return None
        year, separator, month = self.intai[:4], self.intai[4], self.intai[5:7]
        if not year.isdigit() or separator != "/" or not month.isdigit():
            return None
        return f"{year}/{month}"

    @property
    def is_active(self) -> bool:
        return self.intai is None


@dataclass(frozen=True)
class LabelRow:
    rikid: str
    latest_shikona: str
    latest_shikona_first_used: str
    hatsu_dohyo: str
    intai: str
    role: str
    label_kind: str
    proposed_label: str


@dataclass(frozen=True)
class Finding:
    kind: str
    latest_shikona: str
    rikid: str
    detail: str


@dataclass(frozen=True)
class FixResult:
    intai: str | None
    findings: tuple[Finding, ...]


def optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"expected string or null, got {type(value).__name__}")
    if value == "" or value == "unknown":
        return None
    return value


def normalise_rikid(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError(f"rikid must be a string, got {type(value).__name__}")
    if not value.isdigit():
        raise ValueError(f"rikid must contain only digits: {value!r}")
    return str(int(value))


def public_shikona_key(value: str | None, *, full_shikona: bool = False) -> str | None:
    """
    Return the prototype public shikona key used for collision probing.

    By default this probe groups on the first token because the public-label
    problem being tested may be the leading shikona element, not the full parsed
    string. Pass ``full_shikona=True`` to probe using the complete normalised
    latest shikona string instead.
    """
    if value is None:
        return None

    parts = value.split()
    if not parts:
        return None

    if full_shikona:
        return " ".join(parts)

    return parts[0]


def latest_shikona_from_history(raw: object) -> tuple[str | None, str | None]:
    if raw is None:
        return None, None
    if not isinstance(raw, dict):
        raise TypeError(f"Shikona must be an object or null, got {type(raw).__name__}")
    if not raw:
        return None, None

    latest_date = sorted(raw)[-1]
    latest = raw[latest_date]

    if not isinstance(latest, str):
        raise TypeError(
            f"latest shikona value at {latest_date!r} must be a string, "
            f"got {type(latest).__name__}"
        )

    return latest, latest_date


def parse_bio_records(raw: object, *, full_shikona: bool = False) -> list[BioRecord]:
    if not isinstance(raw, dict):
        raise TypeError(f"top-level JSON must be an object, got {type(raw).__name__}")

    records = []

    for rikid, record in sorted(raw.items()):
        if not isinstance(record, dict):
            raise TypeError(f"record for {rikid} must be an object")

        latest_shikona, latest_shikona_first_used = latest_shikona_from_history(
            record["Shikona"]
        )

        records.append(
            BioRecord(
                rikid=normalise_rikid(rikid),
                latest_shikona=public_shikona_key(
                    latest_shikona,
                    full_shikona=full_shikona,
                ),
                latest_shikona_first_used=latest_shikona_first_used,
                hatsu_dohyo=optional_text(record["Hatsu Dohyo"]),
                intai=optional_text(record["Intai"]),
            )
        )

    return records


def load_probe_history(history_zip: Path | None) -> History:
    if history_zip is not None:
        return load_history_from_zip(history_zip)
    return get_history()


def latest_basho_rikids(history: History) -> tuple[str, set[str]]:
    dates = represented_dates(history)
    if not dates:
        raise ValueError("No represented basho dates found")

    latest_date = dates[-1]
    return str(latest_date), {
        normalise_rikid(str(int(rikid)))
        for rikid in history(latest_date).banzuke.riks
    }


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
    assert record.latest_shikona is not None

    path = search_page_path(output_dir, record.latest_shikona)

    if path.exists():
        return path.read_text(encoding="utf-8")

    text = download_search_page(record.latest_shikona)

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

    print(
        "Intai fix needed: "
        f"rikid={record.rikid} "
        f"shikona={record.latest_shikona!r} "
        f"hatsu={empty_if_none(record.hatsu_dohyo)}"
    )

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


def choose_bare_holder(records: list[BioRecord]) -> tuple[BioRecord | None, list[Finding]]:
    latest_shikona = records[0].latest_shikona
    assert latest_shikona is not None

    active = [record for record in records if record.is_active]
    findings = []

    if len(active) == 1:
        return active[0], findings

    if len(active) > 1:
        for record in active:
            findings.append(
                Finding(
                    kind="multiple_active_holders",
                    latest_shikona=latest_shikona,
                    rikid=record.rikid,
                    detail="More than one rikishi with this latest shikona has no Intai value.",
                )
            )
        return None, findings

    dated = [record for record in records if record.intai is not None]
    missing_intai = [record for record in records if record.intai is None]

    for record in missing_intai:
        findings.append(
            Finding(
                kind="missing_intai_in_collision_group",
                latest_shikona=latest_shikona,
                rikid=record.rikid,
                detail="Collision group has no active holder, but this rikishi has no Intai value.",
            )
        )

    if not dated:
        findings.append(
            Finding(
                kind="no_bare_holder",
                latest_shikona=latest_shikona,
                rikid="",
                detail="No active holder and no dated retired holder can be chosen as bare holder.",
            )
        )
        return None, findings

    latest_intai = max(record.intai for record in dated if record.intai is not None)
    tied = [record for record in dated if record.intai == latest_intai]

    if len(tied) > 1:
        for record in tied:
            findings.append(
                Finding(
                    kind="latest_holder_tie",
                    latest_shikona=latest_shikona,
                    rikid=record.rikid,
                    detail=f"More than one retired holder has latest Intai {latest_intai}.",
                )
            )
        return None, findings

    return tied[0], findings


def empty_if_none(value: str | None) -> str:
    return "" if value is None else value


def build_label_row(
    *,
    record: BioRecord,
    role: str,
    label_kind: str,
    proposed_label: str,
) -> LabelRow:
    assert record.latest_shikona is not None
    return LabelRow(
        rikid=record.rikid,
        latest_shikona=record.latest_shikona,
        latest_shikona_first_used=empty_if_none(record.latest_shikona_first_used),
        hatsu_dohyo=empty_if_none(record.hatsu_dohyo),
        intai=empty_if_none(record.intai),
        role=role,
        label_kind=label_kind,
        proposed_label=proposed_label,
    )


def suffix_label_for_earlier_holder(
    *,
    latest_shikona: str,
    record: BioRecord,
    intai_year_counts: Counter[str],
) -> tuple[str, str, Finding | None]:
    intai_year = record.intai_year
    if intai_year is None:
        return "", "unresolved", Finding(
            kind="missing_intai_year_for_suffix",
            latest_shikona=latest_shikona,
            rikid=record.rikid,
            detail="Earlier/non-bare holder needs an Intai year suffix, but no usable Intai year exists.",
        )

    if intai_year_counts[intai_year] == 1:
        return f"{latest_shikona} ({intai_year})", "intai_year_suffix", None

    intai_month_label = record.intai_month_label
    if intai_month_label is None:
        return "", "unresolved", Finding(
            kind="missing_intai_month_for_suffix",
            latest_shikona=latest_shikona,
            rikid=record.rikid,
            detail="Earlier/non-bare holder shares an Intai year and needs YYYY/MM, but no usable Intai month exists.",
        )

    return f"{latest_shikona} ({intai_month_label})", "intai_month_suffix", None


def analyse(records: list[BioRecord]) -> tuple[list[LabelRow], list[LabelRow], list[Finding]]:
    findings: list[Finding] = []
    records_with_shikona = []

    for record in records:
        if record.latest_shikona is None:
            findings.append(
                Finding(
                    kind="missing_shikona_history",
                    latest_shikona="",
                    rikid=record.rikid,
                    detail="Bio record has no parsed Shikona history.",
                )
            )
        else:
            records_with_shikona.append(record)

    by_latest_shikona: dict[str, list[BioRecord]] = defaultdict(list)
    for record in records_with_shikona:
        assert record.latest_shikona is not None
        by_latest_shikona[record.latest_shikona].append(record)

    all_labels: list[LabelRow] = []
    collision_labels: list[LabelRow] = []

    for latest_shikona, group in sorted(by_latest_shikona.items()):
        ordered_group = sorted(group, key=lambda record: record.rikid)

        if len(ordered_group) == 1:
            record = ordered_group[0]
            all_labels.append(
                build_label_row(
                    record=record,
                    role="unique",
                    label_kind="bare_unique",
                    proposed_label=latest_shikona,
                )
            )
            continue

        bare_holder, group_findings = choose_bare_holder(ordered_group)
        findings.extend(group_findings)

        earlier_holders = [
            record
            for record in ordered_group
            if bare_holder is None or record.rikid != bare_holder.rikid
        ]
        intai_year_counts = Counter(
            record.intai_year
            for record in earlier_holders
            if record.intai_year is not None
        )

        for record in ordered_group:
            if bare_holder is not None and record.rikid == bare_holder.rikid:
                row = build_label_row(
                    record=record,
                    role="bare_holder",
                    label_kind="bare_collision",
                    proposed_label=latest_shikona,
                )
            else:
                proposed_label, label_kind, finding = suffix_label_for_earlier_holder(
                    latest_shikona=latest_shikona,
                    record=record,
                    intai_year_counts=intai_year_counts,
                )
                if finding is not None:
                    findings.append(finding)

                row = build_label_row(
                    record=record,
                    role="earlier_holder",
                    label_kind=label_kind,
                    proposed_label=proposed_label,
                )

            all_labels.append(row)
            collision_labels.append(row)

    findings.extend(find_label_collisions(all_labels))

    return all_labels, collision_labels, findings


def find_label_collisions(rows: list[LabelRow]) -> list[Finding]:
    rows_by_label: dict[str, list[LabelRow]] = defaultdict(list)

    for row in rows:
        if row.proposed_label:
            rows_by_label[row.proposed_label].append(row)

    findings = []

    for proposed_label, label_rows in sorted(rows_by_label.items()):
        if len(label_rows) <= 1:
            continue

        latest_shikona = label_rows[0].latest_shikona
        rikids = " ".join(row.rikid for row in label_rows)

        for row in label_rows:
            findings.append(
                Finding(
                    kind="proposed_label_collision",
                    latest_shikona=latest_shikona,
                    rikid=row.rikid,
                    detail=f"Proposed label {proposed_label!r} is shared by rikids {rikids}.",
                )
            )

    return findings


def write_label_csv(path: Path, rows: list[LabelRow]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "rikid",
                "latest_shikona",
                "latest_shikona_first_used",
                "hatsu_dohyo",
                "intai",
                "role",
                "label_kind",
                "proposed_label",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_finding_csv(path: Path, findings: list[Finding]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["kind", "latest_shikona", "rikid", "detail"],
        )
        writer.writeheader()
        for finding in findings:
            writer.writerow(finding.__dict__)


def write_summary(
    path: Path,
    records: list[BioRecord],
    all_rows: list[LabelRow],
    collision_rows: list[LabelRow],
    findings: list[Finding],
    *,
    latest_basho: str,
    latest_basho_rikid_count: int,
    full_shikona: bool,
) -> None:
    records_with_shikona = [record for record in records if record.latest_shikona is not None]
    latest_shikona_counts = Counter(record.latest_shikona for record in records_with_shikona)
    collision_groups = {
        shikona: count
        for shikona, count in latest_shikona_counts.items()
        if count > 1
    }
    finding_counts = Counter(finding.kind for finding in findings)
    label_kind_counts = Counter(row.label_kind for row in all_rows)
    shikona_key_mode = "full recorded latest shikona" if full_shikona else "first token"

    lines = [
        "Shikona normalisation probe summary",
        "====================================",
        "",
        f"bio records read: {len(records)}",
        f"records with shikona history: {len(records_with_shikona)}",
        f"records missing shikona history: {len(records) - len(records_with_shikona)}",
        f"shikona key mode: {shikona_key_mode}",
        f"latest represented basho: {latest_basho}",
        f"rikishi in latest represented basho: {latest_basho_rikid_count}",
        f"distinct latest shikona: {len(latest_shikona_counts)}",
        f"latest-shikona collision groups: {len(collision_groups)}",
        f"rikishi in collision groups: {len(collision_rows)}",
        f"unresolved findings: {len(findings)}",
        "",
        "Labels by kind:",
    ]

    if label_kind_counts:
        for kind, count in sorted(label_kind_counts.items()):
            lines.append(f"  {kind}: {count}")
    else:
        lines.append("  none")

    lines.extend(["", "Findings by kind:"])

    if finding_counts:
        for kind, count in sorted(finding_counts.items()):
            lines.append(f"  {kind}: {count}")
    else:
        lines.append("  none")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe the proposed get_bios shikona normalisation rule.",
    )
    parser.add_argument(
        "--input-json",
        default=str(DEFAULT_INPUT_JSON),
        help=f"Parsed get_bios JSON input path (default: {DEFAULT_INPUT_JSON})",
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Optional zip-backed History serialisation. If absent, use the live store.",
    )
    parser.add_argument(
        "--full-shikona",
        action="store_true",
        help="Use the full recorded latest shikona string instead of the default first-token key.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_json = Path(args.input_json)
    output_dir = Path(args.output_dir)

    history = load_probe_history(args.history_zip)
    latest_basho, latest_basho_rikids_set = latest_basho_rikids(history)
    print(
        f"Latest represented basho is {latest_basho} "
        f"with {len(latest_basho_rikids_set)} rikishi."
    )

    raw: Any = json.loads(input_json.read_text(encoding="utf-8"))
    records = parse_bio_records(raw, full_shikona=args.full_shikona)
    records, fix_findings = try_fix_missing_intai(
        records,
        output_dir,
        latest_basho=latest_basho,
        latest_basho_rikids_set=latest_basho_rikids_set,
    )
    all_labels, collision_labels, findings = analyse(records)
    findings = [*fix_findings, *findings]

    output_dir.mkdir(parents=True, exist_ok=True)

    write_summary(
        output_dir / "summary.txt",
        records,
        all_labels,
        collision_labels,
        findings,
        latest_basho=latest_basho,
        latest_basho_rikid_count=len(latest_basho_rikids_set),
        full_shikona=args.full_shikona,
    )
    write_label_csv(output_dir / "proposed_labels.csv", all_labels)
    write_label_csv(output_dir / "latest_shikona_collisions.csv", collision_labels)
    write_finding_csv(output_dir / "unresolved_findings.csv", findings)

    print(f"Read {len(records)} bio records from {input_json}")
    print(f"Wrote {output_dir / 'summary.txt'}")
    print(f"Wrote {output_dir / 'proposed_labels.csv'}")
    print(f"Wrote {output_dir / 'latest_shikona_collisions.csv'}")
    print(f"Wrote {output_dir / 'unresolved_findings.csv'}")

    if findings:
        print(f"\nProbe found {len(findings)} unresolved findings.")
    else:
        print("\nProbe found no unresolved findings.")


if __name__ == "__main__":
    main()

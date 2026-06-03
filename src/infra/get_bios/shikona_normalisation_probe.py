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
* report data/model pressure rather than inventing fallbacks.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import urlopen


OUTPUT_ROOT = Path("files") / "output" / "infra" / "get_bios"
DEFAULT_INPUT_JSON = OUTPUT_ROOT / "rikishi_bios.json"
DEFAULT_OUTPUT_DIR = OUTPUT_ROOT / "shikona_normalisation_probe"

SEARCH_BASE_URL = "https://sumodb.sumogames.de/Rikishi.aspx"
DOWNLOAD_TIMEOUT_SECONDS = 10
REQUEST_PAUSE_SECONDS = 1
MINIMUM_FILE_SIZE_BYTES = 512


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
        if self.intai is None:
            return None
        if len(self.intai) < 7:
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


def parse_bio_records(raw: object) -> list[BioRecord]:
    if not isinstance(raw, dict):
        raise TypeError(f"top-level JSON must be an object, got {type(raw).__name__}")

    records = []

    for rikid, record in sorted(raw.items()):
        if not isinstance(rikid, str):
            raise TypeError(f"rikid key must be a string, got {type(rikid).__name__}")
        if not isinstance(record, dict):
            raise TypeError(f"record for {rikid} must be an object")

        latest_shikona, latest_shikona_first_used = latest_shikona_from_history(
            record["Shikona"]
        )
        latest_shikona = latest_shikona.split( " " )[0]

        records.append(
            BioRecord(
                rikid=rikid,
                latest_shikona=latest_shikona,
                latest_shikona_first_used=latest_shikona_first_used,
                hatsu_dohyo=optional_text(record["Hatsu Dohyo"]),
                intai=optional_text(record["Intai"]),
            )
        )

    return records


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


def download_search_page(shikona: str) -> str | None:
    url = search_url(shikona)

    try:
        with urlopen(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
            data = response.read()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"{shikona}: Intai fix download glitch: {exc}")
        return None

    if len(data) < MINIMUM_FILE_SIZE_BYTES:
        print(f"{shikona}: Intai fix download glitch: too small: {len(data)} bytes")
        return None

    return data.decode("utf-8", errors="replace")


def read_or_download_search_page(record: BioRecord, output_dir: Path) -> str | None:
    assert record.latest_shikona is not None

    path = search_page_path(output_dir, record.latest_shikona)

    if path.exists():
        return path.read_text(encoding="utf-8")

    text = download_search_page(record.latest_shikona)
    if text is None:
        return None

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    sleep(REQUEST_PAUSE_SECONDS)
    return text


def parse_intai_from_search_page(record: BioRecord, text: str) -> FixResult:
    assert record.latest_shikona is not None

    # Prototype stub.  The next step is to inspect real cached search pages and
    # teach this function to find the row for record.rikid and extract Intai.
    return FixResult(
        intai=None,
        findings=(
            Finding(
                kind="intai_fix_parser_stub",
                latest_shikona=record.latest_shikona,
                rikid=record.rikid,
                detail="Cached/downloaded SumoDB search page was available, but the Intai parser is still a stub.",
            ),
        ),
    )


def fix_intai(record: BioRecord, output_dir: Path) -> FixResult:
    assert record.latest_shikona is not None
    print( record )

    text = read_or_download_search_page(record, output_dir)
    if text is None:
        return FixResult(
            intai=None,
            findings=(
                Finding(
                    kind="intai_fix_download_failed",
                    latest_shikona=record.latest_shikona,
                    rikid=record.rikid,
                    detail="Could not read or download the SumoDB shikona-search page needed to investigate missing Intai.",
                ),
            ),
        )

    return parse_intai_from_search_page(record, text)


def try_fix_missing_intai(
    records: list[BioRecord],
    output_dir: Path,
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

            result = fix_intai(record, output_dir)
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

    lines = [
        "Shikona normalisation probe summary",
        "====================================",
        "",
        f"bio records read: {len(records)}",
        f"records with shikona history: {len(records_with_shikona)}",
        f"records missing shikona history: {len(records) - len(records_with_shikona)}",
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
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_json = Path(args.input_json)
    output_dir = Path(args.output_dir)

    raw: Any = json.loads(input_json.read_text(encoding="utf-8"))
    records = parse_bio_records(raw)
    records, fix_findings = try_fix_missing_intai(records, output_dir)
    all_labels, collision_labels, findings = analyse(records)
    findings = [*fix_findings, *findings]

    output_dir.mkdir(parents=True, exist_ok=True)

    write_summary(output_dir / "summary.txt", records, all_labels, collision_labels, findings)
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

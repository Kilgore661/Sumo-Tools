# src/infra/get_bios/shikona_normalisation_probe_analysis.py

"""
Label analysis and report-writing helpers for the shikona normalisation probe.

This is prototype support code for ``shikona_normalisation_probe.py``.  It is
not the production normalisation API.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from src.infra.get_bios.shikona_normalisation_probe_model import (
    BioRecord,
    Finding,
    LabelRow,
    empty_if_none,
)


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

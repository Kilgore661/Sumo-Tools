# src/infra/get_bios/integrity.py

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from src.infra.persistence.new_sumo_serialiser import load_history_with_annotations
from src.infra.parser.parser2 import OUTPUT_DIR
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date

from .api import BioBashoDate, BioStore, RikishiBio, load_bio_store


DEFAULT_HISTORY = Path(OUTPUT_DIR) / "Historys" / "1958_01 to 2026_11"
DEFAULT_OUTPUT_CSV = Path(OUTPUT_DIR) / "infra" / "rikishi_bio_history_integrity.csv"


@dataclass(frozen=True)
class HistoryAppearances:
    first_seen: Date
    last_seen: Date
    count: int
    first_seen_shikona: str
    last_seen_shikona: str


@dataclass(frozen=True)
class IntegrityFinding:
    kind: str
    rikid: RikId
    shikona: str
    first_seen: Date | None
    last_seen: Date | None
    hatsu_dohyo: BioBashoDate | None
    intai: BioBashoDate | None
    represented_basho_offset: int | None
    detail: str


def bio_key(value: BioBashoDate) -> tuple[int, int]:
    return value.year, value.month


def history_key(value: Date) -> tuple[int, int]:
    return int(value.year), int(value.month)


def compare_bio_to_history_date(bio_date: BioBashoDate, history_date: Date) -> int:
    left = bio_key(bio_date)
    right = history_key(history_date)
    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def format_optional(value) -> str:
    if value is None:
        return ""
    return str(value)


def shikona_for_finding(
    *,
    bio: RikishiBio | None,
    appearances: HistoryAppearances | None,
) -> str:
    if bio is not None and bio.shikona_history:
        return str(bio.latest_shikona())
    if appearances is not None:
        return appearances.last_seen_shikona
    return ""


def build_appearances_by_rikishi(history) -> dict[RikId, HistoryAppearances]:
    dates_by_rikishi: dict[RikId, list[Date]] = defaultdict(list)

    for date in sorted(history.keys()):
        for rikid in history[date].banzuke.riks:
            dates_by_rikishi[rikid].append(date)

    return {
        rikid: HistoryAppearances(
            first_seen=dates[0],
            last_seen=dates[-1],
            count=len(dates),
            first_seen_shikona=str(history[dates[0]].banzuke.get_shik(rikid)),
            last_seen_shikona=str(history[dates[-1]].banzuke.get_shik(rikid)),
        )
        for rikid, dates in dates_by_rikishi.items()
    }


def first_history_index_on_or_after(
    dates: tuple[Date, ...],
    target: BioBashoDate,
) -> int | None:
    for index, date in enumerate(dates):
        if history_key(date) >= bio_key(target):
            return index
    return None


def last_history_index_on_or_before(
    dates: tuple[Date, ...],
    target: BioBashoDate,
) -> int | None:
    result = None
    for index, date in enumerate(dates):
        if history_key(date) <= bio_key(target):
            result = index
        else:
            break
    return result


def check_hatsu_dohyo(
    *,
    rikid: RikId,
    bio: RikishiBio,
    appearances: HistoryAppearances | None,
    history_dates: tuple[Date, ...],
    grace_basho_after_hatsu: int,
) -> list[IntegrityFinding]:
    findings: list[IntegrityFinding] = []
    hatsu = bio.hatsu_dohyo
    shikona = shikona_for_finding(bio=bio, appearances=appearances)

    if hatsu is None:
        findings.append(
            IntegrityFinding(
                kind="bio_missing_hatsu_dohyo",
                rikid=rikid,
                shikona=shikona,
                first_seen=appearances.first_seen if appearances else None,
                last_seen=appearances.last_seen if appearances else None,
                hatsu_dohyo=None,
                intai=bio.intai,
                represented_basho_offset=None,
                detail="Bio has no Hatsu Dohyo value.",
            )
        )
        return findings

    if appearances is None:
        findings.append(
            IntegrityFinding(
                kind="bio_present_but_never_seen_in_history",
                rikid=rikid,
                shikona=shikona,
                first_seen=None,
                last_seen=None,
                hatsu_dohyo=hatsu,
                intai=bio.intai,
                represented_basho_offset=None,
                detail="Bio exists, but rikishi never appears on any parsed History banzuke.",
            )
        )
        return findings

    if compare_bio_to_history_date(hatsu, appearances.first_seen) > 0:
        findings.append(
            IntegrityFinding(
                kind="history_seen_before_bio_hatsu",
                rikid=rikid,
                shikona=shikona,
                first_seen=appearances.first_seen,
                last_seen=appearances.last_seen,
                hatsu_dohyo=hatsu,
                intai=bio.intai,
                represented_basho_offset=None,
                detail="Rikishi appears in History before Bio Hatsu Dohyo.",
            )
        )
        return findings

    first_expected_index = first_history_index_on_or_after(history_dates, hatsu)
    if first_expected_index is None:
        # Hatsu is after the represented History range.  That is already covered
        # by the seen-before-hatsu check above if this rikishi appears.
        return findings

    first_seen_index = history_dates.index(appearances.first_seen)
    delay = first_seen_index - first_expected_index

    if delay > grace_basho_after_hatsu:
        findings.append(
            IntegrityFinding(
                kind="bio_hatsu_long_before_first_history_appearance",
                rikid=rikid,
                shikona=shikona,
                first_seen=appearances.first_seen,
                last_seen=appearances.last_seen,
                hatsu_dohyo=hatsu,
                intai=bio.intai,
                represented_basho_offset=delay,
                detail=(
                    "Bio Hatsu Dohyo is within represented History, but first "
                    "banzuke appearance is later."
                ),
            )
        )

    return findings


def check_intai(
    *,
    rikid: RikId,
    bio: RikishiBio,
    appearances: HistoryAppearances | None,
    history_dates: tuple[Date, ...],
    grace_basho_after_intai: int,
) -> list[IntegrityFinding]:
    findings: list[IntegrityFinding] = []
    intai = bio.intai

    if appearances is None or intai is None:
        return findings

    shikona = shikona_for_finding(bio=bio, appearances=appearances)
    last_allowed_index = last_history_index_on_or_before(history_dates, intai)
    if last_allowed_index is None:
        findings.append(
            IntegrityFinding(
                kind="bio_intai_before_history_but_seen",
                rikid=rikid,
                shikona=shikona,
                first_seen=appearances.first_seen,
                last_seen=appearances.last_seen,
                hatsu_dohyo=bio.hatsu_dohyo,
                intai=intai,
                represented_basho_offset=None,
                detail="Bio Intai is before represented History, but rikishi appears in History.",
            )
        )
        return findings

    last_seen_index = history_dates.index(appearances.last_seen)
    overrun = last_seen_index - last_allowed_index

    if overrun > grace_basho_after_intai:
        findings.append(
            IntegrityFinding(
                kind="history_seen_after_bio_intai",
                rikid=rikid,
                shikona=shikona,
                first_seen=appearances.first_seen,
                last_seen=appearances.last_seen,
                hatsu_dohyo=bio.hatsu_dohyo,
                intai=intai,
                represented_basho_offset=overrun,
                detail="Rikishi appears on a History banzuke after Bio Intai.",
            )
        )

    return findings


def check_history_ids_have_bios(
    *,
    appearances_by_rikishi: dict[RikId, HistoryAppearances],
    bio_store: BioStore,
) -> list[IntegrityFinding]:
    findings = []

    for rikid, appearances in sorted(appearances_by_rikishi.items(), key=lambda item: int(item[0])):
        if rikid in bio_store.bios:
            continue

        findings.append(
            IntegrityFinding(
                kind="history_seen_but_no_bio",
                rikid=rikid,
                shikona=shikona_for_finding(bio=None, appearances=appearances),
                first_seen=appearances.first_seen,
                last_seen=appearances.last_seen,
                hatsu_dohyo=None,
                intai=None,
                represented_basho_offset=None,
                detail="Rikishi appears in History, but has no parsed Bio record.",
            )
        )

    return findings


def run_checks(
    *,
    history,
    bio_store: BioStore,
    grace_basho_after_hatsu: int,
    grace_basho_after_intai: int,
) -> list[IntegrityFinding]:
    history_dates = tuple(sorted(history.keys()))
    appearances_by_rikishi = build_appearances_by_rikishi(history)

    findings: list[IntegrityFinding] = []

    for rikid, bio in sorted(bio_store.bios.items(), key=lambda item: int(item[0])):
        appearances = appearances_by_rikishi.get(rikid)
        findings.extend(
            check_hatsu_dohyo(
                rikid=rikid,
                bio=bio,
                appearances=appearances,
                history_dates=history_dates,
                grace_basho_after_hatsu=grace_basho_after_hatsu,
            )
        )
        findings.extend(
            check_intai(
                rikid=rikid,
                bio=bio,
                appearances=appearances,
                history_dates=history_dates,
                grace_basho_after_intai=grace_basho_after_intai,
            )
        )

    findings.extend(
        check_history_ids_have_bios(
            appearances_by_rikishi=appearances_by_rikishi,
            bio_store=bio_store,
        )
    )

    return sorted(findings, key=lambda finding: (finding.kind, int(finding.rikid)))


def write_csv(path: Path, findings: list[IntegrityFinding]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "kind",
                "rikid",
                "shikona",
                "first_seen",
                "last_seen",
                "hatsu_dohyo",
                "intai",
                "represented_basho_offset",
                "detail",
            ],
        )
        writer.writeheader()
        for finding in findings:
            writer.writerow(
                {
                    "kind": finding.kind,
                    "rikid": str(int(finding.rikid)),
                    "shikona": finding.shikona,
                    "first_seen": format_optional(finding.first_seen),
                    "last_seen": format_optional(finding.last_seen),
                    "hatsu_dohyo": format_optional(finding.hatsu_dohyo),
                    "intai": format_optional(finding.intai),
                    "represented_basho_offset": format_optional(finding.represented_basho_offset),
                    "detail": finding.detail,
                }
            )


def print_summary(findings: list[IntegrityFinding]) -> None:
    counts = Counter(finding.kind for finding in findings)

    if not findings:
        print("No bio/history integrity findings.")
        return

    print("Bio/history integrity findings:")
    for kind, count in sorted(counts.items()):
        print(f"  {kind}: {count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check parsed rikishi bio career dates against History banzuke appearances.",
    )
    parser.add_argument(
        "--history-zip",
        default=str(DEFAULT_HISTORY),
        help=(
            "History zip path without .zip extension "
            f"(default: {DEFAULT_HISTORY})"
        ),
    )
    parser.add_argument(
        "--output-csv",
        default=str(DEFAULT_OUTPUT_CSV),
        help=f"CSV report path (default: {DEFAULT_OUTPUT_CSV})",
    )
    parser.add_argument(
        "--grace-basho-after-hatsu",
        type=int,
        default=1,
        help=(
            "Allowed represented-basho delay between Bio Hatsu Dohyo and "
            "first parsed banzuke appearance. Default 1, because Hatsu Dohyo "
            "may refer to maezumo before normal banzuke listing."
        ),
    )
    parser.add_argument(
        "--grace-basho-after-intai",
        type=int,
        default=1,
        help=(
            "Allowed represented-basho delay after Bio Intai before reporting "
            "continued History banzuke appearances. Default 1 to allow boundary "
            "and announcement-date ambiguity."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    history = load_history_with_annotations(args.history_zip)
    bio_store = load_bio_store()

    findings = run_checks(
        history=history,
        bio_store=bio_store,
        grace_basho_after_hatsu=args.grace_basho_after_hatsu,
        grace_basho_after_intai=args.grace_basho_after_intai,
    )

    output_csv = Path(args.output_csv)
    write_csv(output_csv, findings)
    print_summary(findings)
    print(f"\nWrote {output_csv}")


if __name__ == "__main__":
    main()

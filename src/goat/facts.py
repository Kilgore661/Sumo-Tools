"""Produce spreadsheet-ready GOAT facts and descriptive aggregates."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

from src.goat.playoffs import playoff_evidence
from src.sumo_core.BasicEnums import Division, MSD, Prize
from src.sumo_core.BasicPrimitives import Month, RikId, Year
from src.sumo_core.History import Date, History


CONTRACT_NAME = "goat-prototype-csv"
CONTRACT_VERSION = 1
DATA_EPOCH = Date(Year(1958), Month(1))
LOWER_DIVISION_BOUTS_COMPLETE_FROM = Date(Year(1989), Month(1))
TECHNICAL_EXAMINATION = Date(Year(2011), Month(5))


@dataclass(frozen=True)
class RikishiFact:
    rikishi_id: int
    display_shikona: str
    active_on_latest_banzuke: bool
    first_banzuke: str
    last_banzuke: str
    first_makuuchi: str
    last_makuuchi: str


@dataclass(frozen=True)
class BashoFact:
    basho: str
    sequence: int
    tournament_status: str
    playoff_status: str


@dataclass(frozen=True)
class BanzukeFact:
    basho: str
    rikishi_id: int
    shikona: str
    chii: str
    division: str
    rank_number: int
    side: str
    annotation: str
    makuuchi_level: str
    opposition_level_index: int | str


@dataclass(frozen=True)
class BoutFact:
    basho: str
    day: int
    rikishi1_id: int
    rikishi1_outcome: str
    rikishi2_id: int
    rikishi2_outcome: str
    decision: str
    symbol: str


@dataclass(frozen=True)
class MarkerFact:
    basho: str
    rikishi_id: int
    marker: str


@dataclass(frozen=True)
class PlayoffFact:
    basho: str
    sequence: int
    winner_id: int
    loser_id: int
    source: str


@dataclass(frozen=True)
class RikishiSummary:
    rikishi_id: int
    display_shikona: str
    active_on_latest_banzuke: bool
    first_makuuchi: str
    last_makuuchi: str
    makuuchi_banzuke_basho_1958_onwards: int
    yokozuna_banzuke_basho_1958_onwards: int
    makuuchi_yusho_1958_onwards: int
    makuuchi_doten_yusho_1958_onwards: int
    makuuchi_jun_yusho_1958_onwards: int
    makuuchi_kanto_sho_1958_onwards: int
    makuuchi_gino_sho_1958_onwards: int
    makuuchi_shukun_sho_1958_onwards: int
    makuuchi_W_1958_onwards: int
    makuuchi_FS_1958_onwards: int
    all_division_W_1989_onwards: int
    all_division_FS_1989_onwards: int
    makuuchi_contested_bouts_with_opponent_level_1958_onwards: int
    makuuchi_opponent_level_sum_1958_onwards: int
    makuuchi_mean_opponent_level_1958_onwards: float | str
    makuuchi_mean_defeated_opponent_level_1958_onwards: float | str
    makuuchi_mean_lost_to_opponent_level_1958_onwards: float | str
    makuuchi_contested_bouts_without_opponent_level_1958_onwards: int


@dataclass(frozen=True)
class SummaryDefinition:
    column: str
    definition: str
    complete_from: str
    status: str


@dataclass(frozen=True)
class CoverageRow:
    fact: str
    scope: str
    complete_from: str
    earlier_status: str
    notes: str


@dataclass(frozen=True)
class ValidationCheck:
    check_id: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class GoatFacts:
    source_first_basho: str
    source_last_basho: str
    rikishi: tuple[RikishiFact, ...]
    basho: tuple[BashoFact, ...]
    banzuke: tuple[BanzukeFact, ...]
    bouts: tuple[BoutFact, ...]
    markers: tuple[MarkerFact, ...]
    playoffs: tuple[PlayoffFact, ...]
    rikishi_summary: tuple[RikishiSummary, ...]
    summary_definitions: tuple[SummaryDefinition, ...]
    coverage: tuple[CoverageRow, ...]
    validation: tuple[ValidationCheck, ...]


@dataclass(frozen=True)
class GoatFactOutputs:
    output_root: Path
    manifest_csv: Path
    rikishi_csv: Path
    basho_csv: Path
    banzuke_csv: Path
    bouts_csv: Path
    markers_csv: Path
    playoffs_csv: Path
    rikishi_summary_csv: Path
    summary_definitions_csv: Path
    coverage_csv: Path
    validation_csv: Path


def build_goat_facts(
    history: History,
    output_root: Path,
    labels: Mapping[RikId, str] | None = None,
) -> GoatFactOutputs:
    facts = extract_goat_facts(history, labels=labels)
    failed = tuple(check for check in facts.validation if not check.passed)
    if failed:
        detail = "; ".join(f"{check.check_id}: {check.detail}" for check in failed)
        raise ValueError(f"GOAT fact validation failed: {detail}")
    return write_goat_facts(facts, output_root)


def extract_goat_facts(
    history: History,
    *,
    labels: Mapping[RikId, str] | None = None,
) -> GoatFacts:
    dates = tuple(date for date in sorted(history) if date >= DATA_EPOCH)
    if not dates:
        raise ValueError("History contains no basho in the data epoch (1958/01 onwards)")

    basho_rows: list[BashoFact] = []
    banzuke_rows: list[BanzukeFact] = []
    bout_rows: list[BoutFact] = []
    marker_rows: list[MarkerFact] = []
    playoff_rows: list[PlayoffFact] = []
    appearances: dict[RikId, list[tuple[Date, bool]]] = defaultdict(list)
    latest_shikona: dict[RikId, str] = {}
    all_ids: set[RikId] = set()

    for sequence, date in enumerate(dates, start=1):
        state = history(date)
        playoff = playoff_evidence(history, date)
        last_maegashira = max(
            (
                state.banzuke.get_chii(rikishi_id).number
                for rikishi_id in state.banzuke.riks
                if state.banzuke.get_chii(rikishi_id).level == MSD.MAEGASHIRA
            ),
            default=0,
        )
        basho_rows.append(
            BashoFact(
                basho=str(date),
                sequence=sequence,
                tournament_status=(
                    "technical_examination" if date == TECHNICAL_EXAMINATION else "regular"
                ),
                playoff_status=playoff.status.value,
            )
        )

        for rikishi_id in sorted(state.banzuke.riks, key=int):
            chii = state.banzuke.get_chii(rikishi_id)
            shikona = str(state.banzuke.get_shik(rikishi_id))
            is_makuuchi = isinstance(chii.level, MSD)
            all_ids.add(rikishi_id)
            latest_shikona[rikishi_id] = shikona
            appearances[rikishi_id].append((date, is_makuuchi))
            banzuke_rows.append(
                BanzukeFact(
                    basho=str(date),
                    rikishi_id=int(rikishi_id),
                    shikona=shikona,
                    chii=str(chii),
                    division="MAKUUCHI" if is_makuuchi else chii.level.name,
                    rank_number=chii.number,
                    side=chii.side.name,
                    annotation=chii.ann.name,
                    makuuchi_level=chii.level.as_abbreviation() if is_makuuchi else "",
                    opposition_level_index=_opposition_level(chii.level, chii.number, last_maegashira),
                )
            )

        for day in sorted(state.summary):
            for bout in state.summary(day).results_lookup.values():
                all_ids.update((bout.rikishi1, bout.rikishi2))
                decision = getattr(bout.decision, "value", bout.decision)
                bout_rows.append(
                    BoutFact(
                        str(date), int(day), int(bout.rikishi1), bout.outcome1.name,
                        int(bout.rikishi2), bout.outcome2.name, str(decision), bout.symbol.name,
                    )
                )

        for rikishi_id, performance in sorted(
            state.summary.performances.items(), key=lambda item: int(item[0])
        ):
            all_ids.add(rikishi_id)
            for prize in sorted(performance.prizes, key=_marker):
                marker_rows.append(MarkerFact(str(date), int(rikishi_id), _marker(prize)))

        for bout in playoff.bouts:
            all_ids.update((bout.winner_id, bout.loser_id))
            playoff_rows.append(
                PlayoffFact(str(date), bout.sequence, int(bout.winner_id), int(bout.loser_id), bout.source)
            )

    latest_riks = history(dates[-1]).banzuke.riks
    rikishi_rows: list[RikishiFact] = []
    for rikishi_id in sorted(all_ids, key=int):
        seen = appearances.get(rikishi_id, [])
        makuuchi_dates = [date for date, is_makuuchi in seen if is_makuuchi]
        supplied_label = labels.get(rikishi_id) if labels is not None else None
        rikishi_rows.append(
            RikishiFact(
                int(rikishi_id),
                str(supplied_label or latest_shikona.get(rikishi_id, "")),
                rikishi_id in latest_riks,
                str(seen[0][0]) if seen else "",
                str(seen[-1][0]) if seen else "",
                str(makuuchi_dates[0]) if makuuchi_dates else "",
                str(makuuchi_dates[-1]) if makuuchi_dates else "",
            )
        )

    summaries = _summaries(rikishi_rows, banzuke_rows, bout_rows, marker_rows)
    validation = _validate(rikishi_rows, banzuke_rows, bout_rows, marker_rows, playoff_rows, summaries)
    return GoatFacts(
        str(dates[0]), str(dates[-1]), tuple(rikishi_rows), tuple(basho_rows),
        tuple(banzuke_rows), tuple(bout_rows), tuple(marker_rows), tuple(playoff_rows),
        summaries, _summary_definitions(), _coverage(), validation,
    )


def _summaries(rikishi, banzuke, bouts, markers) -> tuple[RikishiSummary, ...]:
    identities = {row.rikishi_id: row for row in rikishi}
    makuuchi_keys = {(row.basho, row.rikishi_id) for row in banzuke if row.division == "MAKUUCHI"}
    candidates = sorted({rikishi_id for _, rikishi_id in makuuchi_keys})
    makuuchi_basho = Counter(rikishi_id for _, rikishi_id in makuuchi_keys)
    yokozuna_basho = Counter(row.rikishi_id for row in banzuke if row.makuuchi_level == "Y")
    makuuchi_markers = Counter(
        (row.rikishi_id, row.marker) for row in markers
        if (row.basho, row.rikishi_id) in makuuchi_keys
    )
    makuuchi_outcomes = Counter()
    modern_outcomes = Counter()
    chii_by_key = {(row.basho, row.rikishi_id): row for row in banzuke}
    opposition_levels: dict[int, list[int]] = defaultdict(list)
    defeated_levels: dict[int, list[int]] = defaultdict(list)
    lost_to_levels: dict[int, list[int]] = defaultdict(list)
    unsupported_opposition = Counter()
    for row in bouts:
        for rikishi_id, outcome in ((row.rikishi1_id, row.rikishi1_outcome), (row.rikishi2_id, row.rikishi2_outcome)):
            if (row.basho, rikishi_id) in makuuchi_keys:
                makuuchi_outcomes[(rikishi_id, outcome)] += 1
            if row.basho >= str(LOWER_DIVISION_BOUTS_COMPLETE_FROM):
                modern_outcomes[(rikishi_id, outcome)] += 1
        if {row.rikishi1_outcome, row.rikishi2_outcome} != {"W", "L"}:
            continue
        for rikishi_id, outcome, opponent_id in (
            (row.rikishi1_id, row.rikishi1_outcome, row.rikishi2_id),
            (row.rikishi2_id, row.rikishi2_outcome, row.rikishi1_id),
        ):
            if (row.basho, rikishi_id) not in makuuchi_keys:
                continue
            opponent = chii_by_key.get((row.basho, opponent_id))
            if opponent is None or opponent.opposition_level_index == "":
                unsupported_opposition[rikishi_id] += 1
                continue
            level = int(opponent.opposition_level_index)
            opposition_levels[rikishi_id].append(level)
            (defeated_levels if outcome == "W" else lost_to_levels)[rikishi_id].append(level)

    rows = []
    for rikishi_id in candidates:
        identity = identities[rikishi_id]
        rows.append(RikishiSummary(
            rikishi_id, identity.display_shikona, identity.active_on_latest_banzuke,
            identity.first_makuuchi, identity.last_makuuchi,
            makuuchi_basho[rikishi_id], yokozuna_basho[rikishi_id],
            makuuchi_markers[(rikishi_id, "Y")], makuuchi_markers[(rikishi_id, "D")],
            makuuchi_markers[(rikishi_id, "J")], makuuchi_markers[(rikishi_id, "K")],
            makuuchi_markers[(rikishi_id, "G")], makuuchi_markers[(rikishi_id, "S")],
            makuuchi_outcomes[(rikishi_id, "W")], makuuchi_outcomes[(rikishi_id, "FS")],
            modern_outcomes[(rikishi_id, "W")], modern_outcomes[(rikishi_id, "FS")],
            len(opposition_levels[rikishi_id]), sum(opposition_levels[rikishi_id]),
            _mean(opposition_levels[rikishi_id]), _mean(defeated_levels[rikishi_id]),
            _mean(lost_to_levels[rikishi_id]), unsupported_opposition[rikishi_id],
        ))
    return tuple(rows)


def _summary_definitions() -> tuple[SummaryDefinition, ...]:
    return (
        SummaryDefinition("makuuchi_banzuke_basho_1958_onwards", "Basho on a Makuuchi banzuke", "1958/01", "descriptive"),
        SummaryDefinition("yokozuna_banzuke_basho_1958_onwards", "Basho at Yokozuna", "1958/01", "descriptive"),
        SummaryDefinition("makuuchi_yusho_1958_onwards", "Y markers while on the Makuuchi banzuke", "1958/01", "descriptive"),
        SummaryDefinition("makuuchi_doten_yusho_1958_onwards", "D markers while on the Makuuchi banzuke", "1958/01", "descriptive"),
        SummaryDefinition("makuuchi_jun_yusho_1958_onwards", "J markers while on the Makuuchi banzuke", "1958/01", "descriptive"),
        SummaryDefinition("makuuchi_kanto_sho_1958_onwards", "K markers while on the Makuuchi banzuke", "1958/01", "descriptive"),
        SummaryDefinition("makuuchi_gino_sho_1958_onwards", "G markers while on the Makuuchi banzuke", "1958/01", "descriptive"),
        SummaryDefinition("makuuchi_shukun_sho_1958_onwards", "S markers while on the Makuuchi banzuke", "1958/01", "descriptive"),
        SummaryDefinition("makuuchi_W_1958_onwards", "Recorded W outcomes while on the Makuuchi banzuke", "1958/01", "descriptive"),
        SummaryDefinition("makuuchi_FS_1958_onwards", "Recorded FS outcomes while on the Makuuchi banzuke", "1958/01", "descriptive"),
        SummaryDefinition("all_division_W_1989_onwards", "Recorded W outcomes in any division from 1989/01", "1989/01", "descriptive; not a full-career total for earlier rikishi"),
        SummaryDefinition("all_division_FS_1989_onwards", "Recorded FS outcomes in any division from 1989/01", "1989/01", "descriptive; not a full-career total for earlier rikishi"),
        SummaryDefinition("makuuchi_contested_bouts_with_opponent_level_1958_onwards", "Makuuchi W/L bouts whose opponent has a published Makuuchi-or-Juryo level", "1958/01", "descriptive; denominator for mean opposition"),
        SummaryDefinition("makuuchi_opponent_level_sum_1958_onwards", "Sum of opponent level indices over supported Makuuchi W/L bouts", "1958/01", "descriptive; Y=0,O=1,S=2,K=3,Mn=3+n,Jn=3+last M rank+n"),
        SummaryDefinition("makuuchi_mean_opponent_level_1958_onwards", "Opponent level sum divided by supported Makuuchi W/L bouts", "1958/01", "descriptive; lower means stronger opposition"),
        SummaryDefinition("makuuchi_mean_defeated_opponent_level_1958_onwards", "Mean level index of opponents defeated by W in Makuuchi", "1958/01", "descriptive; lower means stronger opponents defeated"),
        SummaryDefinition("makuuchi_mean_lost_to_opponent_level_1958_onwards", "Mean level index of opponents in Makuuchi L outcomes", "1958/01", "descriptive; lower means stronger opponents"),
        SummaryDefinition("makuuchi_contested_bouts_without_opponent_level_1958_onwards", "Makuuchi W/L bouts whose opponent lacks a Makuuchi-or-Juryo banzuke level", "1958/01", "descriptive completeness count"),
    )


def _coverage() -> tuple[CoverageRow, ...]:
    return (
        CoverageRow("banzuke", "all divisions", "1958/01", "outside data epoch", "Published History banzuke"),
        CoverageRow("bouts", "Makuuchi", "1958/01", "outside data epoch", "Recorded scheduled bouts"),
        CoverageRow("bouts", "Juryo", "1958/01", "outside data epoch", "Recorded scheduled bouts"),
        CoverageRow("bouts", "sub-sekitori", "1989/01", "incomplete", "Earlier records must not be treated as zero"),
        CoverageRow("performance markers", "Y,D,J,K,G,S", "1958/01", "outside data epoch", "Raw administrative markers"),
        CoverageRow("playoff bouts", "all divisions", "", "per-basho availability", "See basho.csv playoff_status"),
    )


def _validate(rikishi, banzuke, bouts, markers, playoffs, summaries) -> tuple[ValidationCheck, ...]:
    rikishi_ids = {row.rikishi_id for row in rikishi}
    return (
        _unique("unique_rikishi", [(row.rikishi_id,) for row in rikishi]),
        _unique("unique_banzuke", [(row.basho, row.rikishi_id) for row in banzuke]),
        _unique("unique_bouts", [(row.basho, row.day, min(row.rikishi1_id, row.rikishi2_id), max(row.rikishi1_id, row.rikishi2_id)) for row in bouts]),
        _unique("unique_markers", [(row.basho, row.rikishi_id, row.marker) for row in markers]),
        _unique("unique_playoffs", [(row.basho, row.sequence) for row in playoffs]),
        _unique("unique_summaries", [(row.rikishi_id,) for row in summaries]),
        ValidationCheck("rikishi_foreign_keys", all(row.rikishi_id in rikishi_ids for row in banzuke) and all(row.rikishi_id in rikishi_ids for row in markers) and all(row.rikishi1_id in rikishi_ids and row.rikishi2_id in rikishi_ids for row in bouts), "all factual rikishi IDs occur in rikishi.csv"),
    )


def write_goat_facts(facts: GoatFacts, output_root: Path) -> GoatFactOutputs:
    output_root.mkdir(parents=True, exist_ok=True)
    outputs = GoatFactOutputs(
        output_root, output_root / "manifest.csv", output_root / "rikishi.csv",
        output_root / "basho.csv", output_root / "banzuke.csv", output_root / "bouts.csv",
        output_root / "markers.csv", output_root / "playoffs.csv",
        output_root / "rikishi_summary.csv", output_root / "summary_definitions.csv",
        output_root / "coverage.csv", output_root / "validation.csv",
    )
    tables = {
        outputs.rikishi_csv: facts.rikishi,
        outputs.basho_csv: facts.basho,
        outputs.banzuke_csv: facts.banzuke,
        outputs.bouts_csv: facts.bouts,
        outputs.markers_csv: facts.markers,
        outputs.playoffs_csv: facts.playoffs,
        outputs.rikishi_summary_csv: facts.rikishi_summary,
        outputs.summary_definitions_csv: facts.summary_definitions,
        outputs.coverage_csv: facts.coverage,
        outputs.validation_csv: facts.validation,
    }
    for path, rows in tables.items():
        _write_csv(path, rows)

    with outputs.manifest_csv.open("w", encoding="utf-8", newline="") as stream:
        fields = ("record_type", "name", "value", "row_count", "sha256")
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerow({"record_type": "metadata", "name": "contract", "value": CONTRACT_NAME})
        writer.writerow({"record_type": "metadata", "name": "schema_version", "value": CONTRACT_VERSION})
        writer.writerow({"record_type": "metadata", "name": "data_epoch", "value": DATA_EPOCH})
        writer.writerow({"record_type": "metadata", "name": "first_basho", "value": facts.source_first_basho})
        writer.writerow({"record_type": "metadata", "name": "last_basho", "value": facts.source_last_basho})
        writer.writerow({"record_type": "metadata", "name": "goat_ranking_included", "value": False})
        for path, rows in tables.items():
            writer.writerow({"record_type": "file", "name": path.name, "row_count": len(rows), "sha256": _sha256(path)})
    return outputs


def _write_csv(path: Path, rows: tuple) -> None:
    if not rows:
        row_type = {
            "rikishi.csv": RikishiFact,
            "basho.csv": BashoFact,
            "banzuke.csv": BanzukeFact,
            "bouts.csv": BoutFact,
            "markers.csv": MarkerFact,
            "playoffs.csv": PlayoffFact,
            "rikishi_summary.csv": RikishiSummary,
            "summary_definitions.csv": SummaryDefinition,
            "coverage.csv": CoverageRow,
            "validation.csv": ValidationCheck,
        }.get(path.name)
        if row_type is None:
            raise ValueError(f"Cannot infer columns for empty {path.name}")
        fieldnames = tuple(row_type.__dataclass_fields__)
    else:
        fieldnames = tuple(rows[0].__dataclass_fields__)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def _marker(prize: Prize) -> str:
    return {Prize.YUSHO: "Y", Prize.DOTEN_YUSHO: "D", Prize.JUN_YUSHO: "J", Prize.KANTO: "K", Prize.GINO: "G", Prize.SHUKUN: "S"}[prize]


def _opposition_level(level, number: int, last_maegashira: int) -> int | str:
    if level == MSD.YOKOZUNA:
        return 0
    if level == MSD.OZEKI:
        return 1
    if level == MSD.SEKIWAKE:
        return 2
    if level == MSD.KOMUSUBI:
        return 3
    if level == MSD.MAEGASHIRA:
        return 3 + number
    if level == Division.JURYO:
        return 3 + last_maegashira + number
    return ""


def _mean(values: list[int]) -> float | str:
    return sum(values) / len(values) if values else ""


def _unique(check_id: str, keys: list[tuple]) -> ValidationCheck:
    return ValidationCheck(check_id, len(keys) == len(set(keys)), f"{len(keys)} rows; {len(set(keys))} unique keys")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

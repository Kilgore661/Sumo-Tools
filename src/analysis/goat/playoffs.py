"""Probe Makuuchi leaderboard ties and their Y/D/J administrative markers."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import MSD, Outcome, Prize
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


DEFAULT_HISTORY_ZIP = Path("files/output/Historys/1958_01 to 2026_11.zip")
DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/goat/playoffs")
OFFICIAL_WIN_OUTCOMES = frozenset({Outcome.W, Outcome.FS})
MARKER_ORDER = (Prize.YUSHO, Prize.DOTEN_YUSHO, Prize.JUN_YUSHO)
MARKER_LABEL = {
    Prize.YUSHO: "Y",
    Prize.DOTEN_YUSHO: "D",
    Prize.JUN_YUSHO: "J",
}


@dataclass(frozen=True)
class PlayoffLeaderRow:
    basho: str
    winning_score: int
    leader_count: int
    rikishi_id: int
    shikona: str
    chii: str
    markers: str
    yusho: bool
    doten_yusho: bool
    jun_yusho: bool


@dataclass(frozen=True)
class PlayoffBashoRow:
    basho: str
    winning_score: int
    leader_count: int
    yusho_count: int
    doten_yusho_count: int
    jun_yusho_count: int
    marker_pattern: str
    leaders: str


@dataclass(frozen=True)
class FindingRow:
    basho: str
    kind: str
    detail: str


@dataclass(frozen=True)
class PlayoffProbe:
    history_first_basho: str
    history_last_basho: str
    history_basho_count: int
    tied_basho: tuple[PlayoffBashoRow, ...]
    leaders: tuple[PlayoffLeaderRow, ...]
    findings: tuple[FindingRow, ...]


@dataclass(frozen=True)
class PlayoffProbeOutputs:
    output_root: Path
    basho_csv: Path
    leaders_csv: Path
    findings_csv: Path
    summary_json: Path


def probe_playoffs(history: History) -> PlayoffProbe:
    """Find Makuuchi ties at the top score and test the observed marker pattern."""

    dates = sorted(history)
    if not dates:
        raise ValueError("Cannot probe an empty History")

    tied_basho: list[PlayoffBashoRow] = []
    leader_rows: list[PlayoffLeaderRow] = []
    findings: list[FindingRow] = []

    for date in dates:
        state = history(date)
        makuuchi = {
            rikishi_id
            for rikishi_id in state.banzuke.riks
            if isinstance(state.banzuke.get_chii(rikishi_id).level, MSD)
        }
        if not makuuchi:
            findings.append(
                FindingRow(str(date), "no_makuuchi_banzuke", "No Makuuchi rikishi found")
            )
            continue

        wins = official_wins(state.summary, makuuchi)
        winning_score = max(wins.values())
        leaders = {
            rikishi_id for rikishi_id, win_count in wins.items()
            if win_count == winning_score
        }
        markers_by_rikishi = administrative_markers(
            state.summary.performances,
            makuuchi,
        )
        yusho = marked_rikishi(markers_by_rikishi, Prize.YUSHO)
        doten = marked_rikishi(markers_by_rikishi, Prize.DOTEN_YUSHO)
        jun_yusho = marked_rikishi(markers_by_rikishi, Prize.JUN_YUSHO)

        findings.extend(
            marker_findings(
                date=date,
                leaders=leaders,
                yusho=yusho,
                doten=doten,
                jun_yusho=jun_yusho,
            )
        )

        if len(leaders) < 2:
            continue

        ordered_leaders = tuple(
            sorted(leaders, key=lambda rid: state.banzuke.get_chii(rid).ordinal())
        )
        marker_pattern = marker_pattern_for(
            ordered_leaders,
            markers_by_rikishi,
        )
        leader_descriptions = []
        for rikishi_id in ordered_leaders:
            prizes = markers_by_rikishi.get(rikishi_id, frozenset())
            markers = marker_text(prizes)
            chii = state.banzuke.get_chii(rikishi_id)
            shikona = str(state.banzuke.get_shik(rikishi_id))
            leader_rows.append(
                PlayoffLeaderRow(
                    basho=str(date),
                    winning_score=winning_score,
                    leader_count=len(leaders),
                    rikishi_id=int(rikishi_id),
                    shikona=shikona,
                    chii=str(chii),
                    markers=markers,
                    yusho=Prize.YUSHO in prizes,
                    doten_yusho=Prize.DOTEN_YUSHO in prizes,
                    jun_yusho=Prize.JUN_YUSHO in prizes,
                )
            )
            leader_descriptions.append(
                f"{shikona} ({int(rikishi_id)}, {chii}, {markers or '-'})"
            )

        tied_basho.append(
            PlayoffBashoRow(
                basho=str(date),
                winning_score=winning_score,
                leader_count=len(leaders),
                yusho_count=len(yusho),
                doten_yusho_count=len(doten),
                jun_yusho_count=len(jun_yusho & leaders),
                marker_pattern=marker_pattern,
                leaders="; ".join(leader_descriptions),
            )
        )

    return PlayoffProbe(
        history_first_basho=str(dates[0]),
        history_last_basho=str(dates[-1]),
        history_basho_count=len(dates),
        tied_basho=tuple(tied_basho),
        leaders=tuple(leader_rows),
        findings=tuple(findings),
    )


def official_wins(summary, makuuchi: set[RikId]) -> dict[RikId, int]:
    """Return official basho wins, including fusensho, for Makuuchi rikishi."""

    wins = {rikishi_id: 0 for rikishi_id in makuuchi}
    for day in sorted(summary):
        for bout in summary(day).results_lookup.values():
            if bout.rikishi1 in wins and bout.outcome1 in OFFICIAL_WIN_OUTCOMES:
                wins[bout.rikishi1] += 1
            if bout.rikishi2 in wins and bout.outcome2 in OFFICIAL_WIN_OUTCOMES:
                wins[bout.rikishi2] += 1
    return wins


def administrative_markers(performances, makuuchi: set[RikId]):
    """Return only the Yusho, Doten-Yusho and Jun-Yusho markers in Makuuchi."""

    return {
        rikishi_id: frozenset(prize for prize in performance.prizes if prize in MARKER_ORDER)
        for rikishi_id, performance in performances.items()
        if rikishi_id in makuuchi
    }


def marked_rikishi(markers_by_rikishi, prize: Prize) -> set[RikId]:
    return {
        rikishi_id
        for rikishi_id, prizes in markers_by_rikishi.items()
        if prize in prizes
    }


def marker_findings(
    *,
    date: Date,
    leaders: set[RikId],
    yusho: set[RikId],
    doten: set[RikId],
    jun_yusho: set[RikId],
) -> tuple[FindingRow, ...]:
    """Report departures from the hypothesised one-Y/rest-D marker convention."""

    findings: list[FindingRow] = []
    if len(yusho) != 1:
        findings.append(
            FindingRow(
                str(date),
                "yusho_marker_count",
                f"Expected one Makuuchi Y marker; found {sorted(map(int, yusho))}",
            )
        )
    if not yusho.issubset(leaders):
        findings.append(
            FindingRow(
                str(date),
                "yusho_not_at_max_score",
                f"Y={sorted(map(int, yusho))}; leaders={sorted(map(int, leaders))}",
            )
        )

    expected_doten = leaders - yusho if len(leaders) > 1 else set()
    if doten != expected_doten:
        findings.append(
            FindingRow(
                str(date),
                "doten_marker_mismatch",
                (
                    f"Expected D={sorted(map(int, expected_doten))}; "
                    f"found D={sorted(map(int, doten))}"
                ),
            )
        )

    leader_jun_yusho = leaders & jun_yusho
    if leader_jun_yusho:
        findings.append(
            FindingRow(
                str(date),
                "jun_yusho_on_tied_leader",
                f"Tied leaders marked J={sorted(map(int, leader_jun_yusho))}",
            )
        )
    return tuple(findings)


def marker_text(prizes: frozenset[Prize]) -> str:
    return "".join(MARKER_LABEL[prize] for prize in MARKER_ORDER if prize in prizes)


def marker_pattern_for(ordered_leaders, markers_by_rikishi) -> str:
    return "/".join(
        marker_text(markers_by_rikishi.get(rikishi_id, frozenset())) or "-"
        for rikishi_id in ordered_leaders
    )


def write_outputs(
    probe: PlayoffProbe,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> PlayoffProbeOutputs:
    output_root.mkdir(parents=True, exist_ok=True)
    outputs = PlayoffProbeOutputs(
        output_root=output_root,
        basho_csv=output_root / "playoff_basho.csv",
        leaders_csv=output_root / "playoff_leaders.csv",
        findings_csv=output_root / "findings.csv",
        summary_json=output_root / "summary.json",
    )
    write_dataclass_csv(probe.tied_basho, outputs.basho_csv)
    write_dataclass_csv(probe.leaders, outputs.leaders_csv)
    write_dataclass_csv(probe.findings, outputs.findings_csv)
    leader_counts = Counter(row.leader_count for row in probe.tied_basho)
    marker_patterns = Counter(row.marker_pattern for row in probe.tied_basho)
    outputs.summary_json.write_text(
        json.dumps(
            {
                "history": {
                    "first_basho": probe.history_first_basho,
                    "last_basho": probe.history_last_basho,
                    "basho_count": probe.history_basho_count,
                },
                "tied_basho_count": len(probe.tied_basho),
                "tied_basho_by_leader_count": {
                    str(count): frequency for count, frequency in sorted(leader_counts.items())
                },
                "marker_patterns": dict(sorted(marker_patterns.items())),
                "finding_count": len(probe.findings),
                "findings_by_kind": dict(
                    sorted(Counter(row.kind for row in probe.findings).items())
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return outputs


def write_dataclass_csv(rows: Iterable[object], output_path: Path) -> None:
    rows = tuple(rows)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=tuple(rows[0].__dataclass_fields__.keys()),
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def load_history_from_zip(path: Path) -> History:
    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history-zip",
        type=Path,
        help="Load History from a zip instead of the live store.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Output directory. Default: {DEFAULT_OUTPUT_ROOT}.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    history = (
        load_history_from_zip(args.history_zip)
        if args.history_zip is not None
        else get_history()
    )
    probe = probe_playoffs(history)
    outputs = write_outputs(probe, args.output_root)
    counts = Counter(row.leader_count for row in probe.tied_basho)
    print(
        f"History: {probe.history_first_basho} to {probe.history_last_basho} "
        f"({probe.history_basho_count} basho)"
    )
    print(f"Tied Makuuchi leader basho: {len(probe.tied_basho)}")
    print("Leader counts: " + ", ".join(f"{count}-way={n}" for count, n in sorted(counts.items())))
    print(f"Marker findings: {len(probe.findings)}")
    print(f"Output: {outputs.output_root}")


if __name__ == "__main__":
    main()

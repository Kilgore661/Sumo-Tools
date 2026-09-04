"""Probe the score semantics of Makuuchi J and D markers."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from src.analysis.goat.playoffs import (
    DEFAULT_HISTORY_ZIP,
    administrative_markers,
    load_history_from_zip,
    marked_rikishi,
    official_wins,
)
from src.infra.live_store.api import get_history
from src.sumo_core.BasicEnums import MSD, Prize
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/goat/jun_yusho")


@dataclass(frozen=True)
class JunYushoBashoRow:
    """One row per Makuuchi basho, including those without J."""

    basho: str
    winning_score: int
    second_highest_score: int | None
    winning_score_gap: int | None
    top_score_count: int
    second_score_count: int
    yusho_count: int
    doten_yusho_count: int
    jun_yusho_count: int
    j_and_d_coexist: bool
    j_equals_second_score_set: bool
    second_score_without_j: bool


@dataclass(frozen=True)
class JunYushoRikishiRow:
    basho: str
    rikishi_id: int
    shikona: str
    score: int
    winning_score: int
    gap_from_winner: int
    distinct_score_position: int
    rikishi_sharing_score: int
    all_at_score_marked_j: bool


@dataclass(frozen=True)
class FindingRow:
    basho: str
    kind: str
    detail: str


@dataclass(frozen=True)
class JunYushoProbe:
    basho: tuple[JunYushoBashoRow, ...]
    rikishi: tuple[JunYushoRikishiRow, ...]
    findings: tuple[FindingRow, ...]


def probe_jun_yusho(history: History) -> JunYushoProbe:
    """Compare Makuuchi J/D markers with official score ordering."""

    basho_rows: list[JunYushoBashoRow] = []
    rikishi_rows: list[JunYushoRikishiRow] = []
    findings: list[FindingRow] = []

    for date in sorted(history):
        state = history(date)
        makuuchi = {
            rikishi_id
            for rikishi_id in state.banzuke.riks
            if isinstance(state.banzuke.get_chii(rikishi_id).level, MSD)
        }
        if not makuuchi:
            continue

        wins = official_wins(state.summary, makuuchi)
        distinct_scores = sorted(set(wins.values()), reverse=True)
        winning_score = distinct_scores[0]
        second_score = distinct_scores[1] if len(distinct_scores) > 1 else None
        top = {rikishi_id for rikishi_id, score in wins.items() if score == winning_score}
        second = (
            {rikishi_id for rikishi_id, score in wins.items() if score == second_score}
            if second_score is not None
            else set()
        )
        markers = administrative_markers(state.summary.performances, makuuchi)
        yusho = marked_rikishi(markers, Prize.YUSHO)
        doten = marked_rikishi(markers, Prize.DOTEN_YUSHO)
        jun_yusho = marked_rikishi(markers, Prize.JUN_YUSHO)

        j_equals_second = jun_yusho == second
        basho_rows.append(
            JunYushoBashoRow(
                basho=str(date),
                winning_score=winning_score,
                second_highest_score=second_score,
                winning_score_gap=(
                    winning_score - second_score if second_score is not None else None
                ),
                top_score_count=len(top),
                second_score_count=len(second),
                yusho_count=len(yusho),
                doten_yusho_count=len(doten),
                jun_yusho_count=len(jun_yusho),
                j_and_d_coexist=bool(jun_yusho and doten),
                j_equals_second_score_set=j_equals_second,
                second_score_without_j=bool(second and not jun_yusho),
            )
        )

        if jun_yusho and doten:
            findings.append(
                FindingRow(
                    str(date),
                    "j_and_d_coexist",
                    f"J={_ids(jun_yusho)}; D={_ids(doten)}",
                )
            )
        if jun_yusho != second:
            findings.append(
                FindingRow(
                    str(date),
                    "j_not_second_score_set",
                    f"J={_ids(jun_yusho)}; second-score rikishi={_ids(second)}",
                )
            )

        for rikishi_id in sorted(jun_yusho, key=int):
            score = wins[rikishi_id]
            same_score = {
                other_id for other_id, other_score in wins.items() if other_score == score
            }
            rikishi_rows.append(
                JunYushoRikishiRow(
                    basho=str(date),
                    rikishi_id=int(rikishi_id),
                    shikona=str(state.banzuke.get_shik(rikishi_id)),
                    score=score,
                    winning_score=winning_score,
                    gap_from_winner=winning_score - score,
                    distinct_score_position=distinct_scores.index(score) + 1,
                    rikishi_sharing_score=len(same_score),
                    all_at_score_marked_j=same_score == jun_yusho,
                )
            )

    return JunYushoProbe(
        basho=tuple(basho_rows),
        rikishi=tuple(rikishi_rows),
        findings=tuple(findings),
    )


def write_outputs(
    probe: JunYushoProbe,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    _write_csv(probe.basho, output_root / "basho.csv")
    _write_csv(probe.rikishi, output_root / "rikishi.csv")
    _write_csv(probe.findings, output_root / "findings.csv")

    summary = {
        "basho_count": len(probe.basho),
        "basho_with_j": sum(row.jun_yusho_count > 0 for row in probe.basho),
        "basho_with_d": sum(row.doten_yusho_count > 0 for row in probe.basho),
        "basho_with_both_j_and_d": sum(row.j_and_d_coexist for row in probe.basho),
        "j_marker_count": len(probe.rikishi),
        "j_gap_from_winner": dict(
            sorted(Counter(row.gap_from_winner for row in probe.rikishi).items())
        ),
        "j_distinct_score_position": dict(
            sorted(Counter(row.distinct_score_position for row in probe.rikishi).items())
        ),
        "basho_where_j_equals_full_second_score_set": sum(
            row.j_equals_second_score_set for row in probe.basho
        ),
        "basho_with_second_score_but_no_j": sum(
            row.second_score_without_j for row in probe.basho
        ),
        "finding_count": len(probe.findings),
        "findings_by_kind": dict(
            sorted(Counter(row.kind for row in probe.findings).items())
        ),
    }
    (output_root / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_csv(rows: Iterable[object], path: Path) -> None:
    rows = tuple(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].__dataclass_fields__)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def _ids(rikishi: set[RikId]) -> list[int]:
    return sorted(map(int, rikishi))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history-zip",
        type=Path,
        help=f"Load a History zip instead of the live store (example: {DEFAULT_HISTORY_ZIP}).",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    history = (
        load_history_from_zip(args.history_zip)
        if args.history_zip is not None
        else get_history()
    )
    probe = probe_jun_yusho(history)
    write_outputs(probe, args.output_root)
    print(f"Makuuchi basho: {len(probe.basho)}")
    print(f"Basho with J: {sum(row.jun_yusho_count > 0 for row in probe.basho)}")
    print(f"J markers: {len(probe.rikishi)}")
    print(f"J and D coexist: {sum(row.j_and_d_coexist for row in probe.basho)}")
    print(f"Findings: {len(probe.findings)}")
    print(f"Output: {args.output_root}")


if __name__ == "__main__":
    main()

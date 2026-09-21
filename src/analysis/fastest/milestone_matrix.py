"""Produce the all-rikishi first-rank-group milestone CSV."""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, TextIO

from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.get_bios.api import BioStore, load_bio_store
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import RikId, Riks
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


GROUPS = ("Jk", "Jd", "Sd", "Ms", "J", "M", "KS", "O", "Y")
MATRIX_FILE_NAME = "first_rank_group_appearances.csv"
MISSING_BIOS_FILE_NAME = "missing_bios.csv"
RANKINGS_FILE_NAME = "rankings.json"
DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/fastest/milestone_matrix")


@dataclass(frozen=True)
class Milestone:
    chii: Chii
    date: Date
    basho_ordinal: int


@dataclass(frozen=True)
class MissingBio:
    rik_id: RikId
    shikona: str
    milestone: Milestone


@dataclass(frozen=True)
class MatrixOutputs:
    matrix_csv: Path
    missing_bios_csv: Path
    rankings_json: Path
    row_count: int
    missing_bio_count: int


def rank_group(chii: Chii) -> str:
    """Return the progression group containing an exact chii."""
    if chii.level == Division.JONOKUCHI:
        return "Jk"
    if chii.level == Division.JONIDAN:
        return "Jd"
    if chii.level == Division.SANDANME:
        return "Sd"
    if chii.level == Division.MAKUSHITA:
        return "Ms"
    if chii.level == Division.JURYO:
        return "J"
    if chii.level == MSD.MAEGASHIRA:
        return "M"
    if chii.level in {MSD.KOMUSUBI, MSD.SEKIWAKE}:
        return "KS"
    if chii.level == MSD.OZEKI:
        return "O"
    if chii.level == MSD.YOKOZUNA:
        return "Y"
    raise ValueError(f"Unsupported chii level: {chii}")


def matrix_fieldnames() -> list[str]:
    fields = ["shikona", "rik_id"]
    for group in GROUPS:
        fields.extend(
            (
                f"{group}_chii",
                f"{group}_chii_ordinal",
                f"{group}_date",
                f"{group}_basho_ordinal",
            )
        )
    return fields


def produce_milestone_matrix(
    history: History,
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    bios: BioStore | None = None,
    shikona_store: FullShikonaStore | None = None,
    warning_stream: TextIO | None = None,
) -> MatrixOutputs:
    """Write the milestone matrix and the runtime-discovered missing-bio audit."""
    _validate_history(history)
    resolved_bios = bios if bios is not None else load_bio_store()
    first_observations = _first_observations(history)
    missing_rik_ids = frozenset(first_observations) - frozenset(resolved_bios.bios)
    missing_bios = tuple(
        MissingBio(
            rik_id=rik_id,
            shikona=first_observations[rik_id][0],
            milestone=first_observations[rik_id][1],
        )
        for rik_id in sorted(missing_rik_ids, key=int)
    )

    eligible_history = _without_rikishi(history, missing_rik_ids)
    names = (
        shikona_store
        if shikona_store is not None
        else FullShikonaStore.from_sources(eligible_history, bios=resolved_bios)
    )
    milestones = _first_group_appearances(eligible_history)
    rows = _matrix_rows(milestones, names)
    rankings = _build_rankings(
        milestones,
        names,
        history=history,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    matrix_csv = _write_dict_rows(
        output_root / MATRIX_FILE_NAME,
        matrix_fieldnames(),
        rows,
    )
    missing_bios_csv = _write_dict_rows(
        output_root / MISSING_BIOS_FILE_NAME,
        (
            "rik_id",
            "shikona",
            "chii",
            "chii_ordinal",
            "date",
            "basho_ordinal",
            "reason",
        ),
        (_missing_bio_row(item) for item in missing_bios),
    )
    rankings_json = output_root / RANKINGS_FILE_NAME
    rankings_json.write_text(
        json.dumps(rankings, indent=2) + "\n",
        encoding="utf-8",
    )
    _warn_missing_bios(
        missing_bios,
        stream=warning_stream if warning_stream is not None else sys.stderr,
    )
    return MatrixOutputs(
        matrix_csv=matrix_csv,
        missing_bios_csv=missing_bios_csv,
        rankings_json=rankings_json,
        row_count=len(rows),
        missing_bio_count=len(missing_bios),
    )


def _validate_history(history: History) -> None:
    if not history:
        raise ValueError("History is empty")
    first_date = min(history)
    if str(first_date) != "1958/01":
        raise ValueError(
            "Fastest/slowest milestone production requires full History "
            f"beginning at 1958/01; received {first_date}"
        )


def _first_observations(
    history: History,
) -> dict[RikId, tuple[str, Milestone]]:
    observations: dict[RikId, tuple[str, Milestone]] = {}
    for basho_ordinal, date in enumerate(sorted(history), start=1):
        banzuke = history[date].banzuke
        for rik_id in banzuke.riks:
            observations.setdefault(
                rik_id,
                (
                    str(banzuke.rikshik[rik_id]),
                    Milestone(
                        chii=banzuke.rikchii[rik_id],
                        date=date,
                        basho_ordinal=basho_ordinal,
                    ),
                ),
            )
    return observations


def _without_rikishi(history: History, excluded: frozenset[RikId]) -> History:
    if not excluded:
        return history
    filtered = History()
    for date in sorted(history):
        state = history[date]
        retained = state.banzuke.riks - excluded
        filtered[date] = BashoState(
            banzuke=Banzuke(
                riks=Riks(retained),
                rikchii=RikChii(
                    {rik_id: state.banzuke.rikchii[rik_id] for rik_id in retained}
                ),
                rikshik=RikShikona(
                    {rik_id: state.banzuke.rikshik[rik_id] for rik_id in retained}
                ),
            ),
            summary=state.summary,
        )
    return filtered


def _first_group_appearances(
    history: History,
) -> dict[RikId, dict[str, Milestone]]:
    milestones: dict[RikId, dict[str, Milestone]] = {}
    for basho_ordinal, date in enumerate(sorted(history), start=1):
        banzuke = history[date].banzuke
        for rik_id in banzuke.riks:
            chii = banzuke.rikchii[rik_id]
            milestones.setdefault(rik_id, {}).setdefault(
                rank_group(chii),
                Milestone(chii=chii, date=date, basho_ordinal=basho_ordinal),
            )
    return milestones


def _matrix_rows(
    milestones: Mapping[RikId, Mapping[str, Milestone]],
    names: FullShikonaStore,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rik_id in sorted(milestones, key=int):
        row: dict[str, object] = {
            "shikona": names.full_shikona(rik_id),
            "rik_id": int(rik_id),
        }
        for group in GROUPS:
            milestone = milestones[rik_id].get(group)
            row[f"{group}_chii"] = "" if milestone is None else str(milestone.chii)
            row[f"{group}_chii_ordinal"] = (
                "" if milestone is None else milestone.chii.ordinal()
            )
            row[f"{group}_date"] = "" if milestone is None else str(milestone.date)
            row[f"{group}_basho_ordinal"] = (
                "" if milestone is None else milestone.basho_ordinal
            )
        rows.append(row)
    return rows


def _missing_bio_row(item: MissingBio) -> dict[str, object]:
    return {
        "rik_id": int(item.rik_id),
        "shikona": item.shikona,
        "chii": str(item.milestone.chii),
        "chii_ordinal": item.milestone.chii.ordinal(),
        "date": str(item.milestone.date),
        "basho_ordinal": item.milestone.basho_ordinal,
        "reason": "missing_bio",
    }


def _write_dict_rows(
    path: Path,
    fieldnames: list[str] | tuple[str, ...],
    rows,
) -> Path:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _warn_missing_bios(missing_bios: tuple[MissingBio, ...], *, stream: TextIO) -> None:
    for item in missing_bios:
        print(
            "WARNING: missing bio; excluded "
            f"rik_id={int(item.rik_id)} "
            f"shikona={item.shikona} "
            f"chii={item.milestone.chii} "
            f"chii_ordinal={item.milestone.chii.ordinal()} "
            f"date={item.milestone.date} "
            f"basho_ordinal={item.milestone.basho_ordinal}",
            file=stream,
        )


def _build_rankings(
    milestones: Mapping[RikId, Mapping[str, Milestone]],
    names: FullShikonaStore,
    *,
    history: History,
) -> dict[str, object]:
    group_position = {group: index for index, group in enumerate(GROUPS)}
    cohorts: dict[str, list[tuple[RikId, str, Milestone]]] = {
        group: [] for group in GROUPS
    }
    for rik_id, rikishi_milestones in milestones.items():
        start_group, start = min(
            rikishi_milestones.items(),
            key=lambda item: (item[1].basho_ordinal, group_position[item[0]]),
        )
        if start.basho_ordinal == 1:
            continue
        cohorts[start_group].append((rik_id, start_group, start))

    routes: dict[str, object] = {}
    for start_index, start_group in enumerate(GROUPS):
        cohort = cohorts[start_group]
        if not cohort:
            continue
        for finish_group in GROUPS[start_index + 1 :]:
            records = []
            for rik_id, _, start in cohort:
                finish = milestones[rik_id].get(finish_group)
                if finish is None or finish.basho_ordinal <= start.basho_ordinal:
                    continue
                records.append(
                    {
                        "rik_id": int(rik_id),
                        "shikona": names.full_shikona(rik_id),
                        "elapsed_basho": finish.basho_ordinal
                        - start.basho_ordinal,
                        "start_chii": str(start.chii),
                        "start_chii_ordinal": start.chii.ordinal(),
                        "start_date": str(start.date),
                        "start_basho_ordinal": start.basho_ordinal,
                        "finish_chii": str(finish.chii),
                        "finish_chii_ordinal": finish.chii.ordinal(),
                        "finish_date": str(finish.date),
                        "finish_basho_ordinal": finish.basho_ordinal,
                    }
                )
            fastest = sorted(
                records,
                key=lambda row: (
                    row["elapsed_basho"],
                    row["finish_basho_ordinal"],
                    row["rik_id"],
                ),
            )
            slowest = sorted(
                records,
                key=lambda row: (
                    -row["elapsed_basho"],
                    row["finish_basho_ordinal"],
                    row["rik_id"],
                ),
            )
            slowest_position = {
                row["rik_id"]: position
                for position, row in enumerate(slowest, start=1)
            }
            ranked_records = [
                {
                    "fastest_position": position,
                    "slowest_position": slowest_position[row["rik_id"]],
                    **row,
                }
                for position, row in enumerate(fastest, start=1)
            ]
            routes[f"{start_group}:{finish_group}"] = {
                "start_group": start_group,
                "finish_group": finish_group,
                "starter_count": len(cohort),
                "reached_count": len(records),
                "not_reached_count": len(cohort) - len(records),
                "records": ranked_records,
            }
    dates = sorted(history)
    return {
        "schema_version": 1,
        "history": {
            "start": str(dates[0]),
            "end": str(dates[-1]),
            "basho_count": len(dates),
            "basho_ordinal_base": 1,
        },
        "ranking_policy": (
            "complete consecutive positions; equal elapsed values are ordered "
            "by finish_basho_ordinal then rik_id"
        ),
        "routes": routes,
    }

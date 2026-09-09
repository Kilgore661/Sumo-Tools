"""Read and validate a saved production run without invoking its producer."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_output(output: Path, inputs: list[Path]) -> None:
    output = output.resolve()
    for source in inputs:
        source = source.resolve()
        if output == source or output in source.parents or source in output.parents:
            raise ValueError(f"Output overlaps input: {output} and {source}")


@dataclass
class Inputs:
    manifest: dict
    starts: dict
    ends: dict
    adjustments: dict
    bouts: dict
    counts: dict
    metadata: dict
    paths: dict
    hashes: dict
    history_digest: str

    @property
    def dates(self):
        return sorted(self.ends)

    def verify_unchanged(self):
        for key, path in self.paths.items():
            if digest(path) != self.hashes[key]:
                raise ValueError(f"Input changed during analysis: {path}")


def load_inputs(root: Path, history) -> Inputs:
    root = root.resolve()
    paths = {"manifest": root / "manifest.json"}
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    if manifest.get("model_id") != "elo-89":
        raise ValueError("Expected an elo-89 production run")
    for key in ("basho_start_ratings", "basho_end_ratings", "basho_adjustments", "bout_ledger"):
        path = (root / manifest["files"][key]).resolve()
        if root not in path.parents:
            raise ValueError(f"Artifact outside input root: {path}")
        paths[key] = path
    hashes = {key: digest(path) for key, path in paths.items()}
    starts = json.loads(paths["basho_start_ratings"].read_text())
    ends = json.loads(paths["basho_end_ratings"].read_text())
    dates = sorted(ends)
    if not dates or set(starts) != set(ends):
        raise ValueError("Empty or inconsistent snapshot dates")
    if dates[0] != manifest["history"]["start"] or dates[-1] != manifest["history"]["end"]:
        raise ValueError("Snapshot coverage disagrees with manifest")
    states = {str(date): history[date] for date in history if dates[0] <= str(date) <= dates[-1]}
    if set(states) != set(dates):
        raise ValueError("History and saved run have different represented dates")
    with paths["basho_adjustments"].open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    adjustments = {row["date"]: {key: (value if key == "date" else float(value))
                                for key, value in row.items()} for row in rows}
    if len(rows) != len(dates) or set(adjustments) != set(dates):
        raise ValueError("Duplicate or missing basho adjustments")
    metadata, previous, history_records = {}, set(), []
    from src.sumo_core.BasicEnums import MSD
    for date in dates:
        active = set(starts[date])
        if active != set(ends[date]):
            raise ValueError(f"Snapshot membership differs at {date}")
        row = adjustments[date]
        if not all(math.isfinite(value) for key, value in row.items() if key != "date"):
            raise ValueError(f"Non-finite adjustment at {date}")
        if (row["active_count"] != len(active)
                or row["new_rikishi_count"] != len(active - previous)
                or row["departing_rikishi_count"] != len(previous - active)):
            raise ValueError(f"Population counts disagree at {date}")
        target = float(manifest["target_mean"])
        if (abs(row["target_mean"] - target) > 1e-6
                or abs(row["raw_start_mean"] + row["start_adjustment"] - target) > 1e-6
                or abs(row["raw_end_mean"] + row["end_adjustment"] - target) > 1e-6):
            raise ValueError(f"Adjustment means disagree at {date}")
        for snapshot in (starts[date], ends[date]):
            if not all(math.isfinite(float(value)) for value in snapshot.values()):
                raise ValueError("Non-finite rating")
            if abs(sum(snapshot.values()) / len(active) - target) > 1e-6:
                raise ValueError(f"Snapshot mean disagrees at {date}")
        state = states[date]
        if not {str(int(rid)) for rid in state.banzuke.riks} <= active:
            raise ValueError(f"History banzuke differs at {date}")
        metadata[date] = {}
        for rid in active:
            chii = state.banzuke.rikchii.get(int(rid))
            division = ("unclassified" if chii is None else
                        "makuuchi" if isinstance(chii.level, MSD) else
                        chii.level.name.lower())
            metadata[date][rid] = {
                "chii": "" if chii is None else str(chii), "division": division,
                "name": str(state.banzuke.rikshik.get(int(rid), f"Rikishi {rid}")),
            }
        history_records.append([date, sorted((rid, value) for rid, value in metadata[date].items())])
        previous = active

    # This uses the same eligible-bout selector as production, not a replay.
    from src.analysis.prediction.bouts import select_rated_bouts
    date_keys = {str(date): date for date in history}
    selection = select_rated_bouts(history, start_date=date_keys[dates[0]], end_date=date_keys[dates[-1]])
    expected = {}
    for bout in selection.bouts:
        contest = bout.contest
        key = (str(contest.id.date), int(contest.id.day), int(contest.rikishi_a), int(contest.rikishi_b))
        if key in expected:
            raise ValueError(f"Duplicate History bout: {key}")
        expected[key] = bool(bout.a_won)
    bouts, counts, seen = {}, {}, set()
    with paths["bout_ledger"].open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            date = row["date"]
            key = (date, int(row["day"]), int(row["rikishi_a"]), int(row["rikishi_b"]))
            if key in seen or key not in expected or (row["a_won"].lower() == "true") != expected[key]:
                raise ValueError(f"History and ledger bout mismatch: {key}")
            seen.add(key)
            for side in ("a", "b"):
                rid = row[f"rikishi_{side}"]
                if rid not in starts[date]:
                    raise ValueError(f"Inactive ledger participant: {date}/{rid}")
                if row[f"chii_{side}"] != metadata[date][rid]["chii"]:
                    raise ValueError(f"History and ledger chii mismatch: {date}/{rid}")
                delta = float(row[f"delta_{side}"])
                if not math.isfinite(delta):
                    raise ValueError("Non-finite bout delta")
                pair = date, rid
                bouts[pair] = bouts.get(pair, 0.0) + delta
                counts[pair] = counts.get(pair, 0) + 1
    if seen != set(expected) or len(seen) != manifest["selection"]["rated_bout_count"]:
        raise ValueError("History and ledger bout coverage differs")
    participants = {date: {str(int(rid)) for rid in states[date].banzuke.riks} for date in dates}
    for date, _day, a, b in seen:
        participants[date].update((str(a), str(b)))
    if any(participants[date] != set(starts[date]) for date in dates):
        raise ValueError("Active snapshots differ from History banzuke and bout participants")
    fingerprint = hashlib.sha256(json.dumps([history_records, sorted(expected.items())],
                                            sort_keys=True).encode()).hexdigest()
    result = Inputs(manifest, starts, ends, adjustments, bouts, counts, metadata,
                    paths, hashes, fingerprint)
    result.verify_unchanged()
    return result

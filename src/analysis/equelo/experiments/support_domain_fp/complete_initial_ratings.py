"""Build a total entrant-initial-rating surface from the latest n=60 run."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.analysis.equelo.config_main import BIOS_PATH
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.fixed_v2.build import oracle_collapse_mode
from src.analysis.probability.builder import load_ratings_csv
from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History


SWEEP_ROOT = Path("files/output/Equelo/experiments/support_domain_fp/min_appearance_sweeps")
MIN_APPEARANCES = 60


@dataclass(frozen=True)
class CompletedInitialRating:
    chii: Chii
    initial_rating: float
    source_chii: Chii
    source_rating: float
    source_kind: str


def main() -> None:
    sweep_dir = latest_sweep_dir()
    source_csv = latest_min_appearance_csv(sweep_dir, MIN_APPEARANCES)
    output_root = sweep_dir / f"completed_initial_ratings_min_app_{MIN_APPEARANCES}"

    print(f"Sweep directory: {sweep_dir}")
    print(f"Source CSV: {source_csv}")
    print("[complete-initial-ratings] loading and cleaning history")
    history = cleaned_history()
    required_chii = required_chii_for_simulation(history)
    source_ratings = load_ratings_csv(source_csv)
    completed = complete_initial_ratings(
        required_chii=required_chii,
        source_ratings=source_ratings,
    )
    outputs = write_outputs(
        completed,
        output_root=output_root,
        source_csv=source_csv,
        sweep_dir=sweep_dir,
    )
    direct = sum(1 for row in completed if row.source_kind == "direct")
    nearest = sum(1 for row in completed if row.source_kind == "nearest_supported")
    print(f"Required chii: {len(completed)}")
    print(f"Direct: {direct}")
    print(f"Nearest-supported: {nearest}")
    print(f"Initial ratings CSV: {outputs.initial_ratings_csv}")
    print(f"Audit CSV: {outputs.audit_csv}")
    print(f"Manifest: {outputs.manifest_json}")


@dataclass(frozen=True)
class CompletedInitialRatingOutputs:
    output_root: Path
    initial_ratings_csv: Path
    audit_csv: Path
    manifest_json: Path


def complete_initial_ratings(
    *,
    required_chii: Iterable[Chii],
    source_ratings: dict[Chii, float],
) -> list[CompletedInitialRating]:
    supported = sorted(source_ratings, key=lambda chii: chii.ordinal())
    if not supported:
        raise ValueError("Cannot complete initial ratings from an empty supported rating map")

    completed = []
    for chii in sorted(set(required_chii), key=lambda item: item.ordinal()):
        if chii in source_ratings:
            source_chii = chii
            source_kind = "direct"
        else:
            source_chii = nearest_supported_chii(chii, supported)
            source_kind = "nearest_supported"
        completed.append(
            CompletedInitialRating(
                chii=chii,
                initial_rating=float(source_ratings[source_chii]),
                source_chii=source_chii,
                source_rating=float(source_ratings[source_chii]),
                source_kind=source_kind,
            )
        )
    return completed


def nearest_supported_chii(chii: Chii, supported: list[Chii]) -> Chii:
    target = chii.ordinal()
    best = supported[0]
    best_distance = abs(best.ordinal() - target)
    for candidate in supported[1:]:
        distance = abs(candidate.ordinal() - target)
        if distance < best_distance:
            best = candidate
            best_distance = distance
            continue
        if distance == best_distance and candidate.ordinal() < best.ordinal():
            best = candidate
            best_distance = distance
    return best


def cleaned_history() -> History:
    return make_oracle(
        get_history(),
        load_bios(),
        collapse_mode=oracle_collapse_mode(),
    ).history


def load_bios() -> dict[RikId, dict]:
    with BIOS_PATH.open("r", encoding="utf-8") as f:
        raw_bios = json.load(f)
    return {RikId(int(key)): value for key, value in raw_bios.items()}


def required_chii_for_simulation(history: History) -> set[Chii]:
    return {
        chii
        for basho in history.values()
        for chii in basho.banzuke.rikchii.values()
    }


def latest_sweep_dir() -> Path:
    if not SWEEP_ROOT.exists():
        raise FileNotFoundError(f"Sweep root not found: {SWEEP_ROOT}")
    sweep_dirs = sorted(
        (path for path in SWEEP_ROOT.iterdir() if path.is_dir()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not sweep_dirs:
        raise FileNotFoundError(f"No sweep folders found under {SWEEP_ROOT}")
    return sweep_dirs[0]


def latest_min_appearance_csv(sweep_dir: Path, min_appearances: int) -> Path:
    manifest_paths = sorted(
        (sweep_dir / f"rfsc_min_app_{min_appearances}").glob("*/manifest.json")
    )
    if not manifest_paths:
        raise FileNotFoundError(
            f"No min_app_{min_appearances} manifest found under {sweep_dir}"
        )
    manifest_path = max(manifest_paths, key=lambda path: path.stat().st_mtime)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    csv_path = manifest.get("result", {}).get("combined_final_csv")
    if not csv_path:
        raise ValueError(f"Manifest has no result.combined_final_csv: {manifest_path}")
    return Path(csv_path)


def write_outputs(
    rows: list[CompletedInitialRating],
    *,
    output_root: Path,
    source_csv: Path,
    sweep_dir: Path,
) -> CompletedInitialRatingOutputs:
    output_root.mkdir(parents=True, exist_ok=True)
    outputs = CompletedInitialRatingOutputs(
        output_root=output_root,
        initial_ratings_csv=output_root / "entrant_initial_ratings.csv",
        audit_csv=output_root / "entrant_initial_rating_sources.csv",
        manifest_json=output_root / "manifest.json",
    )
    write_initial_ratings_csv(outputs.initial_ratings_csv, rows)
    write_audit_csv(outputs.audit_csv, rows)
    write_manifest(
        outputs.manifest_json,
        rows=rows,
        source_csv=source_csv,
        sweep_dir=sweep_dir,
    )
    return outputs


def write_initial_ratings_csv(path: Path, rows: list[CompletedInitialRating]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["chii", "ordinal", "initial_rating"])
        for row in rows:
            writer.writerow([str(row.chii), row.chii.ordinal(), f"{row.initial_rating:.12f}"])


def write_audit_csv(path: Path, rows: list[CompletedInitialRating]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "chii",
            "ordinal",
            "initial_rating",
            "source_chii",
            "source_ordinal",
            "source_rating",
            "source_kind",
        ])
        for row in rows:
            writer.writerow([
                str(row.chii),
                row.chii.ordinal(),
                f"{row.initial_rating:.12f}",
                str(row.source_chii),
                row.source_chii.ordinal(),
                f"{row.source_rating:.12f}",
                row.source_kind,
            ])


def write_manifest(
    path: Path,
    *,
    rows: list[CompletedInitialRating],
    source_csv: Path,
    sweep_dir: Path,
) -> None:
    payload = {
        "kind": "completed_initial_ratings",
        "min_appearances": MIN_APPEARANCES,
        "sweep_dir": str(sweep_dir),
        "source_csv": str(source_csv),
        "required_chii_count": len(rows),
        "direct_count": sum(1 for row in rows if row.source_kind == "direct"),
        "nearest_supported_count": sum(
            1 for row in rows if row.source_kind == "nearest_supported"
        ),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

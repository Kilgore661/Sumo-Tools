"""Execute and persist the paired Elo89a fixed-point experiment."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from datetime import datetime
import hashlib
import json
from pathlib import Path

from src.analysis.absences.jsa_check.source import (
    DEFAULT_STANDINGS_ROOT,
    load_final_records,
)
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo_bkp1.params import (
    DEFAULT_K_CONFIG,
    MODEL_BASE,
    MODEL_Q,
    load_divisional_k,
)
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date

from .model import ExperimentArm, FixedPointResult
from .replay import prepare_replay_evidence
from .solve import solve


DEFAULT_HISTORY_ZIP = Path("files/output/Historys/1989_01 to 2026_11.zip")
DEFAULT_PRIOR = Path("files/output/analysis/equelo_bkp1/prior.csv")
DEFAULT_OUTPUT = Path("files/output/analysis/elo_penalties/elo89a")
LANDMARKS = (
    "Y1e",
    "O1e",
    "S1e",
    "K1e",
    "M1e",
    "M10e",
    "M18e",
    "J1e",
    "J14e",
    "Ms1e",
    "Ms60e",
    "Sd1e",
    "Sd100e",
    "Jd1e",
    "Jd100e",
    "Jk1e",
)


def main(argv: list[str] | None = None) -> int:
    """Run both fixed-point arms and write their comparison artefacts."""

    args = _parser().parse_args(argv)
    history_zip = _resolved_zip(args.history_zip)
    raw_history = load_history_with_annotations(str(history_zip.with_suffix("")))
    history = make_oracle(raw_history, collapse_mode="annotation_only").history

    final_records = load_final_records(
        args.standings_root,
        start=args.start,
        end=args.end,
    )
    if not final_records:
        raise ValueError("Elo89a selected no published final records")
    start_date = Date.from_ints(*args.start)
    end_date = Date.from_ints(*(args.end or _date_key(max(final_records))))
    dates = tuple(
        date
        for date in sorted(history)
        if start_date <= date <= end_date
    )
    record_dates = tuple(
        date
        for date in sorted(final_records)
        if start_date <= date <= end_date
    )
    if dates != record_dates:
        history_only = sorted(set(dates) - set(record_dates))
        records_only = sorted(set(record_dates) - set(dates))
        raise ValueError(
            "History and published final-record dates differ: "
            f"{len(history_only)} History-only, {len(records_only)} records-only"
        )

    evidence = prepare_replay_evidence(history, dates, final_records)
    k_config = args.k_config.resolve()
    divisional_k = load_divisional_k(k_config)
    results = {
        arm: solve(
            history,
            evidence,
            divisional_k,
            arm,
            base=MODEL_BASE,
            epsilon=args.epsilon,
            max_iterations=args.max_iterations,
            progress=_progress,
        )
        for arm in (ExperimentArm.CONTROL, ExperimentArm.ELO89A)
    }
    canonical_prior = _load_prior(args.prior.resolve())
    _require_prior_coverage(canonical_prior, results[ExperimentArm.CONTROL])
    _write_outputs(
        output=args.output,
        args=args,
        history_zip=history_zip,
        k_config=k_config,
        dates=dates,
        final_records=final_records,
        evidence=evidence,
        results=results,
        canonical_prior=canonical_prior,
    )
    findings = _findings(results, canonical_prior)
    print(findings, end="")
    return 0 if all(result.converged for result in results.values()) else 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, default=DEFAULT_HISTORY_ZIP)
    parser.add_argument("--standings-root", type=Path, default=DEFAULT_STANDINGS_ROOT)
    parser.add_argument("--prior", type=Path, default=DEFAULT_PRIOR)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--start", type=_parse_year_month, default=(1989, 1))
    parser.add_argument("--end", type=_parse_year_month)
    parser.add_argument("--epsilon", type=float, default=10.0)
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def _write_outputs(
    *,
    output: Path,
    args,
    history_zip: Path,
    k_config: Path,
    dates,
    final_records,
    evidence,
    results: dict[ExperimentArm, FixedPointResult],
    canonical_prior: dict[Chii, float],
) -> None:
    """Persist the complete reproducible experiment artefact set."""

    output.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output / "basho_adjustments.csv",
        (
            asdict(row)
            for arm in (ExperimentArm.CONTROL, ExperimentArm.ELO89A)
            for row in results[arm].replay.adjustments
        ),
    )
    _write_csv(
        output / "iterations.csv",
        (
            asdict(row)
            for arm in (ExperimentArm.CONTROL, ExperimentArm.ELO89A)
            for row in results[arm].iteration_rows
        ),
    )
    _write_csv(
        output / "iteration_priors.csv",
        (
            asdict(row)
            for arm in (ExperimentArm.CONTROL, ExperimentArm.ELO89A)
            for row in results[arm].iteration_priors
        ),
    )
    control = results[ExperimentArm.CONTROL]
    elo89a = results[ExperimentArm.ELO89A]
    _write_csv(
        output / "prior_comparison.csv",
        (
            {
                "chii": str(chii),
                "ordinal": chii.ordinal(),
                "observations": control.support[chii],
                "canonical_p1": canonical_prior[chii],
                "control": control.priors[chii],
                "elo89a": elo89a.priors[chii],
                "elo89a_minus_control": elo89a.priors[chii] - control.priors[chii],
                "elo89a_minus_canonical": elo89a.priors[chii] - canonical_prior[chii],
            }
            for chii in sorted(control.priors, key=lambda item: item.ordinal())
        ),
    )
    findings = _findings(results, canonical_prior)
    (output / "findings.md").write_text(findings, encoding="utf-8")

    prior_path = args.prior.resolve()
    manifest = {
        "experiment": "Elo89a viability fixed point",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "interval": {"start": str(dates[0]), "end": str(dates[-1])},
        "q": MODEL_Q,
        "base": MODEL_BASE,
        "epsilon": args.epsilon,
        "max_iterations": args.max_iterations,
        "penalty": "divisional_k / 2 per FP and published A",
        "penalty_timing": "basho end before whole-population normalisation",
        "history_zip": str(history_zip),
        "history_zip_sha256": _sha256(history_zip),
        "final_records_root": str(args.standings_root.resolve()),
        "selected_final_records_sha256": _final_records_sha256(
            dates,
            final_records,
        ),
        "canonical_prior": str(prior_path),
        "canonical_prior_sha256": _sha256(prior_path),
        "k_config": str(k_config),
        "k_config_sha256": _sha256(k_config),
        "selection": {
            "raw_result_count": evidence.raw_result_count,
            "rated_bout_count": evidence.rated_bout_count,
            "excluded_fusen_count": evidence.excluded_fusen_count,
            "excluded_draw_count": evidence.excluded_draw_count,
        },
        "arms": {
            arm.value: {
                "converged": results[arm].converged,
                "iterations": results[arm].iterations,
                "final_delta": results[arm].final_delta,
                "minimum_prior": min(results[arm].priors.values()),
                "maximum_prior": max(results[arm].priors.values()),
            }
            for arm in (ExperimentArm.CONTROL, ExperimentArm.ELO89A)
        },
        "files": {
            "basho_adjustments": "basho_adjustments.csv",
            "iterations": "iterations.csv",
            "iteration_priors": "iteration_priors.csv",
            "prior_comparison": "prior_comparison.csv",
            "findings": "findings.md",
        },
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _findings(
    results: dict[ExperimentArm, FixedPointResult],
    canonical_prior: dict[Chii, float],
) -> str:
    """Return a factual human-inspection summary without quality judgement."""

    control = results[ExperimentArm.CONTROL]
    elo89a = results[ExperimentArm.ELO89A]
    lines = [
        "# Elo89a viability experiment",
        "",
        "| Arm | Converged | Iterations | Final maximum change | Minimum prior | Maximum prior |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for result in (control, elo89a):
        lines.append(
            f"| {result.arm.value} | {result.converged} | {result.iterations} | "
            f"{result.final_delta:.6f} | {min(result.priors.values()):.3f} | "
            f"{max(result.priors.values()):.3f} |"
        )
    lines.extend(
        [
            "",
            "## Selected chii landmarks",
            "",
            "| Chii | Canonical P1 | Control | Elo89a | Elo89a - control |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for label in LANDMARKS:
        chii = Chii.from_str(label)
        if chii not in control.priors:
            continue
        lines.append(
            f"| {label} | {canonical_prior[chii]:.3f} | "
            f"{control.priors[chii]:.3f} | {elo89a.priors[chii]:.3f} | "
            f"{elo89a.priors[chii] - control.priors[chii]:+.3f} |"
        )
    lines.extend(
        [
            "",
            "The complete comparison is in `prior_comparison.csv`; complete",
            "iteration maps are in `iteration_priors.csv`.",
            "",
        ]
    )
    return "\n".join(lines)


def _load_prior(path: Path) -> dict[Chii, float]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = tuple(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"Empty canonical P1 prior: {path}")
    return {Chii.from_str(row["chii"]): float(row["rating"]) for row in rows}


def _require_prior_coverage(
    canonical_prior: dict[Chii, float],
    result: FixedPointResult,
) -> None:
    missing = set(result.priors) - set(canonical_prior)
    if missing:
        raise KeyError(f"Canonical P1 omits {len(missing)} experimental chii")


def _write_csv(path: Path, rows) -> None:
    iterator = iter(rows)
    first = next(iterator)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(first))
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(iterator)


def _progress(row) -> None:
    if row.iteration == 1 or row.iteration % 10 == 0 or row.max_prior_change < 10.0:
        print(
            f"[{row.arm}] iteration={row.iteration} "
            f"delta={row.max_prior_change:.6f} max={row.max_change_chii} "
            f"n={row.max_change_observation_count}",
            flush=True,
        )


def _parse_year_month(value: str) -> tuple[int, int]:
    try:
        year_text, month_text = value.split("/", maxsplit=1)
        year, month = int(year_text), int(month_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"Expected YYYY/MM, got {value!r}") from error
    if month not in (1, 3, 5, 7, 9, 11):
        raise argparse.ArgumentTypeError(f"Not a basho month: {value}")
    return year, month


def _resolved_zip(path: Path) -> Path:
    resolved = path.resolve()
    zip_path = resolved if resolved.suffix == ".zip" else resolved.with_suffix(".zip")
    if not zip_path.is_file():
        raise FileNotFoundError(f"History zip not found: {zip_path}")
    return zip_path


def _date_key(date: Date) -> tuple[int, int]:
    return int(date.year), int(date.month)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _final_records_sha256(dates, final_records) -> str:
    digest = hashlib.sha256()
    for date in dates:
        for rikishi, record in sorted(final_records[date].items()):
            digest.update(
                f"{date},{int(rikishi)},{record.source_text}\n".encode("utf-8")
            )
    return digest.hexdigest()

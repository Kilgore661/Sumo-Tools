"""Run a sandbox fixed-point solve with support-domain filtering."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.analysis.equelo.config_main import INITIAL_ELO
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import DEFAULT_K_CONFIG_PATH, build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode
from src.analysis.equelo.expt2.diagnostics import (
    IterationDiagnosticsWriter,
    default_probe_set,
)
from src.analysis.equelo.expt2.solve import solve_variant_combined
from src.analysis.equelo.fixed_v2.build import load_bios, oracle_collapse_mode
from src.analysis.equelo.fixed_v2.model import FP_SOURCE, K_POLICY, Q
from src.analysis.equelo.support_domain.reports import write_support_domain_reports
from src.analysis.probability.builder import load_ratings_csv
from src.infra.live_store.api import get_history
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .history import (
    FilteredHistory,
    build_max_chii_filtered_history,
    build_min_appearances_filtered_history,
    build_threshold_filtered_history,
)


OUTPUT_ROOT = Path("files/output/Equelo/experiments/support_domain_fp")
DEFAULT_THRESHOLD = 0.01
DEFAULT_MAX_CHII = "Jd100w"
DEFAULT_MIN_APPEARANCES = 100


@dataclass(frozen=True)
class ExperimentOutputs:
    run_dir: Path
    manifest_json: Path
    support_csv: Path
    threshold_summary_csv: Path
    modern_final_csv: Path | None
    combined_final_csv: Path | None
    combined_stats_csv: Path | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run support-domain filtered Equelo fixed-point sandbox."
    )
    parser.add_argument(
        "--domain",
        choices=("support-threshold", "max-chii", "min-appearances"),
        default="support-threshold",
        help="Choose the experimental rating-domain policy.",
    )
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument(
        "--max-chii",
        default=DEFAULT_MAX_CHII,
        help="Lowest included chii for --domain max-chii.",
    )
    parser.add_argument(
        "--min-appearances",
        type=int,
        default=DEFAULT_MIN_APPEARANCES,
        help="Minimum collapsed basho-start appearances for --domain min-appearances.",
    )
    parser.add_argument("--epsilon", type=float, default=1.0)
    parser.add_argument("--max-iter", type=int, default=10000000)
    parser.add_argument("--modern-start-year", type=int, default=1989)
    parser.add_argument("--modern-end-year", type=int, default=2026)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--fp-source", type=Path, default=FP_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = run_experiment(
        threshold=args.threshold,
        domain=args.domain,
        max_chii=Chii.from_str(args.max_chii),
        min_appearances=args.min_appearances,
        epsilon=args.epsilon,
        max_iter=args.max_iter,
        modern_start_year=args.modern_start_year,
        modern_end_year=args.modern_end_year,
        output_root=args.output_root,
        fp_source=args.fp_source,
    )
    print("Support-domain FP sandbox complete")
    print(f"Run directory: {outputs.run_dir}")
    print(f"Manifest: {outputs.manifest_json}")
    print(f"Support CSV: {outputs.support_csv}")
    print(f"Threshold summary: {outputs.threshold_summary_csv}")
    print(f"Modern final CSV: {outputs.modern_final_csv}")
    print(f"Combined final CSV: {outputs.combined_final_csv}")
    print(f"Combined stats CSV: {outputs.combined_stats_csv}")


def run_experiment(
    *,
    threshold: float,
    domain: str,
    max_chii: Chii,
    min_appearances: int,
    epsilon: float,
    max_iter: int,
    modern_start_year: int,
    modern_end_year: int,
    output_root: Path,
    fp_source: Path,
    raw_history: History | None = None,
) -> ExperimentOutputs:
    run_dir = _create_run_dir(
        output_root,
        domain=domain,
        threshold=threshold,
        max_chii=max_chii,
        min_appearances=min_appearances,
    )
    print(f"[support-domain-fp] run_dir={run_dir}")
    print("[support-domain-fp] loading history")
    oracle = make_oracle(
        get_history() if raw_history is None else raw_history,
        load_bios(),
        collapse_mode=oracle_collapse_mode(),
    )
    filtered = _build_filtered_history(
        oracle.history,
        domain=domain,
        threshold=threshold,
        max_chii=max_chii,
        min_appearances=min_appearances,
    )
    report_outputs = write_support_domain_reports(
        measurement=filtered.measurement,
        fixed_point_ratings=load_ratings_csv(fp_source),
        thresholds=(threshold,),
        output_root=run_dir / "support_domain",
    )

    params = build_elo_params(
        k_policy=K_POLICY,
        q=Q,
        config_path=DEFAULT_K_CONFIG_PATH,
    )
    probes = _available_default_probes(
        filtered.history,
        modern_start_year=modern_start_year,
        modern_end_year=modern_end_year,
    )
    result = solve_variant_combined(
        history=filtered.history,
        params=params,
        epsilon=epsilon,
        max_iter=max_iter,
        modern_start_year=modern_start_year,
        modern_end_year=modern_end_year,
        mode=SimulationMode.CLOSED,
        probes=probes,
        output_csv_path=run_dir / f"{_run_stem(domain, threshold, max_chii, min_appearances)}_combined_final.csv",
        diagnostics=IterationDiagnosticsWriter(
            probes=probes,
            stem="combined_iterations",
            output_root=run_dir,
            metadata=_diagnostics_metadata(
                filtered,
                domain=domain,
                threshold=threshold,
                max_chii=max_chii,
                min_appearances=min_appearances,
            ),
        ),
        modern_output_csv_path=run_dir / f"{_run_stem(domain, threshold, max_chii, min_appearances)}_modern_final.csv",
        modern_diagnostics=IterationDiagnosticsWriter(
            probes=probes,
            stem="modern_iterations",
            output_root=run_dir,
            metadata=_diagnostics_metadata(
                filtered,
                domain=domain,
                threshold=threshold,
                max_chii=max_chii,
                min_appearances=min_appearances,
            ),
        ),
        base=INITIAL_ELO,
    )

    manifest_path = run_dir / "manifest.json"
    _write_manifest(
        manifest_path,
        threshold=threshold,
        domain=domain,
        max_chii=max_chii,
        min_appearances=min_appearances,
        epsilon=epsilon,
        max_iter=max_iter,
        modern_start_year=modern_start_year,
        modern_end_year=modern_end_year,
        filtered=filtered,
        result=result,
    )
    return ExperimentOutputs(
        run_dir=run_dir,
        manifest_json=manifest_path,
        support_csv=report_outputs.support_csv,
        threshold_summary_csv=report_outputs.threshold_summary_csv,
        modern_final_csv=result.modern_output_csv_path,
        combined_final_csv=result.output_csv_path,
        combined_stats_csv=result.stats_csv_path,
    )


def _build_filtered_history(
    history,
    *,
    domain: str,
    threshold: float,
    max_chii: Chii,
    min_appearances: int,
) -> FilteredHistory:
    if domain == "support-threshold":
        return build_threshold_filtered_history(history, threshold=threshold)
    if domain == "max-chii":
        return build_max_chii_filtered_history(history, max_chii=max_chii)
    if domain == "min-appearances":
        return build_min_appearances_filtered_history(
            history,
            min_appearances=min_appearances,
        )
    raise ValueError(f"Unsupported domain policy: {domain}")


def _create_run_dir(
    output_root: Path,
    *,
    domain: str,
    threshold: float,
    max_chii: Chii,
    min_appearances: int,
) -> Path:
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = output_root / _run_stem(domain, threshold, max_chii, min_appearances) / stamp
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def _run_stem(domain: str, threshold: float, max_chii: Chii, min_appearances: int) -> str:
    if domain == "max-chii":
        return f"rfsc_max_{max_chii}"
    if domain == "min-appearances":
        return f"rfsc_min_app_{min_appearances}"
    threshold_stem = f"{threshold:.3f}".replace(".", "_")
    return f"rfsc_s_{threshold_stem}"


def _diagnostics_metadata(
    filtered: FilteredHistory,
    *,
    domain: str,
    threshold: float,
    max_chii: Chii,
    min_appearances: int,
) -> dict[str, str]:
    metadata = {
        "policy": "RFSC",
        "domain": filtered.domain_label,
    }
    if domain == "support-threshold":
        metadata["threshold"] = f"{threshold:g}"
    if domain == "max-chii":
        metadata["max_chii"] = str(max_chii)
    if domain == "min-appearances":
        metadata["min_appearances"] = str(min_appearances)
    return metadata


def _available_default_probes(
    history,
    *,
    modern_start_year: int,
    modern_end_year: int,
):
    full_domain = _chii_domain(history)
    modern_domain = _chii_domain({
        date: basho
        for date, basho in history.items()
        if modern_start_year <= date.year <= modern_end_year
    })
    available = full_domain & modern_domain
    return [
        probe
        for probe in default_probe_set()
        if probe in available
    ]


def _chii_domain(history) -> set[Chii]:
    return {
        chii
        for basho in history.values()
        for chii in basho.banzuke.rikchii.values()
    }


def _write_manifest(
    path: Path,
    *,
    threshold: float,
    domain: str,
    max_chii: Chii,
    min_appearances: int,
    epsilon: float,
    max_iter: int,
    modern_start_year: int,
    modern_end_year: int,
    filtered: FilteredHistory,
    result,
) -> None:
    payload = {
        "policy": "RFSC",
        "domain": domain,
        "domain_label": filtered.domain_label,
        "threshold": threshold,
        "configured_max_chii": str(max_chii),
        "min_appearances": min_appearances,
        "epsilon": epsilon,
        "max_iter": max_iter,
        "modern_start_year": modern_start_year,
        "modern_end_year": modern_end_year,
        "supported_chii_count": len(filtered.supported_chii),
        "retained_bouts": filtered.retained_bouts,
        "ignored_bouts": filtered.ignored_bouts,
        "result": {
            "converged": result.converged,
            "iterations": result.iterations,
            "final_delta": result.final_delta,
            "combined_final_csv": None if result.output_csv_path is None else str(result.output_csv_path),
            "combined_stats_csv": None if result.stats_csv_path is None else str(result.stats_csv_path),
            "modern_final_csv": None if result.modern_output_csv_path is None else str(result.modern_output_csv_path),
        },
    }
    if domain == "max-chii":
        payload["max_chii"] = str(max_chii)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

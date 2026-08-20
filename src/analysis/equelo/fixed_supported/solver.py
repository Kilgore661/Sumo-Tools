"""Supported-domain fixed-point solver for fixed-supported Equelo."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.analysis.equelo.config_main import INITIAL_ELO
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode
from src.analysis.equelo.expt2.diagnostics import (
    IterationDiagnosticsWriter,
    default_probe_set,
)
from src.analysis.equelo.expt2.solve import solve_variant_combined
from src.analysis.equelo.smoothing.chart import (
    write_chii_support_csv,
    write_supported_fixed_point_chart,
)
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .build import oracle_collapse_mode
from .model import K_CONFIG, K_POLICY, OUTPUT_ROOT, Q
from .support import FilteredHistory, build_min_appearances_filtered_history


@dataclass(frozen=True)
class SupportedSolveOutputs:
    run_dir: Path
    manifest_json: Path
    modern_final_csv: Path | None
    combined_final_csv: Path | None
    combined_stats_csv: Path | None
    all_chii_support_csv: Path
    supported_estimates_chart_html: Path | None


def run_supported_solve(
    *,
    raw_history: History,
    min_appearances: int,
    epsilon: float,
    max_iter: int,
    modern_start_year: int,
    modern_end_year: int,
    output_root: Path = OUTPUT_ROOT / "solver_runs",
) -> SupportedSolveOutputs:
    """Run the production supported-domain fixed-point solve."""

    run_dir = _create_run_dir(output_root, min_appearances=min_appearances)
    print(f"[fixed-supported] run_dir={run_dir}")
    print("[fixed-supported] preparing cleaned history")
    oracle = make_oracle(
        raw_history,
        collapse_mode=oracle_collapse_mode(),
    )
    filtered = build_min_appearances_filtered_history(
        oracle.history,
        min_appearances=min_appearances,
    )
    params = build_elo_params(
        k_policy=K_POLICY,
        q=Q,
        config_path=K_CONFIG,
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
        output_csv_path=run_dir / f"rfsc_min_app_{min_appearances}_combined_final.csv",
        diagnostics=IterationDiagnosticsWriter(
            probes=probes,
            stem="combined_iterations",
            output_root=run_dir,
            metadata=_diagnostics_metadata(filtered, min_appearances=min_appearances),
        ),
        modern_output_csv_path=run_dir / f"rfsc_min_app_{min_appearances}_modern_final.csv",
        modern_diagnostics=IterationDiagnosticsWriter(
            probes=probes,
            stem="modern_iterations",
            output_root=run_dir,
            metadata=_diagnostics_metadata(filtered, min_appearances=min_appearances),
        ),
        base=INITIAL_ELO,
    )
    all_chii_support_csv = write_chii_support_csv(
        run_dir / "all_chii_support.csv",
        filtered.measurement.appearances,
    )
    supported_estimates_chart = (
        None
        if result.stats_csv_path is None
        else write_supported_fixed_point_chart(
            result.stats_csv_path,
            support_csv=all_chii_support_csv,
        )
    )
    manifest_path = run_dir / "manifest.json"
    _write_manifest(
        manifest_path,
        min_appearances=min_appearances,
        epsilon=epsilon,
        max_iter=max_iter,
        modern_start_year=modern_start_year,
        modern_end_year=modern_end_year,
        filtered=filtered,
        result=result,
        all_chii_support_csv=all_chii_support_csv,
        supported_estimates_chart=supported_estimates_chart,
    )
    return SupportedSolveOutputs(
        run_dir=run_dir,
        manifest_json=manifest_path,
        modern_final_csv=result.modern_output_csv_path,
        combined_final_csv=result.output_csv_path,
        combined_stats_csv=result.stats_csv_path,
        all_chii_support_csv=all_chii_support_csv,
        supported_estimates_chart_html=supported_estimates_chart,
    )


def _create_run_dir(output_root: Path, *, min_appearances: int) -> Path:
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = output_root / f"rfsc_min_app_{min_appearances}" / stamp
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def _diagnostics_metadata(
    filtered: FilteredHistory,
    *,
    min_appearances: int,
) -> dict[str, str]:
    return {
        "policy": "RFSC",
        "domain": filtered.domain_label,
        "min_appearances": str(min_appearances),
    }


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
    return [probe for probe in default_probe_set() if probe in available]


def _chii_domain(history) -> set[Chii]:
    return {
        chii
        for basho in history.values()
        for chii in basho.banzuke.rikchii.values()
    }


def _write_manifest(
    path: Path,
    *,
    min_appearances: int,
    epsilon: float,
    max_iter: int,
    modern_start_year: int,
    modern_end_year: int,
    filtered: FilteredHistory,
    result,
    all_chii_support_csv: Path,
    supported_estimates_chart: Path | None,
) -> None:
    payload = {
        "policy": "RFSC",
        "domain": "min-appearances",
        "domain_label": filtered.domain_label,
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
            "all_chii_support_csv": str(all_chii_support_csv),
            "supported_estimates_chart_html": None if supported_estimates_chart is None else str(supported_estimates_chart),
        },
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

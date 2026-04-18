from __future__ import annotations

import argparse
import csv
import datetime
import json
from dataclasses import dataclass
from pathlib import Path

from src.infra.config import EPOCH
from src.infra.connect import connect
from src.sumo_core.BasicPrimitives import RikId

from src.analysis.equelo.config_main import BIOS_PATH, INITIAL_ELO
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import DEFAULT_K_CONFIG_PATH, build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode, expect, simulate

# Import from expt3c so the sweep uses the same observer / summaries / initialiser plumbing
from .expt3c import (
    Expt3ProbabilityObserver,
    _select_entrant_initialiser,
    build_calibration_rows_from_bouts,
    summarise_brier_raw,
    summarise_brier_binned,
)


@dataclass(frozen=True)
class SweepRow:
    alpha: float
    raw_brier: float
    raw_baseline_brier: float
    raw_brier_skill: float
    binned_brier: float
    binned_baseline_brier: float
    binned_brier_skill: float
    brier_reliability: float
    brier_resolution: float
    brier_uncertainty: float
    calibration_mae_binned: float
    calibration_rmse_binned: float
    raw_bout_observations: int
    base_rate: float


MINIMISE_OBJECTIVES = {"raw_brier", "calibration_mae_binned"}
MAXIMISE_OBJECTIVES = {"raw_brier_skill"}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sweep expt2_scaled alpha for Expt3, loading history only once."
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--closed", action="store_true")

    parser.add_argument("--k-policy", choices=("constant", "divisional"), default="divisional")
    parser.add_argument("--k-value", type=float, default=None)
    parser.add_argument("--k-config", type=Path, default=None)

    parser.add_argument("--b", type=float, default=INITIAL_ELO)
    parser.add_argument("--q", type=float, default=900.0)
    parser.add_argument("--bin-width", type=float, default=0.02)

    parser.add_argument("--alpha-start", type=float, required=True)
    parser.add_argument("--alpha-end", type=float, required=True)
    parser.add_argument("--alpha-step", type=float, required=True)

    parser.add_argument(
        "--objective",
        choices=("raw_brier", "raw_brier_skill", "calibration_mae_binned"),
        default="calibration_mae_binned",
        help="Objective used for console arrows and best-row reporting.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("files/output/Equelo/expt3_alpha_sweep.csv"),
        help="Output CSV path.",
    )
    return parser


def _validate_k_policy_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.k_policy == "constant" and args.k_config is not None:
        parser.error("--k-config is only valid with --k-policy divisional")
    if args.k_policy == "divisional" and args.k_value is not None:
        parser.error("--k-value is only valid with --k-policy constant")


def _validate_objective(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.objective not in MINIMISE_OBJECTIVES | MAXIMISE_OBJECTIVES:
        parser.error(f"Unknown objective: {args.objective}")


def _alpha_values(start: float, end: float, step: float) -> list[float]:
    if step <= 0:
        raise ValueError(f"alpha-step must be positive, got {step}")
    if end < start:
        raise ValueError(f"alpha-end must be >= alpha-start, got {start}..{end}")

    values: list[float] = []
    alpha = start
    eps = step / 1_000_000
    while alpha <= end + eps:
        values.append(round(alpha, 10))
        alpha += step
    return values


def _run_one_alpha(
    *,
    history,
    alpha: float,
    mode: SimulationMode,
    k_policy: str,
    k_value: float | None,
    k_config: Path | None,
    b: float,
    q: float,
    bin_width: float,
) -> SweepRow:
    params = build_elo_params(
        k_policy=k_policy,
        b=b,
        q=q,
        k_value=k_value,
        config_path=k_config,
    )

    entrant_initialiser = _select_entrant_initialiser(
        entrant_policy="expt2_scaled",
        baseline=params.b,
        expt2_alpha=alpha,
    )

    observer = Expt3ProbabilityObserver(q=params.q)
    simulate(
        history=history,
        params=params,
        entrant_initialiser=entrant_initialiser,
        mode=mode,
        observer=observer,
    )

    bout_rows = observer.rows
    cal_rows = build_calibration_rows_from_bouts(bout_rows, bin_width=bin_width)
    raw = summarise_brier_raw(bout_rows)
    binned = summarise_brier_binned(cal_rows)

    return SweepRow(
        alpha=alpha,
        raw_brier=float(raw["brier"]),
        raw_baseline_brier=float(raw["baseline_brier"]),
        raw_brier_skill=float(raw["brier_skill"]),
        binned_brier=float(binned["brier"]),
        binned_baseline_brier=float(binned["baseline_brier"]),
        binned_brier_skill=float(binned["brier_skill"]),
        brier_reliability=float(binned["brier_reliability"]),
        brier_resolution=float(binned["brier_resolution"]),
        brier_uncertainty=float(binned["brier_uncertainty"]),
        calibration_mae_binned=float(binned["mae"]),
        calibration_rmse_binned=float(binned["rmse"]),
        raw_bout_observations=int(raw["n_obs"]),
        base_rate=float(raw["base_rate"]),
    )


def _write_csv(rows: list[SweepRow], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "alpha",
                "raw_brier",
                "raw_baseline_brier",
                "raw_brier_skill",
                "binned_brier",
                "binned_baseline_brier",
                "binned_brier_skill",
                "brier_reliability",
                "brier_resolution",
                "brier_uncertainty",
                "calibration_mae_binned",
                "calibration_rmse_binned",
                "raw_bout_observations",
                "base_rate",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.alpha,
                    row.raw_brier,
                    row.raw_baseline_brier,
                    row.raw_brier_skill,
                    row.binned_brier,
                    row.binned_baseline_brier,
                    row.binned_brier_skill,
                    row.brier_reliability,
                    row.brier_resolution,
                    row.brier_uncertainty,
                    row.calibration_mae_binned,
                    row.calibration_rmse_binned,
                    row.raw_bout_observations,
                    row.base_rate,
                ]
            )
    return output_path


def _objective_value(row: SweepRow, objective: str) -> float:
    return float(getattr(row, objective))


def _is_better(new: float, old: float, objective: str) -> bool:
    if objective in MINIMISE_OBJECTIVES:
        return new < old
    return new > old


def _arrow(previous: float | None, current: float, objective: str) -> str:
    if previous is None:
        return "•"
    if current == previous:
        return "→"
    if objective in MINIMISE_OBJECTIVES:
        return "↓" if current < previous else "↑"
    return "↑" if current > previous else "↓"


def _best_row(rows: list[SweepRow], objective: str) -> SweepRow:
    if objective in MINIMISE_OBJECTIVES:
        return min(rows, key=lambda r: _objective_value(r, objective))
    return max(rows, key=lambda r: _objective_value(r, objective))


def _local_minima_indices(rows: list[SweepRow], objective: str) -> list[int]:
    values = [_objective_value(r, objective) for r in rows]
    is_minimise = objective in MINIMISE_OBJECTIVES
    out: list[int] = []

    for i, v in enumerate(values):
        left_ok = True
        right_ok = True

        if i > 0:
            left_ok = v < values[i - 1] if is_minimise else v > values[i - 1]
        if i < len(values) - 1:
            right_ok = v < values[i + 1] if is_minimise else v > values[i + 1]

        if left_ok and right_ok:
            out.append(i)

    return out


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _validate_k_policy_args(args, parser)
    _validate_objective(args, parser)

    mode = SimulationMode.CLOSED if args.closed else SimulationMode.OPEN
    alphas = _alpha_values(args.alpha_start, args.alpha_end, args.alpha_step)

    raw_history = connect(args.start, args.end, use_zip=args.zip)

    with open(BIOS_PATH, "r", encoding="utf-8") as f:
        raw_bios = json.load(f)
    bios = {RikId(int(k)): v for k, v in raw_bios.items()}

    oracle = make_oracle(raw_history, bios)
    history = oracle.history

    rows: list[SweepRow] = []
    prev_objective: float | None = None

    for alpha in alphas:
        row = _run_one_alpha(
            history=history,
            alpha=alpha,
            mode=mode,
            k_policy=args.k_policy,
            k_value=args.k_value,
            k_config=args.k_config,
            b=args.b,
            q=args.q,
            bin_width=args.bin_width,
        )
        rows.append(row)

        current_objective = _objective_value(row, args.objective)
        trend = _arrow(prev_objective, current_objective, args.objective)
        prev_objective = current_objective

        print(
            f"alpha={row.alpha:0.12f} "
            f"raw_brier={row.raw_brier:.12f} "
            f"mae={row.calibration_mae_binned:.12f} "
            f"{args.objective}={current_objective:.12f} {trend}"
        )

    written = _write_csv(rows, args.output)
    best = _best_row(rows, args.objective)
    local_idxs = _local_minima_indices(rows, args.objective)

    print()
    print(f"Wrote {len(rows)} rows to: {written}")
    print(f"Objective: {args.objective}")
    print("Best row:")
    print(f"  alpha: {best.alpha:0.12f}")
    print(f"  raw_brier: {best.raw_brier:.12f}")
    print(f"  raw_brier_skill: {best.raw_brier_skill:.12f}")
    print(f"  calibration_mae_binned: {best.calibration_mae_binned:.12f}")
    print(f"  brier_reliability: {best.brier_reliability:.12f}")

    print("Discrete local optima on sampled grid:")
    if not local_idxs:
        print("  none")
    else:
        for idx in local_idxs:
            row = rows[idx]
            value = _objective_value(row, args.objective)
            print(
                f"  alpha={row.alpha:0.12f} "
                f"{args.objective}={value:.12f} "
                f"raw_brier={row.raw_brier:.12f} "
                f"mae={row.calibration_mae_binned:.12f}"
            )


if __name__ == "__main__":
    from time import time
    print( 'best alpha = 0.54873' )
    t= time()
    main()
    print( time()-t)

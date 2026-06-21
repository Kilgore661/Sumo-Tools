from __future__ import annotations

import argparse
import csv
import datetime
from dataclasses import dataclass
from pathlib import Path

from src.infra.config import EPOCH
from src.infra.connect import connect
from src.analysis.equelo.config_main import INITIAL_ELO, CONSTANT_K
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.initialisation import constant_initialiser
from src.analysis.equelo.expt1.params import DEFAULT_K_CONFIG_PATH, build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode, SimulationObserver, expect, simulate
from src.analysis.probability.classes import CalibrationBins, CalibrationRow


@dataclass(frozen=True)
class BoutForecast:
    predicted: float
    outcome: int


@dataclass(frozen=True)
class SweepRow:
    q: float
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


class Expt3SweepObserver(SimulationObserver):
    def __init__(self, q: float) -> None:
        self.q = float(q)
        self._rows: list[BoutForecast] = []

    @property
    def rows(self) -> list[BoutForecast]:
        return self._rows

    def on_basho_start(self, date, ratings, banzuke) -> None:
        return None

    def on_entry(self, date, rikid, rating, ratings) -> None:
        return None

    def on_retirement(
        self,
        date,
        rikid,
        rating,
        n,
        delta,
        delta_per_rikishi,
        abs_delta_per_rikishi,
        closed,
    ) -> None:
        return None

    def on_day_start(self, date, day, ratings) -> None:
        return None

    def on_bout(
        self,
        date,
        day,
        bout,
        delta,
        r1_before,
        r2_before,
        r1_after,
        r2_after,
        rating_mass_before,
        rating_mass_after,
    ) -> None:
        del date, day, delta, r1_after, r2_after, rating_mass_before, rating_mass_after
        p = expect(r1_before, r2_before, self.q)
        y = 1 if bout.outcome1.name == "W" else 0
        self._rows.append(BoutForecast(predicted=float(p), outcome=int(y)))

    def on_ignored_bout(self, date, day, bout) -> None:
        return None

    def on_day_end(self, date, day, ratings) -> None:
        return None

    def on_basho_end(self, date, ratings, banzuke) -> None:
        return None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sweep q for Expt3, loading history only once."
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--closed", action="store_true")
    parser.add_argument("--k-policy", choices=("constant", "divisional"), default="constant")
    parser.add_argument("--k-value", type=float, default=None)
    parser.add_argument("--k-config", type=Path, default=None)
    parser.add_argument("--b", type=float, default=INITIAL_ELO)
    parser.add_argument("--bin-width", type=float, default=0.01)

    parser.add_argument("--q-start", type=float, required=True)
    parser.add_argument("--q-end", type=float, required=True)
    parser.add_argument("--q-step", type=float, required=True)

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("files/output/Equelo/expt3_q_sweep.csv"),
        help="Output CSV path.",
    )
    return parser


def _validate_k_policy_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.k_policy == "constant" and args.k_config is not None:
        parser.error("--k-config is only valid with --k-policy divisional")
    if args.k_policy == "divisional" and args.k_value is not None:
        parser.error("--k-value is only valid with --k-policy constant")


def _q_values(start: float, end: float, step: float) -> list[float]:
    if step <= 0:
        raise ValueError(f"q-step must be positive, got {step}")
    if end < start:
        raise ValueError(f"q-end must be >= q-start, got {start}..{end}")

    values: list[float] = []
    q = start
    eps = step / 1_000_000
    while q <= end + eps:
        values.append(round(q, 10))
        q += step
    return values


def build_calibration_rows_from_bouts(
    bouts: list[BoutForecast],
    bin_width: float,
) -> list[CalibrationRow]:
    bins = CalibrationBins(bin_width=bin_width)
    for row in bouts:
        bins.record(predicted_probability=row.predicted, outcome=row.outcome)
    return bins.to_rows()


def summarise_brier_raw(bouts: list[BoutForecast]) -> dict[str, float | int]:
    if not bouts:
        raise ValueError("Cannot summarise empty bout forecasts")

    n = len(bouts)
    total_wins = sum(row.outcome for row in bouts)
    base_rate = total_wins / n

    brier = sum((row.predicted - row.outcome) ** 2 for row in bouts) / n
    baseline_brier = sum((base_rate - row.outcome) ** 2 for row in bouts) / n
    brier_skill = 0.0 if baseline_brier == 0.0 else 1.0 - (brier / baseline_brier)

    return {
        "n_obs": n,
        "base_rate": base_rate,
        "brier": brier,
        "baseline_brier": baseline_brier,
        "brier_skill": brier_skill,
    }


def summarise_brier_binned(rows: list[CalibrationRow]) -> dict[str, float | int]:
    if not rows:
        raise ValueError("Cannot summarise empty calibration rows")

    total_obs = sum(row.n_obs for row in rows)
    total_wins = sum(row.n_wins_c1 for row in rows)
    base_rate = total_wins / total_obs

    reliability = sum(row.n_obs * row.sq_error for row in rows) / total_obs
    resolution = sum(
        row.n_obs * (row.observed_win_rate - base_rate) ** 2 for row in rows
    ) / total_obs
    uncertainty = base_rate * (1.0 - base_rate)
    brier = reliability - resolution + uncertainty
    baseline_brier = uncertainty
    brier_skill = 0.0 if baseline_brier == 0.0 else 1.0 - (brier / baseline_brier)

    mae = sum(row.n_obs * row.abs_error for row in rows) / total_obs
    rmse = (sum(row.n_obs * row.sq_error for row in rows) / total_obs) ** 0.5

    return {
        "n_rows": len(rows),
        "total_obs": total_obs,
        "base_rate": base_rate,
        "mae": mae,
        "rmse": rmse,
        "brier": brier,
        "baseline_brier": baseline_brier,
        "brier_skill": brier_skill,
        "brier_reliability": reliability,
        "brier_resolution": resolution,
        "brier_uncertainty": uncertainty,
    }


def _run_one_q(
    *,
    history,
    q: float,
    mode: SimulationMode,
    k_policy: str,
    k_value: float | None,
    k_config: Path | None,
    b: float,
    bin_width: float,
) -> SweepRow:
    params = build_elo_params(
        k_policy=k_policy,
        b=b,
        q=q,
        k_value=k_value,
        config_path=k_config,
    )

    observer = Expt3SweepObserver(q=params.q)
    simulate(
        history=history,
        params=params,
        entrant_initialiser=constant_initialiser(params.b),
        mode=mode,
        observer=observer,
    )

    bout_rows = observer.rows
    cal_rows = build_calibration_rows_from_bouts(bout_rows, bin_width=bin_width)
    raw = summarise_brier_raw(bout_rows)
    binned = summarise_brier_binned(cal_rows)

    return SweepRow(
        q=q,
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
                "q",
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
                    row.q,
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


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _validate_k_policy_args(args, parser)

    mode = SimulationMode.CLOSED if args.closed else SimulationMode.OPEN
    q_values = _q_values(args.q_start, args.q_end, args.q_step)

    raw_history = connect(args.start, args.end, use_zip=args.zip)

    oracle = make_oracle(raw_history)
    history = oracle.history

    rows: list[SweepRow] = []
    for q in q_values:
        row = _run_one_q(
            history=history,
            q=q,
            mode=mode,
            k_policy=args.k_policy,
            k_value=args.k_value,
            k_config=args.k_config,
            b=args.b,
            bin_width=args.bin_width,
        )
        rows.append(row)
        print(
            f"q={q:g} raw_brier={row.raw_brier:.6f} "
            f"raw_skill={row.raw_brier_skill:.6f} "
            f"reliability={row.brier_reliability:.6f} "
            f"resolution={row.brier_resolution:.6f}"
        )

    written = _write_csv(rows, args.output)
    best = min(rows, key=lambda r: r.raw_brier)

    print()
    print(f"Wrote {len(rows)} rows to: {written}")
    print("Best q by raw Brier:")
    print(f"  q: {best.q:g}")
    print(f"  raw_brier: {best.raw_brier:.6f}")
    print(f"  raw_brier_skill: {best.raw_brier_skill:.6f}")
    print(f"  brier_reliability: {best.brier_reliability:.6f}")
    print(f"  brier_resolution: {best.brier_resolution:.6f}")


if __name__ == "__main__":
    main()

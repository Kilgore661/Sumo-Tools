from __future__ import annotations

import argparse
import csv
import datetime
import json
import math
from dataclasses import dataclass
from pathlib import Path

from src.infra.config import EPOCH
from src.infra.connect import connect
from src.sumo_core.BasicPrimitives import RikId, Day
from src.sumo_core.History import Date
from src.sumo_core.Summary import BoutResult

from src.analysis.equelo.config_main import BIOS_PATH, INITIAL_ELO, INITIAL_Q, CONSTANT_K
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.initialisation import constant_initialiser
from src.analysis.equelo.expt1.params import DEFAULT_K_CONFIG_PATH, build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode, SimulationObserver, expect, simulate
from src.analysis.probability.builder import write_calibration_csv
from src.analysis.probability.classes import CalibrationBins, CalibrationRow


@dataclass(frozen=True)
class BoutForecast:
    date: str
    day: int
    rikishi1: int
    rikishi2: int
    r1_before: float
    r2_before: float
    predicted: float
    outcome: int


class Expt1ProbabilityObserver(SimulationObserver):
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
        date: Date,
        day: Day,
        bout: BoutResult,
        delta: float,
        r1_before: float,
        r2_before: float,
        r1_after: float,
        r2_after: float,
        rating_mass_before: float,
        rating_mass_after: float,
    ) -> None:
        del delta, r1_after, r2_after, rating_mass_before, rating_mass_after
        p = expect(r1_before, r2_before, self.q)
        y = 1 if bout.outcome1.name == "W" else 0
        self._rows.append(
            BoutForecast(
                date=str(date),
                day=int(day),
                rikishi1=int(bout.rikishi1),
                rikishi2=int(bout.rikishi2),
                r1_before=float(r1_before),
                r2_before=float(r2_before),
                predicted=float(p),
                outcome=int(y),
            )
        )

    def on_ignored_bout(self, date, day, bout) -> None:
        return None

    def on_day_end(self, date, day, ratings) -> None:
        return None

    def on_basho_end(self, date, ratings, banzuke) -> None:
        return None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate Expt1 wrestler-level pre-bout probabilities with Brier and calibration summaries."
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--closed", action="store_true")
    parser.add_argument("--k-policy", choices=("constant", "divisional"), default="constant")
    parser.add_argument("--k-value", type=float, default=None)
    parser.add_argument("--k-config", type=Path, default=None)
    parser.add_argument("--b", type=float, default=INITIAL_ELO)
    parser.add_argument("--q", type=float, default=INITIAL_Q)
    parser.add_argument("--bin-width", type=float, default=0.01)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Calibration CSV output path. Defaults to files/output/Equelo/expt1_calibration.csv",
    )
    parser.add_argument(
        "--bout-output",
        type=Path,
        default=None,
        help="Optional CSV output path for raw bout-level forecasts.",
    )
    return parser


def _validate_k_policy_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.k_policy == "constant" and args.k_config is not None:
        parser.error("--k-config is only valid with --k-policy divisional")
    if args.k_policy == "divisional" and args.k_value is not None:
        parser.error("--k-value is only valid with --k-policy constant")


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
    rmse = math.sqrt(sum(row.n_obs * row.sq_error for row in rows) / total_obs)

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


def _default_output_path() -> Path:
    return Path("files/output/Equelo/expt1_calibration.csv")


def write_bout_forecasts_csv(rows: list[BoutForecast], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "date",
                "day",
                "rikishi1",
                "rikishi2",
                "r1_before",
                "r2_before",
                "predicted",
                "outcome",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.date,
                    row.day,
                    row.rikishi1,
                    row.rikishi2,
                    row.r1_before,
                    row.r2_before,
                    row.predicted,
                    row.outcome,
                ]
            )
    return output_path


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _validate_k_policy_args(args, parser)

    raw_history = connect(args.start, args.end, use_zip=args.zip)

    with open(BIOS_PATH, "r", encoding="utf-8") as f:
        raw_bios = json.load(f)
    bios = {RikId(int(k)): v for k, v in raw_bios.items()}

    oracle = make_oracle(raw_history, bios)
    params = build_elo_params(
        k_policy=args.k_policy,
        b=args.b,
        q=args.q,
        k_value=args.k_value,
        config_path=args.k_config,
    )
    mode = SimulationMode.CLOSED if args.closed else SimulationMode.OPEN

    observer = Expt1ProbabilityObserver(q=params.q)
    simulate(
        history=oracle.history,
        params=params,
        entrant_initialiser=constant_initialiser(params.b),
        mode=mode,
        observer=observer,
    )

    bout_rows = observer.rows
    cal_rows = build_calibration_rows_from_bouts(bout_rows, bin_width=args.bin_width)
    raw_summary = summarise_brier_raw(bout_rows)
    binned_summary = summarise_brier_binned(cal_rows)

    output_path = args.output if args.output else _default_output_path()
    written = write_calibration_csv(cal_rows, output_path)

    print(f"Evaluation years: {args.start}-{args.end}")
    print(f"Mode: {mode.value}")
    print(f"K policy: {args.k_policy}")
    if args.k_policy == "constant":
        print(f"K value: {CONSTANT_K if args.k_value is None else args.k_value}")
    else:
        print(f"K config: {DEFAULT_K_CONFIG_PATH if args.k_config is None else args.k_config}")
    print(f"Baseline b: {args.b}")
    print(f"q: {args.q}")
    print(f"Raw bout observations: {raw_summary['n_obs']}")
    print(f"Base rate: {raw_summary['base_rate']:.6f}")
    print(f"Raw Brier score: {raw_summary['brier']:.6f}")
    print(f"Raw baseline Brier: {raw_summary['baseline_brier']:.6f}")
    print(f"Raw Brier skill score: {raw_summary['brier_skill']:.6f}")
    print(f"Binned rows written: {binned_summary['n_rows']}")
    print(f"Calibration MAE (binned): {binned_summary['mae']:.6f}")
    print(f"Calibration RMSE (binned): {binned_summary['rmse']:.6f}")
    print(f"Binned Brier: {binned_summary['brier']:.6f}")
    print(f"Binned baseline Brier: {binned_summary['baseline_brier']:.6f}")
    print(f"Binned Brier skill score: {binned_summary['brier_skill']:.6f}")
    print(f"Brier reliability: {binned_summary['brier_reliability']:.6f}")
    print(f"Brier resolution: {binned_summary['brier_resolution']:.6f}")
    print(f"Brier uncertainty: {binned_summary['brier_uncertainty']:.6f}")
    print(f"Calibration CSV: {written}")

    if args.bout_output is not None:
        bout_written = write_bout_forecasts_csv(bout_rows, args.bout_output)
        print(f"Bout forecasts CSV: {bout_written}")


if __name__ == "__main__":
    main()

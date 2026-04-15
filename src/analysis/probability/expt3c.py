"""Expt3c: probability evaluation for Expt3 with selectable entrant initialisation.

This module is the maintained Expt3 entry point.

It reuses the Expt1 simulator to generate pre-bout Elo-style probabilities and
then evaluates those probabilities using calibration summaries and Brier-score
metrics.

Entrant initialisation is configurable at the experiment boundary:

* ``constant`` is the default and preferred Expt3 policy
* ``expt2_example`` demonstrates one non-constant policy backed by Expt2 output

The non-constant path is included to preserve and demonstrate the simulator's
entrant-initialisation boundary. It is an example mechanism rather than the
recommended default for Expt3.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import math
from pathlib import Path

from src.infra.config import EPOCH
from src.infra.connect import connect
from src.sumo_core.BasicPrimitives import RikId, Day
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date
from src.sumo_core.Summary import BoutResult

from src.analysis.equelo.config_main import BIOS_PATH, INITIAL_ELO, INITIAL_Q, CONSTANT_K
from src.analysis.equelo.config_main import OUTPUT_ROOT as EXPT2_OUTPUT_ROOT
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.initialisation import constant_initialiser
from src.analysis.equelo.expt1.params import DEFAULT_K_CONFIG_PATH, build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode, SimulationObserver, expect, simulate
from src.analysis.probability.builder import write_calibration_csv, load_ratings_csv
from src.analysis.probability.classes import CalibrationBins, CalibrationRow

from .expt3_report import build_bottom_line, render_bottom_line
from .expt3_types import BoutForecast, DeltaCalibrationRow


class Expt3ProbabilityObserver(SimulationObserver):
    """Collect bout-level forecasts emitted during one Expt3 simulation run.

    The observer ignores entry, retirement, and day/basho lifecycle events.
    Its only purpose is to capture the pre-bout ratings needed to compute
    implied win probabilities and the realised outcomes needed for calibration
    analysis.
    """

    def __init__(self, q: float) -> None:
        """Store the link-scale parameter used to convert rating deltas to probabilities."""
        self.q = float(q)
        self._rows: list[BoutForecast] = []

    @property
    def rows(self) -> list[BoutForecast]:
        """Return the collected bout-level forecast rows."""
        return self._rows

    def on_basho_start(self, date, ratings, banzuke) -> None:
        """Ignore basho-start notifications."""
        return None

    def on_entry(self, date, rikid, rating, ratings) -> None:
        """Ignore entrant notifications."""
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
        """Ignore retirement notifications."""
        return None

    def on_day_start(self, date, day, ratings) -> None:
        """Ignore day-start notifications."""
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
        """Record one scored bout as a pre-bout probability forecast."""
        del delta, r1_after, r2_after, rating_mass_before, rating_mass_after
        p = expect(r1_before, r2_before, self.q)
        y = 1 if bout.outcome1.name == "W" else 0
        dr = float(r1_before - r2_before)
        self._rows.append(
            BoutForecast(
                date=str(date),
                day=int(day),
                rikishi1=int(bout.rikishi1),
                rikishi2=int(bout.rikishi2),
                r1_before=float(r1_before),
                r2_before=float(r2_before),
                delta=dr,
                predicted=float(p),
                outcome=int(y),
            )
        )

    def on_ignored_bout(self, date, day, bout) -> None:
        """Ignore non-rating bouts such as fusen and blank."""
        return None

    def on_day_end(self, date, day, ratings) -> None:
        """Ignore day-end notifications."""
        return None

    def on_basho_end(self, date, ratings, banzuke) -> None:
        """Ignore basho-end notifications."""
        return None


class DeltaBins:
    """Fixed-width bins over rating delta for delta-based calibration summaries."""

    def __init__(self, bin_width: float) -> None:
        """Initialise empty delta bins with a positive fixed width."""
        if bin_width <= 0:
            raise ValueError(f"delta bin_width must be positive, got {bin_width}")
        self.bin_width = float(bin_width)
        self._data: dict[int, dict[str, float | int]] = {}

    def _bin_index(self, delta: float) -> int:
        """Map one delta value to its integer bin index."""
        return math.floor(delta / self.bin_width)

    def _bin_bounds(self, index: int) -> tuple[float, float]:
        """Return the lower and upper bounds of one delta bin."""
        lo = index * self.bin_width
        hi = lo + self.bin_width
        return lo, hi

    def record(self, delta: float, predicted: float, outcome: int) -> None:
        """Add one observed bout to the appropriate delta bin."""
        index = self._bin_index(delta)
        if index not in self._data:
            self._data[index] = {
                "n_obs": 0,
                "n_wins_r1": 0,
                "sum_delta": 0.0,
                "sum_predicted": 0.0,
            }

        bucket = self._data[index]
        bucket["n_obs"] += 1
        bucket["n_wins_r1"] += int(outcome)
        bucket["sum_delta"] += float(delta)
        bucket["sum_predicted"] += float(predicted)

    def to_rows(self) -> list[DeltaCalibrationRow]:
        """Convert accumulated bins to serialisable calibration rows."""
        rows: list[DeltaCalibrationRow] = []

        for index in sorted(self._data):
            bucket = self._data[index]
            n_obs = int(bucket["n_obs"])
            n_wins = int(bucket["n_wins_r1"])
            mean_delta = float(bucket["sum_delta"]) / n_obs
            mean_predicted = float(bucket["sum_predicted"]) / n_obs
            observed = n_wins / n_obs
            signed_error = observed - mean_predicted
            lo, hi = self._bin_bounds(index)

            rows.append(
                DeltaCalibrationRow(
                    delta_bin_lo=lo,
                    delta_bin_hi=hi,
                    n_obs=n_obs,
                    n_wins_r1=n_wins,
                    n_losses_r1=n_obs - n_wins,
                    mean_delta=mean_delta,
                    mean_predicted=mean_predicted,
                    observed_win_rate=observed,
                    signed_error=signed_error,
                    abs_error=abs(signed_error),
                    sq_error=signed_error ** 2,
                )
            )

        return rows


def _build_parser() -> argparse.ArgumentParser:
    """Build the Expt3c command-line parser."""
    parser = argparse.ArgumentParser(
        description="Evaluate Expt3 wrestler-level pre-bout probabilities with Brier and calibration summaries."
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument(
        "--open",
        action="store_true",
        help="Run in open mode. Default is closed mode.",
    )
    parser.add_argument("--k-policy", choices=("constant", "divisional"), default="divisional")
    parser.add_argument("--k-value", type=float, default=None)
    parser.add_argument("--k-config", type=Path, default=None)
    parser.add_argument("--b", type=float, default=INITIAL_ELO)
    parser.add_argument("--q", type=float, default=INITIAL_Q)
    parser.add_argument("--bin-width", type=float, default=0.02)
    parser.add_argument(
        "--entrant-policy",
        choices=("constant", "expt2_example"),
        default="constant",
        help=(
            "Entrant initialisation policy. "
            "'constant' is the default Expt3 policy. "
            "'expt2_example' demonstrates one non-constant alternative backed by Expt2 output."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Probability-binned calibration CSV output path. Defaults to files/output/Equelo/expt3_calibration.csv",
    )
    parser.add_argument(
        "--bout-output",
        type=Path,
        default=None,
        help="Optional CSV output path for raw bout-level forecasts.",
    )
    parser.add_argument(
        "--delta-bin-width",
        type=float,
        default=None,
        help="Optional delta bin width. If provided, also write a delta-binned calibration CSV.",
    )
    parser.add_argument(
        "--delta-output",
        type=Path,
        default=None,
        help="Optional CSV output path for delta-binned calibration. Defaults to files/output/Equelo/expt3_delta_calibration.csv when --delta-bin-width is set.",
    )
    parser.add_argument(
        "--support-se-threshold",
        type=float,
        default=0.02,
        help="Support adequacy threshold on standard error of observed win rate.",
    )
    parser.add_argument(
        "--error-threshold",
        type=float,
        default=0.025,
        help="Absolute-error threshold used to identify the central low-error region.",
    )
    return parser


def _validate_k_policy_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    """Enforce the mutually exclusive K-policy argument surface."""
    if args.k_policy == "constant" and args.k_config is not None:
        parser.error("--k-config is only valid with --k-policy divisional")
    if args.k_policy == "divisional" and args.k_value is not None:
        parser.error("--k-value is only valid with --k-policy constant")


def build_calibration_rows_from_bouts(
    bouts: list[BoutForecast],
    bin_width: float,
) -> list[CalibrationRow]:
    """Aggregate bout-level forecasts into fixed-width probability calibration rows."""
    bins = CalibrationBins(bin_width=bin_width)
    for row in bouts:
        bins.record(predicted_probability=row.predicted, outcome=row.outcome)
    return bins.to_rows()


def build_delta_calibration_rows_from_bouts(
    bouts: list[BoutForecast],
    bin_width: float,
) -> list[DeltaCalibrationRow]:
    """Aggregate bout-level forecasts into fixed-width delta calibration rows."""
    bins = DeltaBins(bin_width=bin_width)
    for row in bouts:
        bins.record(delta=row.delta, predicted=row.predicted, outcome=row.outcome)
    return bins.to_rows()


def summarise_brier_raw(bouts: list[BoutForecast]) -> dict[str, float | int]:
    """Compute raw, unbinned Brier-score summary statistics from bout forecasts."""
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
    """Compute binned calibration and Brier-decomposition statistics."""
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


def summarise_delta_rows(rows: list[DeltaCalibrationRow]) -> dict[str, float | int]:
    """Compute summary statistics over delta-binned calibration rows."""
    if not rows:
        raise ValueError("Cannot summarise empty delta calibration rows")

    total_obs = sum(row.n_obs for row in rows)
    mae = sum(row.n_obs * row.abs_error for row in rows) / total_obs
    rmse = math.sqrt(sum(row.n_obs * row.sq_error for row in rows) / total_obs)
    max_abs_error = max(row.abs_error for row in rows)

    return {
        "n_rows": len(rows),
        "total_obs": total_obs,
        "mae": mae,
        "rmse": rmse,
        "max_abs_error": max_abs_error,
    }


def _quantile_from_sorted(sorted_values: list[float], p: float) -> float:
    """Return an interpolated quantile from a pre-sorted list."""
    if not sorted_values:
        raise ValueError("Cannot compute quantile of empty list")
    if p <= 0:
        return sorted_values[0]
    if p >= 1:
        return sorted_values[-1]

    n = len(sorted_values)
    pos = (n - 1) * p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return sorted_values[lo]
    frac = pos - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def summarise_abs_delta(bouts: list[BoutForecast]) -> dict[str, float]:
    """Summarise the distribution of absolute pre-bout rating deltas."""
    if not bouts:
        raise ValueError("Cannot summarise empty bout forecasts")

    abs_deltas = sorted(abs(row.delta) for row in bouts)
    n = len(abs_deltas)
    mean_abs_delta = sum(abs_deltas) / n

    return {
        "mean_abs_delta": mean_abs_delta,
        "median_abs_delta": _quantile_from_sorted(abs_deltas, 0.50),
        "p75_abs_delta": _quantile_from_sorted(abs_deltas, 0.75),
        "p90_abs_delta": _quantile_from_sorted(abs_deltas, 0.90),
        "p95_abs_delta": _quantile_from_sorted(abs_deltas, 0.95),
        "p99_abs_delta": _quantile_from_sorted(abs_deltas, 0.99),
    }


def _default_output_path() -> Path:
    """Return the default probability-calibration CSV path."""
    return Path("files/output/Equelo/expt3_calibration.csv")


def _default_delta_output_path() -> Path:
    """Return the default delta-calibration CSV path."""
    return Path("files/output/Equelo/expt3_delta_calibration.csv")


def write_bout_forecasts_csv(rows: list[BoutForecast], output_path: Path) -> Path:
    """Write raw bout-level probability forecasts to CSV."""
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
                "delta",
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
                    row.delta,
                    row.predicted,
                    row.outcome,
                ]
            )
    return output_path


def write_delta_calibration_csv(rows: list[DeltaCalibrationRow], output_path: Path) -> Path:
    """Write delta-binned calibration rows to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "delta_bin_lo",
                "delta_bin_hi",
                "n_obs",
                "n_wins_r1",
                "n_losses_r1",
                "mean_delta",
                "mean_predicted",
                "observed_win_rate",
                "signed_error",
                "abs_error",
                "sq_error",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.delta_bin_lo,
                    row.delta_bin_hi,
                    row.n_obs,
                    row.n_wins_r1,
                    row.n_losses_r1,
                    row.mean_delta,
                    row.mean_predicted,
                    row.observed_win_rate,
                    row.signed_error,
                    row.abs_error,
                    row.sq_error,
                ]
            )
    return output_path


def variable_initialiser(chii_ratings: dict[Chii, float]):
    """Build a rank-based entrant initialiser from a Chii→rating mapping.

    This is used only for the ``expt2_example`` entrant policy. It preserves an
    example of non-constant entrant initialisation at the experiment boundary.
    """
    def initialise(chii: Chii) -> float:
        """Return the supplied rating for the entrant's basho-start Chii."""
        return float(chii_ratings[chii])

    return initialise


def _select_entrant_initialiser(
    entrant_policy: str,
    baseline: float,
):
    """Resolve the entrant initialiser from the selected entrant policy."""
    if entrant_policy == "constant":
        return constant_initialiser(baseline)

    if entrant_policy == "expt2_example":
        # Example only: this preserves one concrete non-constant entrant rule
        # using Expt2-derived Chii ratings. It is not the default or preferred
        # Expt3 configuration.
        return variable_initialiser(
            load_ratings_csv(EXPT2_OUTPUT_ROOT / "expt2_combined_final.csv")
        )

    raise ValueError(f"Unknown entrant_policy: {entrant_policy}")

import statistics
from collections import Counter


def summarise_predicted_distribution(
    bouts: list[BoutForecast],
    hist_bin_width: float = 0.05,
) -> dict[str, object]:
    """Summarise the distribution of predicted probabilities."""
    if not bouts:
        raise ValueError("Cannot summarise empty bout forecasts")
    if not (0.0 < hist_bin_width <= 1.0):
        raise ValueError(f"hist_bin_width must lie in (0, 1], got {hist_bin_width}")

    ps = sorted(float(row.predicted) for row in bouts)
    n = len(ps)

    mean_p = statistics.fmean(ps)
    stdev_p = statistics.pstdev(ps)  # population stdev

    # Quantiles
    summary = {
        "n_obs": n,
        "mean_predicted": mean_p,
        "stdev_predicted": stdev_p,
        "min_predicted": ps[0],
        "p01_predicted": _quantile_from_sorted(ps, 0.01),
        "p05_predicted": _quantile_from_sorted(ps, 0.05),
        "p10_predicted": _quantile_from_sorted(ps, 0.10),
        "p25_predicted": _quantile_from_sorted(ps, 0.25),
        "median_predicted": _quantile_from_sorted(ps, 0.50),
        "p75_predicted": _quantile_from_sorted(ps, 0.75),
        "p90_predicted": _quantile_from_sorted(ps, 0.90),
        "p95_predicted": _quantile_from_sorted(ps, 0.95),
        "p99_predicted": _quantile_from_sorted(ps, 0.99),
        "max_predicted": ps[-1],
    }

    # Fixed-width histogram on [0, 1]
    n_bins = math.ceil(1.0 / hist_bin_width)
    counts = Counter()

    for p in ps:
        idx = min(int(p / hist_bin_width), n_bins - 1)
        counts[idx] += 1

    histogram: list[dict[str, float | int]] = []
    for idx in range(n_bins):
        lo = idx * hist_bin_width
        hi = min(1.0, lo + hist_bin_width)
        count = counts.get(idx, 0)
        histogram.append(
            {
                "p_bin_lo": lo,
                "p_bin_hi": hi,
                "n_obs": count,
                "share": count / n,
            }
        )

    summary["histogram"] = histogram
    return summary

def main() -> None:
    """Run Expt3c from the command line."""
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
    mode = SimulationMode.OPEN if args.open else SimulationMode.CLOSED
    entrant_initialiser = _select_entrant_initialiser(
        entrant_policy=args.entrant_policy,
        baseline=params.b,
    )

    observer = Expt3ProbabilityObserver(q=params.q)
    simulate(
        history=oracle.history,
        params=params,
        entrant_initialiser=entrant_initialiser,
        mode=mode,
        observer=observer,
    )

    bout_rows = observer.rows
    cal_rows = build_calibration_rows_from_bouts(bout_rows, bin_width=args.bin_width)
    raw_summary = summarise_brier_raw(bout_rows)
    binned_summary = summarise_brier_binned(cal_rows)
    abs_delta_summary = summarise_abs_delta(bout_rows)

    output_path = args.output if args.output else _default_output_path()
    written = write_calibration_csv(cal_rows, output_path)

    predicted_dist = summarise_predicted_distribution(bout_rows, hist_bin_width=0.05)

    cal_rows = build_calibration_rows_from_bouts(bout_rows, bin_width=args.bin_width)
    raw_summary = summarise_brier_raw(bout_rows)
    binned_summary = summarise_brier_binned(cal_rows)
    abs_delta_summary = summarise_abs_delta(bout_rows)

    print(f"Predicted p mean: {predicted_dist['mean_predicted']:.6f}")
    print(f"Predicted p stdev: {predicted_dist['stdev_predicted']:.6f}")
    print(f"Predicted p min: {predicted_dist['min_predicted']:.6f}")
    print(f"Predicted p p01: {predicted_dist['p01_predicted']:.6f}")
    print(f"Predicted p p05: {predicted_dist['p05_predicted']:.6f}")
    print(f"Predicted p p10: {predicted_dist['p10_predicted']:.6f}")
    print(f"Predicted p p25: {predicted_dist['p25_predicted']:.6f}")
    print(f"Predicted p median: {predicted_dist['median_predicted']:.6f}")
    print(f"Predicted p p75: {predicted_dist['p75_predicted']:.6f}")
    print(f"Predicted p p90: {predicted_dist['p90_predicted']:.6f}")
    print(f"Predicted p p95: {predicted_dist['p95_predicted']:.6f}")
    print(f"Predicted p p99: {predicted_dist['p99_predicted']:.6f}")
    print(f"Predicted p max: {predicted_dist['max_predicted']:.6f}")

    print("Predicted p histogram:")
    for bucket in predicted_dist["histogram"]:
        print(
            f"  {bucket['p_bin_lo']:.2f} <= p < {bucket['p_bin_hi']:.2f}: "
            f"n={bucket['n_obs']}, share={bucket['share']:.6f}"
        )

    print(f"Evaluation years: {args.start}-{args.end}")
    print(f"Mode: {mode.value}")
    print(f"Entrant policy: {args.entrant_policy}")
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
    print(f"Mean abs(delta): {abs_delta_summary['mean_abs_delta']:.6f}")
    print(f"Median abs(delta): {abs_delta_summary['median_abs_delta']:.6f}")
    print(f"P75 abs(delta): {abs_delta_summary['p75_abs_delta']:.6f}")
    print(f"P90 abs(delta): {abs_delta_summary['p90_abs_delta']:.6f}")
    print(f"P95 abs(delta): {abs_delta_summary['p95_abs_delta']:.6f}")
    print(f"P99 abs(delta): {abs_delta_summary['p99_abs_delta']:.6f}")
    print(f"Calibration CSV: {written}")

    bottom_line = build_bottom_line(
        cal_rows,
        q=args.q,
        support_se_threshold=args.support_se_threshold,
        error_threshold=args.error_threshold,
    )
    for line in render_bottom_line(
        bottom_line,
        support_se_threshold=args.support_se_threshold,
        error_threshold=args.error_threshold,
    ):
        print(line)

    if args.bout_output is not None:
        bout_written = write_bout_forecasts_csv(bout_rows, args.bout_output)
        print(f"Bout forecasts CSV: {bout_written}")

    if args.delta_bin_width is not None:
        delta_rows = build_delta_calibration_rows_from_bouts(
            bout_rows,
            bin_width=args.delta_bin_width,
        )
        delta_summary = summarise_delta_rows(delta_rows)
        delta_output = args.delta_output if args.delta_output else _default_delta_output_path()
        delta_written = write_delta_calibration_csv(delta_rows, delta_output)

        print(f"Delta bins written: {delta_summary['n_rows']}")
        print(f"Delta calibration MAE: {delta_summary['mae']:.6f}")
        print(f"Delta calibration RMSE: {delta_summary['rmse']:.6f}")
        print(f"Delta calibration max abs error: {delta_summary['max_abs_error']:.6f}")
        print(f"Delta calibration CSV: {delta_written}")


if __name__ == "__main__":
    main()

from dataclasses import dataclass
from math import floor, sqrt


Z95 = 1.959963984540054


@dataclass(frozen=True)
class CalibrationRow:
    p_bin_lo: float
    p_bin_hi: float
    n_obs: int
    n_wins_c1: int
    n_losses_c1: int
    mean_predicted: float
    observed_win_rate: float
    ci95_lower: float
    ci95_upper: float
    abs_error: float
    sq_error: float


@dataclass
class _BinAccumulator:
    n_obs: int = 0
    n_wins_c1: int = 0
    sum_predicted: float = 0.0

    def record(self, predicted_probability: float, outcome: int) -> None:
        self.n_obs += 1
        self.n_wins_c1 += int(outcome)
        self.sum_predicted += predicted_probability

    def observed_win_rate(self) -> float:
        return self.n_wins_c1 / self.n_obs

    def mean_predicted(self) -> float:
        return self.sum_predicted / self.n_obs

    def wilson95(self) -> tuple[float, float]:
        n = self.n_obs
        phat = self.n_wins_c1 / n
        z2 = Z95 * Z95
        denom = 1.0 + z2 / n
        centre = (phat + z2 / (2.0 * n)) / denom
        halfwidth = (
            Z95
            * sqrt((phat * (1.0 - phat) / n) + (z2 / (4.0 * n * n)))
            / denom
        )
        return centre - halfwidth, centre + halfwidth


class CalibrationBins:
    """Fixed-width probability bins for calibration rows."""

    def __init__(self, bin_width: float) -> None:
        if not (0.0 < bin_width <= 1.0):
            raise ValueError(f"bin_width must lie in (0, 1], got {bin_width}")
        self.bin_width = float(bin_width)
        self._data: dict[int, _BinAccumulator] = {}

    def _bin_index(self, predicted_probability: float) -> int:
        p = max(0.0, min(1.0, float(predicted_probability)))
        if p == 1.0:
            return int(round(1.0 / self.bin_width)) - 1
        return int(floor(p / self.bin_width))

    def _bin_bounds(self, index: int) -> tuple[float, float]:
        lo = index * self.bin_width
        hi = min(1.0, lo + self.bin_width)
        return lo, hi

    def record(self, predicted_probability: float, outcome: int) -> None:
        index = self._bin_index(predicted_probability)
        if index not in self._data:
            self._data[index] = _BinAccumulator()
        self._data[index].record(predicted_probability=predicted_probability, outcome=outcome)

    def to_rows(self) -> list[CalibrationRow]:
        rows: list[CalibrationRow] = []

        for index in sorted(self._data):
            stats = self._data[index]
            lo, hi = self._bin_bounds(index)
            observed = stats.observed_win_rate()
            predicted = stats.mean_predicted()
            ci_lower, ci_upper = stats.wilson95()

            rows.append(
                CalibrationRow(
                    p_bin_lo=lo,
                    p_bin_hi=hi,
                    n_obs=stats.n_obs,
                    n_wins_c1=stats.n_wins_c1,
                    n_losses_c1=stats.n_obs - stats.n_wins_c1,
                    mean_predicted=predicted,
                    observed_win_rate=observed,
                    ci95_lower=ci_lower,
                    ci95_upper=ci_upper,
                    abs_error=abs(observed - predicted),
                    sq_error=(observed - predicted) ** 2,
                )
            )

        return rows

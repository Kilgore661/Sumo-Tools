from __future__ import annotations

import csv
from pathlib import Path

from ....sumo_core.Chii import Chii

from .types import IterationDiagnosticsRow, ProbeCounts, ProbeSet
from ..config_main import OUTPUT_ROOT


PROBE_LABEL_WIDTH = 6
VALUE_WIDTH = 10
COUNT_WIDTH = 6
ITER_WIDTH = 4
DELTA_WIDTH = 12
SHIFT_WIDTH = 12
TIME_WIDTH = 9


def default_probe_set() -> ProbeSet:
    """Return the standard Expt2 diagnostic probe set."""
    return [
        Chii.from_str("Y1e"),
        Chii.from_str("O1e"),
        Chii.from_str("S1e"),
        Chii.from_str("K1e"),
        Chii.from_str("M1e"),
        Chii.from_str("J1e"),
        Chii.from_str("Ms1e"),
        Chii.from_str("Sd1e"),
        Chii.from_str("Jd1e"),
        Chii.from_str("Jk1e"),
    ]


def probe_values(
    mu: dict[Chii, float],
    counts: ProbeCounts,
    probes: ProbeSet,
) -> tuple[dict[Chii, float], dict[Chii, int]]:
    """Return probe ratings and counts in probe order.

    Presence of all probes is assumed by contract.
    """
    return (
        {chii: mu[chii] for chii in probes},
        {chii: counts[chii] for chii in probes},
    )


class IterationDiagnosticsWriter:
    """Fixed-width one-line iteration logger for Expt2.

    A plain-text log is written with aligned columns. A CSV companion file is
    also written for easier inspection.
    """

    def __init__(
        self,
        probes: ProbeSet,
        stem: str = "expt2_iterations",
        echo_to_console: bool = True,
    ) -> None:
        self.probes = list(probes)
        self.stem = stem
        self.echo_to_console = echo_to_console
        self._rows: list[IterationDiagnosticsRow] = []
        self._printed_header = False
        self._printed_counts = False
        self._cached_probe_counts: dict[Chii, int] | None = None

    def record(self, row: IterationDiagnosticsRow) -> None:
        self._rows.append(row)

        if self._cached_probe_counts is None:
            self._cached_probe_counts = dict(row.probe_counts)

        if self.echo_to_console:
            if not self._printed_header:
                print(self._header_line())
                self._printed_header = True
            if not self._printed_counts:
                print(self._counts_line())
                self._printed_counts = True
            print(self._format_row(row))

    def finalise(self) -> Path | None:
        if not self._rows:
            return None

        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        txt_path = OUTPUT_ROOT / f"{self.stem}.txt"
        csv_path = OUTPUT_ROOT / f"{self.stem}.csv"
        self._write_text_log(txt_path)
        self._write_csv(csv_path)
        return txt_path

    def _write_text_log(self, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._header_line() + "\n")
            for row in self._rows:
                f.write(self._format_row(row) + "\n")

    def _write_csv(self, path: Path) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            header = ["iter", "delta", "shift", "iter_seconds"]
            header.extend(str(chii) for chii in self.probes)
            header.extend(f"n_{chii}" for chii in self.probes)
            writer.writerow(header)
            for row in self._rows:
                values = [row.iteration, row.delta, row.shift, row.iter_seconds]
                values.extend(row.probe_values[chii] for chii in self.probes)
                values.extend(row.probe_counts[chii] for chii in self.probes)
                writer.writerow(values)

    def _header_line(self) -> str:
        left = (
            f"{'iter':>{ITER_WIDTH}} "
            f"{'delta':>{DELTA_WIDTH}} "
            f"{'shift':>{SHIFT_WIDTH}} "
            f"{'secs':>{TIME_WIDTH}}"
        )
        probe_value_cols = " ".join(f"{str(chii):>{VALUE_WIDTH}}" for chii in self.probes)
        return f"{left}  {probe_value_cols}"

    def _counts_line(self) -> str:
        assert self._cached_probe_counts is not None
        left = " " * (ITER_WIDTH + 1 + DELTA_WIDTH + 1 + SHIFT_WIDTH + 1 + TIME_WIDTH)
        count_cols = " ".join(
            f"{('n_' + str(chii) + '=' + str(self._cached_probe_counts[chii])):>{VALUE_WIDTH}}"
            for chii in self.probes
        )
        return f"{left}  {count_cols}"

    def _format_row(self, row: IterationDiagnosticsRow) -> str:
        left = (
            f"{row.iteration:>{ITER_WIDTH}d} "
            f"{row.delta:>{DELTA_WIDTH}.6f} "
            f"{row.shift:>{SHIFT_WIDTH}.6f} "
            f"{row.iter_seconds:>{TIME_WIDTH}.3f}"
        )
        probe_value_cols = " ".join(
            f"{row.probe_values[chii]:>{VALUE_WIDTH}.3f}" for chii in self.probes
        )
        return f"{left}  {probe_value_cols}"

    def summary_line(self) -> str | None:
        if not self._rows:
            return None
        total = sum(row.iter_seconds for row in self._rows)
        avg = total / len(self._rows)
        return f"[diagnostics] iterations={len(self._rows)} avg_secs={avg:.3f} total_secs={total:.3f}"

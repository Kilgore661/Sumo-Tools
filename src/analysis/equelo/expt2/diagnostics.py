from pdb import set_trace

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
    also written for easier inspection. Optional run metadata is written to the
    start of the text log and repeated in every CSV row.
    """

    def __init__(
        self,
        probes: ProbeSet,
        stem: str = "expt2_iterations",
        echo_to_console: bool = True,
        metadata: dict[str, str] | None = None,
        output_root: Path | None = None,
    ) -> None:
        self.probes = list(probes)
        self.stem = stem
        self.echo_to_console = echo_to_console
        self.metadata = {} if metadata is None else {str(k): str(v) for k, v in metadata.items()}
        self.output_root = OUTPUT_ROOT if output_root is None else output_root
        self._rows: list[IterationDiagnosticsRow] = []
        self._printed_header = False
        self._printed_counts = False
        self._printed_metadata = False
        self._cached_probe_counts: dict[Chii, int] | None = None

    def record(self, row: IterationDiagnosticsRow) -> None:
        self._rows.append(row)

        if self._cached_probe_counts is None:
            self._cached_probe_counts = dict(row.probe_counts)

        if self.echo_to_console:
            if not self._printed_metadata:
                for line in self._metadata_lines():
                    print(line)
                self._printed_metadata = True
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

        self.output_root.mkdir(parents=True, exist_ok=True)
        csv_path = self.output_root / f"{self.stem}.csv"
        self._write_csv(csv_path)
        return csv_path

    def _write_csv(self, path: Path) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            metadata_keys = sorted(self.metadata)
            header = [
                "iter",
                "delta",
                "shift",
                "iter_seconds",
                "max_delta_chii",
                "max_delta_value",
                "max_delta_count",
                "max_delta_previous",
                "max_delta_raw",
                "max_delta_next",
                "max_delta_raw_minus_previous",
            ]
            header.extend(metadata_keys)
            header.extend(str(chii) for chii in self.probes)
            header.extend(f"n_{chii}" for chii in self.probes)
            writer.writerow(header)
            for row in self._rows:
                values = [
                    row.iteration,
                    row.delta,
                    row.shift,
                    row.iter_seconds,
                    "" if row.max_delta_chii is None else str(row.max_delta_chii),
                    "" if row.max_delta_value is None else row.max_delta_value,
                    "" if row.max_delta_count is None else row.max_delta_count,
                    "" if row.max_delta_previous is None else row.max_delta_previous,
                    "" if row.max_delta_raw is None else row.max_delta_raw,
                    "" if row.max_delta_next is None else row.max_delta_next,
                    (
                        ""
                        if row.max_delta_raw is None or row.max_delta_previous is None
                        else row.max_delta_raw - row.max_delta_previous
                    ),
                ]
                values.extend(self.metadata[key] for key in metadata_keys)
                values.extend(row.probe_values[chii] for chii in self.probes)
                values.extend(row.probe_counts[chii] for chii in self.probes)
                writer.writerow(values)

    def _metadata_lines(self) -> list[str]:
        return [f"# {key}={value}" for key, value in sorted(self.metadata.items())]

    def _header_line(self) -> str:
        left = (
            f"{'iter':>{ITER_WIDTH}} "
            f"{'delta':>{DELTA_WIDTH}} "
            f"{'shift':>{SHIFT_WIDTH}} "
            f"{'secs':>{TIME_WIDTH}}"
        )
        probe_value_cols = " ".join(f"{str(chii):>{VALUE_WIDTH}}" for chii in self.probes)
        return (
            f"{left}  "
            f"{'max_delta':>{VALUE_WIDTH}} "
            f"{'n':>{COUNT_WIDTH}} "
            f"{'raw-prev':>{DELTA_WIDTH}} "
            f"{'raw':>{VALUE_WIDTH}} "
            f"{'next':>{VALUE_WIDTH}}  "
            f"{probe_value_cols}"
        )

    def _counts_line(self) -> str:
        assert self._cached_probe_counts is not None
        left = " " * (ITER_WIDTH + 1 + DELTA_WIDTH + 1 + SHIFT_WIDTH + 1 + TIME_WIDTH)
        count_cols = " ".join(
            f"{('n_' + str(chii) + '=' + str(self._cached_probe_counts[chii])):>{VALUE_WIDTH}}"
            for chii in self.probes
        )
        return (
            f"{left}  "
            f"{'':>{VALUE_WIDTH}} "
            f"{'':>{COUNT_WIDTH}} "
            f"{'':>{DELTA_WIDTH}} "
            f"{'':>{VALUE_WIDTH}} "
            f"{'':>{VALUE_WIDTH}}  "
            f"{count_cols}"
        )

    def _format_row(self, row: IterationDiagnosticsRow) -> str:
        left = (
            f"{row.iteration:>{ITER_WIDTH}d} "
            f"{row.delta:>{DELTA_WIDTH}.6f} "
            f"{row.shift:>{SHIFT_WIDTH}.6f} "
            f"{row.iter_seconds:>{TIME_WIDTH}.3f}"
        )
        max_delta = "" if row.max_delta_chii is None else str(row.max_delta_chii)
        max_count = "" if row.max_delta_count is None else str(row.max_delta_count)
        raw_minus_previous = (
            None
            if row.max_delta_raw is None or row.max_delta_previous is None
            else row.max_delta_raw - row.max_delta_previous
        )
        raw_minus_previous_text = "" if raw_minus_previous is None else f"{raw_minus_previous:.3f}"
        raw_text = "" if row.max_delta_raw is None else f"{row.max_delta_raw:.3f}"
        next_text = "" if row.max_delta_next is None else f"{row.max_delta_next:.3f}"
        probe_value_cols = " ".join(
            f"{row.probe_values[chii]:>{VALUE_WIDTH}.3f}" for chii in self.probes
        )
        return (
            f"{left}  "
            f"{max_delta:>{VALUE_WIDTH}} "
            f"{max_count:>{COUNT_WIDTH}} "
            f"{raw_minus_previous_text:>{DELTA_WIDTH}} "
            f"{raw_text:>{VALUE_WIDTH}} "
            f"{next_text:>{VALUE_WIDTH}}  "
            f"{probe_value_cols}"
        )

    def summary_line(self) -> str | None:
        if not self._rows:
            return None
        total = sum(row.iter_seconds for row in self._rows)
        avg = total / len(self._rows)
        if not self.metadata:
            return f"[diagnostics] iterations={len(self._rows)} avg_secs={avg:.3f} total_secs={total:.3f}"
        metadata_bits = " ".join(f"{key}={value}" for key, value in sorted(self.metadata.items()))
        return (
            f"[diagnostics] {metadata_bits} iterations={len(self._rows)} "
            f"avg_secs={avg:.3f} total_secs={total:.3f}"
        )

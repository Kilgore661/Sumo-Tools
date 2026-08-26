from __future__ import annotations

import csv
import json
from math import isclose

from src.analysis.elo_model_selection.dual_k_mass import (
    LedgerMassRow,
    analyse,
    read_ledger,
    write_outputs,
)


def test_dual_k_mass_reconciles_models_pairs_and_basho() -> None:
    rows = (
        _row("B", "1989/01", 35, 35, 4, -4),
        _row("B", "1989/03", 35, 35, -3, 3),
        _row("B_k", "1989/01", 10, 15, 4, -6),
        _row("B_k", "1989/01", 15, 10, -3, 2),
        _row("B_k", "1989/03", 25, 35, 5, -2),
        _row("B_k", "1989/03", 15, 15, 4, -4),
        _row("B_P", "1989/01", 35, 35, 2, -2),
        _row("B_kP", "1989/01", 10, 15, 5, -2),
        _row("B_kP", "1989/03", 25, 35, -4, 1),
    )

    result = analyse(rows)
    summaries = {row.model: row for row in result.models}

    assert summaries["B"].unequal_k_bout_count == 0
    assert summaries["B_P"].net_mass_change == 0
    assert summaries["B_k"].rated_bout_count == 4
    assert summaries["B_k"].unequal_k_bout_count == 3
    assert summaries["B_k"].net_mass_change == 0
    assert summaries["B_k"].gross_absolute_mass_change == 6
    assert summaries["B_k"].positive_mass_change == 3
    assert summaries["B_k"].negative_mass_change == -3
    assert summaries["B_k"].cancellation_share == 1
    assert summaries["B_k"].same_k_residual == 0
    assert summaries["B_kP"].net_mass_change == 0

    bk_pairs = tuple(row for row in result.k_pairs if row.model == "B_k")
    assert tuple((row.k_low, row.k_high) for row in bk_pairs) == (
        (10, 15),
        (25, 35),
    )
    assert sum(row.net_mass_change for row in bk_pairs) == 0
    assert sum(row.gross_absolute_mass_change for row in bk_pairs) == 6

    bk_basho = tuple(row for row in result.basho if row.model == "B_k")
    assert tuple(row.date for row in bk_basho) == ("1989/01", "1989/03")
    assert tuple(row.net_mass_change for row in bk_basho) == (-3, 3)
    assert tuple(row.cumulative_net_mass_change for row in bk_basho) == (-3, 0)


def test_dual_k_mass_reads_and_persists_reproducible_outputs(tmp_path) -> None:
    ledger = tmp_path / "forecast_ledger.csv"
    fields = ("model", "date", "k_a", "k_b", "delta_a", "delta_b")
    with ledger.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for model in ("B", "B_k", "B_P", "B_kP"):
            writer.writerow(
                {
                    "model": model,
                    "date": "1989/01",
                    "k_a": 10 if "_k" in model else 35,
                    "k_b": 15 if "_k" in model else 35,
                    "delta_a": 4,
                    "delta_b": -6 if "_k" in model else -4,
                }
            )

    result = analyse(read_ledger(ledger))
    output = tmp_path / "output"
    write_outputs(result, ledger, output)

    assert (output / "summary.csv").is_file()
    assert (output / "by_k_pair.csv").is_file()
    assert (output / "by_basho.csv").is_file()
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_ledger"]["path"] == str(ledger.resolve())
    assert len(manifest["source_ledger"]["sha256"]) == 64
    report = (output / "report.md").read_text(encoding="utf-8")
    assert "Cumulative Unequal-K Rating Mass" in report
    assert "sanyaku--maegashira" in report
    assert "active-population mean" in report
    assert isclose(result.models[-1].unequal_k_bout_share, 1.0)


def _row(
    model: str,
    date: str,
    k_a: float,
    k_b: float,
    delta_a: float,
    delta_b: float,
) -> LedgerMassRow:
    return LedgerMassRow(
        model=model,
        date=date,
        k_a=k_a,
        k_b=k_b,
        delta_a=delta_a,
        delta_b=delta_b,
    )

"""CSV reports for Equelo support-domain evidence."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from src.analysis.equelo.support_domain.measure import SupportMeasurement
from src.analysis.probability.builder import ChiiRatings
from src.sumo_core.Chii import Chii


DEFAULT_OUTPUT_ROOT = Path("files/output/Equelo/support_domain")
DEFAULT_THRESHOLDS = (0.005, 0.01, 0.02, 0.03, 0.05, 0.1)


@dataclass(frozen=True)
class SupportRow:
    chii: str
    ordinal: int
    raw_members: str
    appearances: int
    max_possible_rikishi_bouts: int
    max_support_ratio_m1e: str
    actual_scored_rikishi_bouts: int
    actual_support_ratio_m1e: str
    max_total_pct: str
    actual_total_pct: str
    fixed_point_rating: str


@dataclass(frozen=True)
class ThresholdSummaryRow:
    threshold_s: str
    excluded_chii: int
    ignored_scored_bouts: int
    ignored_scored_bout_pct: str
    excluded_max_total_pct: str
    excluded_actual_total_pct: str
    strongest_excluded_chii: str


@dataclass(frozen=True)
class ReportOutputs:
    output_root: Path
    support_csv: Path
    threshold_summary_csv: Path
    exclusion_csvs: tuple[Path, ...]


def write_support_domain_reports(
    *,
    measurement: SupportMeasurement,
    fixed_point_ratings: ChiiRatings,
    thresholds: Iterable[float] = DEFAULT_THRESHOLDS,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> ReportOutputs:
    """Write support, threshold, and threshold-exclusion CSVs."""

    output_root.mkdir(parents=True, exist_ok=True)
    support_rows = build_support_rows(
        measurement=measurement,
        fixed_point_ratings=fixed_point_ratings,
    )
    support_csv = output_root / "support_by_chii.csv"
    _write_dataclass_csv(support_rows, support_csv)

    threshold_values = tuple(float(threshold) for threshold in thresholds)
    summary_rows = build_threshold_summary_rows(
        measurement=measurement,
        support_rows=support_rows,
        thresholds=threshold_values,
    )
    threshold_summary_csv = output_root / "threshold_summary.csv"
    _write_dataclass_csv(summary_rows, threshold_summary_csv)

    exclusion_csvs = tuple(
        _write_exclusion_csv(
            support_rows=support_rows,
            threshold=threshold,
            output_root=output_root,
        )
        for threshold in threshold_values
    )
    return ReportOutputs(
        output_root=output_root,
        support_csv=support_csv,
        threshold_summary_csv=threshold_summary_csv,
        exclusion_csvs=exclusion_csvs,
    )


def build_support_rows(
    *,
    measurement: SupportMeasurement,
    fixed_point_ratings: ChiiRatings,
) -> tuple[SupportRow, ...]:
    """Build one row per RFSC-collapsed chii."""

    m1e = Chii.from_str("M1e")
    max_m1e = measurement.max_possible_rikishi_bouts[m1e]
    actual_m1e = measurement.actual_scored_rikishi_bouts[m1e]
    rows: list[SupportRow] = []

    for chii in sorted(measurement.max_possible_rikishi_bouts, key=lambda c: c.ordinal()):
        max_bouts = measurement.max_possible_rikishi_bouts[chii]
        actual_bouts = measurement.actual_scored_rikishi_bouts[chii]
        rows.append(
            SupportRow(
                chii=str(chii),
                ordinal=chii.ordinal(),
                raw_members=_raw_members_text(measurement, chii),
                appearances=measurement.appearances[chii],
                max_possible_rikishi_bouts=max_bouts,
                max_support_ratio_m1e=_ratio(max_bouts, max_m1e),
                actual_scored_rikishi_bouts=actual_bouts,
                actual_support_ratio_m1e=_ratio(actual_bouts, actual_m1e),
                max_total_pct=_percent(
                    max_bouts,
                    measurement.total_max_possible_rikishi_bouts,
                ),
                actual_total_pct=_percent(
                    actual_bouts,
                    measurement.total_actual_scored_rikishi_bouts,
                ),
                fixed_point_rating=_rating_text(fixed_point_ratings, chii),
            )
        )

    return tuple(rows)


def build_threshold_summary_rows(
    *,
    measurement: SupportMeasurement,
    support_rows: Iterable[SupportRow],
    thresholds: Iterable[float],
) -> tuple[ThresholdSummaryRow, ...]:
    """Summarise how much each support threshold excludes."""

    rows = tuple(support_rows)
    output: list[ThresholdSummaryRow] = []

    for threshold in thresholds:
        excluded = _excluded_rows(rows, threshold)
        excluded_names = {row.chii for row in excluded}
        ignored_bouts = sum(
            count
            for (chii1, chii2), count in measurement.actual_scored_bouts_by_pair.items()
            if str(chii1) in excluded_names or str(chii2) in excluded_names
        )
        strongest = min(excluded, key=lambda row: row.ordinal).chii if excluded else ""
        excluded_max = sum(row.max_possible_rikishi_bouts for row in excluded)
        excluded_actual = sum(row.actual_scored_rikishi_bouts for row in excluded)
        output.append(
            ThresholdSummaryRow(
                threshold_s=_threshold_text(threshold),
                excluded_chii=len(excluded),
                ignored_scored_bouts=ignored_bouts,
                ignored_scored_bout_pct=_percent(
                    ignored_bouts,
                    measurement.total_actual_scored_bouts,
                ),
                excluded_max_total_pct=_percent(
                    excluded_max,
                    measurement.total_max_possible_rikishi_bouts,
                ),
                excluded_actual_total_pct=_percent(
                    excluded_actual,
                    measurement.total_actual_scored_rikishi_bouts,
                ),
                strongest_excluded_chii=strongest,
            )
        )

    return tuple(output)


def _write_exclusion_csv(
    *,
    support_rows: Iterable[SupportRow],
    threshold: float,
    output_root: Path,
) -> Path:
    rows = _excluded_rows(tuple(support_rows), threshold)
    path = output_root / f"excluded_s_{_threshold_stem(threshold)}.csv"
    _write_dataclass_csv(rows, path)
    return path


def _excluded_rows(rows: Iterable[SupportRow], threshold: float) -> tuple[SupportRow, ...]:
    return tuple(
        row for row in rows
        if float(row.max_support_ratio_m1e) < threshold
    )


def _raw_members_text(measurement: SupportMeasurement, chii: Chii) -> str:
    raw_members = sorted(
        measurement.raw_members_by_collapsed_chii.get(chii, ()),
        key=lambda raw_chii: raw_chii.ordinal(),
    )
    return "|".join(str(raw_chii) for raw_chii in raw_members)


def _rating_text(ratings: ChiiRatings, chii: Chii) -> str:
    rating = ratings.get(chii)
    if rating is None:
        return ""
    return f"{rating:.6f}"


def _ratio(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return ""
    return f"{numerator / denominator:.9f}"


def _percent(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return ""
    return f"{100.0 * numerator / denominator:.6f}"


def _threshold_text(threshold: float) -> str:
    return f"{threshold:.6f}".rstrip("0").rstrip(".")


def _threshold_stem(threshold: float) -> str:
    return f"{threshold:.3f}".replace(".", "_")


def _write_dataclass_csv(rows: Iterable[object], path: Path) -> None:
    rows = tuple(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tuple(rows[0].__dataclass_fields__))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))

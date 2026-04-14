from __future__ import annotations

import math
from dataclasses import dataclass

from src.analysis.probability.classes import CalibrationRow

from .expt3_types import Expt3BottomLine, ProbabilityRegion


@dataclass(frozen=True)
class _IndexedRow:
    index: int
    row: CalibrationRow
    p_mid: float
    support_adequate: bool
    low_error: bool


def probability_to_delta(p: float, q: float) -> float | None:
    if q <= 0:
        return None
    if not (0.0 < p < 1.0):
        return None
    return q * math.log10(p / (1.0 - p))


def support_se_from_row(row: CalibrationRow) -> float | None:
    if row.n_obs <= 0:
        return None
    p = float(row.mean_predicted)
    if not (0.0 < p < 1.0):
        return None
    return math.sqrt((p * (1.0 - p)) / row.n_obs)


def support_is_adequate(row: CalibrationRow, se_threshold: float) -> bool:
    se = support_se_from_row(row)
    return se is not None and se <= se_threshold


def _sorted_rows(rows: list[CalibrationRow]) -> list[CalibrationRow]:
    return sorted(rows, key=lambda r: r.mean_predicted)


def _index_rows(
    rows: list[CalibrationRow],
    se_threshold: float,
    error_threshold: float,
) -> list[_IndexedRow]:
    indexed: list[_IndexedRow] = []
    for i, row in enumerate(_sorted_rows(rows)):
        indexed.append(
            _IndexedRow(
                index=i,
                row=row,
                p_mid=float(row.mean_predicted),
                support_adequate=support_is_adequate(row, se_threshold),
                low_error=float(row.abs_error) <= error_threshold,
            )
        )
    return indexed


def _rows_to_region(group: list[_IndexedRow], *, include_error: bool) -> ProbabilityRegion:
    if not group:
        raise ValueError("Cannot convert empty group to region")

    p_lo = group[0].p_mid
    p_hi = group[-1].p_mid
    n_bins = len(group)
    n_obs = sum(item.row.n_obs for item in group)
    max_abs_error = max(float(item.row.abs_error) for item in group) if include_error else None

    return ProbabilityRegion(
        p_lo=p_lo,
        p_hi=p_hi,
        n_bins=n_bins,
        n_obs=n_obs,
        max_abs_error=max_abs_error,
    )


def _group_contiguous(items: list[_IndexedRow]) -> list[list[_IndexedRow]]:
    if not items:
        return []

    groups: list[list[_IndexedRow]] = [[items[0]]]
    for item in items[1:]:
        prev = groups[-1][-1]
        if item.index == prev.index + 1:
            groups[-1].append(item)
        else:
            groups.append([item])
    return groups


def _find_support_regions(
    indexed: list[_IndexedRow],
) -> tuple[list[ProbabilityRegion], list[ProbabilityRegion]]:
    adequate = [item for item in indexed if item.support_adequate]
    inadequate = [item for item in indexed if not item.support_adequate]

    adequate_regions = [_rows_to_region(g, include_error=False) for g in _group_contiguous(adequate)]
    inadequate_regions = [_rows_to_region(g, include_error=False) for g in _group_contiguous(inadequate)]
    return inadequate_regions, adequate_regions


def _find_central_low_error_region(
    indexed: list[_IndexedRow],
    q: float,
) -> tuple[ProbabilityRegion | None, float | None, float | None]:
    if not indexed:
        return None, None, None

    eligible = [item for item in indexed if item.support_adequate and item.low_error]
    if not eligible:
        return None, None, None

    groups = _group_contiguous(eligible)
    if not groups:
        return None, None, None

    # Choose the maximal contiguous eligible region containing the bin closest to p=0.5.
    all_items = [item for group in groups for item in group]
    central_item = min(all_items, key=lambda item: abs(item.p_mid - 0.5))

    chosen_group: list[_IndexedRow] | None = None
    for group in groups:
        if any(item.index == central_item.index for item in group):
            chosen_group = group
            break

    if chosen_group is None:
        return None, None, None

    region = _rows_to_region(chosen_group, include_error=True)
    delta_lo = probability_to_delta(region.p_lo, q)
    delta_hi = probability_to_delta(region.p_hi, q)
    return region, delta_lo, delta_hi


def build_bottom_line(
    rows: list[CalibrationRow],
    *,
    q: float,
    support_se_threshold: float,
    error_threshold: float,
) -> Expt3BottomLine:
    warnings: list[str] = []

    if not rows:
        return Expt3BottomLine(
            support_regions_inadequate=[],
            support_regions_adequate=[],
            central_low_error_region=None,
            central_low_error_delta_lo=None,
            central_low_error_delta_hi=None,
            warnings=["No calibration rows available."],
        )

    if q <= 0:
        warnings.append(f"Cannot convert probability to delta because q={q:g} is not positive.")

    indexed = _index_rows(
        rows=rows,
        se_threshold=support_se_threshold,
        error_threshold=error_threshold,
    )

    inadequate_regions, adequate_regions = _find_support_regions(indexed)

    if not adequate_regions:
        warnings.append("No adequate-support probability bins were found.")
    if len(inadequate_regions) == 0:
        warnings.append("No inadequate-support probability bins were found.")
    elif len(inadequate_regions) > 2:
        warnings.append(
            f"Found {len(inadequate_regions)} inadequate-support regions; expected tail regions only."
        )

    central_region, delta_lo, delta_hi = _find_central_low_error_region(indexed, q=q)
    if central_region is None:
        warnings.append(
            "No central contiguous region containing p≈0.5 satisfied both the support and error thresholds."
        )

    return Expt3BottomLine(
        support_regions_inadequate=inadequate_regions,
        support_regions_adequate=adequate_regions,
        central_low_error_region=central_region,
        central_low_error_delta_lo=delta_lo,
        central_low_error_delta_hi=delta_hi,
        warnings=warnings,
    )


def render_bottom_line(
    bottom_line: Expt3BottomLine,
    *,
    support_se_threshold: float,
    error_threshold: float,
) -> list[str]:
    lines: list[str] = []
    lines.append("Bottom-line summary:")
    lines.append(f"  Support SE threshold: {support_se_threshold:.6f}")
    lines.append(f"  Error threshold: {error_threshold:.6f}")

    if bottom_line.support_regions_inadequate:
        lines.append("  Inadequate-support probability regions:")
        for region in bottom_line.support_regions_inadequate:
            lines.append(
                "    "
                f"{region.p_lo:.2f} <= p <= {region.p_hi:.2f} "
                f"(bins={region.n_bins}, obs={region.n_obs})"
            )
    else:
        lines.append("  Inadequate-support probability regions: none")

    if bottom_line.central_low_error_region is not None:
        region = bottom_line.central_low_error_region
        lines.append("  Central adequate low-error region:")
        lines.append(
            "    "
            f"{region.p_lo:.2f} <= p <= {region.p_hi:.2f} "
            f"(bins={region.n_bins}, obs={region.n_obs}, "
            f"max_abs_error={region.max_abs_error:.6f})"
        )
        if (
            bottom_line.central_low_error_delta_lo is not None
            and bottom_line.central_low_error_delta_hi is not None
        ):
            lines.append(
                "    "
                f"Corresponding delta range: "
                f"{bottom_line.central_low_error_delta_lo:.6f} <= delta <= "
                f"{bottom_line.central_low_error_delta_hi:.6f}"
            )
        else:
            lines.append("    Corresponding delta range: unavailable")
    else:
        lines.append("  Central adequate low-error region: none")

    if bottom_line.warnings:
        lines.append("  Warnings:")
        for warning in bottom_line.warnings:
            lines.append(f"    - {warning}")

    return lines

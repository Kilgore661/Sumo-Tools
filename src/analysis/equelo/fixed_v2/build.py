"""Build first-stage fixed_v2 comparison artefacts."""

from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass
from pathlib import Path

from src.analysis.equelo.fixed_v1.initial_rating import (
    InitialRatingCurve,
    V1_MAX_CHII,
    V3_MASK_ORDINALS,
    V4_DELETE_ORDINALS,
    V5_EXTRA_MASK_ORDINALS,
)
from src.analysis.probability.builder import load_ratings_csv
from src.sumo_core.Chii import Chii

from .model import (
    BRIER_ALPHA,
    COMPARISON_CSV_FILE_NAME,
    FP_SOURCE,
    OUTPUT_ROOT,
    SANITISATION_REPORT_FILE_NAME,
)


ChiiRatings = dict[Chii, float]
OrdinalRatings = dict[int, float]


@dataclass(frozen=True)
class FixedV2ComparisonOutputs:
    """Paths written by the first fixed_v2 comparison build."""

    output_root: Path
    comparison_csv: Path
    sanitisation_report: Path


def build_fixed_v2_comparison(
    *,
    fp_source: Path = FP_SOURCE,
    output_root: Path = OUTPUT_ROOT,
    alpha: float = BRIER_ALPHA,
) -> FixedV2ComparisonOutputs:
    """Write the FP/Brier/sanitised comparison CSV for manual inspection."""

    fp_by_chii = load_ratings_csv(fp_source)
    fp_by_ordinal = to_ordinal_ratings(fp_by_chii)
    brier_by_ordinal = brier_ratings_from_fp(fp_by_ordinal, alpha=alpha)

    fp_curve = InitialRatingCurve.from_ordinal_ratings(fp_by_ordinal)
    brier_curve = InitialRatingCurve.from_ordinal_ratings(brier_by_ordinal)

    output_root.mkdir(parents=True, exist_ok=True)
    comparison_csv = output_root / COMPARISON_CSV_FILE_NAME
    write_comparison_csv(
        path=comparison_csv,
        fp_by_ordinal=fp_by_ordinal,
        brier_by_ordinal=brier_by_ordinal,
        fp_curve=fp_curve,
        brier_curve=brier_curve,
    )

    sanitisation_report = output_root / SANITISATION_REPORT_FILE_NAME
    write_fp_sanitisation_report(
        path=sanitisation_report,
        fp_by_ordinal=fp_by_ordinal,
        fp_curve=fp_curve,
    )

    return FixedV2ComparisonOutputs(
        output_root=output_root,
        comparison_csv=comparison_csv,
        sanitisation_report=sanitisation_report,
    )


def to_ordinal_ratings(ratings: ChiiRatings) -> OrdinalRatings:
    """Convert a Chii-keyed rating map to an ordinal-keyed rating map."""

    return {
        chii.ordinal(): float(rating)
        for chii, rating in ratings.items()
    }


def brier_ratings_from_fp(
    fp_by_ordinal: OrdinalRatings,
    *,
    alpha: float = BRIER_ALPHA,
) -> OrdinalRatings:
    """Reconstruct fixed_v1 Brier entrant ratings from FP ratings."""

    # fixed_v1 historically wrote the Brier entrant ratings to:
    #   files/output/Equelo/fixed_v1/entrant_initial_ratings.json
    #
    # That generated file is not an independent source. It is reconstructed
    # exactly from the Expt2 fixed-point ratings by the affine contraction:
    #
    #   Brier(c) = μ + α(FP(c) - μ)
    #
    # where μ is the mean FP rating and fixed_v1 used α = 0.55.
    if not fp_by_ordinal:
        raise ValueError("Cannot derive Brier ratings from an empty FP map")

    mu = sum(fp_by_ordinal.values()) / len(fp_by_ordinal)
    return {
        ordinal: mu + alpha * (rating - mu)
        for ordinal, rating in fp_by_ordinal.items()
    }


def write_comparison_csv(
    *,
    path: Path,
    fp_by_ordinal: OrdinalRatings,
    brier_by_ordinal: OrdinalRatings,
    fp_curve: InitialRatingCurve,
    brier_curve: InitialRatingCurve,
) -> None:
    """Write the five-column first-stage comparison CSV."""

    all_ordinals = sorted(fp_by_ordinal)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "chii_ordinal",
                "fp_rating",
                "brier_rating",
                "fp_sanitised_rating",
                "brier_sanitised_rating",
            ]
        )
        for ordinal in all_ordinals:
            writer.writerow(
                [
                    ordinal,
                    fp_by_ordinal[ordinal],
                    brier_by_ordinal[ordinal],
                    maybe_curve_rating(fp_curve, ordinal),
                    maybe_curve_rating(brier_curve, ordinal),
                ]
            )


def maybe_curve_rating(curve: InitialRatingCurve, ordinal: int) -> float | str:
    """Return a sanitised curve value, or blank if the ordinal was deleted."""

    if ordinal not in curve.index_by_ordinal:
        return ""
    return curve.rating_for_ordinal(ordinal)


def write_fp_sanitisation_report(
    *,
    path: Path,
    fp_by_ordinal: OrdinalRatings,
    fp_curve: InitialRatingCurve,
    epsilon: float = 1e-6,
) -> None:
    """Write a short report on FP→Sanitised(FP) distortion."""

    observed_ordinals = set(fp_by_ordinal)
    below_cutoff = {
        ordinal for ordinal in observed_ordinals
        if ordinal > V1_MAX_CHII
    }

    in_cutoff_domain = observed_ordinals - below_cutoff

    # These are the explicit low-support / historical-rank exclusions used for
    # this first fixed_v2 distortion report.  The v5 bridge mask is deliberately
    # not included here: the M12→Ms2 bridge is retained as part of the population
    # of interest, because its interpolation movement is exactly what the report
    # is meant to measure.
    policy_exclusion_ordinals = (
        set(V4_DELETE_ORDINALS)
        | set(V3_MASK_ORDINALS)
        | set(V5_EXTRA_MASK_ORDINALS)
    )
    excluded_by_policy = in_cutoff_domain & policy_exclusion_ordinals

    report_population = sorted(in_cutoff_domain - excluded_by_policy)

    changed_rows: list[tuple[int, float]] = []
    unchanged_count = 0
    missing_after_sanitisation: list[int] = []

    for ordinal in report_population:
        if ordinal not in fp_curve.index_by_ordinal:
            missing_after_sanitisation.append(ordinal)
            continue

        delta = abs(fp_curve.rating_for_ordinal(ordinal) - fp_by_ordinal[ordinal])
        if delta <= epsilon:
            unchanged_count += 1
        else:
            changed_rows.append((ordinal, delta))

    deltas = [delta for _, delta in changed_rows]
    mean_delta = statistics.fmean(deltas) if deltas else 0.0
    max_delta = max(deltas) if deltas else 0.0
    stdev_delta = statistics.stdev(deltas) if len(deltas) >= 2 else 0.0

    max_rows = [
        (ordinal, delta)
        for ordinal, delta in changed_rows
        if abs(delta - max_delta) <= epsilon
    ]

    lines = [
        "FP sanitisation distortion report",
        "=================================",
        "",
        f"Number of observed chii: {len(observed_ordinals)}",
        f"Excluded Jd101 and below: {len(below_cutoff)}",
        f"Excluded as per v4/v5: {len(excluded_by_policy)}",
        f"Remaining after exclusions: {len(report_population)}",
        f"Excluded because there is no difference: {unchanged_count}",
        f"Missing after sanitisation: {len(missing_after_sanitisation)}",
        f"Analysed changed chii: {len(changed_rows)}",
        "",
        "Absolute difference statistics for analysed changed chii:",
        f"Mean: {mean_delta}",
        f"Max: {max_delta}",
        f"Stdev: {stdev_delta}",
    ]

    if max_rows:
        lines.extend([
            "",
            "Chii with max absolute difference:",
            *[
                f"{ordinal} ({Chii.from_ordinal(ordinal)}): {delta}"
                for ordinal, delta in max_rows
            ],
        ])

    if missing_after_sanitisation:
        lines.extend([
            "",
            "Missing after sanitisation:",
            *[
                f"{ordinal} ({Chii.from_ordinal(ordinal)})"
                for ordinal in missing_after_sanitisation
            ],
        ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

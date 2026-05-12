"""Build first-stage fixed_v2 comparison artefacts."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from src.analysis.equelo.fixed_v1.initial_rating import InitialRatingCurve
from src.analysis.probability.builder import load_ratings_csv
from src.sumo_core.Chii import Chii

from .model import BRIER_ALPHA, COMPARISON_CSV_FILE_NAME, FP_SOURCE, OUTPUT_ROOT


ChiiRatings = dict[Chii, float]
OrdinalRatings = dict[int, float]


@dataclass(frozen=True)
class FixedV2ComparisonOutputs:
    """Paths written by the first fixed_v2 comparison build."""

    output_root: Path
    comparison_csv: Path


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

    return FixedV2ComparisonOutputs(
        output_root=output_root,
        comparison_csv=comparison_csv,
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

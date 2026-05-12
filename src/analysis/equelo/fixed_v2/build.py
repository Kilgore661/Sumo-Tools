"""Build first-stage fixed_v2 comparison artefacts."""

from __future__ import annotations

import csv
import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from src.analysis.equelo.fixed_v1.initial_rating import (
    InitialRatingCurve,
    V1_MAX_CHII,
    V3_MASK_ORDINALS,
    V4_DELETE_ORDINALS,
    V5_EXTRA_MASK_ORDINALS,
)
from src.analysis.equelo.config_main import BIOS_PATH
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode, SimulationResult, simulate
from src.analysis.probability.builder import load_ratings_csv
from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .model import (
    BRIER_ALPHA,
    COLLAPSE_MODE,
    COMPARISON_CSV_FILE_NAME,
    FP_SOURCE,
    K_CONFIG,
    K_POLICY,
    OUTPUT_ROOT,
    Q,
    SANITISATION_REPORT_FILE_NAME,
)
from .output import write_outputs


EntrantInitialiser = Callable[[Chii], float]
ChiiRatings = dict[Chii, float]
OrdinalRatings = dict[int, float]

M13_TO_J1_START_ORDINAL = Chii.from_str("M13e").ordinal()
M13_TO_J1_END_ORDINAL = Chii.from_str("J1w").ordinal()


def build_fixed_v2(output_root: Path = OUTPUT_ROOT) -> dict[str, Path]:
    """Generate and persist the fixed_v2 Equelo rating series."""

    raw_history = get_history()
    result, cleaned_history, entrant_initial_ratings = compute_fixed_v2(raw_history)
    return write_outputs(
        history=cleaned_history,
        day_end_ratings=result.day_end_ratings,
        entrant_initial_ratings=entrant_initial_ratings,
        output_root=output_root,
    )


def compute_fixed_v2(raw_history: History) -> tuple[SimulationResult, History, ChiiRatings]:
    """Compute fixed_v2 ratings from a supplied raw History."""

    oracle = make_oracle(
        raw_history,
        load_bios(),
        collapse_mode=oracle_collapse_mode(),
    )
    params = build_elo_params(
        k_policy=K_POLICY,
        q=Q,
        config_path=K_CONFIG,
    )
    entrant_initial_ratings = fixed_point_ratings()
    result = simulate(
        history=oracle.history,
        params=params,
        entrant_initialiser=make_chii_initialiser(entrant_initial_ratings),
        mode=SimulationMode.CLOSED,
    )

    return result, oracle.history, entrant_initial_ratings


def load_bios() -> dict[RikId, dict]:
    """Load bios for Oracle construction."""

    with BIOS_PATH.open("r", encoding="utf-8") as f:
        raw_bios = json.load(f)

    return {RikId(int(key)): value for key, value in raw_bios.items()}


def fixed_point_ratings(*, source: Path = FP_SOURCE) -> ChiiRatings:
    """Return the fixed_v2 raw fixed-point chii-to-entrant-rating map."""

    return load_ratings_csv(source)


def make_chii_initialiser(ratings: ChiiRatings) -> EntrantInitialiser:
    """Build a chii-based entrant initialiser from an explicit ratings map."""

    def initialise(chii: Chii) -> float:
        return float(ratings[chii])

    return initialise


def fixed_point_initialiser(*, source: Path = FP_SOURCE) -> EntrantInitialiser:
    """Build the fixed_v2 raw fixed-point chii-based entrant initialiser."""

    return make_chii_initialiser(fixed_point_ratings(source=source))


def oracle_collapse_mode() -> str:
    """Return the Oracle collapse mode token for the fixed_v2 spec value."""

    if COLLAPSE_MODE == "annotation-only":
        return "annotation_only"

    return COLLAPSE_MODE


def is_m13_to_j1_ordinal(ordinal: int) -> bool:
    """Return True for the M13e→J1w rank band used as a final report exclusion."""

    return M13_TO_J1_START_ORDINAL <= ordinal <= M13_TO_J1_END_ORDINAL


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

    post_policy_population = in_cutoff_domain - excluded_by_policy
    excluded_m13_to_j1 = {
        ordinal for ordinal in post_policy_population
        if is_m13_to_j1_ordinal(ordinal)
    }

    report_population = sorted(post_policy_population - excluded_m13_to_j1)

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
        f"Excluded M13e→J1w bridge region: {len(excluded_m13_to_j1)}",
        f"Remaining after exclusions: {len(report_population)}",
        f"Excluded because there is no difference: {unchanged_count}",
        f"Missing after sanitisation: {len(missing_after_sanitisation)}",
        f"Analysed changed chii: {len(changed_rows)}",
        "",
        "Absolute difference statistics for analysed changed chii:",
        f"Mean: {mean_delta:.2f}",
        f"Max: {max_delta:.2f}",
        f"Stdev: {stdev_delta:.2f}",
    ]

    if max_rows:
        lines.extend([
            "",
            "Chii with max absolute difference:",
            *[
                f"{ordinal} ({Chii.from_ordinal(ordinal)}): {delta:.2f}"
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

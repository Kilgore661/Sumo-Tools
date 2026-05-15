"""Data-reference declarations for the public site."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from .classes import DataRef
from .site_config import (
    BASHO_RESULTS_OUTPUT_ROOT,
    BASHO_RESULTS_SITE_OUTPUT_DIR,
    BCR_OUTPUT_ROOT,
    CAREER_LENGTH_SITE_OUTPUT_DIR,
    DIVISION_STABILITY_SITE_BUNDLE,
    DIVISION_STABILITY_SITE_OUTPUT_DIR,
    FIRST_CHII_APPEARANCE_SITE_BUNDLE,
    FIRST_CHII_APPEARANCE_SITE_OUTPUT_DIR,
    RANK_AT_RETIREMENT_SITE_OUTPUT_DIR,
    STANDINGS_PUBLISHER_DATA,
    TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR,
    WIN_PROBABILITY_SITE_BUNDLE,
)
from .site_refs import data, published_data_refs
from src.analysis.equelo.fixed_v2.v5_landmarks import V5LandmarkOutputs
from src.analysis.sumo_history.career_lifecycle.career_length import CareerLengthOutputs
from src.analysis.sumo_history.career_lifecycle.rank_at_retirement import (
    RankAtRetirementOutputs,
)


STANDINGS_DATA = published_data_refs(
    source_dir=STANDINGS_PUBLISHER_DATA,
    output_dir="current-sumo/standings-by-wins/data",
    id_prefix="standings",
)


BANZUKE_CHANGES_DATA = (
    data(
        id="banzuke_changes_page_bundle",
        source_path=BCR_OUTPUT_ROOT / "page_bundle.json",
        output_path="current-sumo/banzuke-changes/page_bundle.json",
        media_type="application/json",
    ),
    data(
        id="banzuke_changes_site_config",
        source_path=BCR_OUTPUT_ROOT / "site_config.json",
        output_path="current-sumo/banzuke-changes/site_config.json",
        media_type="application/json",
    ),
    data(
        id="banzuke_change_report",
        source_path=BCR_OUTPUT_ROOT / "data" / "banzuke_change_report.csv",
        output_path="current-sumo/banzuke-changes/data/banzuke_change_report.csv",
        media_type="text/csv",
    ),
)


BASHO_RESULTS_INDEX_DATA = (
    data(
        id="basho_results_index",
        source_path=BASHO_RESULTS_OUTPUT_ROOT / "basho_results_index.json",
        output_path=f"{BASHO_RESULTS_SITE_OUTPUT_DIR}/basho_results_index.json",
        media_type="application/json",
    ),
)


BASHO_RESULTS_PAYLOAD_DATA = (
    *published_data_refs(
        source_dir=BASHO_RESULTS_OUTPUT_ROOT / "by-basho",
        output_dir=f"{BASHO_RESULTS_SITE_OUTPUT_DIR}/by-basho",
        id_prefix="basho_results",
    ),
)


BASHO_RESULTS_DATA = BASHO_RESULTS_INDEX_DATA + BASHO_RESULTS_PAYLOAD_DATA


def basho_results_data_refs(
    *,
    payload_mode: Literal["all", "latest", "none"] = "all",
) -> tuple[DataRef, ...]:
    if payload_mode == "all":
        return BASHO_RESULTS_DATA
    if payload_mode == "latest":
        return BASHO_RESULTS_INDEX_DATA + latest_basho_results_payload_data()
    if payload_mode != "none":
        raise ValueError(f"Unsupported basho results payload mode: {payload_mode}")
    return BASHO_RESULTS_INDEX_DATA


def latest_basho_results_payload_data() -> tuple[DataRef, ...]:
    index_path = BASHO_RESULTS_OUTPUT_ROOT / "basho_results_index.json"
    with index_path.open(encoding="utf-8") as handle:
        index = json.load(handle)
    default_basho = index.get("default_basho")
    entries = index.get("entries") or []
    entry = next(
        (item for item in entries if item.get("basho") == default_basho),
        entries[-1] if entries else None,
    )
    payload_path = entry.get("payload_path") if entry else None
    if not payload_path:
        return ()
    payload_name = payload_path.replace("\\", "/").rsplit("/", 1)[-1]
    return (
        data(
            id=f"basho_results_{Path(payload_name).stem}",
            source_path=BASHO_RESULTS_OUTPUT_ROOT / "by-basho" / payload_name,
            output_path=f"{BASHO_RESULTS_SITE_OUTPUT_DIR}/by-basho/{payload_name}",
            media_type="text/csv",
        ),
    )


WIN_PROBABILITY_BY_STANDING_DATA = (
    data(
        id="win_probability_by_standing_page_config",
        source_path=WIN_PROBABILITY_SITE_BUNDLE / "page.json",
        output_path=(
            "ratings-models/observed-vs-modelled/"
            "win-probability-by-standing/data/page.json"
        ),
        media_type="application/json",
    ),
    data(
        id="observed_standing_win_probability",
        source_path=WIN_PROBABILITY_SITE_BUNDLE / "observed_trace_points.csv",
        output_path=(
            "ratings-models/observed-vs-modelled/"
            "win-probability-by-standing/data/observed_trace_points.csv"
        ),
        media_type="text/csv",
    ),
    data(
        id="equelo_standing_win_probability",
        source_path=WIN_PROBABILITY_SITE_BUNDLE / "equelo_trace_points.csv",
        output_path=(
            "ratings-models/observed-vs-modelled/"
            "win-probability-by-standing/data/equelo_trace_points.csv"
        ),
        media_type="text/csv",
    ),
    data(
        id="win_probability_by_standing_metadata",
        source_path=WIN_PROBABILITY_SITE_BUNDLE / "metadata.json",
        output_path=(
            "ratings-models/observed-vs-modelled/"
            "win-probability-by-standing/data/metadata.json"
        ),
        media_type="application/json",
    ),
)


DIVISION_STABILITY_DATA = (
    data(
        id="division_stability_page_config",
        source_path=DIVISION_STABILITY_SITE_BUNDLE / "page.json",
        output_path=f"{DIVISION_STABILITY_SITE_OUTPUT_DIR}/page.json",
        media_type="application/json",
    ),
    data(
        id="division_stability_persistence",
        source_path=DIVISION_STABILITY_SITE_BUNDLE / "persistence.csv",
        output_path=f"{DIVISION_STABILITY_SITE_OUTPUT_DIR}/persistence.csv",
        media_type="text/csv",
    ),
    data(
        id="division_stability_metadata",
        source_path=DIVISION_STABILITY_SITE_BUNDLE / "metadata.json",
        output_path=f"{DIVISION_STABILITY_SITE_OUTPUT_DIR}/metadata.json",
        media_type="application/json",
    ),
)


FIRST_CHII_APPEARANCE_DATA = (
    data(
        id="first_chii_appearance_page_config",
        source_path=FIRST_CHII_APPEARANCE_SITE_BUNDLE / "page.json",
        output_path=f"{FIRST_CHII_APPEARANCE_SITE_OUTPUT_DIR}/page.json",
        media_type="application/json",
    ),
    data(
        id="first_chii_appearance_appearances",
        source_path=FIRST_CHII_APPEARANCE_SITE_BUNDLE / "appearances.csv",
        output_path=f"{FIRST_CHII_APPEARANCE_SITE_OUTPUT_DIR}/appearances.csv",
        media_type="text/csv",
    ),
    data(
        id="first_chii_appearance_metadata",
        source_path=FIRST_CHII_APPEARANCE_SITE_BUNDLE / "metadata.json",
        output_path=f"{FIRST_CHII_APPEARANCE_SITE_OUTPUT_DIR}/metadata.json",
        media_type="application/json",
    ),
)


def career_length_data_refs(outputs: CareerLengthOutputs) -> tuple[DataRef, ...]:
    return (
        data(
            id="career_length_page_config",
            source_path=outputs.page_json,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/page.json",
            media_type="application/json",
        ),
        data(
            id="career_length_distribution",
            source_path=outputs.distribution_csv,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/distribution.csv",
            media_type="text/csv",
        ),
        data(
            id="career_length_pmf",
            source_path=outputs.pmf_csv,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/pmf.csv",
            media_type="text/csv",
        ),
        data(
            id="career_length_cdf",
            source_path=outputs.cdf_csv,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/cdf.csv",
            media_type="text/csv",
        ),
        data(
            id="career_length_survival",
            source_path=outputs.survival_csv,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/survival.csv",
            media_type="text/csv",
        ),
        data(
            id="career_length_longest",
            source_path=outputs.longest_csv,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/longest.csv",
            media_type="text/csv",
        ),
        data(
            id="career_length_metadata",
            source_path=outputs.metadata_json,
            output_path=f"{CAREER_LENGTH_SITE_OUTPUT_DIR}/metadata.json",
            media_type="application/json",
        ),
    )


def rank_at_retirement_data_refs(
    outputs: RankAtRetirementOutputs,
) -> tuple[DataRef, ...]:
    return (
        data(
            id="rank_at_retirement_page_config",
            source_path=outputs.page_json,
            output_path=f"{RANK_AT_RETIREMENT_SITE_OUTPUT_DIR}/page.json",
            media_type="application/json",
        ),
        data(
            id="rank_at_retirement_distribution",
            source_path=outputs.distribution_csv,
            output_path=f"{RANK_AT_RETIREMENT_SITE_OUTPUT_DIR}/distribution.csv",
            media_type="text/csv",
        ),
        data(
            id="rank_at_retirement_metadata",
            source_path=outputs.metadata_json,
            output_path=f"{RANK_AT_RETIREMENT_SITE_OUTPUT_DIR}/metadata.json",
            media_type="application/json",
        ),
    )


def typical_equelo_values_data_refs(
    outputs: V5LandmarkOutputs,
) -> tuple[DataRef, ...]:
    return (
        data(
            id="typical_equelo_values_page_config",
            source_path=outputs.page_json,
            output_path=f"{TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR}/page.json",
            media_type="application/json",
        ),
        data(
            id="typical_equelo_values_csv",
            source_path=outputs.site_landmarks_csv,
            output_path=(
                f"{TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR}/"
                "typical_equelo_values.csv"
            ),
            media_type="text/csv",
        ),
        data(
            id="typical_equelo_values_metadata",
            source_path=outputs.site_metadata_json,
            output_path=f"{TYPICAL_EQUELO_VALUES_SITE_OUTPUT_DIR}/metadata.json",
            media_type="application/json",
        ),
    )

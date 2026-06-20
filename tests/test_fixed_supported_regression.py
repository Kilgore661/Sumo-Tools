import csv
import json

import pytest

from src.analysis.equelo.fixed_supported.policy import (
    CompletedInitialRating,
    collapse_chii,
    complete_initial_ratings,
    nearest_supported_chii,
)
from src.analysis.equelo.fixed_supported.api import (
    load_master_chii_initial_rating_map,
    master_chii_initial_rating_map_metadata_path,
    master_chii_initial_rating_map_path,
)
from src.analysis.equelo.fixed_supported.master_map import (
    rows_from_completed,
    write_master_chii_initial_rating_map,
    write_master_map_metadata,
)
from src.sumo_core.Chii import Chii


def test_support_collapse_removes_annotations() -> None:
    assert collapse_chii(Chii.from_str("Ms60eTD")) == Chii.from_str("Ms60e")


def test_support_collapse_maps_numbered_sanyaku_overflow_to_first_pair_west() -> None:
    assert collapse_chii(Chii.from_str("O2e")) == Chii.from_str("O1w")
    assert collapse_chii(Chii.from_str("O3w")) == Chii.from_str("O1w")
    assert collapse_chii(Chii.from_str("S2e")) == Chii.from_str("S1w")
    assert collapse_chii(Chii.from_str("K2w")) == Chii.from_str("K1w")


def test_support_collapse_keeps_ordinary_numbered_east_west_chii_distinct() -> None:
    assert collapse_chii(Chii.from_str("M12e")) == Chii.from_str("M12e")
    assert collapse_chii(Chii.from_str("M12w")) == Chii.from_str("M12w")
    assert collapse_chii(Chii.from_str("Jd73w")) == Chii.from_str("Jd73w")


def test_nearest_supported_chii_uses_nearest_ordinal() -> None:
    supported = [
        Chii.from_str("Jk45w"),
        Chii.from_str("Jk64w"),
        Chii.from_str("Jk76e"),
    ]

    assert nearest_supported_chii(Chii.from_str("Jk73w"), supported) == Chii.from_str(
        "Jk76e"
    )


def test_nearest_supported_chii_ties_choose_stronger_lower_ordinal() -> None:
    supported = [
        Chii.from_str("Jk64w"),
        Chii.from_str("Jk66w"),
    ]

    assert nearest_supported_chii(Chii.from_str("Jk65w"), supported) == Chii.from_str(
        "Jk64w"
    )


def test_complete_initial_ratings_keeps_direct_values_and_marks_sources() -> None:
    direct_chii = Chii.from_str("Jk64w")
    completed = complete_initial_ratings(
        required_chii=[direct_chii],
        source_ratings={direct_chii: 1510.25},
    )

    assert len(completed) == 1
    row = completed[0]
    assert row.chii == direct_chii
    assert row.initial_rating == 1510.25
    assert row.source_chii == direct_chii
    assert row.source_rating == 1510.25
    assert row.source_kind == "direct"


def test_complete_initial_ratings_completes_unsupported_chii_from_supported_source() -> None:
    source_chii = Chii.from_str("Jk64w")
    target_chii = Chii.from_str("Jk65e")

    completed = complete_initial_ratings(
        required_chii=[target_chii],
        source_ratings={source_chii: 1510.25},
    )

    assert len(completed) == 1
    row = completed[0]
    assert row.chii == target_chii
    assert row.initial_rating == 1510.25
    assert row.source_chii == source_chii
    assert row.source_rating == 1510.25
    assert row.source_kind == "nearest_supported"


def test_complete_initial_ratings_fails_loudly_without_supported_source() -> None:
    with pytest.raises(ValueError, match="empty supported rating map"):
        complete_initial_ratings(
            required_chii=[Chii.from_str("Jk65e")],
            source_ratings={},
        )


def test_master_map_outputs_keep_chii_map_and_audit_sources(tmp_path) -> None:
    direct = CompletedInitialRating(
        chii=Chii.from_str("Jk64w"),
        initial_rating=1510.25,
        source_chii=Chii.from_str("Jk64w"),
        source_rating=1510.25,
        source_kind="direct",
    )
    filled = CompletedInitialRating(
        chii=Chii.from_str("Jk65e"),
        initial_rating=1510.25,
        source_chii=Chii.from_str("Jk64w"),
        source_rating=1510.25,
        source_kind="nearest_supported",
    )

    map_path = write_master_chii_initial_rating_map(
        master_chii_initial_rating_map_path(tmp_path),
        rows_from_completed([direct, filled]),
    )
    metadata_path = write_master_map_metadata(
        master_chii_initial_rating_map_metadata_path(tmp_path),
        master_map_path=map_path,
        source_csv=tmp_path / "supported.csv",
        direct_count=1,
        nearest_supported_count=1,
        required_chii_count=2,
    )

    with map_path.open(newline="", encoding="utf-8") as f:
        initial_rows = list(csv.DictReader(f))
    assert [row["chii"] for row in initial_rows] == ["Jk64w", "Jk65e"]
    assert initial_rows[0]["source_kind"] == "direct"
    assert initial_rows[0]["source_chii"] == "Jk64w"
    assert initial_rows[1]["source_kind"] == "nearest_supported"
    assert initial_rows[1]["source_chii"] == "Jk64w"

    loaded_rows = load_master_chii_initial_rating_map(tmp_path)
    assert [row.chii for row in loaded_rows] == ["Jk64w", "Jk65e"]

    manifest = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert manifest["required_chii_count"] == 2
    assert manifest["direct_count"] == 1
    assert manifest["nearest_supported_count"] == 1
    assert manifest["policy"]["model_version"] == "fixed_supported"

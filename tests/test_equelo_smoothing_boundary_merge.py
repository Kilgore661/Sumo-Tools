import csv
import json
from pathlib import Path

import pytest

from src.analysis.equelo.smoothing.boundary_merge import (
    build_boundary_merge,
)
from src.analysis.equelo.smoothing.paired_merge import build_paired_merge


FIELDS = (
    "chii",
    "division",
    "appearance_count",
    "contextual_resolved_prior_mean",
)


def test_boundary_merge_blends_juryo_and_flattens_below_cutoff(
    tmp_path: Path,
) -> None:
    mj = tmp_path / "mj.csv"
    lower = tmp_path / "lower.csv"
    _write(mj, [
        ("M1e", "M", 2, 110.0),
        ("J1e", "J", 2, 100.0),
        ("J1w", "J", 1, 90.0),
    ])
    _write(lower, [
        ("J1e", "J", 2, 120.0),
        ("J1w", "J", 1, 100.0),
        ("Ms1e", "Ms", 2, 80.0),
        ("Jd100e", "Jd", 2, 60.0),
        ("Jd100w", "Jd", 2, 50.0),
        ("Jk1e", "Jk", 2, 40.0),
    ])
    outputs = build_boundary_merge(
        mj,
        lower,
        tmp_path / "merge.csv",
        cutoff_chii="Jd100e",
    )
    with outputs.data_csv.open(newline="", encoding="utf-8") as stream:
        rows = {row["chii"]: row for row in csv.DictReader(stream)}

    assert outputs.chart_html.exists()
    metadata = json.loads(outputs.metadata_json.read_text())
    assert metadata["construction"]["cutoff_chii"] == "Jd100e"
    assert metadata["construction"]["smoothing_applied"] is False
    assert metadata["outputs"]["row_count"] == 7
    assert metadata["inputs"]["mj_comparison_csv"]["sha256"]
    assert float(rows["J1e"]["pre_smoothing_rating"]) == 100.0
    assert float(rows["J1w"]["pre_smoothing_rating"]) == pytest.approx(
        83.3333333333
    )
    anchor = float(rows["Jd100e"]["pre_smoothing_rating"])
    assert float(rows["Jd100w"]["pre_smoothing_rating"]) == anchor
    assert float(rows["Jk1e"]["pre_smoothing_rating"]) == anchor
    assert rows["Jk1e"]["source"] == "flat tail from Jd100e"

    paired = build_paired_merge(
        outputs.data_csv,
        tmp_path / "paired.csv",
    )
    with paired.data_csv.open(newline="", encoding="utf-8") as stream:
        paired_rows = {row["rank_pair"]: row for row in csv.DictReader(stream)}
    assert paired.chart_html.exists()
    assert float(paired_rows["J1"]["pre_smoothing_rating"]) == pytest.approx(
        91.6666666667
    )
    assert paired_rows["Jk1"]["member_chii"] == "Jk1e"


def _write(path: Path, rows: list[tuple[str, str, int, float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for chii, division, count, rating in rows:
            writer.writerow({
                "chii": chii,
                "division": division,
                "appearance_count": count,
                "contextual_resolved_prior_mean": rating,
            })

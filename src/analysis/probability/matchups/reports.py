from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from src.analysis.probability.matchups.classes import EmpiricalMatchupResults


BOUT_CSV = "empirical_bouts.csv"
CHII_PAIR_CSV = "empirical_chii_pairs.csv"
SELECTED_CHII_CSV = "empirical_selected_chii_matchups.csv"
SIDELESS_CHII_PAIR_CSV = "empirical_sideless_chii_pairs.csv"
SIDELESS_DISTRIBUTION_CSV = "empirical_sideless_probability_distribution.csv"
METADATA_JSON = "metadata.json"


def write_empirical_outputs(
    results: EmpiricalMatchupResults,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "bout_csv": output_dir / BOUT_CSV,
        "chii_pair_csv": output_dir / CHII_PAIR_CSV,
        "selected_chii_csv": output_dir / SELECTED_CHII_CSV,
        "sideless_chii_pair_csv": output_dir / SIDELESS_CHII_PAIR_CSV,
        "sideless_distribution_csv": output_dir / SIDELESS_DISTRIBUTION_CSV,
        "metadata_json": output_dir / METADATA_JSON,
    }

    _write_dataclass_csv(results.bout_rows, paths["bout_csv"])
    _write_dataclass_csv(results.chii_pair_rows, paths["chii_pair_csv"])
    _write_dataclass_csv(results.selected_chii_rows, paths["selected_chii_csv"])
    _write_dataclass_csv(results.sideless_chii_pair_rows, paths["sideless_chii_pair_csv"])
    _write_dataclass_csv(results.sideless_distribution_rows, paths["sideless_distribution_csv"])
    _write_metadata(results, paths["metadata_json"])

    return paths


def _write_dataclass_csv(rows, output_path: Path) -> None:
    rows = tuple(rows)
    if not rows:
        raise ValueError(f"Cannot write empty CSV without fieldnames: {output_path}")

    with output_path.open("w", newline="", encoding="utf-8") as f:
        first = asdict(rows[0])
        writer = csv.DictWriter(f, fieldnames=tuple(first.keys()))
        writer.writeheader()
        writer.writerow(first)

        for row in rows[1:]:
            writer.writerow(asdict(row))


def _write_metadata(results: EmpiricalMatchupResults, output_path: Path) -> None:
    payload = {
        **asdict(results.metadata),
        "outputs": {
            "bout_csv": BOUT_CSV,
            "chii_pair_csv": CHII_PAIR_CSV,
            "selected_chii_csv": SELECTED_CHII_CSV,
            "sideless_chii_pair_csv": SIDELESS_CHII_PAIR_CSV,
            "sideless_distribution_csv": SIDELESS_DISTRIBUTION_CSV,
        },
        "notes": {
            "chii_policy": "annotation collapsed, side preserved",
            "sideless_chii_policy": "annotation collapsed, side removed",
            "sideless_distribution_policy": (
                "bout-weighted histogram of p_higher_or_equal_wins from "
                "empirical_sideless_chii_pairs.csv"
            ),
            "canonical_pair_policy": (
                "higher_or_equal_chii is chosen by lower/equal Chii.ordinal(); "
                "reverse-complement inference is intended only when same_chii is 0"
            ),
        },
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

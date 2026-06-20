"""Validation reports for Equelo rating-domain questions.

See api.py for the public rating-domain predicate.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from src.analysis.equelo.api import annotation_free_chii, no_rating
from src.analysis.equelo.fixed_supported.api import (
    EntrantInitialRatings,
    load_entrant_initial_ratings,
)
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


DEFAULT_HISTORY_ZIP = Path("files/output/Historys/1958_01 to 2025_11.zip")
DEFAULT_OUTPUT_PATH = Path("files/output/equelo/obscure_chii.csv")


@dataclass(frozen=True)
class ObscureChiiRow:
    chii: Chii
    ordinal: int
    first_seen: Date
    basho_count: int


def write_obscure_chii_report(
    *,
    history: History,
    entrant_initial_ratings: EntrantInitialRatings,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    """Write raw-History chii that lack fixed-supported chii initial ratings."""

    rows = obscure_chii_rows(
        history=history,
        entrant_initial_ratings=entrant_initial_ratings,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["chii", "ordinal", "first_seen", "basho_count"])
        for row in rows:
            writer.writerow(
                [
                    str(row.chii),
                    row.ordinal,
                    str(row.first_seen),
                    row.basho_count,
                ]
            )
    return output_path


def obscure_chii_rows(
    *,
    history: History,
    entrant_initial_ratings: EntrantInitialRatings,
) -> tuple[ObscureChiiRow, ...]:
    rated_ordinals = {int(ordinal) for ordinal in entrant_initial_ratings}
    stats: dict[Chii, tuple[Date, int]] = {}

    for date in sorted(history.keys()):
        basho = history(date)
        for chii in basho.banzuke.rikchii.values():
            public_chii = annotation_free_chii(chii)
            first_seen, basho_count = stats.get(public_chii, (date, 0))
            stats[public_chii] = (first_seen, basho_count + 1)

    rows = tuple(
        ObscureChiiRow(
            chii=chii,
            ordinal=chii.ordinal(),
            first_seen=first_seen,
            basho_count=basho_count,
        )
        for chii, (first_seen, basho_count) in sorted(
            stats.items(),
            key=lambda item: item[0].ordinal(),
        )
        if chii.ordinal() not in rated_ordinals
    )
    for row in rows:
        if not no_rating(row.chii):
            raise AssertionError(f"Obscure chii not covered by no_rating: {row.chii}")
    return rows


def load_history_from_zip(path: Path) -> History:
    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def main() -> None:
    history = load_history_from_zip(DEFAULT_HISTORY_ZIP)
    output_path = write_obscure_chii_report(
        history=history,
        entrant_initial_ratings=load_entrant_initial_ratings(),
        output_path=DEFAULT_OUTPUT_PATH,
    )
    print(output_path)


if __name__ == "__main__":
    main()

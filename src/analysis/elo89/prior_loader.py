"""Strict loader for the frozen paired Elo-89 entrant prior."""

from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path

from src.analysis.elo_model_selection.model import AdoptedPrior
from src.sumo_core.BasicEnums import Annotation, MSD, Side
from src.sumo_core.Chii import Chii


EXPECTED_COLUMNS = ("rank_pair", "ordinal", "rating")
SANYAKU_FAMILIES = frozenset({"Y", "O", "S", "K"})


def load_paired_prior(path: Path) -> AdoptedPrior:
    """Load an already-aggregated paired prior without transforming it."""

    resolved = path.resolve()
    with resolved.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != EXPECTED_COLUMNS:
            raise ValueError(
                "Paired Elo-89 prior must have exactly the columns "
                f"{EXPECTED_COLUMNS}; received {tuple(reader.fieldnames or ())}"
            )
        rows = tuple(reader)
    if not rows:
        raise ValueError(f"Paired Elo-89 prior contains no rows: {resolved}")

    ratings: dict[str, float] = {}
    previous_ordinal: int | None = None
    for line_number, row in enumerate(rows, start=2):
        pair = row["rank_pair"].strip()
        if not pair:
            raise ValueError(f"Blank rank_pair at {resolved}:{line_number}")
        if pair in ratings:
            raise ValueError(f"Duplicate paired-prior rank_pair {pair!r}: {resolved}")
        try:
            chii = Chii.from_str(pair)
            ordinal = int(row["ordinal"])
            rating = float(row["rating"])
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid paired prior row at {resolved}:{line_number}: {error}"
            ) from error
        if chii.side != Side.NONE or chii.ann != Annotation.EMPTY:
            raise ValueError(
                f"Paired prior rank must be side- and annotation-free: {pair!r}"
            )
        family = chii.level.as_abbreviation()
        if (
            isinstance(chii.level, MSD)
            and family in SANYAKU_FAMILIES
            and chii.number != 1
        ):
            raise ValueError(
                f"Paired sanyaku rank must use canonical slot 1: {pair!r}"
            )
        if ordinal != chii.ordinal():
            raise ValueError(
                f"Ordinal mismatch for {pair!r}: received {ordinal}, "
                f"expected {chii.ordinal()}"
            )
        if previous_ordinal is not None and ordinal <= previous_ordinal:
            raise ValueError(
                "Paired prior rows must be in strictly increasing ordinal order: "
                f"{pair!r} at {resolved}:{line_number}"
            )
        if not math.isfinite(rating):
            raise ValueError(f"Non-finite rating at {resolved}:{line_number}")
        ratings[pair] = rating
        previous_ordinal = ordinal

    return AdoptedPrior(
        source_path=str(resolved),
        sha256=hashlib.sha256(resolved.read_bytes()).hexdigest(),
        rating_by_pair=ratings,
        fallback_rating=min(ratings.values()),
    )

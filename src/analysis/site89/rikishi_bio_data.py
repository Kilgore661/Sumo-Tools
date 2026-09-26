"""Produce the latest-banzuke rikishi biographical snapshot."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.get_bios.api import BioStore
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.History import History

from .common import write_csv


def produce_rikishi_bio_data(
    *, history: History, bios: BioStore, output_root: Path
) -> Path:
    """Write one row for every rikishi on the latest represented banzuke."""

    latest_date = max(history)
    snapshot = history(latest_date).banzuke
    as_of = date(int(latest_date.year), int(latest_date.month), 1)
    names = FullShikonaStore.from_sources(history, bios=bios)
    rows = []

    for rid in sorted(snapshot.riks, key=lambda item: snapshot.rikchii[item].ordinal()):
        chii = snapshot.rikchii[rid]
        bio = bios.bios.get(rid)
        birth_date = None if bio is None else bio.birth_date
        height = None if bio is None else bio.height_cm
        weight = None if bio is None else bio.weight_kg
        rows.append(
            {
                "rikishi_id": int(rid),
                "shikona": names.full_shikona(rid),
                "division": division_id(chii.level),
                "chii": str(chii),
                "chii_ordinal": chii.ordinal(),
                "age": "" if birth_date is None else completed_years(birth_date.value, as_of),
                "height_cm": decimal_text(height),
                "weight_kg": decimal_text(weight),
                "bmi": bmi_text(height, weight),
                "snapshot_banzuke": str(latest_date),
            }
        )

    return write_csv(
        output_root / "rikishi_bio_data.csv",
        rows,
        fieldnames=(
            "rikishi_id",
            "shikona",
            "division",
            "chii",
            "chii_ordinal",
            "age",
            "height_cm",
            "weight_kg",
            "bmi",
            "snapshot_banzuke",
        ),
    )


def division_id(level: MSD | Division) -> str:
    if isinstance(level, MSD):
        return "makuuchi"
    return level.name.lower()


def completed_years(birth_date: date, as_of: date) -> int:
    return as_of.year - birth_date.year - (
        (as_of.month, as_of.day) < (birth_date.month, birth_date.day)
    )


def decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    return str(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def bmi_text(height_cm: Decimal | None, weight_kg: Decimal | None) -> str:
    if height_cm is None or weight_kg is None or height_cm <= 0:
        return ""
    height_m = height_cm / Decimal(100)
    return f"{weight_kg / (height_m * height_m):.1f}"

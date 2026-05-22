"""Typed access to parsed SumoDB rikishi bio data."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.History import Date

from .parser import OUTPUT_JSON


@dataclass(frozen=True, order=True)
class BirthDate:
    """
    A real calendar date used for birth dates.

    Some SumoDB bio records omit birth date, and at least one current record
    gives only a year. Those are not BirthDate values.
    """

    value: date

    @classmethod
    def parse(cls, value: str) -> "BirthDate | None":
        if re.fullmatch(r"\d{4}", value):
            return None

        if match := re.match(r"^([A-Za-z]+ \d{1,2}, \d{4})", value):
            return cls(datetime.strptime(match.group(1), "%B %d, %Y").date())

        year, month, day = value.split("/")
        return cls(date(int(year), int(month), int(day)))

    def __str__(self) -> str:
        return self.value.strftime("%Y/%m/%d")


@dataclass(frozen=True, order=True)
class BioBashoDate:
    """
    A year/month label from SumoDB bio pages.

    This is not the canonical 1958+ History Date. Bio pages contain pre-1958
    basho labels, and historical basho labels are not always odd months.
    """

    year: int
    # Intentionally not BasicPrimitives.Month: SumoDB bio pages include
    # pre-modern basho labels such as 1947/06, 1948/10, and 1949/10.
    month: int

    def __post_init__(self) -> None:
        date(self.year, self.month, 1)

    @classmethod
    def parse(cls, value: str) -> "BioBashoDate":
        year, month = value.split("/")
        return cls(int(year), int(month))

    @classmethod
    def from_history_date(cls, value: Date) -> "BioBashoDate":
        return cls(int(value.year), int(value.month))

    def __str__(self) -> str:
        return f"{self.year:04d}/{self.month:02d}"


@dataclass(frozen=True)
class ShikonaUse:
    first_basho: BioBashoDate
    shikona: Shikona


@dataclass(frozen=True)
class BodyMeasurement:
    basho: BioBashoDate
    value: Decimal


@dataclass(frozen=True)
class RikishiBio:
    rikid: RikId
    birth_date: BirthDate | None
    shusshin: str
    heya: tuple[str, ...]
    shikona_history: tuple[ShikonaUse, ...]
    hatsu_dohyo: BioBashoDate | None
    intai: BioBashoDate | None
    height_cm: Decimal | None
    weight_kg: Decimal | None
    height_history: tuple[BodyMeasurement, ...]
    weight_history: tuple[BodyMeasurement, ...]

    def latest_shikona(self) -> Shikona:
        return self.shikona_history[-1].shikona

    def shikona_at(self, basho_date: Date) -> Shikona:
        target = BioBashoDate.from_history_date(basho_date)
        return [
            use.shikona
            for use in self.shikona_history
            if use.first_basho <= target
        ][-1]


@dataclass(frozen=True)
class BioStore:
    bios: Mapping[RikId, RikishiBio]

    def __getitem__(self, rikid: RikId) -> RikishiBio:
        return self.bios[rikid]

    def latest_shikona(self, rikid: RikId) -> Shikona:
        return self[rikid].latest_shikona()

    def shikona_at(self, rikid: RikId, basho_date: Date) -> Shikona:
        return self[rikid].shikona_at(basho_date)


def load_bio_store(path: Path = OUTPUT_JSON) -> BioStore:
    raw = json.loads(path.read_text(encoding="utf-8"))
    bios = {
        RikId(int(rikid)): _parse_bio_record(RikId(int(rikid)), record)
        for rikid, record in raw.items()
    }
    return BioStore(MappingProxyType(bios))


def _parse_bio_record(rikid: RikId, record: Mapping[str, object]) -> RikishiBio:
    birth_date = record["Birth Date"]
    intai = record["Intai"]
    height = record["Height"]
    weight = record["Weight"]

    return RikishiBio(
        rikid=rikid,
        birth_date=BirthDate.parse(birth_date) if birth_date is not None else None,
        shusshin=record["Shusshin"],
        heya=tuple(record["Heya"]),
        shikona_history=tuple(
            ShikonaUse(BioBashoDate.parse(first_basho), Shikona(shikona))
            for first_basho, shikona in record["Shikona"].items()
        ),
        hatsu_dohyo=_parse_optional_bio_basho_date(record["Hatsu Dohyo"]),
        intai=_parse_optional_bio_basho_date(intai),
        height_cm=Decimal(height) if height is not None else None,
        weight_kg=Decimal(weight) if weight is not None else None,
        height_history=_parse_measurements(record["Height_by_Date"]),
        weight_history=_parse_measurements(record["Weight_by_Date"]),
    )


def _parse_measurements(raw: object) -> tuple[BodyMeasurement, ...]:
    if raw is None:
        return ()

    return tuple(
        BodyMeasurement(BioBashoDate.parse(basho), Decimal(value))
        for basho, value in raw.items()
    )


def _parse_optional_bio_basho_date(raw: object) -> BioBashoDate | None:
    if raw is None or raw == "unknown":
        return None

    return BioBashoDate.parse(raw)

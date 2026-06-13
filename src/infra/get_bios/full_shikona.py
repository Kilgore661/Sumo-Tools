"""Resolve catalogue-wide full shikona labels for public display."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.get_bios.api import BioStore, load_bio_store
from src.infra.get_bios.make_public_shikona import (
    make_history_shikona_by_rikid,
    make_latest_history_date_by_rikid,
    make_latest_holder_by_history_shikona,
)
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.History import History


@dataclass(frozen=True)
class FullShikona:
    """A rikishi's catalogue-aware public shikona label."""

    rikid: RikId
    history_shikona: Shikona
    is_latest_holder: bool
    intai_year: int | None
    intai_month: int | None
    needs_intai_year: bool
    needs_intai_month: bool

    def history_label(self) -> str:
        """Return the bare History shikona."""
        return str(self.history_shikona)

    def year_label(self) -> str:
        """Return the year-level Intai disambiguation label."""
        return f"{self.history_label()} ({self.intai_year:04d})"

    def month_label(self) -> str:
        """Return the month-level Intai disambiguation label."""
        return f"{self.history_label()} ({self.intai_year:04d}/{self.intai_month:02d})"

    def full_label(self) -> str:
        """Return the shortest catalogue-disambiguating public label."""
        if self.needs_intai_month:
            return self.month_label()
        if self.needs_intai_year:
            return self.year_label()
        return self.history_label()


@dataclass(frozen=True)
class FullShikonaCatalogue:
    """Full-shikona records keyed by rikishi identity."""

    records_by_rikid: Mapping[RikId, FullShikona]

    def __getitem__(self, rikid: RikId) -> FullShikona:
        return self.records_by_rikid[rikid]

    def get_full_shikona(self, rikid: RikId) -> str:
        """Return the full shikona label for a rikishi."""
        return self[rikid].full_label()

    def full_shikona_by_rikid(self) -> dict[RikId, str]:
        """Return full shikona labels for all represented rikishi."""
        return {
            rikid: record.full_label()
            for rikid, record in self.records_by_rikid.items()
        }

    def to_store(self) -> FullShikonaStore:
        """Return the public-label store represented by this catalogue."""
        return FullShikonaStore(MappingProxyType(self.full_shikona_by_rikid()))


def make_full_shikona_catalogue(
    history: History,
    bios: BioStore,
) -> FullShikonaCatalogue:
    """Build full shikona records from the publication History and BioStore."""
    history_shikona_by_rikid = make_history_shikona_by_rikid(history)
    latest_holder_by_history_shikona = make_latest_holder_by_history_shikona(history)
    rikids_by_history_shikona = make_rikids_by_history_shikona(history_shikona_by_rikid)

    records_by_rikid: dict[RikId, FullShikona] = {}

    for history_shikona, rikids in rikids_by_history_shikona.items():
        latest_holder = latest_holder_by_history_shikona[history_shikona]
        earlier_holders = tuple(rikid for rikid in rikids if rikid != latest_holder)
        intai_year_counts = Counter(
            intai_year(bios, rikid)
            for rikid in earlier_holders
        )

        for rikid in rikids:
            is_latest_holder = rikid == latest_holder
            needs_intai_year = len(rikids) > 1 and not is_latest_holder
            year = intai_year(bios, rikid) if needs_intai_year else None
            month = intai_month(bios, rikid) if needs_intai_year else None
            records_by_rikid[rikid] = FullShikona(
                rikid=rikid,
                history_shikona=history_shikona,
                is_latest_holder=is_latest_holder,
                intai_year=year,
                intai_month=month,
                needs_intai_year=needs_intai_year,
                needs_intai_month=needs_intai_year and intai_year_counts[year] > 1,
            )

    return FullShikonaCatalogue(MappingProxyType(records_by_rikid))


def make_full_shikona(
    history: History,
    bios: BioStore | None = None,
) -> dict[RikId, str]:
    """Return full shikona labels for all rikishi represented in History."""
    catalogue = make_full_shikona_catalogue(
        history,
        bios if bios is not None else load_bio_store(),
    )
    return catalogue.full_shikona_by_rikid()


def get_full_shikona(
    rikid: RikId,
    catalogue: FullShikonaCatalogue,
) -> str:
    """Return the full shikona label for one rikishi from a catalogue."""
    return catalogue.get_full_shikona(rikid)


def make_rikids_by_history_shikona(
    history_shikona_by_rikid: Mapping[RikId, Shikona],
) -> dict[Shikona, tuple[RikId, ...]]:
    """Group represented rikishi by latest History shikona."""
    grouped: dict[Shikona, list[RikId]] = defaultdict(list)
    for rikid, history_shikona in history_shikona_by_rikid.items():
        grouped[history_shikona].append(rikid)
    return {
        history_shikona: tuple(sorted(rikids, key=int))
        for history_shikona, rikids in grouped.items()
    }


def intai_year(bios: BioStore, rikid: RikId) -> int | None:
    """Return the Intai year required for earlier-holder disambiguation."""
    intai = bios[rikid].intai
    return intai.year if intai is not None else None


def intai_month(bios: BioStore, rikid: RikId) -> int | None:
    """Return the Intai month required for earlier-holder disambiguation."""
    intai = bios[rikid].intai
    return intai.month if intai is not None else None


if __name__ == "__main__":
    # Main code added purely for testing
    HAKUHO_SHO = RikId(1200)
    EARLIER_HAKUHO = RikId(790)
    HISTORY_ZIP = Path("files") / "output" / "Historys" / "1958_01 to 2026_11.zip"

    try:
        history = get_history()
    except SystemExit:
        history = load_history_with_annotations(str(HISTORY_ZIP.with_suffix("")))

    bios = load_bio_store()
    catalogue = make_full_shikona_catalogue(history, bios)
    history_shikona_by_rikid = make_history_shikona_by_rikid(history)
    latest_history_date_by_rikid = make_latest_history_date_by_rikid(history)
    hakuho_rikids = tuple(
        sorted(
            rikid
            for rikid, history_shikona in history_shikona_by_rikid.items()
            if str(history_shikona) == "Abe"
        )
    )

    print( get_full_shikona(HAKUHO_SHO, catalogue) == "Abe" )
    print( get_full_shikona(EARLIER_HAKUHO, catalogue) == "Abe (2002)" )

    print("Hakuho bin")
    print("==========")
    print("rikid | latest_history_date | intai | latest_holder | full_shikona")
    for rikid in hakuho_rikids:
        record = catalogue[rikid]
        bio = bios[rikid]
        latest_holder = "yes" if record.is_latest_holder else "no"
        print(
            f"{rikid} | "
            f"{latest_history_date_by_rikid[rikid]} | "
            f"{bio.intai} | "
            f"{latest_holder} | "
            f"{record.full_label()}"
        )

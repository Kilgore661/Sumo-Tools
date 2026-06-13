"""In-memory access to catalogue-wide public shikona labels."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Iterable, Mapping

from src.infra.get_bios.api import BioBashoDate, BioStore, load_bio_store
from src.infra.get_bios.make_public_shikona import (
    make_history_shikona_by_rikid,
    make_latest_history_date_by_rikid,
)
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History


DEFAULT_SEARCH_CSV = (
    Path("files")
    / "output"
    / "infra"
    / "tracker"
    / "scraper"
    / "rikishi_aspx_parser"
    / "rikishi_by_shikona.csv"
)
DEFAULT_CACHE_JSON = (
    Path("files")
    / "output"
    / "infra"
    / "get_bios"
    / "FullShikonaStore"
    / "full_shikona_by_rikid.json"
)
SEARCH_INTAI_PAT = re.compile(r"^\d{4}/\d{2}$")


@dataclass(frozen=True)
class FullShikonaStore:
    """Catalogue-wide public shikona labels keyed by rikishi identity."""

    labels_by_rikid: Mapping[RikId, str]

    @classmethod
    def from_json(cls, path: Path = DEFAULT_CACHE_JSON) -> "FullShikonaStore":
        """Load a persisted full-shikona cache."""
        raw = json.loads(path.read_text(encoding="utf-8"))
        labels = {
            RikId(int(rikid)): label
            for rikid, label in raw.items()
        }
        return cls(MappingProxyType(labels))

    @classmethod
    def from_sources(
        cls,
        history: History,
        *,
        bios: BioStore | None = None,
        search_csv: Path = DEFAULT_SEARCH_CSV,
    ) -> "FullShikonaStore":
        """Build full shikona labels from History, BioStore, and search CSV."""
        resolved_bios = bios if bios is not None else load_bio_store()
        search_intai_by_rikid = load_search_intai_by_rikid(search_csv)
        history_shikona_by_rikid = make_history_shikona_by_rikid(history)
        latest_history_date_by_rikid = make_latest_history_date_by_rikid(history)
        represented_rikids = sorted(history_shikona_by_rikid, key=int)
        owner_labels = {
            str(history_shikona)
            for history_shikona in history_shikona_by_rikid.values()
        }

        maximal_shikona_by_rikid = {
            rikid: str(resolved_bios[rikid].latest_shikona())
            for rikid in represented_rikids
        }
        rikids_by_history_shikona: dict[str, list[RikId]] = defaultdict(list)
        for rikid, history_shikona in history_shikona_by_rikid.items():
            rikids_by_history_shikona[str(history_shikona)].append(rikid)

        labels_by_rikid: dict[RikId, str] = {}

        for history_shikona, rikids in rikids_by_history_shikona.items():
            ordered_rikids = tuple(sorted(rikids, key=int))
            latest_holder = max(
                ordered_rikids,
                key=lambda rikid: (latest_history_date_by_rikid[rikid], int(rikid)),
            )
            earlier_holders = tuple(
                rikid for rikid in ordered_rikids if rikid != latest_holder
            )
            candidate_by_rikid = {
                rikid: candidate_label(
                    history_shikona=history_shikona,
                    maximal_shikona=maximal_shikona_by_rikid[rikid],
                )
                for rikid in earlier_holders
            }
            candidate_counts = Counter(candidate_by_rikid.values())
            date_needed = {
                rikid
                for rikid, candidate in candidate_by_rikid.items()
                if (
                    candidate == history_shikona
                    or candidate in owner_labels
                    or candidate_counts[candidate] > 1
                )
            }
            intai_by_rikid = {
                rikid: intai_for_rikid(
                    rikid,
                    bios=resolved_bios,
                    search_intai_by_rikid=search_intai_by_rikid,
                )
                for rikid in date_needed
            }
            date_needed_by_candidate: dict[str, list[RikId]] = defaultdict(list)
            for rikid in date_needed:
                date_needed_by_candidate[candidate_by_rikid[rikid]].append(rikid)

            for rikid in ordered_rikids:
                if rikid == latest_holder:
                    labels_by_rikid[rikid] = history_shikona
                    continue

                if rikid not in date_needed:
                    labels_by_rikid[rikid] = candidate_by_rikid[rikid]

            for candidate, candidate_rikids in date_needed_by_candidate.items():
                intai_year_counts = Counter(
                    intai_by_rikid[rikid].year
                    for rikid in candidate_rikids
                )
                for rikid in candidate_rikids:
                    intai = intai_by_rikid[rikid]
                    if intai_year_counts[intai.year] > 1:
                        labels_by_rikid[rikid] = (
                            f"{candidate} ({intai.year:04d}/{intai.month:02d})"
                        )
                    else:
                        labels_by_rikid[rikid] = f"{candidate} ({intai.year:04d})"

        store = cls(MappingProxyType(labels_by_rikid))
        store.assert_complete_for(represented_rikids)
        store.assert_unique_labels()
        return store

    def __getitem__(self, rikid: RikId) -> str:
        return self.full_shikona(rikid)

    def full_shikona(self, rikid: RikId) -> str:
        """Return the public full shikona for one rikishi."""
        return self.labels_by_rikid[rikid]

    def as_dict(self) -> dict[RikId, str]:
        """Return a caller-owned copy of all labels."""
        return dict(self.labels_by_rikid)

    def assert_complete_for(self, rikids: Iterable[RikId]) -> None:
        """Fail if any represented rikishi has no full-shikona label."""
        missing = sorted(
            (rikid for rikid in rikids if rikid not in self.labels_by_rikid),
            key=int,
        )
        if missing:
            raise ValueError(
                "FullShikonaStore is missing labels for rikids: "
                + ", ".join(str(rikid) for rikid in missing)
            )

    def duplicate_labels(self) -> dict[str, tuple[RikId, ...]]:
        """Return labels that identify more than one rikishi."""
        rikids_by_label: dict[str, list[RikId]] = defaultdict(list)
        for rikid, label in self.labels_by_rikid.items():
            rikids_by_label[label].append(rikid)

        return {
            label: tuple(sorted(rikids, key=int))
            for label, rikids in rikids_by_label.items()
            if len(rikids) > 1
        }

    def assert_unique_labels(self) -> None:
        """Fail if any full-shikona label is not unique."""
        duplicates = self.duplicate_labels()
        if duplicates:
            lines = [
                f"{label}: {', '.join(str(rikid) for rikid in rikids)}"
                for label, rikids in sorted(duplicates.items())
            ]
            raise ValueError(
                "FullShikonaStore has duplicate labels:\n" + "\n".join(lines)
            )

    def write_json(self, path: Path = DEFAULT_CACHE_JSON) -> None:
        """Persist this store as a small RikId-to-label JSON cache."""
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = {
            str(int(rikid)): label
            for rikid, label in sorted(self.labels_by_rikid.items(), key=lambda item: int(item[0]))
        }
        path.write_text(
            json.dumps(raw, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def load_search_intai_by_rikid(path: Path) -> Mapping[RikId, BioBashoDate]:
    """Load Intai dates supplied by Rikishi.aspx search-result rows."""
    intais_by_rikid: dict[RikId, set[BioBashoDate]] = defaultdict(set)

    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            raw_intai = row["intai"]
            if not raw_intai:
                continue
            if SEARCH_INTAI_PAT.fullmatch(raw_intai) is None:
                continue
            rikid = RikId(int(row["rikid"]))
            intais_by_rikid[rikid].add(BioBashoDate.parse(raw_intai))

    resolved: dict[RikId, BioBashoDate] = {}
    conflicting: dict[RikId, tuple[BioBashoDate, ...]] = {}
    for rikid, intais in intais_by_rikid.items():
        if len(intais) == 1:
            resolved[rikid] = next(iter(intais))
        else:
            conflicting[rikid] = tuple(sorted(intais))

    if conflicting:
        lines = [
            f"{rikid}: {', '.join(str(intai) for intai in intais)}"
            for rikid, intais in sorted(conflicting.items(), key=lambda item: int(item[0]))
        ]
        raise ValueError(
            "Rikishi.aspx search CSV has conflicting Intai values:\n"
            + "\n".join(lines)
        )

    return MappingProxyType(resolved)


def intai_for_rikid(
    rikid: RikId,
    *,
    bios: BioStore,
    search_intai_by_rikid: Mapping[RikId, BioBashoDate],
) -> BioBashoDate:
    """Return the Intai date needed to disambiguate an earlier holder."""
    bio_intai = bios[rikid].intai
    if bio_intai is not None:
        return bio_intai

    search_intai = search_intai_by_rikid.get(rikid)
    if search_intai is not None:
        return search_intai

    raise ValueError(f"Rikid {rikid} needs full-shikona Intai, but none is known.")


def candidate_label(*, history_shikona: str, maximal_shikona: str) -> str:
    """Return an earlier holder's first-choice disambiguating label."""
    if maximal_shikona != history_shikona:
        return maximal_shikona
    return history_shikona

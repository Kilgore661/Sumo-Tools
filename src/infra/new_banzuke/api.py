"""Persist and load the latest producer-safe New Banzuke artifact."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.infra.parser.parser2 import get_banzuke
from src.sumo_core.BasicPrimitives import Month, RikId, Riks, Shikona, Year
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


CURRENT_STANDINGS_ROOT = Path("files") / "output" / "current standings"
NEW_BANZUKE_ROOT = Path("files") / "output" / "infra" / "new_banzuke"
NEW_BANZUKE_JSON = NEW_BANZUKE_ROOT / "new_banzuke.json"
CURRENT_STANDINGS_FILE_RE = re.compile(r"^(\d{4}) (\d{2})\.html$")
BASE_URL = "https://sumodb.sumogames.de"


@dataclass(frozen=True)
class NewBanzukeEntry:
    """One rikishi slot in the New Banzuke artifact."""

    rikishi_id: RikId
    shikona: Shikona
    chii_ordinal: int
    chii: str

    @classmethod
    def from_banzuke(cls, banzuke: Banzuke, rikishi_id: RikId) -> "NewBanzukeEntry":
        chii = banzuke.rikchii[rikishi_id]
        return cls(
            rikishi_id=rikishi_id,
            shikona=banzuke.rikshik[rikishi_id],
            chii_ordinal=chii.ordinal(),
            chii=str(chii),
        )

    def to_json_record(self) -> dict[str, object]:
        return {
            "rikishi_id": int(self.rikishi_id),
            "shikona": str(self.shikona),
            "chii_ordinal": self.chii_ordinal,
            "chii": self.chii,
        }

    @classmethod
    def from_json_record(cls, record: dict[str, object]) -> "NewBanzukeEntry":
        chii = Chii.from_ordinal(int(record["chii_ordinal"]))
        return cls(
            rikishi_id=RikId(int(record["rikishi_id"])),
            shikona=Shikona(str(record["shikona"])),
            chii_ordinal=chii.ordinal(),
            chii=str(chii),
        )


@dataclass(frozen=True)
class NewBanzuke:
    """Latest parsed Banzuke.aspx publication, separate from History."""

    date: Date
    source_path: Path
    source_url: str
    generated_at: str
    entries: tuple[NewBanzukeEntry, ...]

    @classmethod
    def from_banzuke(
        cls,
        *,
        date: Date,
        banzuke: Banzuke,
        source_path: Path,
        generated_at: str,
    ) -> "NewBanzuke":
        entries = tuple(
            NewBanzukeEntry.from_banzuke(banzuke, rikishi_id)
            for rikishi_id in sorted(
                banzuke.riks,
                key=lambda rid: banzuke.rikchii[rid],
            )
        )
        return cls(
            date=date,
            source_path=source_path,
            source_url=source_url_for(date),
            generated_at=generated_at,
            entries=entries,
        )

    def to_banzuke(self) -> Banzuke:
        return Banzuke(
            riks=Riks(entry.rikishi_id for entry in self.entries),
            rikchii=RikChii(
                {
                    entry.rikishi_id: Chii.from_ordinal(entry.chii_ordinal)
                    for entry in self.entries
                }
            ),
            rikshik=RikShikona(
                {
                    entry.rikishi_id: entry.shikona
                    for entry in self.entries
                }
            ),
        )

    def to_json_payload(self) -> dict[str, object]:
        return {
            "date": str(self.date),
            "source_path": str(self.source_path),
            "source_url": self.source_url,
            "generated_at": self.generated_at,
            "entries": [
                entry.to_json_record()
                for entry in self.entries
            ],
        }

    @classmethod
    def from_json_payload(cls, payload: dict[str, object]) -> "NewBanzuke":
        return cls(
            date=parse_date(str(payload["date"])),
            source_path=Path(str(payload["source_path"])),
            source_url=str(payload["source_url"]),
            generated_at=str(payload["generated_at"]),
            entries=tuple(
                NewBanzukeEntry.from_json_record(record)
                for record in payload["entries"]
            ),
        )


@dataclass(frozen=True)
class NewBanzukeOutput:
    """Names the generated New Banzuke artifact."""

    date: Date
    path: Path


def latest_available_banzuke_source(
    source_root: Path = CURRENT_STANDINGS_ROOT,
) -> tuple[Date, Path]:
    """Return the latest raw Banzuke.aspx source path."""
    candidates = sorted(
        (
            Date(Year(int(match.group(1))), Month(int(match.group(2)))),
            path,
        )
        for path in source_root.glob("*.html")
        if (match := CURRENT_STANDINGS_FILE_RE.fullmatch(path.name)) is not None
    )

    if not candidates:
        raise FileNotFoundError(f"No banzuke source files found in {source_root}")

    return candidates[-1]


def build_new_banzuke(
    *,
    date: Date,
    source_path: Path,
    generated_at: str | None = None,
) -> NewBanzuke:
    """Parse one raw banzuke source into the New Banzuke model."""
    banzuke = get_banzuke(date)
    if banzuke is None:
        raise ValueError(f"No banzuke parsed for {date}")

    return NewBanzuke.from_banzuke(
        date=date,
        banzuke=banzuke,
        source_path=source_path,
        generated_at=(
            generated_at
            if generated_at is not None
            else datetime.now().isoformat(timespec="seconds")
        ),
    )


def write_new_banzuke(
    new_banzuke: NewBanzuke,
    path: Path = NEW_BANZUKE_JSON,
) -> NewBanzukeOutput:
    """Write the New Banzuke JSON artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(new_banzuke.to_json_payload(), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return NewBanzukeOutput(date=new_banzuke.date, path=path)


def load_new_banzuke(path: Path = NEW_BANZUKE_JSON) -> NewBanzuke:
    """Load the persisted New Banzuke artifact."""
    return NewBanzuke.from_json_payload(json.loads(path.read_text(encoding="utf-8")))


def produce_new_banzuke(
    *,
    source_root: Path = CURRENT_STANDINGS_ROOT,
    output_path: Path = NEW_BANZUKE_JSON,
) -> NewBanzukeOutput:
    """Build and persist the latest New Banzuke artifact."""
    date, source_path = latest_available_banzuke_source(source_root)
    return write_new_banzuke(
        build_new_banzuke(date=date, source_path=source_path),
        output_path,
    )


def source_url_for(date: Date) -> str:
    """Return the SumoDB URL for a Banzuke.aspx source date."""
    return (
        f"{BASE_URL}/Banzuke.aspx?"
        f"b={int(date.year)}{int(date.month):02d}&heya=-1&shusshin=-1"
    )


def parse_date(value: str) -> Date:
    """Parse a New Banzuke date key formatted as YYYY/MM."""
    year, month = value.split("/")
    return Date(Year(int(year)), Month(int(month)))

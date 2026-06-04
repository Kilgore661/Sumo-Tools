# src/infra/get_bios/shikona_normalisation_probe_model.py

"""
Shared model and parsing helpers for the shikona normalisation probe.

This is prototype support code for ``shikona_normalisation_probe.py``.  It is
not the production normalisation API.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BioRecord:
    rikid: str
    latest_shikona: str | None
    latest_shikona_first_used: str | None
    hatsu_dohyo: str | None
    intai: str | None

    @property
    def intai_year(self) -> str | None:
        if self.intai is None:
            return None
        if len(self.intai) < 4 or not self.intai[:4].isdigit():
            return None
        return self.intai[:4]

    @property
    def intai_month_label(self) -> str | None:
        if self.intai is None or len(self.intai) < 7:
            return None
        year, separator, month = self.intai[:4], self.intai[4], self.intai[5:7]
        if not year.isdigit() or separator != "/" or not month.isdigit():
            return None
        return f"{year}/{month}"

    @property
    def is_active(self) -> bool:
        return self.intai is None


@dataclass(frozen=True)
class LabelRow:
    rikid: str
    latest_shikona: str
    latest_shikona_first_used: str
    hatsu_dohyo: str
    intai: str
    role: str
    label_kind: str
    proposed_label: str


@dataclass(frozen=True)
class Finding:
    kind: str
    latest_shikona: str
    rikid: str
    detail: str


@dataclass(frozen=True)
class FixResult:
    intai: str | None
    findings: tuple[Finding, ...]


def optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"expected string or null, got {type(value).__name__}")
    if value == "" or value == "unknown":
        return None
    return value


def normalise_rikid(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError(f"rikid must be a string, got {type(value).__name__}")
    if not value.isdigit():
        raise ValueError(f"rikid must contain only digits: {value!r}")
    return str(int(value))


def public_shikona_key(value: str | None, *, full_shikona: bool = False) -> str | None:
    """
    Return the prototype public shikona key used for collision probing.

    By default this probe groups on the first token because the public-label
    problem being tested may be the leading shikona element, not the full parsed
    string. Pass ``full_shikona=True`` to probe using the complete normalised
    latest shikona string instead.
    """
    if value is None:
        return None

    parts = value.split()
    if not parts:
        return None

    if full_shikona:
        return " ".join(parts)

    return parts[0]


def latest_shikona_from_history(raw: object) -> tuple[str | None, str | None]:
    if raw is None:
        return None, None
    if not isinstance(raw, dict):
        raise TypeError(f"Shikona must be an object or null, got {type(raw).__name__}")
    if not raw:
        return None, None

    latest_date = sorted(raw)[-1]
    latest = raw[latest_date]

    if not isinstance(latest, str):
        raise TypeError(
            f"latest shikona value at {latest_date!r} must be a string, "
            f"got {type(latest).__name__}"
        )

    return latest, latest_date


def parse_bio_records(raw: object, *, full_shikona: bool = False) -> list[BioRecord]:
    if not isinstance(raw, dict):
        raise TypeError(f"top-level JSON must be an object, got {type(raw).__name__}")

    records = []

    for rikid, record in sorted(raw.items()):
        if not isinstance(record, dict):
            raise TypeError(f"record for {rikid} must be an object")

        latest_shikona, latest_shikona_first_used = latest_shikona_from_history(
            record["Shikona"]
        )

        records.append(
            BioRecord(
                rikid=normalise_rikid(rikid),
                latest_shikona=public_shikona_key(
                    latest_shikona,
                    full_shikona=full_shikona,
                ),
                latest_shikona_first_used=latest_shikona_first_used,
                hatsu_dohyo=optional_text(record["Hatsu Dohyo"]),
                intai=optional_text(record["Intai"]),
            )
        )

    return records


def empty_if_none(value: str | None) -> str:
    return "" if value is None else value

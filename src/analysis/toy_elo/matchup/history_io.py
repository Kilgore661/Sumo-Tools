from __future__ import annotations

from pathlib import Path

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date, History


def parse_date(value: str) -> Date:
    year_text, month_text = value.replace("-", "/").split("/")
    return Date(Year(int(year_text)), Month(int(month_text)))


def date_token(date: Date) -> str:
    return f"{int(date.year):04d}_{int(date.month):02d}"


def load_history(history_zip: Path | None) -> History:
    if history_zip is None:
        return get_history()
    zipless = history_zip.with_suffix("") if history_zip.suffix == ".zip" else history_zip
    return load_history_with_annotations(str(zipless))


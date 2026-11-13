from __future__ import annotations

from datetime import date

from src.infra.parser.basho_calendar import (
    basho_date_coverage,
    parse_daily_calendar_date,
)
from src.infra.persistence.serialiser import SumoSerialiser
from src.sumo_core.BasicPrimitives import Torikumi
from src.sumo_core.History import Date
from src.sumo_core.Summary import DailyResults, ResultLookup


def test_extracts_and_reconstructs_exact_basho_start(tmp_path) -> None:
    directory = tmp_path / "1965 07"
    directory.mkdir()
    (directory / "02.html").write_text(
        "<h1>Nagoya 1965, Day 2</h1><h2>June 28, 1965</h2>",
        encoding="utf-8",
    )
    (directory / "05.html").write_text(
        "<h1>Nagoya 1965, Day 5</h1><h2>July 1, 1965</h2>",
        encoding="utf-8",
    )

    coverage = basho_date_coverage(Date.from_ints(1965, 7), results_root=tmp_path)

    assert coverage.start_date == date(1965, 6, 27)
    assert coverage.source == "reconstructed"
    assert coverage.daily_dates == 2
    assert coverage.consistent


def test_daily_results_calendar_date_round_trips_and_legacy_data_loads() -> None:
    daily = DailyResults(Torikumi(), ResultLookup(), date(1965, 6, 27))
    restored = SumoSerialiser._deserialise_daily_results(
        SumoSerialiser._serialise_daily_results(daily)
    )
    assert restored.calendar_date == date(1965, 6, 27)

    legacy = {"torikumi": [], "results_lookup": {}}
    assert SumoSerialiser._deserialise_daily_results(legacy).calendar_date is None


def test_parse_daily_calendar_date() -> None:
    assert parse_daily_calendar_date(
        "<h1>Nagoya 1965, Day 1</h1><h2>June 27, 1965</h2>"
    ) == (1, date(1965, 6, 27))

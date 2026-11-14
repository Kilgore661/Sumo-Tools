from __future__ import annotations

import csv
from datetime import date
from types import MappingProxyType

import pytest

from src.analysis.ages.average_age_by_division import (
    DIVISION_ORDER,
    average_age_by_division,
    exact_age_years,
    exact_basho_start_dates,
    write_average_age_by_division_csv,
)
from src.infra.get_bios.api import BioStore, BirthDate, RikishiBio
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_continuous_age_and_leap_day_anniversary() -> None:
    assert exact_age_years(date(2000, 6, 15), date(2020, 6, 15)) == 20
    assert exact_age_years(date(2000, 6, 15), date(2020, 6, 14)) < 20
    assert exact_age_years(date(2000, 6, 15), date(2020, 6, 16)) > 20
    assert exact_age_years(date(2000, 2, 29), date(2021, 2, 28)) < 21
    assert exact_age_years(date(2000, 2, 29), date(2021, 3, 1)) == 21


def test_statistics_divisions_missingness_order_and_csv(tmp_path) -> None:
    basho = Date.from_ints(2020, 1)
    ranks = {
        1: "Y1e", 2: "O1e", 3: "S1e", 4: "K1e", 5: "M1e",
        6: "J1e", 7: "Ms1e", 8: "Sd1e", 9: "Jd1e", 10: "Jk1e",
        11: "Jk2e", 12: "Jk3e",
    }
    history = History({basho: _state(ranks)})
    bios = BioStore(MappingProxyType({
        RikId(i): _bio(i, date(1980 + i, 1, 1)) for i in range(1, 11)
    } | {
        RikId(11): _bio(11, None),
    }))

    rows = average_age_by_division(history, bios, {basho: date(2020, 1, 12)})

    assert [row.division for row in rows] == list(DIVISION_ORDER)
    makuuchi = rows[0]
    expected = [exact_age_years(date(1980 + i, 1, 1), date(2020, 1, 12)) for i in range(1, 6)]
    assert makuuchi.banzuke_rikishi == 5
    assert makuuchi.mean_age_years == pytest.approx(sum(expected) / len(expected))
    assert makuuchi.min_age_years == min(expected)
    assert makuuchi.max_age_years == max(expected)
    jonokuchi = rows[-1]
    assert jonokuchi.exact_birth_date == 1
    assert jonokuchi.missing_exact_birth_date == 2
    assert jonokuchi.missing_bio == 1
    assert jonokuchi.bio_without_exact_birth_date == 1

    output = tmp_path / "ages.csv"
    write_average_age_by_division_csv(rows, output)
    with output.open(newline="", encoding="utf-8") as stream:
        written = list(csv.DictReader(stream))
    assert len(written) == 6
    assert written[0]["start_date"] == "2020-01-12"


def test_group_without_exact_dates_has_blank_statistics(tmp_path) -> None:
    basho = Date.from_ints(2020, 1)
    history = History({basho: _state({1: "Jk1e"})})
    rows = average_age_by_division(history, BioStore(MappingProxyType({})), {basho: date(2020, 1, 12)})

    assert rows[0].division == "Jonokuchi"
    assert rows[0].mean_age_years is None
    output = tmp_path / "ages.csv"
    write_average_age_by_division_csv(rows, output)
    assert list(csv.DictReader(output.open(newline="", encoding="utf-8")))[0]["mean_age_years"] == ""


def test_exact_day_one_coverage_must_match_history(tmp_path) -> None:
    basho = Date.from_ints(2020, 1)
    history = History({basho: _state({1: "M1e"})})
    with pytest.raises(ValueError, match="coverage does not match"):
        average_age_by_division(history, BioStore(MappingProxyType({})), {})
    with pytest.raises(ValueError, match="Cannot resolve exact Day 1"):
        exact_basho_start_dates(history, results_root=tmp_path)

    directory = tmp_path / "2020 01"
    directory.mkdir()
    (directory / "day1.html").write_text(
        "<h1>Hatsu Basho, Day 1</h1><h2>January 12, 2020</h2>", encoding="utf-8"
    )
    (directory / "day2.html").write_text(
        "<h1>Hatsu Basho, Day 2</h1><h2>January 14, 2020</h2>", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="inconsistent"):
        exact_basho_start_dates(history, results_root=tmp_path)


def _state(ranks: dict[int, str]) -> BashoState:
    chii = {RikId(rikishi_id): Chii.from_str(rank) for rikishi_id, rank in ranks.items()}
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(chii),
            rikchii=RikChii(chii),
            rikshik=RikShikona({rikishi_id: Shikona(f"Rikishi {int(rikishi_id)}") for rikishi_id in chii}),
        ),
        summary=Summary({}),
    )


def _bio(rikishi_id: int, value: date | None) -> RikishiBio:
    return RikishiBio(
        rikid=RikId(rikishi_id), birth_date=None if value is None else BirthDate(value),
        shusshin="", heya=(), shikona_history=(), hatsu_dohyo=None, intai=None,
        height_cm=None, weight_kg=None, height_history=(), weight_history=(),
    )

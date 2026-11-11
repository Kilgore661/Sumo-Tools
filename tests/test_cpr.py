from __future__ import annotations

import csv
import math
from dataclasses import replace
from pathlib import Path

import pytest

from src.analysis.cpr.model import (
    RatedBout,
    calculate_metrics,
    cumulative_rows,
    remove_repetitions,
    solve_cpr,
)
from src.analysis.cpr.output import write_csv
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.Chii import Chii


def test_cpr_uses_extended_real_boundaries() -> None:
    opponents = (2400.0, 2500.0)
    assert solve_cpr(opponents, wins=0, q=400) == -math.inf
    assert solve_cpr(opponents, wins=2, q=400) == math.inf
    assert solve_cpr((2400.0, 2400.0), wins=1, q=400) == pytest.approx(2400.0)


def test_no_rated_bouts_are_not_applicable() -> None:
    metrics = calculate_metrics((), start_rating=2400.0, q=400)
    assert metrics.cpr is None
    assert metrics.z_score is None
    assert metrics.tail_probability is None
    assert metrics.tail_direction == "N/A"


def test_two_even_wins_have_infinite_cpr_but_finite_surprise() -> None:
    metrics = calculate_metrics(
        (
            RatedBout(day=1, opponent_rating=2400.0, won=True),
            RatedBout(day=2, opponent_rating=2400.0, won=True),
        ),
        start_rating=2400.0,
        q=400,
    )
    assert metrics.cpr == math.inf
    assert metrics.cpr_minus_start == math.inf
    assert metrics.z_score == pytest.approx(math.sqrt(2.0))
    assert metrics.tail_direction == "upper"
    assert metrics.tail_probability == pytest.approx(0.25)
    assert metrics.cpr_standard_error == math.inf


def test_cumulative_rows_repeat_the_running_record_on_each_day() -> None:
    rikishi = RikId(1)
    rows = cumulative_rows(
        basho="2026/11",
        division="makuuchi",
        latest_day=2,
        rikishi=(rikishi,),
        shikona={rikishi: Shikona("Alpha")},
        chii={rikishi: Chii.from_str("M1e")},
        start_ratings={"1": 2400.0},
        day_end_ratings={"1": {"1": 2410.0}, "2": {"1": 2400.0}},
        ledger=(
            {
                "date": "2026/11",
                "day": "1",
                "rikishi_a": "1",
                "rikishi_b": "2",
                "rating_a_before": "2400",
                "rating_b_before": "2400",
                "a_won": "True",
            },
            {
                "date": "2026/11",
                "day": "2",
                "rikishi_a": "1",
                "rikishi_b": "3",
                "rating_a_before": "2410",
                "rating_b_before": "2400",
                "a_won": "False",
            },
        ),
        q=400,
    )
    assert len(rows) == 2
    assert rows[0].rated_bouts == 1
    assert rows[0].cpr == math.inf
    assert rows[1].rated_bouts == 2
    assert rows[1].rated_wins == 1
    assert rows[1].cpr == pytest.approx(2400.0)


def test_fujiryoga_day_15_metrics() -> None:
    opponent_ratings = (
        2456.616330601102,
        2362.2362320133666,
        2491.1793281697037,
        2558.4181624396106,
        2400.532173273898,
        2461.400324386714,
        2552.247257535292,
        2438.6400301304125,
        2647.528617441604,
        2633.9211579698363,
        2389.624808928411,
        2492.896615039997,
        2500.7542688006747,
        2535.710518717265,
    )
    outcomes = (False, False, True, False, True, False, False, True, False, True, True, True, False, True)
    metrics = calculate_metrics(
        tuple(
            RatedBout(day=index, opponent_rating=opponent, won=won)
            for index, (opponent, won) in enumerate(zip(opponent_ratings, outcomes), 1)
        ),
        start_rating=2360.2048984800786,
        q=400,
    )
    assert metrics.rated_bouts == 14
    assert metrics.rated_wins == 7
    assert metrics.expected_wins == pytest.approx(4.54474793168217)
    assert metrics.cpr == pytest.approx(2493.98212846847)
    assert metrics.z_score == pytest.approx(1.43324842450842)
    assert metrics.tail_probability == pytest.approx(0.127687287236603)
    assert metrics.cpr_standard_error == pytest.approx(95.3574252982337)


def test_csv_formats_infinities_and_not_applicable(tmp_path: Path) -> None:
    from src.analysis.cpr.model import CPRRow

    row = CPRRow(
        basho="2026/11",
        division="makuuchi",
        day=1,
        rikishi_id=1,
        shikona="Alpha",
        chii="M1e",
        chii_ordinal=400100,
        basho_start_rating=2400.0,
        day_end_rating=2400.0,
        rated_bouts=1,
        rated_wins=1,
        rated_losses=0,
        expected_wins=0.5,
        win_variance=0.25,
        cpr=math.inf,
        cpr_minus_start=math.inf,
        z_score=1.0,
        tail_direction="upper",
        tail_probability=0.5,
        cpr_standard_error=math.inf,
    )
    path = write_csv((row,), tmp_path / "cpr.csv")
    with path.open(newline="", encoding="utf-8") as stream:
        written = next(csv.DictReader(stream))
    assert written["cpr"] == "+inf"
    assert written["cpr_minus_start"] == "+inf"
    assert written["cpr_standard_error"] == "+inf"


def test_remove_repetitions_keeps_each_rikishis_highest_z_row() -> None:
    from src.analysis.cpr.model import CPRRow

    base = CPRRow(
        basho="2024/03",
        division="makuuchi",
        day=1,
        rikishi_id=1,
        shikona="Alpha",
        chii="M1e",
        chii_ordinal=400100,
        basho_start_rating=2400.0,
        day_end_rating=2400.0,
        rated_bouts=1,
        rated_wins=1,
        rated_losses=0,
        expected_wins=0.5,
        win_variance=0.25,
        cpr=math.inf,
        cpr_minus_start=math.inf,
        z_score=1.0,
        tail_direction="upper",
        tail_probability=0.5,
        cpr_standard_error=math.inf,
    )
    rows = (
        base,
        replace(base, day=2, z_score=2.0, tail_probability=0.1),
        replace(base, rikishi_id=2, shikona="Beta", z_score=None),
        replace(base, basho="2024/05", day=3, z_score=1.5),
    )
    filtered = remove_repetitions(rows)
    assert [(row.basho, row.rikishi_id, row.day) for row in filtered] == [
        ("2024/03", 1, 2),
        ("2024/05", 1, 3),
        ("2024/03", 2, 1),
    ]

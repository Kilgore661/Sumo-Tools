from __future__ import annotations

import csv
from datetime import date
from types import MappingProxyType

from src.analysis.greatness.sanyaku_transition_probability import (
    OutcomeStatus,
    RiskObservation,
    _outcome_status,
    analyse_transition_probabilities,
    write_outputs,
)
from src.infra.get_bios.api import BioBashoDate, BioStore, BirthDate, RikishiBio
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_exact_age_probability_separates_outcome_statuses() -> None:
    dates = tuple(Date.from_ints(2000 + index // 6, 1 + 2 * (index % 6)) for index in range(14))
    states = {
        dates[0]: _state({1: "Y1e"}),
        dates[1]: _state({2: "J1e", 3: "J2e"}),
        dates[2]: _state({4: "J3e", 5: "J4e"}),
        dates[3]: _state({2: "M1e", 3: "J1e"}),
        dates[4]: _state({2: "K1e", 3: "J1e"}),
    }
    for basho in dates[5:-1]:
        states[basho] = _state({3: "J1e"})
    states[dates[-1]] = _state({3: "J1e", 4: "J2e"})
    history = History(states)
    bios = BioStore(
        MappingProxyType(
            {
                RikId(1): _bio(1, date(1970, 1, 1)),
                RikId(2): _bio(2, date(1980, 1, 1)),
                RikId(3): _bio(3, date(1980, 1, 1)),
                RikId(4): _bio(4, date(1980, 1, 1)),
                RikId(5): _bio(5, date(1980, 1, 1)),
            }
        )
    )

    result = analyse_transition_probabilities(history, bios, horizon_basho=12)
    juryo_age_20 = next(
        row for row in result.exact_age if row.division == "J" and row.age == 20
    )

    assert juryo_age_20.rikishi == 4
    assert juryo_age_20.success == 1
    assert juryo_age_20.failure == 1
    assert juryo_age_20.right_censored == 1
    assert juryo_age_20.unknown == 1
    assert juryo_age_20.resolved_probability == 0.5
    assert juryo_age_20.lower_bound_probability == 0.25
    assert juryo_age_20.upper_bound_probability == 0.75


def test_threshold_cohort_counts_each_rikishi_once_at_earliest_qualifying_state() -> None:
    history = History(
        {
            Date.from_ints(2000, 1): _state({1: "Y1e"}),
            Date.from_ints(2000, 3): _state({2: "J1e"}),
            Date.from_ints(2001, 3): _state({2: "J1e"}),
            Date.from_ints(2002, 3): _state({2: "K1e"}),
        }
    )
    bios = BioStore(
        MappingProxyType({RikId(2): _bio(2, date(1980, 1, 1))})
    )

    result = analyse_transition_probabilities(history, bios, horizon_basho=12)
    row = next(
        item
        for item in result.age_threshold
        if item.division == "J" and item.age_threshold == 20
    )

    assert row.rikishi == 1
    assert row.success == 1


def test_event_after_horizon_is_failure() -> None:
    dates = tuple(Date.from_ints(2000 + index // 6, 1 + 2 * (index % 6)) for index in range(14))
    status = _outcome_status(
        RiskObservation(RikId(2), "J", 20, 0),
        history_dates=dates,
        first_sanyaku_index={RikId(2): 13},
        latest_ids=frozenset({RikId(2)}),
        bios=BioStore(MappingProxyType({RikId(2): _bio(2, date(1980, 1, 1))})),
        horizon_basho=12,
    )
    assert status == OutcomeStatus.FAILURE


def test_event_after_fixed_horizon_is_success_in_eventual_mode() -> None:
    dates = tuple(
        Date.from_ints(2000 + index // 6, 1 + 2 * (index % 6))
        for index in range(14)
    )
    status = _outcome_status(
        RiskObservation(RikId(2), "J", 20, 0),
        history_dates=dates,
        first_sanyaku_index={RikId(2): 13},
        latest_ids=frozenset({RikId(2)}),
        bios=BioStore(
            MappingProxyType({RikId(2): _bio(2, date(1980, 1, 1))})
        ),
        horizon_basho=None,
    )
    assert status == OutcomeStatus.SUCCESS


def test_write_outputs_preserves_censoring_columns(tmp_path) -> None:
    history = History(
        {
            Date.from_ints(2000, 1): _state({1: "Y1e"}),
            Date.from_ints(2000, 3): _state({2: "M1e"}),
            Date.from_ints(2000, 5): _state({2: "K1e"}),
        }
    )
    analysis = analyse_transition_probabilities(
        history,
        BioStore(MappingProxyType({RikId(2): _bio(2, date(1980, 1, 1))})),
    )

    write_outputs(analysis, tmp_path)

    with (tmp_path / "probability_by_division_and_age_threshold.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["success"] == "1"
    assert rows[0]["failure"] == "0"
    assert rows[0]["right_censored"] == "0"
    assert rows[0]["unknown"] == "0"


def _state(ranks: dict[int, str]) -> BashoState:
    chii = {
        RikId(rikishi_id): Chii.from_str(rank)
        for rikishi_id, rank in ranks.items()
    }
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(chii),
            rikchii=RikChii(chii),
            rikshik=RikShikona(
                {
                    rikishi_id: Shikona(f"Rikishi {int(rikishi_id)}")
                    for rikishi_id in chii
                }
            ),
        ),
        summary=Summary({}),
    )


def _bio(rikishi_id: int, birth: date) -> RikishiBio:
    return RikishiBio(
        rikid=RikId(rikishi_id),
        birth_date=BirthDate(birth),
        shusshin="",
        heya=(),
        shikona_history=(),
        hatsu_dohyo=None,
        intai=None,
        height_cm=None,
        weight_kg=None,
        height_history=(),
        weight_history=(),
    )

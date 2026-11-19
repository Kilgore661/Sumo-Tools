from types import MappingProxyType

import pytest

from src.analysis.torikumi_forcasting.analysis import (
    NonMinimalCrossDivisionCase,
    build_case,
)
from src.analysis.torikumi_forcasting.greedy import forecast_greedily
from src.analysis.torikumi_forcasting.heya import HeyaEntry, HeyaIndex
from src.analysis.torikumi_forcasting.model import ForecastCase, Standing
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import Day, Pair, RikId, Riks, Shikona, Torikumi
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary


@pytest.mark.parametrize(
    ("size", "forbidden", "expected_pairs", "expected_unpaired", "success"),
    [
        (4, (), ((1, 2), (3, 4)), (), True),
        (4, ((1, 2),), ((1, 3), (2, 4)), (), True),
        (4, ((3, 4),), ((1, 2),), (3, 4), False),
        (5, (), ((1, 2), (3, 4)), (5,), True),
        (
            5,
            ((3, 4), (3, 5), (4, 5)),
            ((1, 2),),
            (3, 4, 5),
            False,
        ),
        (
            4,
            ((1, 3), (1, 4), (2, 3), (2, 4), (3, 4)),
            ((1, 2),),
            (3, 4),
            False,
        ),
        (3, ((1, 2), (1, 3), (2, 3)), (), (1, 2, 3), False),
    ],
)
def test_predeclared_greedy_cases(
    size, forbidden, expected_pairs, expected_unpaired, success
) -> None:
    case = _greedy_case(size, forbidden)

    result = forecast_greedily(case)

    assert tuple(tuple(int(rikishi) for rikishi in pair.pair) for pair in result.pairs) == expected_pairs
    assert tuple(int(row.rikid) for row in result.unpaired) == expected_unpaired
    assert result.success is success


def test_same_heya_is_skipped_and_output_is_oriented_by_chii() -> None:
    standings = list(_standings(4))
    standings[0] = Standing(
        rikid=standings[0].rikid,
        shikona=standings[0].shikona,
        chii=standings[0].chii,
        wins=standings[0].wins,
        heya="Shared",
        synthetic_heya=False,
        position=standings[0].position,
    )
    standings[1] = Standing(
        rikid=standings[1].rikid,
        shikona=standings[1].shikona,
        chii=standings[1].chii,
        wins=standings[1].wins,
        heya="Shared",
        synthetic_heya=False,
        position=standings[1].position,
    )
    # Put the lower-ranked member first in the greedy order to separate
    # matching order from East/West presentation orientation.
    standings[0], standings[2] = standings[2], standings[0]
    case = ForecastCase(
        basho=Date.from_ints(2026, 11),
        day=11,
        standings=tuple(standings),
        prior_pairs=frozenset(),
        actual_pairs=frozenset(),
        actual_unmatched=(),
    )

    result = forecast_greedily(case)

    assert Pair(RikId(1), RikId(2)) not in {row.pair for row in result.pairs}
    assert all(row.east.chii.ordinal() < row.west.chii.ordinal() for row in result.pairs)


def test_build_case_uses_d_minus_2_wins_d_minus_1_opponents_and_target_population() -> None:
    date = Date.from_ints(2026, 11)
    history = _history_fixture(date)
    entries = {
        (date, RikId(rikid)): HeyaEntry(
            date, RikId(rikid), f"Stable {rikid}", (1,), 1
        )
        for rikid in range(1, 5)
    }
    index = HeyaIndex(MappingProxyType(entries), MappingProxyType({}))

    case = build_case(history, index, date, 11)

    assert [int(row.rikid) for row in case.standings] == [1, 3, 2, 4, 5]
    assert [row.wins for row in case.standings] == [1, 1, 0, 0, 0]
    assert Pair(RikId(1), RikId(5)) in case.prior_pairs  # Day 10 is known.
    assert case.actual_pairs == {
        Pair(RikId(1), RikId(3)),
        Pair(RikId(2), RikId(4)),
    }
    assert case.actual_unmatched == (RikId(5),)
    standing5 = next(row for row in case.standings if row.rikid == RikId(5))
    assert standing5.synthetic_heya
    assert standing5.heya == "heya5"


def test_build_case_declares_extra_cross_division_case_out_of_scope() -> None:
    date = Date.from_ints(2026, 11)
    history = _history_fixture(date)
    history[date].summary[Day(11)] = DailyResults(
        Torikumi({
            Pair(RikId(1), RikId(6)),
            Pair(RikId(2), RikId(99)),
            Pair(RikId(3), RikId(4)),
        }),
        ResultLookup(),
    )
    index = HeyaIndex(MappingProxyType({}), MappingProxyType({}))

    with pytest.raises(NonMinimalCrossDivisionCase) as raised:
        build_case(history, index, date, 11)

    exclusion = raised.value.exclusion
    assert exclusion.population_size == 4
    assert exclusion.actual_unmatched_count == 2
    assert exclusion.parity_minimum == 0


def _greedy_case(size: int, forbidden) -> ForecastCase:
    return ForecastCase(
        basho=Date.from_ints(2026, 11),
        day=11,
        standings=_standings(size),
        prior_pairs=frozenset(Pair(RikId(a), RikId(b)) for a, b in forbidden),
        actual_pairs=frozenset(),
        actual_unmatched=(),
    )


def _standings(size: int) -> tuple[Standing, ...]:
    chii = ("M1e", "M1w", "M2e", "M2w", "M3e")
    return tuple(
        Standing(
            rikid=RikId(index),
            shikona=f"Rikishi {index}",
            chii=Chii.from_str(chii[index - 1]),
            wins=10,
            heya=f"Stable {index}",
            synthetic_heya=False,
            position=index,
        )
        for index in range(1, size + 1)
    )


def _history_fixture(date: Date) -> History:
    ranks = {
        1: "M1e", 2: "M1w", 3: "M2e", 4: "M2w", 5: "M3e", 6: "J1e"
    }
    days = {
        Day(day): DailyResults(Torikumi(), ResultLookup())
        for day in range(1, 16)
    }
    days[Day(1)] = _daily(_result(1, 2, Outcome.W, Outcome.L))
    days[Day(9)] = _daily(_result(3, 4, Outcome.W, Outcome.L))
    days[Day(10)] = _daily(_result(5, 1, Outcome.W, Outcome.L))
    days[Day(11)] = DailyResults(
        Torikumi({Pair(RikId(1), RikId(3)), Pair(RikId(2), RikId(4)), Pair(RikId(5), RikId(6))}),
        ResultLookup(),
    )
    banzuke = Banzuke(
        riks=Riks(RikId(rikid) for rikid in ranks),
        rikchii=RikChii({RikId(rikid): Chii.from_str(rank) for rikid, rank in ranks.items()}),
        rikshik=RikShikona({RikId(rikid): Shikona(f"Rikishi {rikid}") for rikid in ranks}),
    )
    return History({date: BashoState(banzuke=banzuke, summary=Summary(days))})


def _result(a: int, b: int, outcome_a: Outcome, outcome_b: Outcome) -> BoutResult:
    return BoutResult(
        RikId(a), outcome_a, RikId(b), outcome_b, "blank", Symbol[outcome_a.name]
    )


def _daily(*results: BoutResult) -> DailyResults:
    lookup = ResultLookup(
        {Pair(result.rikishi1, result.rikishi2): result for result in results}
    )
    return DailyResults(Torikumi(lookup), lookup)

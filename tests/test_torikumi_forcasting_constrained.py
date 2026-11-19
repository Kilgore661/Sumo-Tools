from random import Random

import pytest

from src.analysis.torikumi_forcasting.constrained import (
    forecast_with_constraints,
    solve_exhaustively,
)
from src.analysis.torikumi_forcasting.model import ForecastCase, Standing
from src.sumo_core.BasicPrimitives import Pair, RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


@pytest.mark.parametrize(
    ("size", "forbidden", "status", "cost", "unmatched_count"),
    [
        (4, (), "OPTIMAL", 2, 0),
        (4, ((1, 2),), "OPTIMAL", 4, 0),
        (4, ((3, 4),), "OPTIMAL", 4, 0),
        (5, (), "OPTIMAL", 2, 1),
        (5, ((3, 4), (3, 5), (4, 5)), "OPTIMAL", 4, 1),
        (
            4,
            ((1, 3), (1, 4), (2, 3), (2, 4), (3, 4)),
            "INFEASIBLE",
            None,
            0,
        ),
        (3, ((1, 2), (1, 3), (2, 3)), "INFEASIBLE", None, 0),
    ],
)
def test_predeclared_constrained_cases(
    size, forbidden, status, cost, unmatched_count
) -> None:
    case = _case(size, forbidden)

    result = forecast_with_constraints(case)

    assert result.status == status
    assert result.objective_cost == cost
    assert len(result.unpaired) == unmatched_count


def test_greedy_trap_finds_one_of_the_optimal_global_solutions() -> None:
    result = forecast_with_constraints(_case(4, ((3, 4),)))

    assert frozenset(row.pair for row in result.pairs) in {
        frozenset({Pair(RikId(1), RikId(3)), Pair(RikId(2), RikId(4))}),
        frozenset({Pair(RikId(1), RikId(4)), Pair(RikId(2), RikId(3))}),
    }


def test_fixed_seed_generated_cases_match_exhaustive_oracle() -> None:
    random = Random(20261119)
    checked = 0
    for size in range(2, 10):
        all_pairs = [
            (first, second)
            for first in range(1, size + 1)
            for second in range(first + 1, size + 1)
        ]
        for permitted_probability in (0.25, 0.50, 0.75):
            for _ in range(20):
                forbidden = tuple(
                    pair
                    for pair in all_pairs
                    if random.random() > permitted_probability
                )
                case = _case(size, forbidden)
                oracle = solve_exhaustively(case)
                solver = forecast_with_constraints(case)

                assert (solver.status == "OPTIMAL") is oracle.feasible
                assert solver.objective_cost == oracle.cost
                if oracle.feasible:
                    assert len(solver.unpaired) == size % 2
                checked += 1

    assert checked == 480


def _case(size: int, forbidden) -> ForecastCase:
    labels = (
        "M1e", "M1w", "M2e", "M2w", "M3e",
        "M3w", "M4e", "M4w", "M5e",
    )
    standings = tuple(
        Standing(
            rikid=RikId(index),
            shikona=f"Rikishi {index}",
            chii=Chii.from_str(labels[index - 1]),
            wins=10,
            heya=f"Stable {index}",
            synthetic_heya=False,
            position=index,
        )
        for index in range(1, size + 1)
    )
    return ForecastCase(
        basho=Date.from_ints(2026, 11),
        day=11,
        standings=standings,
        prior_pairs=frozenset(Pair(RikId(a), RikId(b)) for a, b in forbidden),
        actual_pairs=frozenset(),
        actual_unmatched=(),
    )

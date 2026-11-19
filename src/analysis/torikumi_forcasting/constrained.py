"""Minimum-cost constrained torikumi matching with OR-Tools CP-SAT."""

from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model

from src.sumo_core.BasicPrimitives import Pair, RikId

from .greedy import eligibility_reasons
from .model import ConstrainedForecast, ForecastCase, ForecastPair, Standing


SOLVER_RANDOM_SEED = 20261119


class ConstrainedSolverFailure(RuntimeError):
    pass


@dataclass(frozen=True)
class ExhaustiveSolution:
    feasible: bool
    cost: int | None
    pairs: frozenset[Pair]
    unpaired: tuple[RikId, ...]


def forecast_with_constraints(case: ForecastCase) -> ConstrainedForecast:
    model = cp_model.CpModel()
    standings = case.standings
    pair_variables: dict[tuple[int, int], cp_model.IntVar] = {}
    incident: dict[int, list[cp_model.IntVar]] = {
        index: [] for index in range(len(standings))
    }

    for first in range(len(standings)):
        for second in range(first + 1, len(standings)):
            if eligibility_reasons(standings[first], standings[second], case):
                continue
            variable = model.new_bool_var(f"pair_{first}_{second}")
            pair_variables[(first, second)] = variable
            incident[first].append(variable)
            incident[second].append(variable)

    unpaired_variables = {
        index: model.new_bool_var(f"unpaired_{index}")
        for index in range(len(standings))
    }
    for index in range(len(standings)):
        model.add(sum(incident[index]) + unpaired_variables[index] == 1)
    model.add(sum(unpaired_variables.values()) == len(standings) % 2)
    model.minimize(
        sum(
            abs(standings[first].position - standings[second].position) * variable
            for (first, second), variable in pair_variables.items()
        )
    )

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = SOLVER_RANDOM_SEED
    status = solver.solve(model)
    status_name = solver.status_name(status)

    if status == cp_model.INFEASIBLE:
        return ConstrainedForecast(
            status="INFEASIBLE",
            pairs=(),
            unpaired=(),
            objective_cost=None,
            best_objective_bound=None,
            solve_seconds=solver.wall_time,
        )
    if status != cp_model.OPTIMAL:
        raise ConstrainedSolverFailure(
            f"CP-SAT did not prove optimality for {case.basho} Day {case.day}: "
            f"{status_name}"
        )

    pairs: list[ForecastPair] = []
    for (first, second), variable in pair_variables.items():
        if solver.value(variable):
            east, west = _orient(standings[first], standings[second])
            pairs.append(ForecastPair(east=east, west=west))
    pairs.sort(key=lambda row: min(row.east.position, row.west.position))
    unpaired = tuple(
        standings[index]
        for index, variable in unpaired_variables.items()
        if solver.value(variable)
    )
    objective_cost = sum(
        abs(pair.east.position - pair.west.position) for pair in pairs
    )
    forecast = ConstrainedForecast(
        status="OPTIMAL",
        pairs=tuple(pairs),
        unpaired=unpaired,
        objective_cost=objective_cost,
        best_objective_bound=solver.best_objective_bound,
        solve_seconds=solver.wall_time,
    )
    _validate_optimal_forecast(case, forecast)
    return forecast


def solve_exhaustively(case: ForecastCase) -> ExhaustiveSolution:
    standings = case.standings
    allowed = {
        (first, second)
        for first in range(len(standings))
        for second in range(first + 1, len(standings))
        if not eligibility_reasons(standings[first], standings[second], case)
    }
    best_cost: int | None = None
    best_pairs: tuple[tuple[int, int], ...] = ()
    best_unpaired: tuple[int, ...] = ()

    def visit(
        remaining: tuple[int, ...],
        unmatched_left: int,
        pairs: tuple[tuple[int, int], ...],
        unpaired: tuple[int, ...],
        cost: int,
    ) -> None:
        nonlocal best_cost, best_pairs, best_unpaired
        if best_cost is not None and cost > best_cost:
            return
        if not remaining:
            if unmatched_left == 0 and (best_cost is None or cost < best_cost):
                best_cost = cost
                best_pairs = pairs
                best_unpaired = unpaired
            return

        first = remaining[0]
        rest = remaining[1:]
        if unmatched_left:
            visit(rest, unmatched_left - 1, pairs, unpaired + (first,), cost)
        for offset, second in enumerate(rest):
            edge = (first, second)
            if edge not in allowed:
                continue
            next_remaining = rest[:offset] + rest[offset + 1 :]
            edge_cost = abs(
                standings[first].position - standings[second].position
            )
            visit(
                next_remaining,
                unmatched_left,
                pairs + (edge,),
                unpaired,
                cost + edge_cost,
            )

    visit(tuple(range(len(standings))), len(standings) % 2, (), (), 0)
    if best_cost is None:
        return ExhaustiveSolution(False, None, frozenset(), ())
    return ExhaustiveSolution(
        True,
        best_cost,
        frozenset(
            Pair(standings[first].rikid, standings[second].rikid)
            for first, second in best_pairs
        ),
        tuple(standings[index].rikid for index in best_unpaired),
    )


def allowed_opponent_counts(case: ForecastCase) -> dict[RikId, int]:
    return {
        focal.rikid: sum(
            not eligibility_reasons(focal, opponent, case)
            for opponent in case.standings
            if opponent.rikid != focal.rikid
        )
        for focal in case.standings
    }


def prohibited_edges(case: ForecastCase):
    for first_index, first in enumerate(case.standings):
        for second in case.standings[first_index + 1 :]:
            reasons = eligibility_reasons(first, second, case)
            if reasons:
                yield first.rikid, second.rikid, reasons


def _validate_optimal_forecast(
    case: ForecastCase, forecast: ConstrainedForecast
) -> None:
    participation = [
        rikishi
        for pair in forecast.pairs
        for rikishi in (pair.east.rikid, pair.west.rikid)
    ] + [row.rikid for row in forecast.unpaired]
    expected = sorted(row.rikid for row in case.standings)
    if sorted(participation) != expected:
        raise ConstrainedSolverFailure(
            f"optimal forecast does not cover population for {case.basho} Day {case.day}"
        )
    if len(forecast.unpaired) != len(case.standings) % 2:
        raise ConstrainedSolverFailure(
            f"optimal forecast has wrong unmatched count for {case.basho} Day {case.day}"
        )
    for pair in forecast.pairs:
        reasons = eligibility_reasons(pair.east, pair.west, case)
        if reasons:
            raise ConstrainedSolverFailure(
                f"optimal forecast contains prohibited pair {pair.pair}: {reasons}"
            )
    recomputed = sum(
        abs(pair.east.position - pair.west.position) for pair in forecast.pairs
    )
    if recomputed != forecast.objective_cost:
        raise ConstrainedSolverFailure(
            f"objective mismatch: {recomputed} != {forecast.objective_cost}"
        )
    if forecast.best_objective_bound != float(forecast.objective_cost):
        raise ConstrainedSolverFailure(
            f"optimal bound mismatch: {forecast.best_objective_bound} != "
            f"{forecast.objective_cost}"
        )


def _orient(first: Standing, second: Standing) -> tuple[Standing, Standing]:
    if first.chii.ordinal() < second.chii.ordinal():
        return first, second
    return second, first

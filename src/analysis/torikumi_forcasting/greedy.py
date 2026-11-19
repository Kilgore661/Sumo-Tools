"""Literal non-backtracking greedy torikumi matcher."""

from __future__ import annotations

from src.sumo_core.BasicPrimitives import Pair

from .model import (
    CandidateRejection,
    ForecastCase,
    ForecastPair,
    GreedyForecast,
    Standing,
    UnpairedDiagnostic,
)


def forecast_greedily(case: ForecastCase) -> GreedyForecast:
    remaining = list(case.standings)
    pairs: list[ForecastPair] = []
    unpaired: list[Standing] = []
    diagnostics: list[UnpairedDiagnostic] = []

    while remaining:
        focal = remaining.pop(0)
        rejections: list[CandidateRejection] = []
        selected_index: int | None = None

        for index, opponent in enumerate(remaining):
            reasons = eligibility_reasons(focal, opponent, case)
            if not reasons:
                selected_index = index
                break
            rejections.append(CandidateRejection(opponent.rikid, reasons))

        if selected_index is None:
            unpaired.append(focal)
            diagnostics.append(
                UnpairedDiagnostic(focal.rikid, tuple(rejections))
            )
            continue

        opponent = remaining.pop(selected_index)
        east, west = _orient(focal, opponent)
        pairs.append(ForecastPair(east=east, west=west))

    expected_unpaired = len(case.standings) % 2
    return GreedyForecast(
        pairs=tuple(pairs),
        unpaired=tuple(unpaired),
        diagnostics=tuple(diagnostics),
        success=len(unpaired) == expected_unpaired,
    )


def eligibility_reasons(
    first: Standing,
    second: Standing,
    case: ForecastCase,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if Pair(first.rikid, second.rikid) in case.prior_pairs:
        reasons.append("previous_opponent")
    if first.heya == second.heya:
        reasons.append("same_heya")
    return tuple(reasons)


def _orient(first: Standing, second: Standing) -> tuple[Standing, Standing]:
    if first.chii.ordinal() < second.chii.ordinal():
        return first, second
    return second, first

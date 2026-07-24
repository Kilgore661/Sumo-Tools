"""Application orchestration for clean Elo."""

from pathlib import Path

from src.sumo_core.History import Date, History

from .config import DEFAULT_OUTPUT_ROOT, DEFAULT_Q
from .output import OutputPaths, write_outputs
from .policies import (
    ConstantInitialRatingPolicy,
    FideKPolicy,
    InitialRatingPolicy,
    KPolicy,
)
from .simulate import SimulationResult, simulate


def run_clean_elo(
    *,
    history: History,
    start_date: Date,
    initial_rating_policy: InitialRatingPolicy | None = None,
    k_policy: KPolicy | None = None,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    q: float = DEFAULT_Q,
    count_absences: bool = False,
) -> tuple[SimulationResult, OutputPaths]:
    if initial_rating_policy is None:
        initial_rating_policy = ConstantInitialRatingPolicy()
    if k_policy is None:
        k_policy = FideKPolicy.load()

    result = simulate(
        history=history,
        start_date=start_date,
        initial_rating_policy=initial_rating_policy,
        k_policy=k_policy,
        q=q,
        count_absences=count_absences,
    )
    outputs = write_outputs(
        result=result,
        history=history,
        output_root=output_root,
        start_date=start_date,
        q=q,
        count_absences=count_absences,
        initial_policy_metadata=initial_rating_policy.metadata(),
        k_policy_metadata=k_policy.metadata(),
    )
    return result, outputs

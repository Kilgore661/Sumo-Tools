from dataclasses import dataclass
import random

from ..expt1.initialisation import EntrantContext
from ....sumo_core.Chii import Chii

from .config import (
    ALL_HIGH_VALUE,
    RANDOM_MAX,
    RANDOM_MIN,
    RANDOM_RUN_COUNT,
)


@dataclass(frozen=True)
class RunSpec:
    name: str
    seed: int | None


def build_run_plan(seed_base: int) -> list[RunSpec]:
    specs = [RunSpec(name="all_5000", seed=None)]

    for i in range(RANDOM_RUN_COUNT):
        specs.append(RunSpec(name=f"random_{i:02d}", seed=seed_base + i))

    return specs


def make_initialiser(spec: RunSpec):
    if spec.name == "all_5000":
        return _constant_initialiser(ALL_HIGH_VALUE)

    if spec.seed is None:
        raise ValueError(f"Random run requires a seed: {spec.name}")

    return _random_by_chii_initialiser(spec.seed)


def _constant_initialiser(value: float):
    def initialise(context: EntrantContext) -> float:
        del context
        return value

    return initialise


def _random_by_chii_initialiser(seed: int):
    rng = random.Random(seed)
    by_chii: dict[Chii, float] = {}

    def initialise(context: EntrantContext) -> float:
        chii = context.chii
        if chii not in by_chii:
            by_chii[chii] = rng.uniform(RANDOM_MIN, RANDOM_MAX)
        return by_chii[chii]

    return initialise

from pdb import set_trace

"""Elo parameter definitions for Expt1.

This module keeps numeric Elo parameters separate from configuration loading.
The simulation consumes an :class:`EloParams` value whose ``k`` member is an
already-resolved callable.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable, Literal

from ..config_main import INITIAL_ELO, INITIAL_Q, CONSTANT_K


KFn = Callable[[int], float]
KPolicy = Literal["constant", "divisional"]

DEFAULT_K_CONFIG_PATH = Path("files/input/elo_fide.json")


@dataclass(frozen=True)
class EloParams:
    """Resolved Elo parameters.

    Attributes:
        b:
            Baseline rating used by the conventional flat entrant rule.
            This remains useful as an anchoring constant even when entrant
            initialisation is externalised.
        q:
            Elo scale parameter appearing in the logistic expectation formula.
        k:
            K-factor function indexed by ordinal.
    """

    b: float = INITIAL_ELO
    q: float = INITIAL_Q
    k: KFn | None = None

    def __post_init__(self) -> None:
        if self.k is None:
            object.__setattr__(self, "k", constant_k_fn(CONSTANT_K))

    @classmethod
    def constant(
        cls,
        b: float = INITIAL_ELO,
        q: float = INITIAL_Q,
        k_value: float = CONSTANT_K,
    ) -> "EloParams":
        """Build parameters using a constant K-factor."""
        return cls(b=float(b), q=float(q), k=constant_k_fn(k_value))

    @classmethod
    def divisional(
        cls,
        b: float = INITIAL_ELO,
        q: float = INITIAL_Q,
        config_path: Path = DEFAULT_K_CONFIG_PATH,
    ) -> "EloParams":
        """Build parameters using divisional K loaded from JSON config."""
        return cls(b=float(b), q=float(q), k=load_divisional_k_fn(config_path))


def constant_k_fn(k_value: float = CONSTANT_K) -> KFn:
    """Return a constant K-factor function."""

    def k_fn(ordinal: int) -> float:
        return float(k_value)

    return k_fn


def load_divisional_k_fn(config_path: Path = DEFAULT_K_CONFIG_PATH) -> KFn:
    """Load the legacy divisional K-factor configuration from JSON.

    Expected JSON shape::

        {
            "max": 10,
            "lims": {
                "0": 40,
                "1": 32,
                ...
            }
        }

    The returned function maps an ordinal to a division bucket via
    ``ordinal // 100000``.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    max_k = float(config["max"])
    lims = {int(key): float(value) for key, value in config.get("lims", {}).items()}

    k_map: dict[int, float] = {}
    last_upper = -1

    for upper, value in sorted(lims.items()):
        for division_index in range(last_upper + 1, upper + 1):
            k_map[division_index] = value
        last_upper = upper

    for division_index in range(last_upper + 1, 10):
        k_map[division_index] = max_k

    def k_fn(ordinal: int) -> float:
        division_index = ordinal // 100000
        return k_map[division_index]

    return k_fn


def build_elo_params(
    k_policy: KPolicy,
    b: float = INITIAL_ELO,
    q: float = INITIAL_Q,
    k_value: float | None = None,
    config_path: Path | None = None,
) -> EloParams:
    """Build :class:`EloParams` from an explicit K-policy.

    Strict policy handling is intentional:

    * ``constant`` accepts ``k_value`` and rejects ``config_path``
    * ``divisional`` accepts ``config_path`` and rejects ``k_value``
    """
    if k_policy == "constant":
        if config_path is not None:
            raise ValueError("k_policy='constant' does not accept a divisional config path")
        resolved_k_value = CONSTANT_K if k_value is None else float(k_value)
        return EloParams.constant(b=b, q=q, k_value=resolved_k_value)

    if k_policy == "divisional":
        if k_value is not None:
            raise ValueError("k_policy='divisional' does not accept a constant k_value")
        resolved_config_path = DEFAULT_K_CONFIG_PATH if config_path is None else Path(config_path)
        return EloParams.divisional(b=b, q=q, config_path=resolved_config_path)

    raise ValueError(f"Unknown k_policy: {k_policy}")

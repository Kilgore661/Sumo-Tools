from pathlib import Path
from typing import Callable
import json


KFn = Callable[[int], float]

INITIAL_ELO = 1500.0
INITIAL_Q = 400.0
INITIAL_KFN = "constant"

CONSTANT_K = 35.0
DEFAULT_K_CONFIG_PATH = Path("files/input/elo_fide.json")


class EloParams:
    """
    Elo parameters:
      - b: baseline rating
      - q: Elo scale parameter
      - kstr: K-factor function, resolved at construction time

    Example:
        x = EloParams()
        y = EloParams(b=3, q=100, k="divisional")
        z = EloParams(k="constant")
    """

    def __init__(
        self,
        b: float = INITIAL_ELO,
        q: float = INITIAL_Q,
        kstr: str = INITIAL_KFN,
    ) -> None:
        self.b = float(b)
        self.q = float(q)

        if kstr == "constant":
            self.k = self._make_constant_k_fn()
        elif kstr == "divisional":
            self.k = self._make_divisional_k_fn()
        else:
            raise ValueError(
                f"Unrecognised k specification: {kstr!r}. "
                "Expected 'constant' or 'divisional'."
            )

    @staticmethod
    def _make_constant_k_fn() -> KFn:
        def k_fn(ordinal: int) -> float:
            return float(CONSTANT_K)
        return k_fn

    @staticmethod
    def _make_divisional_k_fn() -> KFn:
        """
        Legacy-style divisional K from JSON config:

        {
            "max": 10,
            "lims": {
                "0": 40,
                "1": 32,
                ...
            }
        }
        """
        with open(DEFAULT_K_CONFIG_PATH, "r", encoding="utf-8") as f:
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

    def __repr__(self) -> str:
        return f"EloParams(b={self.b}, q={self.q}, k={self.k})"

if __name__ == '__main__':
    x = EloParams()
    print( x.k(300100) )
    x = EloParams( 1, 2, 'divisional' )
    print( x.k(300100) )

from pdb import set_trace

"""Entrant-initialisation helpers.

Expt2 needs the simulation boundary to accept a rank-aware initialisation rule.
This module defines that public boundary.
"""

from typing import Callable

from ....sumo_core.BasicPrimitives import RikId
from ....sumo_core.Chii import Chii
from ....sumo_core.History import Date


EntrantInitialiser = Callable[Chii, float]
"""Callable used to initialise a rikishi with no prior visible rating.

The contract is intentionally rank-centred:

* ``chii`` is the primary information Expt2 is expected to use
"""


def constant_initialiser(baseline: float) -> EntrantInitialiser:
    """Return the conventional flat initialisation rule.

    This preserves Expt1 behaviour while keeping the choice external to the
    simulator.
    """

    def initialise(chii: Chii) -> float:
        del chii
        return float(baseline)

    return initialise

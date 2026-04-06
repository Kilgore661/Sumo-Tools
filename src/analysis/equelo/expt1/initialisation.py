from __future__ import annotations

"""Entrant-initialisation helpers.

Expt2 needs the simulation boundary to accept a rank-aware initialisation rule.
This module defines that public boundary.
"""

from typing import Callable

from ....sumo_core.Chii import Chii
from ....sumo_core.History import Date
from ....sumo_core.BasicPrimitives import RikId


EntrantInitialiser = Callable[[RikId, Chii, Date], float]
"""Callable used to initialise a rikishi with no prior visible rating.

The contract is intentionally rank-centred:

* ``rikid`` is provided for flexibility and logging
* ``chii`` is the primary information Expt2 is expected to use
* ``date`` is provided so a future caller may make time-dependent choices
"""


def constant_initialiser(baseline: float) -> EntrantInitialiser:
    """Return the conventional flat initialisation rule.

    This preserves Expt1 behaviour while keeping the choice external to the
    simulator.
    """

    def initialise(rikid: RikId, chii: Chii, date: Date) -> float:
        del rikid, chii, date
        return float(baseline)

    return initialise

from pdb import set_trace

"""Entrant-initialisation helpers.

Expt2 needs the simulation boundary to accept a rank-aware initialisation rule.
This module defines that public boundary.
"""

from dataclasses import dataclass
from typing import Callable

from ....sumo_core.BasicPrimitives import RikId
from ....sumo_core.Banzuke import Banzuke
from ....sumo_core.Chii import Chii
from ....sumo_core.History import Date


@dataclass(frozen=True)
class EntrantContext:
    """Basho context available when a previously unseen rikishi enters."""

    date: Date
    rikid: RikId
    chii: Chii
    banzuke: Banzuke


EntrantInitialiser = Callable[[EntrantContext], float]
"""Callable used to initialise a rikishi with no prior visible rating.

The policy decides which parts of the explicit basho context determine the
entrant rating. Ordinary Equelo uses ``context.chii``; contextual experiments
may also use the contemporaneous banzuke.
"""


def constant_initialiser(baseline: float) -> EntrantInitialiser:
    """Return the conventional flat initialisation rule.

    This preserves Expt1 behaviour while keeping the choice external to the
    simulator.
    """

    def initialise(context: EntrantContext) -> float:
        del context
        return float(baseline)

    return initialise

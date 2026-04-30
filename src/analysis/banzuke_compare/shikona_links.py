"""
Qualified shikona contract for browser links.
"""

import pickle

from src.analysis.standings.config import LEGACY_QUALIFIED_SHIKONA
from src.sumo_core.BasicPrimitives import RikId, Shikona


with LEGACY_QUALIFIED_SHIKONA.open("rb") as f:
    QUALIFIED_SHIKONA = pickle.load(f)


def graph_shikona_for(rikishi_id: RikId, fallback: Shikona) -> str:
    """
    Contract:
        rikishi_id and fallback identify the displayed rikishi.

        Returns the shikona token expected by the Gaspode graph endpoint.  The
        qualified token may include disambiguating dates that are not present
        in History shikona.
    """

    return str(QUALIFIED_SHIKONA.get(rikishi_id, fallback))

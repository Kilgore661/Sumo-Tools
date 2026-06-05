"""
Build the public shikona map used by publication code.

This module is the production counterpart to the exploratory shikona
normalisation probe.  The probe is evidence for the rule; this module owns the
small deterministic transformation needed by the application:

    History + BioStore -> dict[RikId, Shikona]

History owns the normal public shikona value.  BioStore owns the facts that are
not part of History: whether a rikishi has retired, and the rikishi's full
recorded latest shikona.
"""

from __future__ import annotations

from collections import Counter

from src.infra.get_bios.api import BioStore
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.History import History


def make_public_shikona(history: History, bios: BioStore) -> dict[RikId, Shikona]:
    """
    Return the public-facing shikona for every rikishi represented in History.

    The normal public shikona is the latest shikona recorded for the rikishi in
    the supplied History.  If that History shikona is non-unique and the rikishi
    is retired, the public shikona is the full latest shikona from BioStore.
    """
    history_shikona_by_rikid = make_history_shikona_by_rikid(history)
    history_shikona_counts = Counter(history_shikona_by_rikid.values())

    public_shikona_by_rikid: dict[RikId, Shikona] = {}

    for rikid, history_shikona in history_shikona_by_rikid.items():
        bio = bios[rikid]

        if history_shikona_counts[history_shikona] > 1 and bio.intai is not None:
            public_shikona_by_rikid[rikid] = bio.latest_shikona()
        else:
            public_shikona_by_rikid[rikid] = history_shikona

    return public_shikona_by_rikid


def make_history_shikona_by_rikid(history: History) -> dict[RikId, Shikona]:
    """
    Return each represented rikishi's latest shikona in the supplied History.

    A rikishi may occur in several basho.  Iterating dates in order and assigning
    each banzuke shikona leaves the final value as the History shikona from the
    rikishi's latest represented basho.
    """
    history_shikona_by_rikid: dict[RikId, Shikona] = {}

    for basho_date in sorted(history):
        banzuke = history[basho_date].banzuke
        for rikid in banzuke.riks:
            history_shikona_by_rikid[rikid] = banzuke.rikshik[rikid]

    return history_shikona_by_rikid

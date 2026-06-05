"""
Build the public shikona map used by publication code.

This module is the production counterpart to the exploratory shikona
normalisation probe.  The probe is evidence for the rule; this module owns the
small deterministic transformation needed by the application:

    History -> dict[RikId, Shikona]

History owns the normal public shikona value.  BioStore owns the facts that are
not part of History: whether a rikishi has retired, and the rikishi's full
recorded latest shikona.
"""

from __future__ import annotations

from collections import Counter

from src.infra.get_bios.api import BioStore, load_bio_store
from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import RikId, Shikona
from src.sumo_core.History import Date, History


DEMO_RIKIDS = (RikId(1123), RikId(12231))


def make_public_shikona(history: History) -> dict[RikId, Shikona]:
    """
    Return the public-facing shikona for every rikishi represented in History.

    The normal public shikona is the latest shikona recorded for the rikishi in
    the supplied History.  If that History shikona is non-unique, the latest
    holder keeps the History shikona and earlier holders use their full latest
    shikona from the get_bios cache.
    """
    return make_public_shikona_from_bios(history, load_bio_store())


def make_public_shikona_from_bios(
    history: History,
    bios: BioStore,
) -> dict[RikId, Shikona]:
    """
    Return public-facing shikona using an explicit BioStore.

    This helper keeps the transformation testable while leaving publication
    callers with the simpler History-only API.
    """
    history_shikona_by_rikid = make_history_shikona_by_rikid(history)
    latest_holder_by_history_shikona = make_latest_holder_by_history_shikona(history)
    history_shikona_counts = Counter(history_shikona_by_rikid.values())

    public_shikona_by_rikid: dict[RikId, Shikona] = {}

    for rikid, history_shikona in history_shikona_by_rikid.items():
        if history_shikona_counts[history_shikona] == 1:
            public_shikona_by_rikid[rikid] = history_shikona
            continue

        if latest_holder_by_history_shikona[history_shikona] == rikid:
            public_shikona_by_rikid[rikid] = history_shikona
            continue

        public_shikona_by_rikid[rikid] = bios[rikid].latest_shikona()

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


def make_latest_history_date_by_rikid(history: History) -> dict[RikId, Date]:
    """Return each represented rikishi's latest represented date in History."""
    latest_history_date_by_rikid: dict[RikId, Date] = {}

    for basho_date in sorted(history):
        for rikid in history[basho_date].banzuke.riks:
            latest_history_date_by_rikid[rikid] = basho_date

    return latest_history_date_by_rikid


def make_latest_holder_by_history_shikona(history: History) -> dict[Shikona, RikId]:
    """Return the latest holder of each History shikona."""
    history_shikona_by_rikid = make_history_shikona_by_rikid(history)
    latest_history_date_by_rikid = make_latest_history_date_by_rikid(history)

    latest_holder_by_history_shikona: dict[Shikona, RikId] = {}

    for rikid, history_shikona in history_shikona_by_rikid.items():
        latest_holder = latest_holder_by_history_shikona.get(history_shikona)

        if latest_holder is None:
            latest_holder_by_history_shikona[history_shikona] = rikid
            continue

        if latest_history_date_by_rikid[latest_holder] < latest_history_date_by_rikid[rikid]:
            latest_holder_by_history_shikona[history_shikona] = rikid

    return latest_holder_by_history_shikona


def main() -> None:
    """Print sample public shikona values for manual inspection."""
    public_shikona_by_rikid = make_public_shikona(get_history())

    for rikid in DEMO_RIKIDS:
        print(f"{rikid}: {public_shikona_by_rikid[rikid]}")


if __name__ == "__main__":
    main()

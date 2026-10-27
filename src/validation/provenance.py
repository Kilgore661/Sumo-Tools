"""Shared deterministic provenance helpers for validation work."""

from __future__ import annotations

import hashlib

from src.sumo_core.History import History


def history_fingerprint(history: History) -> str:
    """Return a deterministic fingerprint of P1-relevant History fields."""

    digest = hashlib.sha256()
    for date in sorted(history):
        digest.update(f"date:{date}\n".encode())
        basho = history[date]
        for rikishi, chii in sorted(
            basho.banzuke.rikchii.items(), key=lambda item: int(item[0])
        ):
            digest.update(f"rank:{int(rikishi)}:{chii.ordinal()}\n".encode())
        for day in sorted(basho.summary):
            bouts = sorted(
                basho.summary[day].results_lookup.values(),
                key=lambda bout: (int(bout.rikishi1), int(bout.rikishi2)),
            )
            for bout in bouts:
                decision = getattr(bout.decision, "value", bout.decision)
                digest.update(
                    (
                        f"bout:{int(day)}:{int(bout.rikishi1)}:"
                        f"{bout.outcome1.name}:{int(bout.rikishi2)}:"
                        f"{bout.outcome2.name}:{decision}\n"
                    ).encode()
                )
    return digest.hexdigest()

"""Transform published evidence into the Elo89a non-appearance ledger."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping

from src.analysis.absences.jsa_check.model import FinalRecord
from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History

from .model import NonAppearanceCount, NonAppearanceLedger


def build_nonappearance_ledger(
    history: History,
    dates: tuple[Date, ...],
    final_records: Mapping[Date, Mapping[RikId, FinalRecord]],
) -> NonAppearanceLedger:
    """Return explicit FP and published-A counts for every selected basho."""

    ledger: NonAppearanceLedger = {}
    for date in dates:
        basho = history[date]
        records = final_records[date]
        missing = set(basho.banzuke.riks) - set(records)
        if missing:
            raise KeyError(
                f"Published final records for {date} omit {len(missing)} ranked rikishi"
            )

        fusen_pai: dict[RikId, int] = defaultdict(int)
        for daily in basho.summary.values():
            for bout in daily.results_lookup.values():
                if bout.outcome1 is Outcome.FP:
                    fusen_pai[bout.rikishi1] += 1
                if bout.outcome2 is Outcome.FP:
                    fusen_pai[bout.rikishi2] += 1

        affected = set(fusen_pai)
        affected.update(
            rikishi
            for rikishi in basho.banzuke.riks
            if records[rikishi].absences > 0
        )
        ledger[date] = {
            rikishi: NonAppearanceCount(
                fusen_pai=fusen_pai[rikishi],
                absences=(
                    records[rikishi].absences
                    if rikishi in basho.banzuke.riks
                    else 0
                ),
            )
            for rikishi in sorted(affected)
        }
    return ledger

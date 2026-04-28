from statistics import fmean, pstdev

from src.analysis.persistence.classes import (
    DivisionPersistenceRow,
    PersistenceResults,
)
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii, Level
from src.sumo_core.History import Date, History


def _division_from_level(level: Level) -> Division:
    if isinstance(level, MSD):
        return Division.MAKUUCHI

    return level


def _division_from_chii(chii: Chii) -> Division:
    return _division_from_level(chii.level)


def _members_by_division(history: History, date: Date) -> dict[Division, set[RikId]]:
    members: dict[Division, set[RikId]] = {
        division: set()
        for division in Division
    }

    banzuke = history(date).banzuke

    for rikishi_id in banzuke.riks:
        division = _division_from_chii(banzuke.rikchii[rikishi_id])
        members[division].add(rikishi_id)

    return members


def _rikishi_persistence(
    history: History,
    rikishi_id: RikId,
    division: Division,
    window: tuple[Date, ...],
) -> float:
    active_count = 0
    division_count = 0

    for date in window:
        banzuke = history(date).banzuke

        if rikishi_id in banzuke.riks:
            active_count += 1

            if _division_from_chii(banzuke.rikchii[rikishi_id]) == division:
                division_count += 1

    return division_count / active_count


def _division_persistence_row(
    history: History,
    date: Date,
    division: Division,
    window: tuple[Date, ...],
    num_basho: int,
    rikishi_ids: set[RikId],
) -> DivisionPersistenceRow:
    values = [
        _rikishi_persistence(
            history=history,
            rikishi_id=rikishi_id,
            division=division,
            window=window,
        )
        for rikishi_id in rikishi_ids
    ]

    return DivisionPersistenceRow(
        date=date,
        division=division,
        num_basho=num_basho,
        frequency=len(values),
        mean_persistence=fmean(values),
        stdev_persistence=pstdev(values),
    )


def compute_division_persistence(
    history: History,
    num_basho: int,
) -> PersistenceResults:
    dates = tuple(sorted(history.keys()))
    rows: list[DivisionPersistenceRow] = []

    for anchor_index in range(num_basho - 1, len(dates)):
        date = dates[anchor_index]
        window = dates[anchor_index - num_basho + 1 : anchor_index + 1]
        members = _members_by_division(history, date)

        for division in Division:
            rows.append(
                _division_persistence_row(
                    history=history,
                    date=date,
                    division=division,
                    window=window,
                    num_basho=num_basho,
                    rikishi_ids=members[division],
                )
            )

    return PersistenceResults(
        num_basho=num_basho,
        rows=tuple(rows),
    )

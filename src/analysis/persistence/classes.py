from dataclasses import dataclass

from src.sumo_core.BasicEnums import Division
from src.sumo_core.History import Date


@dataclass(frozen=True)
class DivisionPersistenceRow:
    date: Date
    division: Division
    num_basho: int
    frequency: int
    mean_persistence: float
    stdev_persistence: float


@dataclass(frozen=True)
class PersistenceResults:
    num_basho: int
    rows: tuple[DivisionPersistenceRow, ...]

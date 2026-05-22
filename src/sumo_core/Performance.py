from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Optional

from .BasicPrimitives import RikId
from .BasicEnums import Prize, Direction


@dataclass(frozen=True)
class Performance:
    """
    Represents awards and status changes for a basho result.
    Immutable version using dataclass(frozen=True).
    """

    prizes: FrozenSet[Prize] = field(default_factory=frozenset)
    updown: Optional[Direction] = None

    def __post_init__(self):
        """
        Validation performed after the auto-generated __init__ runs.
        """
        if Prize.YUSHO in self.prizes and Prize.JUN_YUSHO in self.prizes:
            raise ValueError(
                "Performance cannot contain both YUSHO and JUN_YUSHO prizes"
            )


class Performances(Dict[RikId, Performance]):
    """
    Mapping of RikId to Performance for a single basho.
    """
    pass

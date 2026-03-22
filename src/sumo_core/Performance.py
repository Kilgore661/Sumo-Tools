from dataclasses import dataclass, field
from typing import FrozenSet, Optional

from .BasicEnums import Prize, Direction

@dataclass(frozen=True)
class Performance:
    """
    Represents awards and status changes for a basho result.
    Immutable version using dataclass(frozen=True).
    """
    # Define fields as class attributes with type hints
    # Use FrozenSet for immutability and hashability
    # Use field(default_factory=...) for mutable defaults like sets
    prizes: FrozenSet[Prize] = field(default_factory=frozenset)
    updown: Optional[Direction] = None

    def __post_init__(self):
        """
        Validation performed after the auto-generated __init__ runs.
        """
        # Check for the conflicting major awards constraint
        if Prize.YUSHO in self.prizes and Prize.JUN_YUSHO in self.prizes:
            raise ValueError("Performance cannot contain both YUSHO and JUN_YUSHO prizes")

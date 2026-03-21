from typing import Union, Literal, Optional, Dict, List, Tuple, FrozenSet
# TBD Use hinting throughout
from dataclasses import dataclass, field
from .BasicEnums import Outcome, Symbol, Decision, Prize, Direction
from .Kimarite import Kimarite
from .BasicPrimitives import RikId, Pair, Torikumi, Day

@dataclass
class BoutResult:
    rikishi1: RikId 
    outcome1: Outcome
    rikishi2: RikId
    outcome2: Outcome
    decision: Decision
    symbol: Symbol

    def __post_init__(self):
        """Validate the bout result components"""
        # Validate rikishi IDs
        _ = Pair(self.rikishi1, self.rikishi2)
        
        # Validate outcomes are Outcome enum values
        if not isinstance(self.outcome1, Outcome):
            raise TypeError(f"outcome1 must be Outcome enum, got {type(self.outcome1)}")
        if not isinstance(self.outcome2, Outcome):
            raise TypeError(f"outcome2 must be Outcome enum, got {type(self.outcome2)}")
            
        # Validate outcome consistency
        self._validate_outcome_consistency()
    
    def _validate_outcome_consistency(self):
        #! Val: Implements constraint E3.2.3.3 from the model.
        """
        Ensure the outcomes are consistent with each other.
        """
        outcome_pair = {self.outcome1, self.outcome2}
        valid_pairs = [
            {Outcome.W, Outcome.L},
            {Outcome.FS, Outcome.FP},
            {Outcome.DRAW, Outcome.DRAW}
        ]
        
        if outcome_pair not in valid_pairs:
            raise ValueError(f"Invalid outcome combination: {self.outcome1}, {self.outcome2}")

from typing import Optional
class ResultLookup(dict):
    """
    Maps pairs of rikishi to their bout results.
    Implements the ResultLookup partial function as per E3.2.4.7.
    """
    def __call__(self, pair: Pair) -> Optional[BoutResult]:
        """Implement partial function behavior"""
        return self.get(pair)

    DEMOTION = '↓'

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

@dataclass
class DailyResults:
    # E3.4.1
    torikumi: Torikumi
    results_lookup: ResultLookup
    # A bit weird there is no validation but this is correct as far as the
    # model is concerned - the constraints all come in BashoState where the
    # daily results (inside a summary) are validated.
    #
    # TBD: Is this weird?

class Summary(dict):
    # E3.4.2
    def __init__(self, daily_results_dict, performances=None):
        super().__init__(daily_results_dict)
        self.performances = performances or {}  # Dict[RikId, Performance]
        #! E3.4.3
        days = sorted(self.keys())
        if days and days[0] != 1:
            raise ValueError(f"E3.4.3 Tournament must start with day 1, found: {days[0]}")
            
        for i in range(1, len(days)):
            if days[i] != days[i-1] + 1:
                raise ValueError(f"E3.4.3 Gap in daily records between days {days[i-1]} and {days[i]}")
    
    def __call__(self, day: Day) -> Optional[DailyResults]:
        """Implement partial function behavior for daily results"""
        return self.get(day)

    # TBD doesn't belong here - only used in Score which itself is only used in calc.
    def last_defined(self) -> Optional[Day]:
        """Returns the last day with defined results, or None if summary is empty"""
        return Day(max(self.keys())) if self else None



from typing import Set, Optional

class RikId(int):
    def __new__(cls, value):
        #! Val: We chose numbers to satisfy constraints is S2.1.1.
        if not isinstance(value, (int, RikId)):
            raise TypeError(f"RikId must be created from int, got {type(value)}")
        #! Val: RikId is abstract and doesn't need to be N (so no equation to
        # reference).
        if value <= 0:
            raise ValueError(f"RikId must be positive, got {value}")
        return super(RikId, cls).__new__(cls, value)

class Day(int):
    def __new__(cls, value):
        """
        Create a Day instance ensuring the value is between 1 and 15.
        
        Args:
            value (int): The day of the tournament (1-15)
        
        Raises:
            ValueError: If the day is not between 1 and 15
        """
        if not isinstance(value, int):
            raise TypeError(f"Day must be an integer, got {type(value)}")
        
        #! Val: E3.1.1
        if value < 1 or value > 15:
            raise ValueError(f"E3.1.1 Day must be between 1 and 15, got {value}")
        
        return super().__new__(cls, value)

class oldPair(tuple):
    def __new__(cls, r1: RikId, r2: RikId):
        if not isinstance(r1, RikId) or not isinstance(r2, RikId):
            raise TypeError("Pair must contain two RikIds")
        #! Val: E3.2.4.2
        if r1 == r2:
            raise ValueError("Pair must contain two different RikIds")
        return super().__new__(cls, (r1, r2))

class Pair(tuple):
    def __new__(cls, r1, r2=None):
        # Special case for pickle reconstruction
        if r2 is None and isinstance(r1, tuple) and len(r1) == 2:
            # This branch handles when pickle recreates the tuple with a single argument
            # that contains the tuple elements ie new((r1,r2)) not new(r1,r2)
            r1, r2 = r1
        
        if not isinstance(r1, RikId) or not isinstance(r2, RikId):
            raise TypeError("Pair must contain two RikIds")
        #! Val: E3.2.4.2
        if r1 == r2:
            raise ValueError("Pair must contain two different RikIds")
        return super().__new__(cls, (r1, r2))

class Torikumi(set):
    def __new__(cls, pairs=None):
        if pairs is not None:
            for pair in pairs:
                if not isinstance(pair, Pair):
                    raise TypeError("Torikumi must contain only Pair objects")
            return super().__new__(cls, pairs)
        return super().__new__(cls)
    #! TBD: Val: S3.3.2: consider set operations that add pairs: can't have rik in twice

from typing import NamedTuple

class Score(NamedTuple):
    wins: int
    losses: int
    absences: int
    
    def __post_init__(self):
        # Validation happens here
        if not all(isinstance(x, int) for x in (self.wins, self.losses, self.absences)):
            raise TypeError("Score components must be integers")
            
        if not all(x >= 0 for x in (self.wins, self.losses, self.absences)):
            raise ValueError("Score components must be natural numbers (≥ 0)")
    
    #! Val: S3.1
    def is_valid_for_day(self, day: int) -> bool:
        """Check if the score is valid for the given day"""
        return self.wins + self.losses + self.absences == day

class Riks(frozenset):
    """
    Represents an immutable set of rikishi IDs.
    """
    
    def __new__(cls, riks: Optional[Set[RikId]] = None):
        """
        Create a new Riks collection.
        
        Args:
            riks: Optional set of RikId objects to initialize with
        """
        if riks is None:
            validated_riks = frozenset()
        else:
            # Validate all elements are RikId
            for r in riks:
                if not isinstance(r, RikId):
                    raise TypeError(f"Riks can only contain RikId objects, got {type(r)}")
            validated_riks = frozenset(riks)
            
        return super().__new__(cls, validated_riks)

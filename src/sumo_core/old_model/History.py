from dataclasses import dataclass
from typing import Optional
from .BashoState import BashoState

class Year(int):
    def __new__(cls, value):
        #! Val: We chose numbers to satisfy constraint E?
        if not isinstance(value, int):
            raise TypeError(f"Year must be created from int, got {type(value)}")
        if value < 1958:
            raise ValueError(f"Year must be at least 1958, got {value}")
        return super(Year, cls).__new__(cls, value)

    def __hash__(self):
        return hash(int(self))

class Month(int):
    def __new__(cls, value):
        #! Val: We chose numbers to satisfy constraint E?
        if not isinstance(value, int):
            raise TypeError(f"Month must be created from int, got {type(value)}")
        if value < 1 or value > 11 or value % 2 != 1:
            raise ValueError(f"Month must be an odd number in the range 1 to 11, got {value}")
        return super(Month, cls).__new__(cls, value)

    def __hash__(self):
        return hash(int(self))

@dataclass(frozen=True) # Frozen to make it hashable
class Date:
    year: Year
    month: Month

    def __post_init__(self):
        #! Val: We chose numbers to satisfy constraint E?
        if not isinstance(self.year, Year):
            raise TypeError(f"Date must be created from Year, got {type(self.year)}")
        if not isinstance(self.month, Month):
            raise TypeError(f"Date must be created from Month, got {type(self.month)}")

        
    def __hash__(self):
        return hash((self.year, self.month))

    def __str__(self):
        return f"{self.year}/{self.month:02d}"
    
    # Comparision of dates is not needed by the spec, but it is useful for
    # testing e.g. for finding the max date in a history.
    def __lt__(self, other):
        if not isinstance(other, Date):
            return NotImplemented
        if self.year < other.year:
            return True
        if self.year > other.year:
            return False
        return self.month < other.month

    def __gt__(self, other):
        if not isinstance(other, Date):
            return NotImplemented
        if self.year > other.year:
            return True
        if self.year < other.year:
            return False
        return self.month > other.month

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other


class History(dict):
    """
    A function from Date to BashoState, implemented as a dictionary (E2.3.2)
    """
    
    def __new__(cls, mapping=None):
        """
        Create a new History mapping.
        
        Args:
            mapping: Optional dictionary mapping Date to BashoState
        """
        instance = super().__new__(cls)
        
        if mapping is not None:
            for date, bs in mapping.items():
                if not isinstance(date, Date):
                    raise TypeError(f"Keys must be Date objects, got {type(date)}")
                if not isinstance(bs, BashoState):
                    raise TypeError(f"Values must be BashoState objects, got {type(bs)}")
                instance[date] = bs
        
        return instance
    
    def __call__(self, date: Date) -> Optional[BashoState]:
        """Implement function-like behavior"""
        return self.get(date)

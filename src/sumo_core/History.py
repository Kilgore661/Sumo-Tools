from dataclasses import dataclass
from .BashoState import BashoState
from .BasicPrimitives import Year, Month

################################################################################

@dataclass(frozen=True)
class Date:
    """
    Date value object for sumo history.

    A Date represents a basho date as a pair (Year, Month).

    It is immutable, hashable, and orderable.
    Its string form is "YYYY/MM".
    """

    year: Year
    month: Month

    def __str__(self) -> str:
        return f"{self.year}/{self.month:02d}"

    def __lt__(self, other: "Date") -> bool:
        return self.year < other.year or (
            self.year == other.year and self.month < other.month
        )

    def __gt__(self, other: "Date") -> bool:
        return self.year > other.year or (
            self.year == other.year and self.month > other.month
        )

    def __le__(self, other: "Date") -> bool:
        return self < other or self == other

    def __ge__(self, other: "Date") -> bool:
        return self > other or self == other
################################################################################

class History(dict):

    """
    Canonical transitional history model.

    NOTE:
    - File name: History.py
    - Class name: History 
    - Will be renamed to History once migration is complete

    Represents the complete recorded history of basho.

    A History is a partial function:

        Date -> BashoState

    Implemented as a dictionary with function-call syntax.
    """

    def __new__(cls, mapping=None):
        instance = super().__new__(cls)

        if mapping is not None:
            for date, basho_state in mapping.items():
                if not isinstance(date, Date):
                    raise TypeError(
                        f"Keys in History must be Date objects, got {type(date)}"
                    )

                if not isinstance(basho_state, BashoState):
                    raise TypeError(
                        "Values in History must be "
                        f"BashoState objects, got {type(basho_state)}"
                    )

                instance[date] = basho_state

        return instance

    def __call__(self, date: Date):
        """
        Return the BashoState for the given date,
        or None if undefined.
        """
        return self[date]

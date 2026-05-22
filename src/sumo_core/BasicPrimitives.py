class RikId(int):
    """
    RikId value object for sumo history.

    Represents the unique identifier of a rikishi.

    Invariant:
    - RikId must be a positive integer

    This is an immutable, hashable value object.
    """

    def __new__(cls, value: int) -> "RikId":
        if value <= 0:
            raise ValueError(f"RikId must be positive, got {value}")

        return int.__new__(cls, value)

    def __repr__(self) -> str:
        return f"{int(self)}"

    def __str__(self) -> str:
        return str(int(self))

################################################################################

class Day(int):
    """
    Day value object for sumo history.

    Represents a day within a basho.

    Invariant:
    - Day must be in range 1..15
    """

    MIN_DAY = 1
    MAX_DAY = 15

    def __new__(cls, value: int) -> "Day":
        if not (cls.MIN_DAY <= value <= cls.MAX_DAY):
            raise ValueError(
                f"Day must be in range {cls.MIN_DAY}..{cls.MAX_DAY}, got {value}"
            )

        return int.__new__(cls, value)

    def __repr__(self) -> str:
        return f"{int(self)}"

    def __str__(self) -> str:
        return str(int(self))

################################################################################

class Month(int):
    """
    Month value object for sumo history.

    Represents a basho month.

    Invariants:
    - Month must be in range 1..12
    - Month must be odd (sumo tournaments occur in odd months only)

    This is an immutable, hashable value object.
    """

    MIN_MONTH = 1
    MAX_MONTH = 12

    def __new__(cls, value: int) -> "Month":
        if not (cls.MIN_MONTH <= value <= cls.MAX_MONTH):
            raise ValueError(f"Month must be in range {cls.MIN_MONTH}..{cls.MAX_MONTH}, got {value}")

        if value % 2 == 0:
            raise ValueError(f"Month must be odd, got {value}")

        return int.__new__(cls, value)

    def __repr__(self) -> str:
        return f"{int(self)}"

    def __str__(self) -> str:
        return str(int(self))

################################################################################

class Year(int):
    """
    Year value object for sumo history.

    A Year represents a calendar year in professional sumo records.
    Valid years begin at 1958, the start of the modern six-basho system.

    This is an immutable, hashable type suitable for use as a key
    in dictionaries (e.g. within Date and History).
    """

    """
    Strongly-typed representation of a sumo calendar year.

    This class subclasses int to allow natural ordering and comparison,
    while enforcing domain-specific constraints at construction time.

    Example:
        y = Year(2024)
        assert y > Year(2000)
    """

    MIN_YEAR = 1958

    def __new__(cls, value: int) -> "Year":
        """
        Create a new Year instance.

        Args:
            value: Integer year (e.g. 2024)

        Returns:
            Year: validated year instance

        Raises:
            ValueError: if value is before MIN_YEAR
        """

        if value < cls.MIN_YEAR:
            raise ValueError(
                f"Year must be >= {cls.MIN_YEAR}, got {value}"
            )

        return int.__new__(cls, value)

    def __repr__(self) -> str:
        return f"{int(self)}"

    def __str__(self) -> str:
        return str(int(self))

################################################################################

class Pair(tuple):
    """
    Pair value object for sumo history.

    Represents an unordered pair of distinct rikishi IDs.

    This is implemented as a tuple subclass.

    Notes:
    - The two rikishi must be distinct.
    - The special tuple-unpacking branch is preserved because it is needed
      for reconstruction in some contexts (notably pickling).
    """

    def __new__(cls, r1: RikId, r2: RikId = None):
        """
        Create a canonical pair of distinct rikishi IDs.

        The pair is stored in sorted order so that:
            Pair(a, b) == Pair(b, a)

        The alternate tuple-unpacking branch is preserved for reconstruction.
        """
        if r2 is None:
            r1, r2 = r1

        if r1 == r2:
            raise ValueError(f"Pair members must be distinct, got {r1} and {r2}")

        return super(Pair, cls).__new__(cls, tuple(sorted((r1, r2))))

    def __repr__(self) -> str:
        return f"({self[0]}, {self[1]})"

    def __str__(self) -> str:
        return f"({self[0]}, {self[1]})"

################################################################################

class Torikumi(set):
    """
    Torikumi value object for sumo history.

    Represents a set of Pair.

    This class does not currently enforce the stronger tournament-level
    constraint that the same rikishi cannot appear twice. That belongs
    to a higher-level validation step if and when it is implemented.
    """

    def __new__(cls, pairs=None):
        if pairs is not None:
            return super().__new__(cls, pairs)
        return super().__new__(cls)

################################################################################

class Riks(frozenset):
    """
    Riks value object for sumo history.

    Represents a set of RikId.

    This is an immutable collection. No constraints are enforced
    on the elements beyond the class contract: they are expected
    to be RikId.
    """

    def __new__(cls, iterable=()):
        return super().__new__(cls, iterable)

    def __repr__(self) -> str:
        return f"{set(self)}"

    def __str__(self) -> str:
        return str(set(self))

################################################################################

class Shikona(str):
    """
    Shikona value object for sumo history.

    Represents a rikishi's shikona.
    """
    pass

################################################################################

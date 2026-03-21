"""
Year value object for sumo history.

A Year represents a calendar year in professional sumo records.
Valid years begin at 1958, the start of the modern six-basho system.

This is an immutable, hashable type suitable for use as a key
in dictionaries (e.g. within Date and History).
"""

from __future__ import annotations


class Year(int):
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

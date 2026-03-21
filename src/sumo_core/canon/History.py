"""
Canonical transitional history model.

NOTE:
- File name: History.py
- Class name: HistoryWithAnnotations (temporary)
- Will be renamed to History once migration is complete

Represents the complete recorded history of basho.

A History is a partial function:

    Date -> BashoStateWithAnnotations

Implemented as a dictionary with function-call syntax.
"""

from __future__ import annotations

from Date import Date
from BashoState import BashoStateWithAnnotations


class HistoryWithAnnotations(dict):
    def __new__(cls, mapping=None):
        instance = super().__new__(cls)

        if mapping is not None:
            for date, basho_state in mapping.items():
                if not isinstance(date, Date):
                    raise TypeError(
                        f"Keys in HistoryWithAnnotations must be Date objects, got {type(date)}"
                    )

                if not isinstance(basho_state, BashoStateWithAnnotations):
                    raise TypeError(
                        "Values in HistoryWithAnnotations must be "
                        f"BashoStateWithAnnotations objects, got {type(basho_state)}"
                    )

                instance[date] = basho_state

        return instance

    def __call__(self, date: Date):
        """
        Return the BashoStateWithAnnotations for the given date,
        or None if undefined.
        """
        return self[date]

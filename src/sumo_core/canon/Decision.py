from __future__ import annotations
"""
Decision value object for sumo history.

Represents how a bout result was decided.

A Decision is one of:
- a Kimarite (normal bout resolution), or
- the string "fusen" (win by default), or
- the string "blank" (no result recorded)

This is implemented as a constrained value constructor rather than an enum,
because the domain is a union of an enum (Kimarite) and special string values.
"""

from typing import Union, Literal
from Kimarite import Kimarite

class Decision:
    def __new__(cls, value: Union[Kimarite, Literal["fusen", "blank"]]):
        if not (isinstance(value, Kimarite) or value in ("fusen", "blank")):
            raise TypeError(f"Decision must be Kimarite or special outcome, got {type(value)}")
        return value

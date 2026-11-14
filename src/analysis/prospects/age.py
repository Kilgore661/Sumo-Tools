"""Civil-age helpers used by the Prospects calculation."""

from __future__ import annotations

from datetime import date


def completed_years(birth_date: date, as_of: date) -> int:
    years = as_of.year - birth_date.year
    anniversary = _birthday_in_year(birth_date, as_of.year)
    return years - (as_of < anniversary)


def _birthday_in_year(birth_date: date, year: int) -> date:
    try:
        return birth_date.replace(year=year)
    except ValueError:
        return date(year, 3, 1)

"""
Small utility helpers for the standings package.

Contains narrow, reusable formatting and filename helpers that do not
belong to the core domain model.
"""

def escape_date(date) -> str:
    return str(date).replace("/", "_")

"""Resolve the active or upcoming basho whose torikumi should be acquired."""

from __future__ import annotations

from dataclasses import dataclass

from src.infra.new_banzuke.api import NewBanzuke
from src.sumo_core.Banzuke import Banzuke
from src.sumo_core.BasicPrimitives import Day
from src.sumo_core.History import Date, History


@dataclass(frozen=True, slots=True)
class TorikumiTarget:
    date: Date
    banzuke: Banzuke
    completed_through: Day | None
    source: str


def resolve_torikumi_target(
    history: History,
    new_banzuke: NewBanzuke | None,
) -> TorikumiTarget | None:
    """Return the represented active basho or its published successor."""

    if not history:
        raise ValueError("Cannot resolve Torikumi target from an empty History")
    latest_date = max(history)
    latest_state = history[latest_date]
    completed = latest_state.summary.last_defined()
    if completed is None or int(completed) < 15:
        return TorikumiTarget(
            date=latest_date,
            banzuke=latest_state.banzuke,
            completed_through=completed,
            source="active History basho",
        )

    if new_banzuke is None or new_banzuke.date <= latest_date:
        return None
    expected = next_basho_date(latest_date)
    if new_banzuke.date != expected:
        raise ValueError(
            "New Banzuke is not the immediate successor to completed History: "
            f"History ends={latest_date}, expected={expected}, "
            f"New Banzuke={new_banzuke.date}"
        )
    return TorikumiTarget(
        date=new_banzuke.date,
        banzuke=new_banzuke.to_banzuke(),
        completed_through=None,
        source="published New Banzuke",
    )


def next_basho_date(date: Date) -> Date:
    month = int(date.month) + 2
    year = int(date.year)
    if month > 12:
        month -= 12
        year += 1
    return Date.from_ints(year, month)

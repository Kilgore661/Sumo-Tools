"""Record helpers for Basho Results Browser."""

from __future__ import annotations

from src.analysis.banzuke_compare.results import (
    calculate_record,
    format_prizes,
    format_record,
)
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.Summary import Summary


def format_result(rikishi_id: RikId, chii: Chii, summary: Summary) -> str:
    """Format one rikishi's basho result using Banzuke Change Report rules."""

    wins, losses, absences = calculate_record(
        rikishi_id=rikishi_id,
        chii=chii,
        summary=summary,
    )
    return format_record(wins=wins, losses=losses, absences=absences)


def format_result_with_prizes(rikishi_id: RikId, chii: Chii, summary: Summary) -> str:
    """Format a result with Banzuke Change Report prize suffixes."""

    record = format_result(rikishi_id=rikishi_id, chii=chii, summary=summary)
    prize_suffix = format_prizes(rikishi_id, summary)
    if prize_suffix:
        return f"{record} {prize_suffix}"
    return record


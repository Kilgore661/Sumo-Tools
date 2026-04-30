"""
Previous-result formatting for the Banzuke Change Report.
"""

from src.analysis.news.classes import BanzukeChange
from src.sumo_core.BasicEnums import Outcome, Prize
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.Summary import Summary
from src.sumo_core.BasicEnums import Division, MSD


def format_previous_result(change: BanzukeChange, summary: Summary) -> str:
    """
    Contract:
        change is a neutral BCR fact.  summary is the previous basho summary.

        Returns the previous-basho result display for this rikishi, including
        prizes when present.  Entrants and rikishi with unavailable previous
        rank context return an empty string.
    """

    if change.previous_chii is None:
        return ""

    wins, losses, absences = calculate_record(
        rikishi_id=change.rikishi_id,
        chii=change.previous_chii,
        summary=summary,
    )
    record = format_record(wins=wins, losses=losses, absences=absences)
    prize_suffix = format_prizes(change.rikishi_id, summary)

    if prize_suffix:
        return f"{record} {prize_suffix}"

    return record


def calculate_record(
    rikishi_id: RikId,
    chii: Chii,
    summary: Summary,
) -> tuple[int, int, int]:
    """
    Contract:
        rikishi_id appeared on the previous banzuke at chii.

        Returns credited wins, losses, and absences for the previous basho.
    """

    wins = 0
    losses = 0
    available_bouts = 0

    for daily_results in summary.values():
        for bout in daily_results.results_lookup.values():
            if bout.rikishi1 == rikishi_id:
                available_bouts += 1
                if bout.outcome1 in {Outcome.W, Outcome.FS}:
                    wins += 1
                elif bout.outcome1 in {Outcome.L, Outcome.FP}:
                    losses += 1
            elif bout.rikishi2 == rikishi_id:
                available_bouts += 1
                if bout.outcome2 in {Outcome.W, Outcome.FS}:
                    wins += 1
                elif bout.outcome2 in {Outcome.L, Outcome.FP}:
                    losses += 1

    absences = expected_bouts_for_chii(chii) - available_bouts

    return wins, losses, absences


def expected_bouts_for_chii(chii: Chii) -> int:
    """
    Contract:
        chii is the rikishi's previous-basho rank.

        Returns the expected number of bouts for record display.
    """

    if isinstance(chii.level, MSD):
        return 15

    if chii.level == Division.JURYO:
        return 15

    return 7


def format_record(wins: int, losses: int, absences: int) -> str:
    """
    Contract:
        wins/losses/absences are the final previous-basho record components.

        Returns the compact sumo record string.
    """

    if absences:
        return f"{wins}-{losses}-{absences}"

    return f"{wins}-{losses}"


def format_prizes(rikishi_id: RikId, summary: Summary) -> str:
    """
    Contract:
        summary.performances contains prize metadata for the previous basho.

        Returns concatenated prize abbreviations, or an empty string.
    """

    performance = summary.performances.get(rikishi_id)

    if performance is None:
        return ""

    prize_order = (Prize.YUSHO, Prize.DOTEN_YUSHO, Prize.JUN_YUSHO, Prize.KANTO, Prize.SHUKUN, Prize.GINO)
    prize_abbreviations = {
        Prize.YUSHO: "Y",
        Prize.DOTEN_YUSHO: "D",
        Prize.JUN_YUSHO: "J",
        Prize.KANTO: "K",
        Prize.SHUKUN: "S",
        Prize.GINO: "G",
    }

    return "".join(
        prize_abbreviations[prize]
        for prize in prize_order
        if prize in performance.prizes
    )

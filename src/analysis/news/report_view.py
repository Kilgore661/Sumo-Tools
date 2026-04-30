"""
Browser-facing report model contract for the Banzuke Change Report.
"""

from src.analysis.news.classes import (
    BanzukeChange,
    BanzukeDiff,
    BcrDivisionReport,
    BcrReport,
    BcrReportRow,
    BcrReportSide,
)
from src.analysis.news.results import format_previous_result
from src.analysis.news.shikona_links import graph_shikona_for
from src.sumo_core.BasicEnums import Division, Side


DIVISION_ORDER = (
    Division.MAKUUCHI,
    Division.JURYO,
    Division.MAKUSHITA,
    Division.SANDANME,
    Division.JONIDAN,
    Division.JONOKUCHI,
)

DIVISION_IDS = {
    Division.MAKUUCHI: "makuuchi",
    Division.JURYO: "juryo",
    Division.MAKUSHITA: "makushita",
    Division.SANDANME: "sandanme",
    Division.JONIDAN: "jonidan",
    Division.JONOKUCHI: "jonokuchi",
}

DIVISION_LABELS = {
    Division.MAKUUCHI: "Makuuchi",
    Division.JURYO: "Juryo",
    Division.MAKUSHITA: "Makushita",
    Division.SANDANME: "Sandanme",
    Division.JONIDAN: "Jonidan",
    Division.JONOKUCHI: "Jonokuchi",
}


def build_bcr_report(diff: BanzukeDiff) -> BcrReport:
    """
    Contract:
        diff satisfies banzuke_diff.build_banzuke_diff's output contract.

        Returns a browser-neutral BCR report whose rows can be serialized
        directly to the CSV/config data contract.
    """

    divisions = tuple(
        build_division_report(diff=diff, division=division)
        for division in DIVISION_ORDER
        if any(change.current_division == division for change in diff.changes)
    )

    return BcrReport(
        diff=diff,
        divisions=divisions,
    )


def build_division_report(
    diff: BanzukeDiff,
    division: Division,
) -> BcrDivisionReport:
    """
    Contract:
        diff contains at least one current-banzuke change in division.

        Returns the browser-facing rows for that division.
    """

    changes = tuple(
        change
        for change in diff.changes
        if change.current_division == division
    )

    return BcrDivisionReport(
        division=division,
        division_id=DIVISION_IDS[division],
        division_label=DIVISION_LABELS[division],
        rows=build_division_rows(diff=diff, changes=changes),
    )


def build_division_rows(
    diff: BanzukeDiff,
    changes: tuple[BanzukeChange, ...],
) -> tuple[BcrReportRow, ...]:
    """
    Contract:
        changes are current-banzuke facts from a single division, ordered by
        current rank.

        Returns one row per displayed bz_chii.
    """

    rows: list[BcrReportRow] = []
    pending_bz_chii = None
    east = None
    west = None

    for change in changes:
        if pending_bz_chii is None:
            pending_bz_chii = change.current_bz_chii

        if change.current_bz_chii != pending_bz_chii:
            rows.append(make_row(pending_bz_chii, east, west))
            pending_bz_chii = change.current_bz_chii
            east = None
            west = None

        side = build_report_side(diff=diff, change=change)

        if change.current_side == Side.EAST:
            if east is not None:
                raise ValueError(f"Duplicate east rikishi for {change.current_bz_chii}")
            east = side
        elif change.current_side == Side.WEST:
            if west is not None:
                raise ValueError(f"Duplicate west rikishi for {change.current_bz_chii}")
            west = side
        else:
            raise ValueError(f"Current BCR row has no east/west side: {change.current_chii}")

    rows.append(make_row(pending_bz_chii, east, west))

    return tuple(rows)


def make_row(
    bz_chii: str,
    east: BcrReportSide | None,
    west: BcrReportSide | None,
) -> BcrReportRow:
    """
    Contract:
        bz_chii is the displayed row rank.  At least one side is populated.

        Returns one browser-facing row.
    """

    if east is None and west is None:
        raise ValueError(f"BCR row has no east or west side: {bz_chii}")

    return BcrReportRow(
        bz_chii=bz_chii,
        east=east,
        west=west,
    )


def build_report_side(
    diff: BanzukeDiff,
    change: BanzukeChange,
) -> BcrReportSide:
    """
    Contract:
        change is a current-banzuke fact from diff.

        Returns the browser-facing side payload.
    """

    return BcrReportSide(
        rikishi_id=change.rikishi_id,
        shikona=change.current_shikona,
        graph_shikona=graph_shikona_for(change.rikishi_id, change.current_shikona),
        old_chii="" if change.previous_chii is None else str(change.previous_chii),
        previous_result=format_previous_context(change, diff),
        delta=format_delta(change.local_delta),
        delta_class=delta_class(change.local_delta),
    )


def format_previous_context(change: BanzukeChange, diff: BanzukeDiff) -> str:
    """
    Contract:
        change is a current-banzuke fact from diff.

        Returns the previous-basho context string shown in the Result column.
        Division-crossing markers are appended when the rikishi's current
        division represents a promotion or demotion from the previous banzuke.
    """

    result = format_previous_result(change, diff.source.previous_summary)
    marker = division_change_marker(change)

    if result and marker:
        return f"{result} {marker}"

    if marker:
        return marker

    return result


def division_change_marker(change: BanzukeChange) -> str:
    """
    Contract:
        change is a neutral BCR fact.

        Returns an arrow when the current division differs from the previous
        division: up for promotion, down for demotion.
    """

    if change.previous_division is None:
        return ""

    if change.current_division == change.previous_division:
        return ""

    previous_index = DIVISION_ORDER.index(change.previous_division)
    current_index = DIVISION_ORDER.index(change.current_division)

    if current_index < previous_index:
        return "↑"

    return "↓"


def format_delta(delta: float | None) -> str:
    """
    Contract:
        delta is the pair-local observed-slot movement metric, or None.

        Returns the display string.
    """

    if delta is None:
        return ""

    if delta == 0:
        return "0"

    return f"{delta:+.1f}"


def delta_class(delta: float | None) -> str:
    """
    Contract:
        delta is the pair-local observed-slot movement metric, or None.

        Returns the CSS class suffix expected by the BCR browser table.
    """

    if delta is None:
        return ""

    if delta == 0:
        return "neutral"

    direction = "up" if delta > 0 else "down"
    magnitude = abs(delta)

    if magnitude <= 1.5:
        band = "low"
    elif magnitude <= 3.0:
        band = "mid"
    else:
        band = "high"

    return f"{direction} {band}"

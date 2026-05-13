"""Build Basho Results Browser producer data."""

from __future__ import annotations

from datetime import datetime, timezone

from src.analysis.banzuke_compare.banzuke_diff import (
    calculate_local_deltas,
    division_for_chii,
)
from src.analysis.banzuke_compare.report_view import format_delta as format_bcr_delta
from src.analysis.banzuke_compare.shikona_links import graph_shikona_for
from src.analysis.sumo_history.basho_results.classes import (
    MISSING,
    BashoResultsIndex,
    BashoResultsIndexEntry,
    BashoResultsRow,
)
from src.analysis.sumo_history.basho_results.dates import (
    basho_label,
    next_history_date,
    payload_file_name,
    previous_represented_date,
    represented_dates,
    status_for_date,
)
from src.analysis.sumo_history.basho_results.ratings import (
    RatingLookup,
    format_delta,
    format_rating,
)
from src.analysis.sumo_history.basho_results.records import (
    format_result,
    format_result_with_prizes,
)
from src.sumo_core.BasicEnums import Division
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


DIVISION_LABELS = {
    Division.MAKUUCHI: "Makuuchi",
    Division.JURYO: "Juryo",
    Division.MAKUSHITA: "Makushita",
    Division.SANDANME: "Sandanme",
    Division.JONIDAN: "Jonidan",
    Division.JONOKUCHI: "Jonokuchi",
}

DIVISION_IDS = {
    Division.MAKUUCHI: "makuuchi",
    Division.JURYO: "juryo",
    Division.MAKUSHITA: "makushita",
    Division.SANDANME: "sandanme",
    Division.JONIDAN: "jonidan",
    Division.JONOKUCHI: "jonokuchi",
}


def build_index(history: History) -> BashoResultsIndex:
    dates = represented_dates(history)
    entries = tuple(build_index_entry(history, dates, date) for date in dates)
    default_basho = entries[-1].basho if entries else ""
    return BashoResultsIndex(
        schema="sumo-tools.basho-results.index.v0",
        generated_at=datetime.now(timezone.utc).isoformat(),
        default_basho=default_basho,
        entries=entries,
    )


def build_index_entry(
    history: History,
    dates: tuple[Date, ...],
    date: Date,
) -> BashoResultsIndexEntry:
    return BashoResultsIndexEntry(
        basho=str(date),
        year=int(date.year),
        month=int(date.month),
        label=basho_label(date),
        status=status_for_date(history, dates, date),
        latest_day=int(history(date).summary.last_defined()),
        payload_path=f"data/by-basho/{payload_file_name(date)}",
    )


def build_payload_rows(
    *,
    history: History,
    date: Date,
    ratings: RatingLookup,
) -> tuple[BashoResultsRow, ...]:
    dates = represented_dates(history)
    previous_date = previous_represented_date(dates, date)
    next_date = next_history_date(history, date)
    current_state = history(date)
    previous_state = history(previous_date) if previous_date is not None else None
    next_state = history(next_date) if next_date is not None else None

    previous_deltas = (
        calculate_local_deltas(
            previous_banzuke=previous_state.banzuke,
            current_banzuke=current_state.banzuke,
        )
        if previous_state is not None
        else {}
    )

    rows = []
    for rikishi_id in sorted(
        current_state.banzuke.riks,
        key=lambda rid: current_state.banzuke.get_chii(rid),
    ):
        chii = current_state.banzuke.get_chii(rikishi_id)
        division = division_for_chii(chii)
        rows.append(
            build_row(
                history=history,
                date=date,
                rikishi_id=rikishi_id,
                chii=chii,
                division=division,
                ratings=ratings,
                previous_date=previous_date,
                previous_state=previous_state,
                next_state=next_state,
                previous_delta=previous_deltas.get(rikishi_id),
            )
        )
    return tuple(rows)


def build_row(
    *,
    history: History,
    date: Date,
    rikishi_id: RikId,
    chii: Chii,
    division: Division,
    ratings: RatingLookup,
    previous_date: Date | None,
    previous_state,
    next_state,
    previous_delta: float | None,
) -> BashoResultsRow:
    current_state = history(date)
    previous_chii = (
        previous_state.banzuke.get_chii(rikishi_id)
        if previous_state is not None and rikishi_id in previous_state.banzuke
        else None
    )
    previous_equelo = (
        ratings.end_rating(
            history=history,
            date=previous_date,
            rikishi_id=rikishi_id,
        )
        if previous_date is not None
        else None
    )
    start_equelo = ratings.start_rating(
        history=history,
        previous_date=previous_date,
        rikishi_id=rikishi_id,
        chii=chii,
    )
    equelo = ratings.end_rating(history=history, date=date, rikishi_id=rikishi_id)
    delta_equelo = (
        equelo - start_equelo
        if equelo is not None and start_equelo is not None
        else None
    )
    nu_chii = (
        next_state.banzuke.get_chii(rikishi_id)
        if next_state is not None and rikishi_id in next_state.banzuke
        else None
    )
    shikona = current_state.banzuke.get_shik(rikishi_id)

    return BashoResultsRow(
        basho=str(date),
        division_id=DIVISION_IDS[division],
        division_label=DIVISION_LABELS[division],
        rikishi_id=str(int(rikishi_id)),
        shikona=str(shikona),
        graph_shikona=graph_shikona_for(rikishi_id, shikona),
        chii=str(chii),
        chii_ordinal=str(chii.ordinal()),
        score=format_result(rikishi_id, chii, current_state.summary),
        previous_delta_direction=format_previous_delta_direction(previous_delta),
        previous_delta=normalise_missing(format_bcr_delta(previous_delta)),
        previous_result=format_previous_result(
            rikishi_id=rikishi_id,
            previous_chii=previous_chii,
            previous_state=previous_state,
        ),
        previous_chii=format_chii(previous_chii),
        previous_chii_ordinal=format_chii_ordinal(previous_chii),
        previous_equelo=format_rating(previous_equelo),
        equelo=format_rating(equelo),
        delta_equelo=format_delta(delta_equelo),
        nu_chii=format_chii(nu_chii),
        nu_chii_ordinal=format_chii_ordinal(nu_chii),
    )


def format_previous_result(*, rikishi_id: RikId, previous_chii: Chii | None, previous_state) -> str:
    if previous_state is None or previous_chii is None:
        return MISSING
    return format_result_with_prizes(rikishi_id, previous_chii, previous_state.summary)


def format_chii(chii: Chii | None) -> str:
    if chii is None:
        return MISSING
    return str(chii)


def format_chii_ordinal(chii: Chii | None) -> str:
    if chii is None:
        return MISSING
    return str(chii.ordinal())


def normalise_missing(value: str) -> str:
    if value == "":
        return MISSING
    return value


def format_previous_delta_direction(delta: float | None) -> str:
    if delta is None:
        return MISSING
    if delta > 0:
        return "↑"
    if delta < 0:
        return "↓"
    return ""

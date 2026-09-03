"""Consume optional playoff detail from a ``History``.

The current ``History`` model has no playoff detail.  The parser is expected
eventually to add a ``history.playoffs`` mapping whose keys are basho ``Date``
objects and whose values are iterables of objects with these attributes:

``sequence``, ``winner_id``, ``loser_id`` and ``source``.

This module deliberately uses that structural contract rather than depending
on a concrete parser class.  Old histories therefore remain usable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Protocol

from src.sumo_core.BasicEnums import MSD, Prize
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


class PlayoffBoutLike(Protocol):
    """The smallest playoff-bout shape required by the GOAT producer."""

    sequence: int
    winner_id: RikId
    loser_id: RikId
    source: str


class PlayoffDataStatus(Enum):
    """Availability of detailed playoff bouts for one basho."""

    NO_PLAYOFF = "no_playoff"
    UNAVAILABLE = "unavailable"
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


@dataclass(frozen=True)
class PlayoffBout:
    """Stable GOAT-side projection of a parser-owned playoff bout."""

    sequence: int
    winner_id: RikId
    loser_id: RikId
    source: str


@dataclass(frozen=True)
class PlayoffEvidence:
    """Playoff evidence and its completeness for one basho."""

    basho: Date
    status: PlayoffDataStatus
    expected_participants: frozenset[RikId]
    bouts: tuple[PlayoffBout, ...]
    issues: tuple[str, ...] = ()

    @property
    def is_complete(self) -> bool:
        return self.status in {
            PlayoffDataStatus.NO_PLAYOFF,
            PlayoffDataStatus.COMPLETE,
        }


@dataclass(frozen=True)
class RikishiPlayoffRecord:
    """A rikishi's playoff record over a selected set of basho.

    Appearances come from Y/D markers and remain available without detailed
    bouts.  Wins and losses are ``None`` if detail is missing for any playoff
    in which the rikishi appeared; partial totals are not presented as final
    totals.
    """

    rikishi_id: RikId
    appearances: int
    wins: int | None
    losses: int | None
    unavailable_basho: tuple[Date, ...]

    @property
    def bout_record_available(self) -> bool:
        return not self.unavailable_basho


_MISSING = object()


def playoff_evidence(history: History, basho: Date) -> PlayoffEvidence:
    """Return normalized playoff detail without requiring new parser data."""

    state = history(basho)
    expected = _marked_playoff_participants(state)
    raw_playoffs = getattr(history, "playoffs", None)

    if raw_playoffs is None:
        return PlayoffEvidence(
            basho=basho,
            status=(
                PlayoffDataStatus.UNAVAILABLE
                if expected
                else PlayoffDataStatus.NO_PLAYOFF
            ),
            expected_participants=expected,
            bouts=(),
        )

    try:
        raw_bouts = raw_playoffs.get(basho, _MISSING)
    except AttributeError as exc:
        raise TypeError("history.playoffs must provide mapping-style get()") from exc

    if raw_bouts is _MISSING:
        return PlayoffEvidence(
            basho=basho,
            status=(
                PlayoffDataStatus.UNAVAILABLE
                if expected
                else PlayoffDataStatus.NO_PLAYOFF
            ),
            expected_participants=expected,
            bouts=(),
        )

    bouts = _normalize_bouts(raw_bouts)
    actual = frozenset(
        rikishi_id
        for bout in bouts
        for rikishi_id in (bout.winner_id, bout.loser_id)
    )
    issues: list[str] = []

    if not expected:
        issues.append("Playoff bouts are present but no Y/D participants are marked")
    if actual != expected:
        issues.append(
            "Playoff participants do not match Y/D markers: "
            f"expected={sorted(map(int, expected))}, "
            f"actual={sorted(map(int, actual))}"
        )

    return PlayoffEvidence(
        basho=basho,
        status=(
            PlayoffDataStatus.COMPLETE
            if expected and not issues
            else PlayoffDataStatus.INCOMPLETE
        ),
        expected_participants=expected,
        bouts=bouts,
        issues=tuple(issues),
    )


def rikishi_playoff_record(
    history: History,
    rikishi_id: RikId,
    dates: Iterable[Date] | None = None,
) -> RikishiPlayoffRecord:
    """Calculate appearances and, when available, detailed playoff record."""

    selected_dates = tuple(sorted(history if dates is None else dates))
    appearances = 0
    wins = 0
    losses = 0
    unavailable: list[Date] = []

    for basho in selected_dates:
        evidence = playoff_evidence(history, basho)
        if rikishi_id not in evidence.expected_participants:
            continue

        appearances += 1
        if evidence.status is not PlayoffDataStatus.COMPLETE:
            unavailable.append(basho)
            continue

        wins += sum(bout.winner_id == rikishi_id for bout in evidence.bouts)
        losses += sum(bout.loser_id == rikishi_id for bout in evidence.bouts)

    complete = not unavailable
    return RikishiPlayoffRecord(
        rikishi_id=rikishi_id,
        appearances=appearances,
        wins=wins if complete else None,
        losses=losses if complete else None,
        unavailable_basho=tuple(unavailable),
    )


def _marked_playoff_participants(state) -> frozenset[RikId]:
    performances = state.summary.performances
    makuuchi = {
        rikishi_id
        for rikishi_id in state.banzuke.riks
        if isinstance(state.banzuke.get_chii(rikishi_id).level, MSD)
    }
    playoff_markers = {Prize.YUSHO, Prize.DOTEN_YUSHO}
    marked = {
        rikishi_id
        for rikishi_id, performance in performances.items()
        if rikishi_id in makuuchi and performance.prizes & playoff_markers
    }
    has_doten = any(
        rikishi_id in makuuchi and Prize.DOTEN_YUSHO in performance.prizes
        for rikishi_id, performance in performances.items()
    )
    return frozenset(marked if has_doten else ())


def _normalize_bouts(raw_bouts: Iterable[PlayoffBoutLike]) -> tuple[PlayoffBout, ...]:
    bouts: list[PlayoffBout] = []
    sequences: set[int] = set()

    for raw in raw_bouts:
        try:
            sequence = raw.sequence
            winner_id = RikId(raw.winner_id)
            loser_id = RikId(raw.loser_id)
            source = raw.source
        except AttributeError as exc:
            raise TypeError(
                "Each playoff bout must provide sequence, winner_id, "
                "loser_id and source"
            ) from exc

        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence <= 0:
            raise ValueError(f"Playoff sequence must be a positive integer, got {sequence!r}")
        if sequence in sequences:
            raise ValueError(f"Duplicate playoff sequence: {sequence}")
        if winner_id == loser_id:
            raise ValueError(f"A playoff rikishi cannot face himself: {winner_id}")
        if not isinstance(source, str) or not source.strip():
            raise ValueError("Playoff source must be a non-empty string")

        sequences.add(sequence)
        bouts.append(
            PlayoffBout(
                sequence=sequence,
                winner_id=winner_id,
                loser_id=loser_id,
                source=source.strip(),
            )
        )

    return tuple(sorted(bouts, key=lambda bout: bout.sequence))

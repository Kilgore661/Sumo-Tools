from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.sumo_core.BasicEnums import Annotation, Division, MSD, Side
from src.sumo_core.Chii import Chii


class GroupingName(str, Enum):
    FINE = "fine"
    NO_SIDE = "no_side"
    BASIC = "basic"


DIVISION_ORDER = {
    "SY": 0,
    "Y": 1,
    "O": 2,
    "S": 3,
    "K": 4,
    "M": 5,
    "J": 6,
    "Ms": 7,
    "Sd": 8,
    "Jd": 9,
    "Jk": 10,
}


@dataclass(frozen=True)
class GroupKey:
    """Grouping-specific rank marker used for matrix rows and columns."""

    level: str
    number: int | None
    side: str | None
    annotation: str | None

    @property
    def label(self) -> str:
        out = self.level
        if self.number is not None:
            out += str(self.number)
        if self.side is not None:
            out += self.side
        if self.annotation is not None:
            out += self.annotation
        return out

    @property
    def sort_key(self) -> tuple[int, int, int, int, str]:
        side_order = {"e": 0, "w": 1}.get(self.side, 2)
        ann_order = 0 if self.annotation is None else 1
        return (
            DIVISION_ORDER.get(self.level, 99),
            self.number if self.number is not None else 0,
            side_order,
            ann_order,
            self.label,
        )


def level_label(chii: Chii) -> str:
    if isinstance(chii.level, MSD):
        return chii.level.as_abbreviation()
    if isinstance(chii.level, Division):
        return chii.level.as_abbreviation()
    raise TypeError(f"Unexpected chii level {chii.level!r}")


def side_label(side: Side) -> str | None:
    if side == Side.EAST:
        return "e"
    if side == Side.WEST:
        return "w"
    return None


def annotation_label(annotation: Annotation) -> str | None:
    if annotation == Annotation.EMPTY:
        return None
    return annotation.name


def group_chii(chii: Chii, grouping: GroupingName) -> GroupKey:
    level = level_label(chii)
    number: int | None = chii.number
    side = side_label(chii.side)
    annotation = annotation_label(chii.ann)

    if grouping == GroupingName.FINE:
        return GroupKey(level=level, number=number, side=side, annotation=annotation)

    if grouping == GroupingName.NO_SIDE:
        annotation = None
        side = None
        if level in {"Y", "O", "S", "K"}:
            number = None
        return GroupKey(level=level, number=number, side=side, annotation=annotation)

    if grouping == GroupingName.BASIC:
        annotation = None
        side = None
        number = None
        if level in {"Y", "O", "S", "K"}:
            level = "SY"
        return GroupKey(level=level, number=number, side=side, annotation=annotation)

    raise ValueError(f"Unknown grouping {grouping!r}")


def division_number(group: GroupKey, division: str) -> int | None:
    if group.level != division or group.number is None:
        return None
    return group.number


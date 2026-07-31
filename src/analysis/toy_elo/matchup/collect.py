from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from src.analysis.boundary_positions import boundary_positions
from src.sumo_core.History import Date, History

from .config import ADJACENT_BOUNDARIES
from .grouping import GroupKey, GroupingName, group_chii


@dataclass(frozen=True)
class BoundaryKey:
    upper_division: str
    lower_division: str
    focal_division: str
    opponent_division: str
    boundary_anchor: str
    boundary_distance: int


@dataclass
class MatchupTallies:
    counts: dict[tuple[int, GroupKey, GroupKey], int]
    row_totals: dict[tuple[int, GroupKey], int]
    boundary_counts: dict[BoundaryKey, int]
    boundary_row_totals: dict[BoundaryKey, int]
    boundary_group_counts: dict[BoundaryKey, dict[str, int]]
    groups: set[GroupKey]
    basho_count: int


def collect_tallies(
    history: History,
    *,
    start: Date,
    end: Date | None,
    grouping: GroupingName,
) -> MatchupTallies:
    counts: dict[tuple[int, GroupKey, GroupKey], int] = defaultdict(int)
    row_totals: dict[tuple[int, GroupKey], int] = defaultdict(int)
    boundary_counts: dict[BoundaryKey, int] = defaultdict(int)
    boundary_row_totals: dict[BoundaryKey, int] = defaultdict(int)
    boundary_group_counts: dict[BoundaryKey, dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    groups: set[GroupKey] = set()
    basho_count = 0

    for date in sorted(history):
        if date < start:
            continue
        if end is not None and date > end:
            continue

        basho_count += 1
        basho = history[date]
        group_by_rikishi = {
            rikishi: group_chii(chii, grouping)
            for rikishi, chii in basho.banzuke.rikchii.items()
        }
        division_position_by_rikishi = boundary_positions(basho.banzuke.rikchii)
        groups.update(group_by_rikishi.values())

        for day_key, daily in basho.summary.items():
            day = int(day_key)
            for pair in daily.torikumi:
                rikishi_a, rikishi_b = pair
                group_a = group_by_rikishi.get(rikishi_a)
                group_b = group_by_rikishi.get(rikishi_b)
                if group_a is None or group_b is None:
                    continue

                counts[(day, group_a, group_b)] += 1
                counts[(day, group_b, group_a)] += 1
                row_totals[(day, group_a)] += 1
                row_totals[(day, group_b)] += 1
                increment_boundary_tallies(
                    boundary_counts=boundary_counts,
                    boundary_row_totals=boundary_row_totals,
                    boundary_group_counts=boundary_group_counts,
                    focal_rikishi=rikishi_a,
                    opponent_rikishi=rikishi_b,
                    group_by_rikishi=group_by_rikishi,
                    position_by_rikishi=division_position_by_rikishi,
                )
                increment_boundary_tallies(
                    boundary_counts=boundary_counts,
                    boundary_row_totals=boundary_row_totals,
                    boundary_group_counts=boundary_group_counts,
                    focal_rikishi=rikishi_b,
                    opponent_rikishi=rikishi_a,
                    group_by_rikishi=group_by_rikishi,
                    position_by_rikishi=division_position_by_rikishi,
                )

    return MatchupTallies(
        counts=dict(counts),
        row_totals=dict(row_totals),
        boundary_counts=dict(boundary_counts),
        boundary_row_totals=dict(boundary_row_totals),
        boundary_group_counts={
            key: dict(counts) for key, counts in boundary_group_counts.items()
        },
        groups=groups,
        basho_count=basho_count,
    )


def increment_boundary_tallies(
    *,
    boundary_counts: dict[BoundaryKey, int],
    boundary_row_totals: dict[BoundaryKey, int],
    boundary_group_counts: dict[BoundaryKey, dict[str, int]],
    focal_rikishi: object,
    opponent_rikishi: object,
    group_by_rikishi: dict[object, GroupKey],
    position_by_rikishi: dict[object, tuple[str, int, int]],
) -> None:
    focal_position = position_by_rikishi.get(focal_rikishi)
    opponent_position = position_by_rikishi.get(opponent_rikishi)
    focal_group = group_by_rikishi.get(focal_rikishi)
    if (
        focal_position is None
        or opponent_position is None
        or focal_group is None
    ):
        return

    focal_division, from_top, from_bottom = focal_position
    opponent_division = opponent_position[0]
    for upper, lower in ADJACENT_BOUNDARIES:
        if focal_division == upper:
            key = BoundaryKey(
                upper_division=upper,
                lower_division=lower,
                focal_division=upper,
                opponent_division=lower,
                boundary_anchor="bottom",
                boundary_distance=from_bottom,
            )
        elif focal_division == lower:
            key = BoundaryKey(
                upper_division=upper,
                lower_division=lower,
                focal_division=lower,
                opponent_division=upper,
                boundary_anchor="top",
                boundary_distance=from_top,
            )
        else:
            continue

        boundary_row_totals[key] += 1
        boundary_group_counts[key][focal_group.label] += 1
        if opponent_division == key.opponent_division:
            boundary_counts[key] += 1

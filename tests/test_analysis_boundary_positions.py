import pytest

from src.analysis.boundary_positions import (
    boundary_positions,
    competitive_division,
    paired_boundary_group,
)
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii


def test_makuuchi_levels_share_one_competitive_division() -> None:
    yokozuna = Chii.from_str("Y1e")
    maegashira_east = Chii.from_str("M1e")
    maegashira_west = Chii.from_str("M1w")
    juryo = Chii.from_str("J1e")
    ranks = {
        RikId(1): yokozuna,
        RikId(2): maegashira_east,
        RikId(3): maegashira_west,
        RikId(4): juryo,
    }

    positions = boundary_positions(ranks)

    assert competitive_division(yokozuna) == "M"
    assert positions[RikId(1)] == ("M", 1, 3)
    assert positions[RikId(2)] == ("M", 2, 2)
    assert positions[RikId(3)] == ("M", 3, 1)
    assert positions[RikId(4)] == ("J", 1, 1)


def test_paired_boundary_group_collapses_adjacent_slots() -> None:
    assert [paired_boundary_group(value) for value in range(1, 7)] == [
        1,
        1,
        2,
        2,
        3,
        3,
    ]
    with pytest.raises(ValueError):
        paired_boundary_group(0)

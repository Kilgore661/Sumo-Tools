from types import MappingProxyType

from src.analysis.sumo_history.records.highest_equelo import highest_equelo_rows
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii


def test_highest_equelo_rows_keep_each_rikishi_best_rating_and_first_point() -> None:
    rows = highest_equelo_rows(
        day_end_ratings={
            "1979/01": {
                "1": {"10": 2100.0, "20": 2200.0},
                "2": {"10": 2150.0, "20": 2190.0},
            },
            "1979/03": {
                "1": {"10": 2150.0, "30": 2300.1254},
            },
        },
        full_shikona_store=FullShikonaStore(
            MappingProxyType(
                {
                    RikId(10): "Alpha",
                    RikId(20): "Beta",
                    RikId(30): "Gamma",
                }
            )
        ),
    )

    assert [row.position for row in rows] == [1, 2, 3]
    assert [row.rikishi_id for row in rows] == [30, 20, 10]
    assert [row.shikona for row in rows] == ["Gamma", "Beta", "Alpha"]
    assert [row.active for row in rows] == [False, False, False]
    assert [row.chii for row in rows] == ["", "", ""]
    assert [row.chii_ordinal for row in rows] == ["", "", ""]
    assert [row.rating for row in rows] == ["2300.125", "2200.000", "2150.000"]
    assert [row.date for row in rows] == ["1979/03/01", "1979/01/01", "1979/01/02"]


def test_highest_equelo_rows_mark_current_banzuke_rikishi() -> None:
    rows = highest_equelo_rows(
        day_end_ratings={
            "1979/01": {
                "1": {"10": 2100.0, "20": 2200.0},
            },
        },
        full_shikona_store=FullShikonaStore(
            MappingProxyType(
                {
                    RikId(10): "Alpha",
                    RikId(20): "Beta",
                }
            )
        ),
        active_rikishi=frozenset({RikId(10)}),
        chii_by_rikishi_and_date={
            (RikId(10), "1979/01"): Chii.from_str("M1e"),
            (RikId(20), "1979/01"): Chii.from_str("J1w"),
        },
    )

    assert [(row.rikishi_id, row.active) for row in rows] == [
        (20, False),
        (10, True),
    ]
    assert [(row.rikishi_id, row.chii, row.chii_ordinal) for row in rows] == [
        (20, "J1w", Chii.from_str("J1w").ordinal()),
        (10, "M1e", Chii.from_str("M1e").ordinal()),
    ]

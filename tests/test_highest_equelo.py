from types import MappingProxyType

from src.analysis.sumo_history.records.highest_equelo import highest_equelo_rows
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.BasicPrimitives import RikId


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
    assert [row.rating for row in rows] == ["2300.125", "2200.000", "2150.000"]
    assert [row.date for row in rows] == ["1979/03/01", "1979/01/01", "1979/01/02"]

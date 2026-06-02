import json
from pathlib import Path

from src.analysis.equelo.api import EqueloLookup, EqueloTiming, no_rating
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.BasicPrimitives import Day, Month, RikId, Riks, Shikona, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary
from src.products.make_site2.perf_chart.build import write_master_data


def test_write_master_data_builds_all_rikishi_points_and_size_report(tmp_path: Path) -> None:
    history = History(
        {
            Date(Year(1980), Month(1)): basho_state(
                {
                    RikId(1): ("Alpha", "Jk1eHD"),
                    RikId(2): ("Beta", "Jk2w"),
                }
            ),
            Date(Year(1980), Month(3)): basho_state(
                {
                    RikId(1): ("Alpha", "Jd1e"),
                    RikId(2): ("Beta", "Jd2w"),
                }
            ),
        }
    )
    equelo_lookup = EqueloLookup.build(
        history=history,
        day_end_ratings={
            "1980/01": {"1": {"1": 1001.0, "2": 1002.0}},
            "1980/03": {"1": {"1": 1011.0, "2": 1012.0}},
        },
        entrant_initial_ratings={
            str(Chii.from_str("Jk1e").ordinal()): 900.0,
            str(Chii.from_str("Jk2w").ordinal()): 901.0,
            str(Chii.from_str("Jd1e").ordinal()): 902.0,
            str(Chii.from_str("Jd2w").ordinal()): 903.0,
            str(Chii.from_str("Ms60w").ordinal()): 1200.0,
        },
    )

    output = write_master_data(
        history=history,
        output_root=tmp_path,
        equelo_lookup=equelo_lookup,
    )

    payload = json.loads(output.data_path.read_text(encoding="utf-8"))
    assert payload["columns"] == ["date", "shikona", "chii", "equelo"]
    assert payload["date_range"] == {"start": "1980/01", "end": "1980/03"}
    assert payload["points_by_rikishi"] == {
        "1": [
            ["1980/01", "Alpha", "Jk1eHD", 900.0],
            ["1980/03", "Alpha", "Jd1e", 1001.0],
        ],
        "2": [
            ["1980/01", "Beta", "Jk2w", 901.0],
            ["1980/03", "Beta", "Jd2w", 1002.0],
        ],
    }

    report = json.loads(output.report_path.read_text(encoding="utf-8"))
    assert report["data_file"] == "trajectory_master.json"
    assert report["rikishi_count"] == 2
    assert report["point_count"] == 4
    assert report["missing_equelo_count"] == 0
    assert report["max_points_per_rikishi"] == 2
    assert report["raw_bytes"] == output.data_path.stat().st_size
    assert report["gzip_bytes"] < report["raw_bytes"]


def test_equelo_lookup_returns_before_and_after_ratings_without_optional_gap() -> None:
    history = History(
        {
            Date(Year(1980), Month(1)): basho_state(
                {
                    RikId(1): ("Alpha", "Jk1eHD"),
                    RikId(2): ("Beta", "Jk2w"),
                }
            ),
            Date(Year(1980), Month(3)): basho_state(
                {
                    RikId(1): ("Alpha", "Jd1e"),
                    RikId(2): ("Beta", "Jd2w"),
                }
            ),
        }
    )
    equelo_lookup = EqueloLookup.build(
        history=history,
        day_end_ratings={
            "1980/01": {"1": {"1": 1001.0}},
            "1980/03": {"1": {"1": 1011.0, "2": 1012.0}},
        },
        entrant_initial_ratings={
            str(Chii.from_str("Jk1e").ordinal()): 900.0,
            str(Chii.from_str("Jk2w").ordinal()): 901.0,
            str(Chii.from_str("Jd1e").ordinal()): 902.0,
            str(Chii.from_str("Jd2w").ordinal()): 903.0,
        },
    )

    assert equelo_lookup.get_equelo(
        RikId(1), Date(Year(1980), Month(1)), EqueloTiming.BEFORE
    ) == 900.0
    assert equelo_lookup.get_equelo(
        RikId(1), Date(Year(1980), Month(1)), EqueloTiming.AFTER
    ) == 1001.0
    assert equelo_lookup.get_equelo(
        RikId(2), Date(Year(1980), Month(1)), EqueloTiming.AFTER
    ) == 901.0
    assert equelo_lookup.get_equelo(
        RikId(2), Date(Year(1980), Month(3)), EqueloTiming.BEFORE
    ) == 901.0


def test_equelo_lookup_returns_none_for_no_rating_chii() -> None:
    date = Date(Year(1980), Month(1))
    history = History(
        {
            date: basho_state(
                {
                    RikId(1): ("Gamma", "Ms70e"),
                }
            ),
        }
    )
    equelo_lookup = EqueloLookup.build(
        history=history,
        day_end_ratings={},
        entrant_initial_ratings={
            str(Chii.from_str("Ms60w").ordinal()): 1200.0,
        },
    )

    assert no_rating(Chii.from_str("Ms70e"))
    assert equelo_lookup.get_equelo(RikId(1), date, EqueloTiming.BEFORE) is None
    assert equelo_lookup.get_equelo(RikId(1), date, EqueloTiming.AFTER) is None


def basho_state(entries: dict[RikId, tuple[str, str]]) -> BashoState:
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(entries.keys()),
            rikchii=RikChii(
                {rikishi_id: Chii.from_str(chii) for rikishi_id, (_, chii) in entries.items()}
            ),
            rikshik=RikShikona(
                {
                    rikishi_id: Shikona(shikona)
                    for rikishi_id, (shikona, _) in entries.items()
                }
            ),
        ),
        summary=Summary({Day(1): object()}),
    )

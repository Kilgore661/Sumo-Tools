from types import MappingProxyType

from src.analysis.equelo.api import EqueloLookup
from src.analysis.sumo_history.basho_results import build
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.BasicPrimitives import Day, Month, RikId, Riks, Shikona, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import DailyResults, ResultLookup, Summary, Torikumi


def test_basho_results_uses_public_shikona_for_display(monkeypatch):
    rikishi_id = RikId(6472)
    date = Date(Year(2005), Month(3))
    history = History(
        {
            date: basho_state(
                {
                    rikishi_id: ("Kono", "Jk35w"),
                }
            ),
        }
    )
    ratings = EqueloLookup.build(
        history=history,
        day_end_ratings={},
        entrant_initial_ratings={
            str(Chii.from_str("Jk35w").ordinal()): 900.0,
        },
    )
    monkeypatch.setattr(
        build,
        "graph_shikona_for",
        lambda rikishi_id, fallback: f"graph:{fallback}",
    )

    rows = build.build_payload_rows(
        history=history,
        date=date,
        ratings=ratings,
        full_shikona_store=FullShikonaStore(
            MappingProxyType({rikishi_id: "Terao"})
        ),
    )

    assert len(rows) == 1
    assert rows[0].rikishi_id == "6472"
    assert rows[0].shikona == "Terao"
    assert rows[0].graph_shikona == "graph:Terao"


def basho_state(entries: dict[RikId, tuple[str, str]]) -> BashoState:
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(entries.keys()),
            rikchii=RikChii(
                {
                    rikishi_id: Chii.from_str(chii)
                    for rikishi_id, (_, chii) in entries.items()
                }
            ),
            rikshik=RikShikona(
                {
                    rikishi_id: Shikona(shikona)
                    for rikishi_id, (shikona, _) in entries.items()
                }
            ),
        ),
        summary=Summary(
            {
                Day(1): DailyResults(
                    torikumi=Torikumi(),
                    results_lookup=ResultLookup(),
                )
            }
        ),
    )

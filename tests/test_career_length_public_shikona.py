from src.analysis.sumo_history.career_lifecycle import career_length
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.BasicPrimitives import Day, Month, RikId, Riks, Shikona, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_career_spans_use_public_shikona_for_table_display(monkeypatch):
    rikishi_id = RikId(7701)
    history = History(
        {
            Date(Year(1980), Month(1)): basho_state(
                {
                    rikishi_id: ("History Fred", "J1e"),
                }
            ),
            Date(Year(1980), Month(3)): basho_state(
                {
                    rikishi_id: ("History Fred", "J1w"),
                }
            ),
        }
    )
    monkeypatch.setattr(
        career_length,
        "make_public_shikona",
        lambda history: {rikishi_id: Shikona("Public Fred")},
    )
    monkeypatch.setattr(
        career_length,
        "_graph_shikona_for",
        lambda rikishi_id, fallback: f"graph:{fallback}",
    )

    spans, warnings = career_length.compute_career_spans(history)

    assert warnings == []
    assert len(spans) == 1
    assert spans[0].shikona == "Public Fred"
    assert spans[0].graph_shikona == "graph:Public Fred"


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
        summary=Summary({Day(1): object()}),
    )

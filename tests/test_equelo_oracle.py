from src.analysis.equelo.api import EqueloLookup
from src.analysis.equelo.expt1.Oracle import _filter_basho_pre_1989
from src.analysis.sumo_history.basho_results.build import build_payload_rows
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import Day, Month, Pair, RikId, Riks, Shikona, Torikumi, Year
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary


def _identity_chii(chii: Chii) -> Chii:
    return chii


def test_pre_1989_oracle_keeps_zenkyujo_sekitori_in_rating_banzuke() -> None:
    zenkyujo_sekitori = RikId(1)
    active_sekitori = RikId(2)
    retained_lower_opponent = RikId(3)
    unobserved_lower_rikishi = RikId(4)

    banzuke = Banzuke(
        riks=Riks(
            {
                zenkyujo_sekitori,
                active_sekitori,
                retained_lower_opponent,
                unobserved_lower_rikishi,
            }
        ),
        rikchii=RikChii(
            {
                zenkyujo_sekitori: Chii.from_str("Y1e"),
                active_sekitori: Chii.from_str("J1e"),
                retained_lower_opponent: Chii.from_str("Ms1e"),
                unobserved_lower_rikishi: Chii.from_str("Ms2e"),
            }
        ),
        rikshik=RikShikona(
            {
                zenkyujo_sekitori: Shikona("Absent Sekitori"),
                active_sekitori: Shikona("Active Sekitori"),
                retained_lower_opponent: Shikona("Retained Opponent"),
                unobserved_lower_rikishi: Shikona("Unobserved Lower"),
            }
        ),
    )
    pair = Pair(active_sekitori, retained_lower_opponent)
    lookup = ResultLookup(
        {
            pair: BoutResult(
                rikishi1=active_sekitori,
                outcome1=Outcome.W,
                rikishi2=retained_lower_opponent,
                outcome2=Outcome.L,
                decision="blank",
                symbol=Symbol.W,
            )
        }
    )
    basho = BashoState(
        banzuke=banzuke,
        summary=Summary(
            {
                Day(1): DailyResults(
                    torikumi=Torikumi({pair}),
                    results_lookup=lookup,
                )
            }
        ),
    )

    cleaned = _filter_basho_pre_1989(basho, _identity_chii)

    assert zenkyujo_sekitori in cleaned.banzuke.riks
    assert active_sekitori in cleaned.banzuke.riks
    assert retained_lower_opponent in cleaned.banzuke.riks
    assert unobserved_lower_rikishi not in cleaned.banzuke.riks


def test_basho_results_uses_equelo_api_continuity_for_missing_day_end_rating() -> None:
    rikishi_id = RikId(1)
    first_date = Date(Year(1980), Month(1))
    second_date = Date(Year(1980), Month(3))
    history = History(
        {
            first_date: _single_rikishi_basho_state(rikishi_id, "Test Rikishi", "J1e"),
            second_date: _single_rikishi_basho_state(rikishi_id, "Test Rikishi", "J1e"),
        }
    )
    ratings = EqueloLookup.build(
        history=history,
        day_end_ratings={
            "1980/01": {"1": {"1": 2000.0}},
            "1980/03": {"1": {}},
        },
        entrant_initial_ratings={
            str(Chii.from_str("J1e").ordinal()): 1900.0,
        },
    )

    rows = build_payload_rows(history=history, date=second_date, ratings=ratings)

    assert len(rows) == 1
    assert rows[0].previous_equelo == "2000"
    assert rows[0].equelo == "2000"
    assert rows[0].delta_equelo == "+0"


def _single_rikishi_basho_state(rikishi_id: RikId, shikona: str, chii: str) -> BashoState:
    return BashoState(
        banzuke=Banzuke(
            riks=Riks({rikishi_id}),
            rikchii=RikChii({rikishi_id: Chii.from_str(chii)}),
            rikshik=RikShikona({rikishi_id: Shikona(shikona)}),
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

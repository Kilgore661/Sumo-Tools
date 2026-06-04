from src.analysis.equelo.expt1.Oracle import _filter_basho_pre_1989
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import Day, Pair, RikId, Riks, Shikona, Torikumi
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
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

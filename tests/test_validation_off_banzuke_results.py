from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import Day, Pair, RikId, Riks, Shikona, Torikumi
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary
from src.validation.off_banzuke_results.census import census_off_banzuke_results


def test_census_classifies_missing_endpoint_by_same_basho_status() -> None:
    date = Date.from_ints(1974, 11)
    history = History({date: _basho()})

    census = census_off_banzuke_results(
        history,
        start=date,
        end=date,
        career_statuses={RikId(2): {date: "Mz"}},
    )

    assert len(census.bouts) == 1
    row = census.bouts[0]
    assert row.missing_statuses == "Mz"
    assert row.every_missing_endpoint_is_mz
    assert not row.post_1988
    assert row.elo89_selector_would_rate


def test_present_annotated_rikishi_is_not_off_banzuke() -> None:
    date = Date.from_ints(2026, 7)
    history = History({date: _basho(include_missing=True)})

    census = census_off_banzuke_results(
        history,
        start=date,
        end=date,
        career_statuses={},
    )

    assert census.bouts == ()


def _basho(*, include_missing: bool = False) -> BashoState:
    ranked = {RikId(1)}
    ranks = {RikId(1): Chii.from_str("Jk1e")}
    if include_missing:
        ranked.add(RikId(2))
        ranks[RikId(2)] = Chii.from_str("Sd80eTD")
    bout = BoutResult(
        rikishi1=RikId(1),
        outcome1=Outcome.W,
        rikishi2=RikId(2),
        outcome2=Outcome.L,
        decision="blank",
        symbol=Symbol.W,
    )
    lookup = ResultLookup({Pair(RikId(1), RikId(2)): bout})
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(ranked),
            rikchii=RikChii(ranks),
            rikshik=RikShikona({rid: Shikona(str(int(rid))) for rid in ranked}),
        ),
        summary=Summary({Day(1): DailyResults(torikumi=Torikumi(set(lookup)), results_lookup=lookup)}),
    )

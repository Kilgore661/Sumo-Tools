from src.analysis.site89.shikona_annotations import (
    banzuke_annotations,
    current_basho_annotations,
)
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.BasicEnums import Outcome, Prize, Symbol
from src.sumo_core.BasicPrimitives import (
    Day,
    Month,
    Pair,
    RikId,
    Riks,
    Shikona,
    Torikumi,
    Year,
)
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Performance import Performance, Performances
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary


CANDIDATE = RikId(1)
OPPONENT = RikId(2)


def test_ozeki32_start_and_current_countdown_are_independent_of_highest_chii():
    dates = (_date(2025, 9), _date(2025, 11), _date(2026, 1))
    history = History(
        {
            dates[0]: _state("K1e", wins=8),
            dates[1]: _state("K1w", wins=14),
            dates[2]: _state("S1e", wins=3, days=5),
        }
    )

    start = banzuke_annotations(history, dates[2])[CANDIDATE]
    during = current_basho_annotations(history, dates[2])[CANDIDATE]

    assert start.highest_chii is True
    assert (start.promotion_kind, start.promotion_status, start.promotion_required) == (
        "ozeki32",
        "open",
        10,
    )
    assert (during.promotion_status, during.promotion_required) == ("open", 7)


def test_ozeki32_current_result_reaches_terminal_states():
    dates = (_date(2025, 9), _date(2025, 11), _date(2026, 1))
    achieved = History(
        {
            dates[0]: _state("K1e", wins=8),
            dates[1]: _state("S1e", wins=14),
            dates[2]: _state("S1e", wins=10),
        }
    )
    impossible = History(
        {
            dates[0]: _state("K1e", wins=8),
            dates[1]: _state("S1e", wins=14),
            dates[2]: _state("S1e", wins=9),
        }
    )

    assert current_basho_annotations(achieved, dates[2])[CANDIDATE].promotion_status == "achieved"
    assert current_basho_annotations(impossible, dates[2])[CANDIDATE].promotion_status == "impossible"


def test_ozeki32_omits_low_total_and_maegashira_start():
    dates = (_date(2025, 9), _date(2025, 11), _date(2026, 1))
    low_total = History(
        {
            dates[0]: _state("K1e", wins=8),
            dates[1]: _state("S1e", wins=8),
            dates[2]: _state("S1e", days=0),
        }
    )
    maegashira_start = History(
        {
            dates[0]: _state("M1e", wins=10),
            dates[1]: _state("S1e", wins=10),
            dates[2]: _state("S1e", days=0),
        }
    )

    assert banzuke_annotations(low_total, dates[2])[CANDIDATE].promotion_kind == ""
    assert banzuke_annotations(maegashira_start, dates[2])[CANDIDATE].promotion_kind == ""


def test_yokydj_stays_open_during_basho_and_is_decided_after_day_15():
    dates = (_date(2025, 11), _date(2026, 1))
    during = History(
        {
            dates[0]: _state("O1w", wins=13, prize=Prize.YUSHO),
            dates[1]: _state("O1e", wins=5, days=7),
        }
    )
    completed = History(
        {
            dates[0]: _state("O1w", wins=13, prize=Prize.YUSHO),
            dates[1]: _state("O1e", wins=12, prize=Prize.DOTEN_YUSHO),
        }
    )

    open_annotation = current_basho_annotations(during, dates[1])[CANDIDATE]
    achieved_annotation = current_basho_annotations(completed, dates[1])[CANDIDATE]

    assert open_annotation.highest_chii is True
    assert (open_annotation.promotion_kind, open_annotation.promotion_status) == (
        "yokydj",
        "open",
    )
    assert open_annotation.promotion_previous_result == "Y"
    assert achieved_annotation.promotion_status == "achieved"


def test_yokydj_after_doten_requires_a_yusho():
    dates = (_date(2025, 11), _date(2026, 1))
    history = History(
        {
            dates[0]: _state("O1w", wins=12, prize=Prize.DOTEN_YUSHO),
            dates[1]: _state("O1e", wins=12, prize=Prize.DOTEN_YUSHO),
        }
    )

    annotation = current_basho_annotations(history, dates[1])[CANDIDATE]

    assert annotation.promotion_previous_result == "D"
    assert annotation.promotion_status == "impossible"


def test_historical_basho_has_no_annotations_after_next_banzuke_exists():
    dates = (_date(2025, 9), _date(2025, 11), _date(2026, 1), _date(2026, 3))
    history = History(
        {
            dates[0]: _state("K1e", wins=8),
            dates[1]: _state("S1e", wins=14),
            dates[2]: _state("S1e", wins=10),
            dates[3]: _state("O1e", days=0),
        }
    )

    assert current_basho_annotations(history, dates[2]) == {}


def test_repeated_exact_career_high_and_lower_rank_are_not_marked():
    dates = (_date(2025, 9), _date(2025, 11), _date(2026, 1))
    repeated = History(
        {
            dates[0]: _state("M2e", wins=8),
            dates[1]: _state("M3e", wins=8),
            dates[2]: _state("M2e", days=0),
        }
    )
    lower = History(
        {
            dates[0]: _state("M2e", wins=8),
            dates[1]: _state("M3e", wins=8),
            dates[2]: _state("M2w", days=0),
        }
    )

    assert banzuke_annotations(repeated, dates[2])[CANDIDATE].highest_chii is False
    assert banzuke_annotations(lower, dates[2])[CANDIDATE].highest_chii is False


def test_first_banzuke_appearance_is_a_first_time_career_high():
    date = _date(2026, 1)
    history = History({date: _state("Jk20e", days=0)})

    assert banzuke_annotations(history, date)[CANDIDATE].highest_chii is True


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))


def _state(
    rank: str,
    *,
    wins: int = 0,
    days: int = 15,
    prize: Prize | None = None,
) -> BashoState:
    summaries = {}
    for day in range(1, days + 1):
        candidate_wins = day <= wins
        first_outcome = Outcome.W if candidate_wins else Outcome.L
        second_outcome = Outcome.L if candidate_wins else Outcome.W
        pair = Pair(CANDIDATE, OPPONENT)
        lookup = ResultLookup(
            {
                pair: BoutResult(
                    rikishi1=CANDIDATE,
                    outcome1=first_outcome,
                    rikishi2=OPPONENT,
                    outcome2=second_outcome,
                    decision="blank",
                    symbol=Symbol[first_outcome.name],
                )
            }
        )
        summaries[Day(day)] = DailyResults(
            torikumi=Torikumi({pair}), results_lookup=lookup
        )
    performances = Performances()
    if prize is not None:
        performances[CANDIDATE] = Performance(prizes=frozenset({prize}))
    ranks = {
        CANDIDATE: Chii.from_str(rank),
        OPPONENT: Chii.from_str("M10e"),
    }
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(ranks),
            rikchii=RikChii(ranks),
            rikshik=RikShikona(
                {CANDIDATE: Shikona("Candidate"), OPPONENT: Shikona("Opponent")}
            ),
        ),
        summary=Summary(summaries, performances=performances),
    )

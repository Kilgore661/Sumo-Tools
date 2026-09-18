from types import SimpleNamespace

from src.analysis.promotion.yokozuna.evaluate_rule import (
    evaluate_championship_finisher_pair,
    evaluate_doten_then_yusho,
    evaluate_two_doten,
    evaluate_two_yusho,
    evaluate_yusho_or_doten_pair,
    evaluate_yusho_then_doten,
)
from src.sumo_core.BasicEnums import Prize
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Performance import Performance, Performances
from src.sumo_core.Summary import Summary


def state(rank, *, prize=None, rikishi_id=1, shikona="Example"):
    performances = Performances()
    if prize is not None:
        performances[rikishi_id] = Performance(prizes=frozenset({prize}))
    return SimpleNamespace(
        banzuke=SimpleNamespace(
            riks={rikishi_id},
            rikchii={rikishi_id: Chii.from_str(rank)},
            rikshik={rikishi_id: shikona},
        ),
        summary=Summary({}, performances),
    )


def history_for(*rows):
    history = History()
    for year, month, rank, prize in rows:
        history[Date(year, month)] = state(rank, prize=prize)
    return history


def test_two_ozeki_yusho_followed_by_yokozuna_is_true_positive():
    history = history_for(
        (2020, 1, "O1e", Prize.YUSHO),
        (2020, 3, "O1e", Prize.YUSHO),
        (2020, 5, "Y1e", None),
    )
    result = evaluate_two_yusho(history)
    assert (result["tp"], result["fp"], result["fn"]) == (1, 0, 0)
    assert result["precision"] == result["recall"] == result["f1"] == 1.0


def test_non_promotion_is_false_positive_and_rank_condition_is_strict():
    history = history_for(
        (2020, 1, "O1e", Prize.YUSHO),
        (2020, 3, "O1e", Prize.YUSHO),
        (2020, 5, "O1e", None),
    )
    result = evaluate_two_yusho(history)
    assert (result["tp"], result["fp"], result["fn"]) == (0, 1, 0)

    history[Date(2020, 1)] = state("S1e", prize=Prize.YUSHO)
    result = evaluate_two_yusho(history)
    assert (result["tp"], result["fp"], result["fn"]) == (0, 0, 0)


def test_other_yokozuna_promotion_is_false_negative():
    history = history_for(
        (2020, 1, "O1e", None),
        (2020, 3, "O1e", Prize.YUSHO),
        (2020, 5, "Y1e", None),
    )
    result = evaluate_two_yusho(history)
    assert (result["tp"], result["fp"], result["fn"]) == (0, 0, 1)
    assert result["false_negatives"][0]["promotion_banzuke"] == "2020/05"


def test_final_window_without_next_rank_is_unresolved():
    history = history_for(
        (2020, 1, "O1e", None),
        (2020, 3, "O1e", Prize.YUSHO),
        (2020, 5, "O1e", Prize.YUSHO),
    )
    result = evaluate_two_yusho(history)
    assert (result["tp"], result["fp"], result["fn"]) == (0, 0, 0)
    assert len(result["unresolved_windows"]) == 1


def test_doten_is_allowed_only_in_the_first_basho_of_relaxed_rule():
    history = history_for(
        (2020, 1, "O1e", Prize.DOTEN_YUSHO),
        (2020, 3, "O1e", Prize.YUSHO),
        (2020, 5, "Y1e", None),
    )
    assert evaluate_two_yusho(history)["fn"] == 1
    relaxed = evaluate_doten_then_yusho(history)
    assert (relaxed["tp"], relaxed["fp"], relaxed["fn"]) == (1, 0, 0)

    history = history_for(
        (2020, 1, "O1e", Prize.YUSHO),
        (2020, 3, "O1e", Prize.DOTEN_YUSHO),
        (2020, 5, "Y1e", None),
    )
    relaxed = evaluate_doten_then_yusho(history)
    assert (relaxed["tp"], relaxed["fp"], relaxed["fn"]) == (0, 0, 1)


def test_yusho_then_doten_rule_allows_doten_only_in_second_basho():
    history = history_for(
        (2020, 1, "O1e", Prize.YUSHO),
        (2020, 3, "O1e", Prize.DOTEN_YUSHO),
        (2020, 5, "Y1e", None),
    )
    relaxed = evaluate_yusho_then_doten(history)
    assert (relaxed["tp"], relaxed["fp"], relaxed["fn"]) == (1, 0, 0)

    history = history_for(
        (2020, 1, "O1e", Prize.DOTEN_YUSHO),
        (2020, 3, "O1e", Prize.YUSHO),
        (2020, 5, "Y1e", None),
    )
    relaxed = evaluate_yusho_then_doten(history)
    assert (relaxed["tp"], relaxed["fp"], relaxed["fn"]) == (0, 0, 1)


def test_two_doten_rule_adds_dd_but_not_mixed_sequences():
    history = history_for(
        (2020, 1, "O1e", Prize.DOTEN_YUSHO),
        (2020, 3, "O1e", Prize.DOTEN_YUSHO),
        (2020, 5, "Y1e", None),
    )
    relaxed = evaluate_two_doten(history)
    assert (relaxed["tp"], relaxed["fp"], relaxed["fn"]) == (1, 0, 0)

    history = history_for(
        (2020, 1, "O1e", Prize.YUSHO),
        (2020, 3, "O1e", Prize.DOTEN_YUSHO),
        (2020, 5, "Y1e", None),
    )
    relaxed = evaluate_two_doten(history)
    assert (relaxed["tp"], relaxed["fp"], relaxed["fn"]) == (0, 0, 1)


def test_yusho_or_doten_pair_accepts_all_four_sequences():
    for first_prize in (Prize.YUSHO, Prize.DOTEN_YUSHO):
        for second_prize in (Prize.YUSHO, Prize.DOTEN_YUSHO):
            history = history_for(
                (2020, 1, "O1e", first_prize),
                (2020, 3, "O1e", second_prize),
                (2020, 5, "Y1e", None),
            )
            result = evaluate_yusho_or_doten_pair(history)
            assert (result["tp"], result["fp"], result["fn"]) == (1, 0, 0)


def test_championship_finisher_pair_accepts_all_nine_sequences():
    prizes = (Prize.YUSHO, Prize.DOTEN_YUSHO, Prize.JUN_YUSHO)
    for first_prize in prizes:
        for second_prize in prizes:
            history = history_for(
                (2020, 1, "O1e", first_prize),
                (2020, 3, "O1e", second_prize),
                (2020, 5, "Y1e", None),
            )
            result = evaluate_championship_finisher_pair(history)
            assert (result["tp"], result["fp"], result["fn"]) == (1, 0, 0)


def test_wakanohana_boundary_supplement_adds_march_1958_promotion():
    history = History()
    history[Date(1958, 1)] = state(
        "O1e", prize=Prize.YUSHO, rikishi_id=3904, shikona="Wakanohana"
    )
    history[Date(1958, 3)] = state("Y1e", rikishi_id=3904, shikona="Wakanohana")
    history[Date(1958, 5)] = state("Y1e", rikishi_id=3904, shikona="Wakanohana")

    strict = evaluate_two_yusho(history)
    assert (strict["tp"], strict["fp"], strict["fn"]) == (0, 0, 1)
    relaxed = evaluate_championship_finisher_pair(history)
    assert (relaxed["tp"], relaxed["fp"], relaxed["fn"]) == (1, 0, 0)
    assert relaxed["qualifying_windows"][0]["source"] == "user_supplied + history"
    assert relaxed["qualifying_windows"][0]["first_wins"] == 12

"""Evaluate the strict yokozuna benchmark: two consecutive yusho as ozeki."""

from __future__ import annotations

from src.sumo_core.BasicEnums import MSD, Outcome, Prize


FIRST_PROMOTION_BANZUKE = "1958/03"
WAKANOHANA_BOUNDARY_SUPPLEMENT = {
    "rikishi_id": 3904,
    "basho": "1957/11",
    "rank": "O",
    "wins": 12,
    "markers": ["J"],
    "source": "user_supplied",
}


def _has_any_prize(state, rikishi_id, prizes) -> bool:
    performance = state.summary.performances.get(rikishi_id)
    return performance is not None and bool(performance.prizes & prizes)


def _wins(state, rikishi_id) -> int:
    wins = 0
    for day, daily in state.summary.items():
        if int(day) > 15:
            continue
        for bout in daily.results_lookup.values():
            outcome = (
                bout.outcome1
                if bout.rikishi1 == rikishi_id
                else bout.outcome2
                if bout.rikishi2 == rikishi_id
                else None
            )
            wins += outcome in {Outcome.W, Outcome.FS}
    return wins


def _markers(state, rikishi_id) -> list[str]:
    performance = state.summary.performances.get(rikishi_id)
    if performance is None:
        return []
    abbreviations = {
        Prize.YUSHO: "Y",
        Prize.DOTEN_YUSHO: "D",
        Prize.JUN_YUSHO: "J",
        Prize.KANTO: "K",
        Prize.SHUKUN: "S",
        Prize.GINO: "G",
    }
    return sorted(abbreviations[prize] for prize in performance.prizes)


def _evidence_row(date, state, rikishi_id) -> dict:
    rank = state.banzuke.rikchii.get(rikishi_id)
    return {
        "basho": str(date),
        "rank": str(rank) if rank is not None else None,
        "wins": _wins(state, rikishi_id),
        "markers": _markers(state, rikishi_id),
    }


def _matches_sequence(first, second, rikishi_id, allowed_sequences) -> bool:
    return any(
        _has_any_prize(first, rikishi_id, frozenset({first_prize}))
        and _has_any_prize(second, rikishi_id, frozenset({second_prize}))
        for first_prize, second_prize in allowed_sequences
    )


def _evaluate_sequence(history, *, name, definition, allowed_sequences) -> dict:
    """Score selected Ozeki championship sequences against entry at yokozuna.

    The observation is a rikishi at a banzuke boundary. Consecutive means
    consecutive held basho present in History. An absent next rank is unresolved.
    """
    dates = sorted(history)
    if len(dates) < 3:
        raise ValueError("Yokozuna promotion analysis requires at least three basho")

    states = {date: history(date) for date in dates}
    actual_events = []
    boundary_events = []
    for index, date in enumerate(dates):
        state = states[date]
        for rikishi_id in sorted(state.banzuke.riks):
            rank = state.banzuke.rikchii[rikishi_id]
            if rank.level != MSD.YOKOZUNA:
                continue
            prior_rank = (
                states[dates[index - 1]].banzuke.rikchii.get(rikishi_id)
                if index
                else None
            )
            if prior_rank is None:
                boundary_events.append(
                    {
                        "rikishi_id": int(rikishi_id),
                        "shikona": str(state.banzuke.rikshik[rikishi_id]),
                        "promotion_banzuke": str(date),
                        "reason": "No adjacent prior rank; entry is not a confirmed promotion.",
                    }
                )
            elif prior_rank.level != MSD.YOKOZUNA:
                evidence = [
                    _evidence_row(prior_date, states[prior_date], rikishi_id)
                    for prior_date in dates[max(0, index - 2) : index]
                ]
                if int(rikishi_id) == 3904 and str(date) == "1958/03":
                    evidence.insert(0, dict(WAKANOHANA_BOUNDARY_SUPPLEMENT))
                event = {
                    "rikishi_id": int(rikishi_id),
                    "shikona": str(state.banzuke.rikshik[rikishi_id]),
                    "promotion_banzuke": str(date),
                    "prior_rank": str(prior_rank),
                    "evidence": evidence,
                }
                if str(date) < FIRST_PROMOTION_BANZUKE:
                    event["reason"] = "Insufficient two-basho evidence before the History boundary."
                    boundary_events.append(event)
                else:
                    actual_events.append(event)

    windows = []
    january_1958 = next((date for date in dates if str(date) == "1958/01"), None)
    march_1958 = next((date for date in dates if str(date) == "1958/03"), None)
    supplement_id = next(
        (
            rikishi_id
            for rikishi_id in states[january_1958].banzuke.riks
            if int(rikishi_id) == WAKANOHANA_BOUNDARY_SUPPLEMENT["rikishi_id"]
        ),
        None,
    ) if january_1958 is not None else None
    if supplement_id is not None and march_1958 is not None:
        first_prize = Prize.JUN_YUSHO
        matching_second_prizes = {
            second_prize
            for allowed_first, second_prize in allowed_sequences
            if allowed_first == first_prize
        }
        january_state = states[january_1958]
        march_state = states[march_1958]
        january_rank = january_state.banzuke.rikchii[supplement_id]
        if (
            january_rank.level == MSD.OZEKI
            and _has_any_prize(january_state, supplement_id, matching_second_prizes)
        ):
            next_rank = march_state.banzuke.rikchii.get(supplement_id)
            status = (
                "unresolved"
                if next_rank is None
                else "true_positive"
                if next_rank.level == MSD.YOKOZUNA
                else "false_positive"
            )
            windows.append(
                {
                    "rikishi_id": int(supplement_id),
                    "shikona": str(january_state.banzuke.rikshik[supplement_id]),
                    "first_basho": WAKANOHANA_BOUNDARY_SUPPLEMENT["basho"],
                    "second_basho": str(january_1958),
                    "promotion_banzuke": str(march_1958),
                    "first_rank": WAKANOHANA_BOUNDARY_SUPPLEMENT["rank"],
                    "second_rank": str(january_rank),
                    "first_wins": WAKANOHANA_BOUNDARY_SUPPLEMENT["wins"],
                    "second_wins": _wins(january_state, supplement_id),
                    "first_markers": WAKANOHANA_BOUNDARY_SUPPLEMENT["markers"],
                    "second_markers": _markers(january_state, supplement_id),
                    "next_rank": str(next_rank) if next_rank is not None else None,
                    "source": "user_supplied + history",
                    "classification": status,
                }
            )
    for end_index in range(1, len(dates)):
        first_date, second_date = dates[end_index - 1 : end_index + 1]
        first, second = states[first_date], states[second_date]
        common = set(first.banzuke.riks) & set(second.banzuke.riks)
        for rikishi_id in sorted(common):
            if not all(
                state.banzuke.rikchii[rikishi_id].level == MSD.OZEKI
                for state in (first, second)
            ):
                continue
            if not _matches_sequence(first, second, rikishi_id, allowed_sequences):
                continue

            next_date = dates[end_index + 1] if end_index + 1 < len(dates) else None
            next_rank = (
                states[next_date].banzuke.rikchii.get(rikishi_id)
                if next_date is not None
                else None
            )
            status = (
                "unresolved"
                if next_rank is None
                else "true_positive"
                if next_rank.level == MSD.YOKOZUNA
                else "false_positive"
            )
            windows.append(
                {
                    "rikishi_id": int(rikishi_id),
                    "shikona": str(second.banzuke.rikshik[rikishi_id]),
                    "first_basho": str(first_date),
                    "second_basho": str(second_date),
                    "promotion_banzuke": str(next_date) if next_date is not None else None,
                    "first_rank": str(first.banzuke.rikchii[rikishi_id]),
                    "second_rank": str(second.banzuke.rikchii[rikishi_id]),
                    "first_wins": _wins(first, rikishi_id),
                    "second_wins": _wins(second, rikishi_id),
                    "first_markers": _markers(first, rikishi_id),
                    "second_markers": _markers(second, rikishi_id),
                    "next_rank": str(next_rank) if next_rank is not None else None,
                    "classification": status,
                }
            )

    resolved = [
        row
        for row in windows
        if row["classification"] != "unresolved"
        and row["promotion_banzuke"] >= FIRST_PROMOTION_BANZUKE
    ]
    actual = {
        (row["rikishi_id"], row["promotion_banzuke"]) for row in actual_events
    }
    predicted = {
        (row["rikishi_id"], row["promotion_banzuke"]) for row in resolved
    }
    tp = len(actual & predicted)
    fp = len(predicted - actual)
    fn = len(actual - predicted)

    def ratio(numerator, denominator):
        return numerator / denominator if denominator else 0.0

    return {
        "schema_version": 1,
        "name": name,
        "definition": definition,
        "first_promotion_banzuke": FIRST_PROMOTION_BANZUKE,
        "history_first_basho": str(dates[0]),
        "history_last_basho": str(dates[-1]),
        "history_basho_count": len(dates),
        "counting": "Promotion opportunities, including overlapping windows; not distinct rikishi.",
        "exclusions": "Unconfirmed initial yokozuna; outcomes before 1958/03; unresolved next rank/banzuke.",
        "supplements": [WAKANOHANA_BOUNDARY_SUPPLEMENT],
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "actual_promotions": len(actual),
        "predicted_promotions": len(predicted),
        "precision": ratio(tp, tp + fp),
        "recall": ratio(tp, tp + fn),
        "f1": ratio(2 * tp, 2 * tp + fp + fn),
        "qualifying_windows": resolved,
        "false_negatives": [
            row
            for row in actual_events
            if (row["rikishi_id"], row["promotion_banzuke"]) not in predicted
        ],
        "unresolved_windows": [
            row for row in windows if row["classification"] == "unresolved"
        ],
        "boundary_events": boundary_events,
    }


def evaluate_two_yusho(history) -> dict:
    """Evaluate the literal two-consecutive-yusho benchmark."""
    return _evaluate_sequence(
        history,
        name="YY",
        definition="Makuuchi yusho in two consecutive held basho while ranked ozeki in both.",
        allowed_sequences=frozenset({(Prize.YUSHO, Prize.YUSHO)}),
    )


def evaluate_doten_then_yusho(history) -> dict:
    """Allow a doten-yusho to substitute for the first of two yusho."""
    return _evaluate_sequence(
        history,
        name="(Y|D)-Y",
        definition=(
            "Makuuchi yusho or doten-yusho, followed by a Makuuchi yusho, "
            "in consecutive held basho while ranked ozeki in both."
        ),
        allowed_sequences=frozenset(
            {
                (Prize.YUSHO, Prize.YUSHO),
                (Prize.DOTEN_YUSHO, Prize.YUSHO),
            }
        ),
    )


def evaluate_yusho_then_doten(history) -> dict:
    """Allow a doten-yusho to substitute for the second of two yusho."""
    return _evaluate_sequence(
        history,
        name="Y-(Y|D)",
        definition=(
            "Makuuchi yusho, followed by a Makuuchi yusho or doten-yusho, "
            "in consecutive held basho while ranked ozeki in both."
        ),
        allowed_sequences=frozenset(
            {
                (Prize.YUSHO, Prize.YUSHO),
                (Prize.YUSHO, Prize.DOTEN_YUSHO),
            }
        ),
    )


def evaluate_two_doten(history) -> dict:
    """Allow two consecutive doten-yusho as an alternative to two yusho."""
    return _evaluate_sequence(
        history,
        name="YY|DD",
        definition=(
            "Two Makuuchi yusho or two Makuuchi doten-yusho in consecutive "
            "held basho while ranked ozeki in both."
        ),
        allowed_sequences=frozenset(
            {
                (Prize.YUSHO, Prize.YUSHO),
                (Prize.DOTEN_YUSHO, Prize.DOTEN_YUSHO),
            }
        ),
    )


def evaluate_yusho_or_doten_pair(history) -> dict:
    """Allow either yusho or doten-yusho in each of the two basho."""
    return _evaluate_sequence(
        history,
        name="{Y,D}^2",
        definition=(
            "Makuuchi yusho or doten-yusho in each of two consecutive held "
            "basho while ranked ozeki in both."
        ),
        allowed_sequences=frozenset(
            {
                (Prize.YUSHO, Prize.YUSHO),
                (Prize.YUSHO, Prize.DOTEN_YUSHO),
                (Prize.DOTEN_YUSHO, Prize.YUSHO),
                (Prize.DOTEN_YUSHO, Prize.DOTEN_YUSHO),
            }
        ),
    )


def evaluate_championship_finisher_pair(history) -> dict:
    """Allow yusho, doten-yusho or jun-yusho in each of the two basho."""
    prizes = (Prize.YUSHO, Prize.DOTEN_YUSHO, Prize.JUN_YUSHO)
    return _evaluate_sequence(
        history,
        name="{Y,D,J}^2",
        definition=(
            "Makuuchi yusho, doten-yusho or jun-yusho in each of two "
            "consecutive held basho while ranked ozeki in both."
        ),
        allowed_sequences=frozenset(
            (first_prize, second_prize)
            for first_prize in prizes
            for second_prize in prizes
        ),
    )


def main() -> None:
    import argparse
    import json

    from src.infra.live_store.api import get_history

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "rule",
        choices=("YY", "DY", "YD", "DD", "YD2", "YDJ2"),
        nargs="?",
        default="YY",
    )
    args = parser.parse_args()
    evaluators = {
        "YY": evaluate_two_yusho,
        "DY": evaluate_doten_then_yusho,
        "YD": evaluate_yusho_then_doten,
        "DD": evaluate_two_doten,
        "YD2": evaluate_yusho_or_doten_pair,
        "YDJ2": evaluate_championship_finisher_pair,
    }
    evaluator = evaluators[args.rule]
    print(json.dumps(evaluator(get_history()), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

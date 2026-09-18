"""Find the maximum-F1 subset of the 16 ordered Y/D/J/N pairs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from math import gcd
from pathlib import Path

from src.sumo_core.BasicEnums import MSD, Prize

from .evaluate_rule import (
    FIRST_PROMOTION_BANZUKE,
    WAKANOHANA_BOUNDARY_SUPPLEMENT,
    _markers,
    _wins,
)


SYMBOLS = ("Y", "D", "J", "N")
SEQUENCES = tuple(first + second for first in SYMBOLS for second in SYMBOLS)
CHAMPIONSHIP_MARKERS = {
    Prize.YUSHO: "Y",
    Prize.DOTEN_YUSHO: "D",
    Prize.JUN_YUSHO: "J",
}
OUTPUT_ROOT = Path("files/output/analysis/promotion/yokozuna")


def _symbol(state, rikishi_id) -> str:
    performance = state.summary.performances.get(rikishi_id)
    prizes = performance.prizes if performance is not None else frozenset()
    symbols = [symbol for prize, symbol in CHAMPIONSHIP_MARKERS.items() if prize in prizes]
    if len(symbols) > 1:
        raise ValueError(
            f"Multiple Y/D/J markers for rikishi {int(rikishi_id)}: {symbols}"
        )
    return symbols[0] if symbols else "N"


def _actual_promotions(dates, states) -> dict[tuple[int, str], dict]:
    actual = {}
    for index, date in enumerate(dates):
        if not index or str(date) < FIRST_PROMOTION_BANZUKE:
            continue
        state = states[date]
        previous = states[dates[index - 1]]
        for rikishi_id in state.banzuke.riks:
            rank = state.banzuke.rikchii[rikishi_id]
            prior_rank = previous.banzuke.rikchii.get(rikishi_id)
            if (
                rank.level == MSD.YOKOZUNA
                and prior_rank is not None
                and prior_rank.level != MSD.YOKOZUNA
            ):
                key = (int(rikishi_id), str(date))
                actual[key] = {
                    "rikishi_id": int(rikishi_id),
                    "shikona": str(state.banzuke.rikshik[rikishi_id]),
                    "promotion_banzuke": str(date),
                    "prior_rank": str(prior_rank),
                }
    return actual


def _window_row(first_date, second_date, next_date, first, second, next_state,
                rikishi_id, *, source="history") -> dict:
    next_rank = next_state.banzuke.rikchii.get(rikishi_id) if next_state else None
    return {
        "rikishi_id": int(rikishi_id),
        "shikona": str(second.banzuke.rikshik[rikishi_id]),
        "first_basho": str(first_date),
        "second_basho": str(second_date),
        "promotion_banzuke": str(next_date) if next_date is not None else None,
        "sequence": _symbol(first, rikishi_id) + _symbol(second, rikishi_id),
        "first_rank": str(first.banzuke.rikchii[rikishi_id]),
        "second_rank": str(second.banzuke.rikchii[rikishi_id]),
        "first_wins": _wins(first, rikishi_id),
        "second_wins": _wins(second, rikishi_id),
        "first_markers": _markers(first, rikishi_id),
        "second_markers": _markers(second, rikishi_id),
        "next_rank": str(next_rank) if next_rank is not None else None,
        "source": source,
        "resolved": next_rank is not None,
        "promoted": next_rank is not None and next_rank.level == MSD.YOKOZUNA,
    }


def build_observations(history) -> dict:
    """Project History into resolved two-basho Ozeki opportunities."""
    dates = sorted(history)
    if len(dates) < 3:
        raise ValueError("Yokozuna partition search requires at least three basho")
    states = {date: history(date) for date in dates}
    actual = _actual_promotions(dates, states)
    opportunities = []
    unresolved = []

    january_1958 = next((date for date in dates if str(date) == "1958/01"), None)
    march_1958 = next((date for date in dates if str(date) == "1958/03"), None)
    if january_1958 is not None and march_1958 is not None:
        january = states[january_1958]
        march = states[march_1958]
        supplement_id = next(
            (
                rikishi_id
                for rikishi_id in january.banzuke.riks
                if int(rikishi_id) == WAKANOHANA_BOUNDARY_SUPPLEMENT["rikishi_id"]
            ),
            None,
        )
        if supplement_id is not None:
            january_rank = january.banzuke.rikchii[supplement_id]
            next_rank = march.banzuke.rikchii.get(supplement_id)
            if january_rank.level == MSD.OZEKI:
                row = {
                    "rikishi_id": int(supplement_id),
                    "shikona": str(january.banzuke.rikshik[supplement_id]),
                    "first_basho": WAKANOHANA_BOUNDARY_SUPPLEMENT["basho"],
                    "second_basho": str(january_1958),
                    "promotion_banzuke": str(march_1958),
                    "sequence": "J" + _symbol(january, supplement_id),
                    "first_rank": WAKANOHANA_BOUNDARY_SUPPLEMENT["rank"],
                    "second_rank": str(january_rank),
                    "first_wins": WAKANOHANA_BOUNDARY_SUPPLEMENT["wins"],
                    "second_wins": _wins(january, supplement_id),
                    "first_markers": WAKANOHANA_BOUNDARY_SUPPLEMENT["markers"],
                    "second_markers": _markers(january, supplement_id),
                    "next_rank": str(next_rank) if next_rank is not None else None,
                    "source": "user_supplied + history",
                    "resolved": next_rank is not None,
                    "promoted": next_rank is not None and next_rank.level == MSD.YOKOZUNA,
                }
                (opportunities if row["resolved"] else unresolved).append(row)

    for end_index in range(1, len(dates)):
        first_date, second_date = dates[end_index - 1 : end_index + 1]
        next_date = dates[end_index + 1] if end_index + 1 < len(dates) else None
        first, second = states[first_date], states[second_date]
        next_state = states[next_date] if next_date is not None else None
        common = set(first.banzuke.riks) & set(second.banzuke.riks)
        for rikishi_id in sorted(common):
            if not all(
                state.banzuke.rikchii[rikishi_id].level == MSD.OZEKI
                for state in (first, second)
            ):
                continue
            row = _window_row(
                first_date, second_date, next_date, first, second, next_state, rikishi_id
            )
            if row["promotion_banzuke"] is not None and row["promotion_banzuke"] < FIRST_PROMOTION_BANZUKE:
                continue
            (opportunities if row["resolved"] else unresolved).append(row)

    keys = [(row["rikishi_id"], row["promotion_banzuke"]) for row in opportunities]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate resolved promotion opportunities")
    opportunity_keys = set(keys)
    missing_actual = sorted(set(actual) - opportunity_keys)
    return {
        "dates": dates,
        "actual": actual,
        "opportunities": opportunities,
        "unresolved": unresolved,
        "actual_without_two_ozeki_basho": [actual[key] for key in missing_actual],
    }


def cell_counts(observations) -> dict[str, dict[str, int]]:
    counts = {sequence: {"tp": 0, "fp": 0, "observations": 0} for sequence in SEQUENCES}
    for row in observations:
        cell = counts[row["sequence"]]
        cell["tp" if row["promoted"] else "fp"] += 1
        cell["observations"] += 1
    return counts


def find_best_partitions(counts, actual_promotions: int) -> dict:
    """Exhaust all 2^16 subsets, comparing F1 as exact integer ratios."""
    normalized = {
        sequence: {
            "tp": int(counts.get(sequence, {}).get("tp", 0)),
            "fp": int(counts.get(sequence, {}).get("fp", 0)),
        }
        for sequence in SEQUENCES
    }
    best_numerator, best_denominator = -1, 1
    winners = []
    for mask in range(1 << len(SEQUENCES)):
        included = tuple(
            sequence for bit, sequence in enumerate(SEQUENCES) if mask & (1 << bit)
        )
        tp = sum(normalized[sequence]["tp"] for sequence in included)
        fp = sum(normalized[sequence]["fp"] for sequence in included)
        fn = actual_promotions - tp
        numerator = 2 * tp
        denominator = 2 * tp + fp + fn
        if denominator == 0:
            numerator, denominator = 0, 1
        comparison = numerator * best_denominator - best_numerator * denominator
        if comparison > 0:
            best_numerator, best_denominator = numerator, denominator
            winners = [(included, tp, fp, fn)]
        elif comparison == 0:
            winners.append((included, tp, fp, fn))

    partitions = []
    for included, tp, fp, fn in winners:
        partitions.append(
            {
                "included": list(included),
                "excluded": [sequence for sequence in SEQUENCES if sequence not in included],
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "predicted_promotions": tp + fp,
                "precision": tp / (tp + fp) if tp + fp else 0.0,
                "recall": tp / (tp + fn) if tp + fn else 0.0,
                "f1": best_numerator / best_denominator,
            }
        )

    included_sets = [set(partition["included"]) for partition in partitions]
    included_in_every = set.intersection(*included_sets) if included_sets else set()
    included_in_any = set.union(*included_sets) if included_sets else set()
    divisor = gcd(best_numerator, best_denominator)
    return {
        "partitions_evaluated": 1 << len(SEQUENCES),
        "best_f1": best_numerator / best_denominator,
        "best_f1_fraction": (
            f"{best_numerator // divisor}/{best_denominator // divisor}"
            if divisor
            else "0/1"
        ),
        "best_partition_count": len(partitions),
        "included_in_every_best_partition": [
            sequence for sequence in SEQUENCES if sequence in included_in_every
        ],
        "included_in_some_but_not_all_best_partitions": [
            sequence
            for sequence in SEQUENCES
            if sequence in included_in_any - included_in_every
        ],
        "partitions": partitions,
    }


def evaluate_partitions(history) -> dict:
    projection = build_observations(history)
    counts = cell_counts(projection["opportunities"])
    search = find_best_partitions(counts, len(projection["actual"]))
    dates = projection["dates"]
    return {
        "schema_version": 1,
        "definition": (
            "Exhaustive in-sample F1 search over every subset of the 16 ordered "
            "two-basho Y/D/J/N sequences, requiring Ozeki rank in both basho."
        ),
        "symbols": {
            "Y": "Makuuchi yusho",
            "D": "Makuuchi doten-yusho",
            "J": "Makuuchi jun-yusho",
            "N": "No Y, D or J marker",
        },
        "first_promotion_banzuke": FIRST_PROMOTION_BANZUKE,
        "history_first_basho": str(dates[0]),
        "history_last_basho": str(dates[-1]),
        "history_basho_count": len(dates),
        "actual_promotions": len(projection["actual"]),
        "resolved_opportunities": len(projection["opportunities"]),
        "unresolved_opportunities": len(projection["unresolved"]),
        "actual_without_two_ozeki_basho": projection["actual_without_two_ozeki_basho"],
        "supplements": [WAKANOHANA_BOUNDARY_SUPPLEMENT],
        "cell_counts": counts,
        "search": search,
        "opportunities": projection["opportunities"],
        "unresolved": projection["unresolved"],
        "limitations": (
            "The maximizing partition is selected and scored on the same historical "
            "sample. It is descriptive, potentially overfit, and not held-out performance."
        ),
    }


def save_evaluation(history, output_path, *, source="live_store") -> Path:
    result = evaluate_partitions(history)
    result.update(source=source, generated_at=datetime.now(timezone.utc).isoformat())
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print("[1/4] Loading the live History snapshot...")
    from src.infra.live_store.api import get_history

    history = get_history()
    print("[2/4] Building two-basho Ozeki opportunities...")
    output = OUTPUT_ROOT / datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ_partitions.json"
    )
    print("[3/4] Evaluating all 65,536 partitions...")
    path = save_evaluation(history, output)
    result = json.loads(path.read_text(encoding="utf-8"))
    search = result["search"]
    print("[4/4] Wrote the audit artifact.")
    print()
    print("Yokozuna promotion: Y/D/J/N pair partition search")
    print(f"Output: {path.resolve()}")
    print(
        f"Sample: {result['actual_promotions']} promotions and "
        f"{result['resolved_opportunities']} resolved opportunities."
    )
    print(
        f"Best F1: {search['best_f1']:.2%} ({search['best_f1_fraction']}); "
        f"{search['best_partition_count']} tied best partition(s)."
    )
    print(
        "Required in every best partition: "
        + (", ".join(search["included_in_every_best_partition"]) or "(none)")
    )
    print(
        "Optional among tied best partitions: "
        + (
            ", ".join(search["included_in_some_but_not_all_best_partitions"])
            or "(none)"
        )
    )
    for index, partition in enumerate(search["partitions"], start=1):
        print(
            f"Partition {index}: {', '.join(partition['included']) or '(empty)'}; "
            f"TP {partition['tp']}, FP {partition['fp']}, FN {partition['fn']}, "
            f"precision {partition['precision']:.2%}, recall {partition['recall']:.2%}."
        )
    print("This is an in-sample descriptive maximum, not held-out performance.")


if __name__ == "__main__":
    main()

"""Find the maximum-F1 partition of the 64 ordered Y/D/J/N triples."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path

from src.sumo_core.BasicEnums import MSD

from .evaluate_rule import _markers, _wins
from .score_partitions import (
    CHAMPIONSHIP_MARKERS,
    OUTPUT_ROOT,
    SEQUENCES as PAIR_SEQUENCES,
    SYMBOLS,
    _actual_promotions,
    _symbol,
)


FIRST_PROMOTION_BANZUKE = "1958/07"
TRIPLES = tuple(
    first + second + third
    for first in SYMBOLS
    for second in SYMBOLS
    for third in SYMBOLS
)


def _triple_row(dates, states, start_index, rikishi_id) -> dict:
    first_date, second_date, third_date = dates[start_index : start_index + 3]
    next_date = dates[start_index + 3] if start_index + 3 < len(dates) else None
    first, second, third = (states[first_date], states[second_date], states[third_date])
    next_state = states[next_date] if next_date is not None else None
    next_rank = next_state.banzuke.rikchii.get(rikishi_id) if next_state else None
    return {
        "rikishi_id": int(rikishi_id),
        "shikona": str(third.banzuke.rikshik[rikishi_id]),
        "first_basho": str(first_date),
        "second_basho": str(second_date),
        "third_basho": str(third_date),
        "promotion_banzuke": str(next_date) if next_date is not None else None,
        "sequence": "".join(_symbol(state, rikishi_id) for state in (first, second, third)),
        "pair_sequence": _symbol(second, rikishi_id) + _symbol(third, rikishi_id),
        "first_rank": str(first.banzuke.rikchii[rikishi_id]),
        "second_rank": str(second.banzuke.rikchii[rikishi_id]),
        "third_rank": str(third.banzuke.rikchii[rikishi_id]),
        "first_wins": _wins(first, rikishi_id),
        "second_wins": _wins(second, rikishi_id),
        "third_wins": _wins(third, rikishi_id),
        "first_markers": _markers(first, rikishi_id),
        "second_markers": _markers(second, rikishi_id),
        "third_markers": _markers(third, rikishi_id),
        "next_rank": str(next_rank) if next_rank is not None else None,
        "source": "history",
        "resolved": next_rank is not None,
        "promoted": next_rank is not None and next_rank.level == MSD.YOKOZUNA,
    }


def build_triple_observations(history) -> dict:
    """Build three-basho contexts whose final two ranks are both Ozeki."""
    dates = sorted(history)
    if len(dates) < 4:
        raise ValueError("Yokozuna triple search requires at least four basho")
    states = {date: history(date) for date in dates}
    actual = {
        key: row
        for key, row in _actual_promotions(dates, states).items()
        if row["promotion_banzuke"] >= FIRST_PROMOTION_BANZUKE
    }
    opportunities = []
    unresolved = []

    for start_index in range(len(dates) - 2):
        first_date, second_date, third_date = dates[start_index : start_index + 3]
        first, second, third = states[first_date], states[second_date], states[third_date]
        common = set(first.banzuke.riks) & set(second.banzuke.riks) & set(third.banzuke.riks)
        for rikishi_id in sorted(common):
            first_rank = first.banzuke.rikchii[rikishi_id]
            if not isinstance(first_rank.level, MSD):
                continue
            if not all(
                state.banzuke.rikchii[rikishi_id].level == MSD.OZEKI
                for state in (second, third)
            ):
                continue
            row = _triple_row(dates, states, start_index, rikishi_id)
            if (
                row["promotion_banzuke"] is not None
                and row["promotion_banzuke"] < FIRST_PROMOTION_BANZUKE
            ):
                continue
            (opportunities if row["resolved"] else unresolved).append(row)

    keys = [(row["rikishi_id"], row["promotion_banzuke"]) for row in opportunities]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate resolved triple opportunities")
    missing_actual = sorted(set(actual) - set(keys))
    return {
        "dates": dates,
        "actual": actual,
        "opportunities": opportunities,
        "unresolved": unresolved,
        "actual_without_three_basho_context": [actual[key] for key in missing_actual],
    }


def count_cells(observations, sequences, *, field="sequence") -> dict[str, dict[str, int]]:
    counts = {sequence: {"tp": 0, "fp": 0, "observations": 0} for sequence in sequences}
    for row in observations:
        cell = counts[row[field]]
        cell["tp" if row["promoted"] else "fp"] += 1
        cell["observations"] += 1
    return counts


def _metrics(included, counts, actual_promotions) -> dict:
    tp = sum(counts[sequence]["tp"] for sequence in included)
    fp = sum(counts[sequence]["fp"] for sequence in included)
    fn = actual_promotions - tp
    denominator = 2 * tp + fp + fn
    f1 = Fraction(2 * tp, denominator) if denominator else Fraction(0, 1)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "predicted_promotions": tp + fp,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "f1": float(f1),
        "f1_fraction": str(f1),
    }


def find_best_threshold_partition(counts, sequences, actual_promotions: int) -> dict:
    """Find the exact best cell subset for F1 using cell-rate thresholds."""
    observed = [sequence for sequence in sequences if counts[sequence]["observations"]]
    empty = [sequence for sequence in sequences if not counts[sequence]["observations"]]
    rates = {
        sequence: Fraction(counts[sequence]["tp"], counts[sequence]["observations"])
        for sequence in observed
    }
    rate_groups = sorted(set(rates.values()), reverse=True)
    candidates = [frozenset()]
    included = set()
    for rate in rate_groups:
        included.update(sequence for sequence in observed if rates[sequence] == rate)
        candidates.append(frozenset(included))

    scored = [(candidate, _metrics(candidate, counts, actual_promotions)) for candidate in candidates]
    best_fraction = max(Fraction(metrics["f1_fraction"]) for _, metrics in scored)
    threshold = best_fraction / 2
    mandatory = [sequence for sequence in sequences if sequence in rates and rates[sequence] > threshold]
    optional = [sequence for sequence in sequences if sequence in rates and rates[sequence] == threshold]
    excluded = [sequence for sequence in sequences if sequence in rates and rates[sequence] < threshold]
    conservative = _metrics(mandatory, counts, actual_promotions)
    expansive = _metrics(mandatory + optional, counts, actual_promotions)
    if Fraction(conservative["f1_fraction"]) != best_fraction:
        raise AssertionError("Threshold optimizer did not reproduce the best F1")
    if Fraction(expansive["f1_fraction"]) != best_fraction:
        raise AssertionError("Optional boundary cells changed the best F1")
    return {
        "method": "Exact promotion-rate threshold search over non-empty cells.",
        "thresholds_evaluated": len(candidates),
        "best_f1": float(best_fraction),
        "best_f1_fraction": str(best_fraction),
        "cell_inclusion_threshold": float(threshold),
        "cell_inclusion_threshold_fraction": str(threshold),
        "included_in_every_best_partition": mandatory,
        "included_in_some_but_not_all_best_partitions": optional,
        "excluded_from_every_best_partition": excluded,
        "empty_cells": empty,
        "observationally_distinct_best_partition_count": 1 << len(optional),
        "formal_best_partition_count_including_empty_cells": 1 << (len(optional) + len(empty)),
        "conservative_best_partition": {
            "included": mandatory,
            **conservative,
        },
        "expansive_best_partition": {
            "included": mandatory + optional,
            **expansive,
        },
    }


def evaluate_triple_partitions(history) -> dict:
    projection = build_triple_observations(history)
    actual_count = len(projection["actual"])
    triple_counts = count_cells(projection["opportunities"], TRIPLES)
    pair_counts = count_cells(
        projection["opportunities"], PAIR_SEQUENCES, field="pair_sequence"
    )
    triple_search = find_best_threshold_partition(triple_counts, TRIPLES, actual_count)
    pair_search = find_best_threshold_partition(pair_counts, PAIR_SEQUENCES, actual_count)
    dates = projection["dates"]
    return {
        "schema_version": 1,
        "definition": (
            "Maximum-F1 partitions of ordered Y/D/J/N triples. The final two "
            "basho must be at Ozeki; the first is Makuuchi context at any rank."
        ),
        "symbols": {
            **{symbol: prize.value for prize, symbol in CHAMPIONSHIP_MARKERS.items()},
            "N": "No Y, D or J marker",
        },
        "first_promotion_banzuke": FIRST_PROMOTION_BANZUKE,
        "history_first_basho": str(dates[0]),
        "history_last_basho": str(dates[-1]),
        "history_basho_count": len(dates),
        "actual_promotions": actual_count,
        "resolved_opportunities": len(projection["opportunities"]),
        "unresolved_opportunities": len(projection["unresolved"]),
        "actual_without_three_basho_context": projection[
            "actual_without_three_basho_context"
        ],
        "triple_cell_counts": triple_counts,
        "triple_search": triple_search,
        "same_sample_pair_cell_counts": pair_counts,
        "same_sample_pair_search": pair_search,
        "opportunities": projection["opportunities"],
        "unresolved": projection["unresolved"],
        "limitations": (
            "The maximizing partitions are selected and scored on the same historical "
            "sample. Triple cells are sparse, so higher in-sample F1 may reflect "
            "fragmentation rather than a stable promotion rule."
        ),
    }


def _format_sequences(sequences) -> str:
    return ", ".join(sequences) if sequences else "(none)"


def print_human_summary(result, path: Path) -> None:
    triple = result["triple_search"]
    pair = result["same_sample_pair_search"]
    conservative = triple["conservative_best_partition"]
    expansive = triple["expansive_best_partition"]
    print()
    print("Yokozuna promotion: Y/D/J/N triple partition search")
    print(f"Output: {path.resolve()}")
    print(
        f"Sample: {result['actual_promotions']} promotions and "
        f"{result['resolved_opportunities']} resolved opportunities; "
        f"promotion banzuke {result['first_promotion_banzuke']} through "
        f"{result['history_last_basho']}."
    )
    print(
        f"Best triple F1: {triple['best_f1']:.2%} "
        f"({triple['best_f1_fraction']}); "
        f"same-sample pair F1: {pair['best_f1']:.2%}."
    )
    print(
        "Required in every best triple partition: "
        + _format_sequences(triple["included_in_every_best_partition"])
    )
    print(
        "Optional at the optimum threshold: "
        + _format_sequences(triple["included_in_some_but_not_all_best_partitions"])
    )
    print(
        "Conservative optimum: "
        f"TP {conservative['tp']}, FP {conservative['fp']}, FN {conservative['fn']}, "
        f"precision {conservative['precision']:.2%}, recall {conservative['recall']:.2%}."
    )
    if expansive["included"] != conservative["included"]:
        print(
            "Expansive tied optimum: "
            f"TP {expansive['tp']}, FP {expansive['fp']}, FN {expansive['fn']}, "
            f"precision {expansive['precision']:.2%}, recall {expansive['recall']:.2%}."
        )
    print(
        f"Empty triple cells: {len(triple['empty_cells'])}; unresolved opportunities: "
        f"{result['unresolved_opportunities']}."
    )
    print("This is an in-sample descriptive maximum, not held-out performance.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print("[1/5] Loading the live History snapshot...")
    from src.infra.live_store.api import get_history

    history = get_history()
    print("[2/5] Building three-basho Ozeki opportunities...")
    result = evaluate_triple_partitions(history)
    print("[3/5] Optimized the 64 triple cells by exact F1 thresholds.")
    print("[4/5] Compared with the pair optimum on the identical sample.")
    output = OUTPUT_ROOT / datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ_triples.json"
    )
    result.update(source="live_store", generated_at=datetime.now(timezone.utc).isoformat())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("[5/5] Wrote the audit artifact.")
    print_human_summary(result, output)


if __name__ == "__main__":
    main()

"""Build the Ozeki promotion-opportunity dataset from one History snapshot."""

from collections import Counter

from src.analysis.promotion.ozeki.analysis import analyse_history
from src.sumo_core.BasicEnums import MSD, Outcome


FIRST_PROMOTION_BANZUKE = "1958/07"
RANK_LABEL = {
    MSD.MAEGASHIRA: "M",
    MSD.KOMUSUBI: "K",
    MSD.SEKIWAKE: "S",
}


def _regular_record(state, rikishi_id):
    counts = Counter()
    for day, daily in state.summary.items():
        if int(day) > 15:
            continue
        outcomes = []
        for bout in daily.results_lookup.values():
            if bout.rikishi1 == rikishi_id:
                outcomes.append(bout.outcome1)
            elif bout.rikishi2 == rikishi_id:
                outcomes.append(bout.outcome2)
        if len(outcomes) > 1:
            raise ValueError(
                f"Multiple regular results for rikishi {rikishi_id} on day {day}"
            )
        counts.update(outcomes)
    return {
        "wins": counts[Outcome.W] + counts[Outcome.FS],
        "losses": counts[Outcome.L] + counts[Outcome.FP],
        "draws": counts[Outcome.DRAW],
        "recorded_bouts": sum(counts.values()),
    }


def build_dataset(history):
    """Return candidate windows and audited promotion events.

    Candidate windows have a first basho at M/K/S and final two basho at K/S.
    Promotion events outside that pool remain in ``promotions`` so rule recall
    is measured against every retained qualification event.
    """
    dates = sorted(history)
    if not dates:
        raise ValueError("Promotion-prospects analysis requires a non-empty History")

    audit = analyse_history(history)
    excluded = {
        (row["rikishi_id"], row["first_ozeki_banzuke"])
        for row in audit["excluded"]
    }
    promotions = [
        dict(row)
        for row in audit["events"]
        if row["first_ozeki_banzuke"] >= FIRST_PROMOTION_BANZUKE
    ]
    actual = {
        (row["rikishi_id"], row["first_ozeki_banzuke"])
        for row in promotions
    }

    states = {str(date): history(date) for date in dates}
    observations = {}
    for date in dates:
        date_text = str(date)
        state = history(date)
        rows = {}
        for rikishi_id, rank in state.banzuke.rikchii.items():
            if rank.level not in RANK_LABEL:
                continue
            row = {
                "rank": str(rank),
                "rank_group": RANK_LABEL[rank.level],
            }
            row.update(_regular_record(state, rikishi_id))
            rows[rikishi_id] = row
        observations[date_text] = rows

    ordered = sorted(observations)
    opportunities = []
    for index in range(2, len(ordered)):
        basho_dates = ordered[index - 2:index + 1]
        common = set.intersection(*(set(observations[date]) for date in basho_dates))
        for rikishi_id in sorted(common):
            rows = [observations[date][rikishi_id] for date in basho_dates]
            if any(row["rank_group"] not in {"K", "S"} for row in rows[1:]):
                continue
            next_basho = ordered[index + 1] if index + 1 < len(ordered) else None
            key = (int(rikishi_id), next_basho)
            if key in excluded:
                continue
            next_rank = (
                states[next_basho].banzuke.rikchii.get(rikishi_id)
                if next_basho else None
            )
            wins = [row["wins"] for row in rows]
            weakest = min(wins)
            weak_positions = [str(i + 1) for i, value in enumerate(wins) if value == weakest]
            resolved = next_rank is not None and next_basho >= FIRST_PROMOTION_BANZUKE
            opportunities.append({
                "opportunity_id": f"{basho_dates[-1]}:{int(rikishi_id)}",
                "rikishi_id": int(rikishi_id),
                "shikona": str(states[basho_dates[-1]].banzuke.rikshik[rikishi_id]),
                "first_basho": basho_dates[0],
                "second_basho": basho_dates[1],
                "third_basho": basho_dates[2],
                "next_basho": next_basho,
                "first_rank": rows[0]["rank"],
                "second_rank": rows[1]["rank"],
                "third_rank": rows[2]["rank"],
                "rank_pattern": "-".join(row["rank_group"] for row in rows),
                "first_wins": wins[0],
                "second_wins": wins[1],
                "third_wins": wins[2],
                "total_wins": sum(wins),
                "minimum_wins": weakest,
                "weak_result_position": ",".join(weak_positions),
                "recorded_bouts": sum(row["recorded_bouts"] for row in rows),
                "complete_45_bouts": all(row["recorded_bouts"] == 15 for row in rows),
                "next_rank": str(next_rank) if next_rank is not None else None,
                "resolved": resolved,
                "promoted": resolved and key in actual,
            })

    return {
        "opportunities": opportunities,
        "promotions": promotions,
        "excluded_reinstatements": audit["excluded"],
        "boundary_cases": audit["boundary"],
        "basho_dates": [str(date) for date in dates],
    }


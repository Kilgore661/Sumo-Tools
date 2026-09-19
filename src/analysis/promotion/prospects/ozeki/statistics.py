"""Statistical summaries for Ozeki promotion prospects."""

from collections import Counter
import math
import random


FIXED_PERIODS = ((1958, 1979), (1980, 1999), (2000, 9999))
RULES = tuple(
    [(family, threshold, 0) for family in ("A", "B") for threshold in range(28, 35)]
    + [("C", 33, 10)]
)


def ratio(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def wilson_interval(successes, observations, z=1.959963984540054):
    if not observations:
        return None, None
    proportion = successes / observations
    denominator = 1 + z * z / observations
    centre = proportion + z * z / (2 * observations)
    margin = z * math.sqrt(
        (proportion * (1 - proportion) + z * z / (4 * observations))
        / observations
    )
    return (centre - margin) / denominator, (centre + margin) / denominator


def _year(value):
    return int(value[:4])


def in_period(value, start, end):
    return value is not None and start <= _year(value) <= end


def describe_groups(opportunities, field, values=None):
    """Describe complete, resolved windows grouped by one named field."""
    rows = [
        row for row in opportunities
        if row["resolved"] and row["complete_45_bouts"]
    ]
    groups = values if values is not None else sorted({row[field] for row in rows})
    result = []
    for value in groups:
        selected = [row for row in rows if row[field] == value]
        promoted = sum(row["promoted"] for row in selected)
        low, high = wilson_interval(promoted, len(selected))
        result.append({
            "group": value,
            "promoted": promoted,
            "resolved_opportunities": len(selected),
            "distinct_rikishi": len({row["rikishi_id"] for row in selected}),
            "promotion_rate": ratio(promoted, len(selected)),
            "wilson_95_low": low,
            "wilson_95_high": high,
        })
    return result


def _qualifies(row, family, threshold, minimum_basho_wins=0):
    if not row["resolved"]:
        return False
    if family in {"A", "C"} and row["rank_pattern"].startswith("M-"):
        return False
    return (
        row["total_wins"] >= threshold
        and row["minimum_wins"] >= minimum_basho_wins
    )


def score_rule(opportunities, promotions, family, threshold,
               minimum_basho_wins=0, period=None):
    candidate_rows = opportunities
    promotion_rows = promotions
    if period is not None:
        start, end = period
        candidate_rows = [
            row for row in candidate_rows
            if in_period(row["next_basho"], start, end)
        ]
        promotion_rows = [
            row for row in promotion_rows
            if in_period(row["first_ozeki_banzuke"], start, end)
        ]
    predicted_rows = [
        row for row in candidate_rows
        if _qualifies(row, family, threshold, minimum_basho_wins)
    ]
    predicted = {
        (row["rikishi_id"], row["next_basho"]) for row in predicted_rows
    }
    actual = {
        (row["rikishi_id"], row["first_ozeki_banzuke"])
        for row in promotion_rows
    }
    tp = len(predicted & actual)
    fp = len(predicted - actual)
    fn = len(actual - predicted)
    true_positive_rikishi = {rikishi_id for rikishi_id, date in predicted & actual}
    false_positive_rikishi = {rikishi_id for rikishi_id, date in predicted - actual}
    false_negative_rikishi = {rikishi_id for rikishi_id, date in actual - predicted}
    precision_low, precision_high = wilson_interval(tp, tp + fp)
    recall_low, recall_high = wilson_interval(tp, tp + fn)
    return {
        "rule": f"{family}{threshold}",
        "family": family,
        "minimum_total_wins": threshold,
        "minimum_basho_wins": minimum_basho_wins,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "predicted_promotions": tp + fp,
        "actual_promotions": tp + fn,
        "precision": ratio(tp, tp + fp),
        "recall": ratio(tp, tp + fn),
        "f1": ratio(2 * tp, 2 * tp + fp + fn),
        "precision_wilson_95_low": precision_low,
        "precision_wilson_95_high": precision_high,
        "recall_wilson_95_low": recall_low,
        "recall_wilson_95_high": recall_high,
        "distinct_predicted_rikishi": len({row["rikishi_id"] for row in predicted_rows}),
        "distinct_actual_rikishi": len({rikishi_id for rikishi_id, date in actual}),
        "distinct_true_positive_rikishi": len(true_positive_rikishi),
        "distinct_false_positive_rikishi": len(false_positive_rikishi),
        "distinct_false_negative_rikishi": len(false_negative_rikishi),
    }


def _percentile(values, quantile):
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def clustered_intervals(opportunities, promotions, family, threshold,
                        minimum_basho_wins, samples, seed):
    """Bootstrap metric intervals, resampling whole rikishi clusters."""
    if samples <= 0:
        return {
            name: None for name in (
                "precision_cluster_95_low", "precision_cluster_95_high",
                "recall_cluster_95_low", "recall_cluster_95_high",
                "f1_cluster_95_low", "f1_cluster_95_high",
            )
        }
    opportunity_by_rikishi = {}
    promotion_by_rikishi = {}
    for row in opportunities:
        opportunity_by_rikishi.setdefault(row["rikishi_id"], []).append(row)
    for row in promotions:
        promotion_by_rikishi.setdefault(row["rikishi_id"], []).append(row)
    rikishi = sorted(set(opportunity_by_rikishi) | set(promotion_by_rikishi))
    if not rikishi:
        return clustered_intervals([], [], family, threshold,
                                   minimum_basho_wins, 0, seed)
    generator = random.Random(seed)
    metrics = {"precision": [], "recall": [], "f1": []}
    for _ in range(samples):
        counts = Counter(generator.choice(rikishi) for __ in rikishi)
        tp = fp = fn = 0
        for rikishi_id, multiplicity in counts.items():
            predicted = {
                row["next_basho"]
                for row in opportunity_by_rikishi.get(rikishi_id, [])
                if _qualifies(row, family, threshold, minimum_basho_wins)
            }
            actual = {
                row["first_ozeki_banzuke"]
                for row in promotion_by_rikishi.get(rikishi_id, [])
            }
            tp += multiplicity * len(predicted & actual)
            fp += multiplicity * len(predicted - actual)
            fn += multiplicity * len(actual - predicted)
        metrics["precision"].append(ratio(tp, tp + fp))
        metrics["recall"].append(ratio(tp, tp + fn))
        metrics["f1"].append(ratio(2 * tp, 2 * tp + fp + fn))
    result = {}
    for name, values in metrics.items():
        result[f"{name}_cluster_95_low"] = _percentile(values, 0.025)
        result[f"{name}_cluster_95_high"] = _percentile(values, 0.975)
    return result


def score_rules(opportunities, promotions, bootstrap_samples, seed):
    result = []
    for index, (family, threshold, minimum) in enumerate(RULES):
        row = score_rule(opportunities, promotions, family, threshold, minimum)
        row.update(clustered_intervals(
            opportunities, promotions, family, threshold, minimum,
            bootstrap_samples, seed + index,
        ))
        result.append(row)
    return result


def period_scores(opportunities, promotions):
    rows = []
    for start, end in FIXED_PERIODS:
        label = f"{start}-{end if end < 9999 else 'latest'}"
        for family, threshold, minimum in RULES:
            row = score_rule(
                opportunities, promotions, family, threshold, minimum,
                period=(start, end),
            )
            row["period"] = label
            rows.append(row)
    return rows


def forward_validation(opportunities, promotions):
    folds = (
        ((1958, 1979), (1980, 1999)),
        ((1958, 1999), (2000, 9999)),
    )
    rows = []
    for training_period, test_period in folds:
        candidates = [
            score_rule(opportunities, promotions, family, threshold, minimum,
                       period=training_period)
            for family, threshold, minimum in RULES
        ]
        selected = sorted(
            candidates,
            key=lambda row: (-row["f1"], -row["precision"], row["rule"]),
        )[0]
        test = score_rule(
            opportunities, promotions,
            selected["family"], selected["minimum_total_wins"],
            selected["minimum_basho_wins"], period=test_period,
        )
        rows.append({
            "training_period": f"{training_period[0]}-{training_period[1]}",
            "test_period": (
                f"{test_period[0]}-"
                f"{test_period[1] if test_period[1] < 9999 else 'latest'}"
            ),
            "selected_rule": selected["rule"],
            "training_tp": selected["tp"],
            "training_fp": selected["fp"],
            "training_fn": selected["fn"],
            "training_precision": selected["precision"],
            "training_recall": selected["recall"],
            "training_f1": selected["f1"],
            "test_tp": test["tp"],
            "test_fp": test["fp"],
            "test_fn": test["fn"],
            "test_precision": test["precision"],
            "test_recall": test["recall"],
            "test_f1": test["f1"],
        })
    return rows

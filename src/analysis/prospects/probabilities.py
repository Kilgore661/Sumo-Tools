from __future__ import annotations

from collections import Counter, defaultdict

from .model import CohortObservation, ProbabilityRow


DIVISION_ORDER = ("M", "J", "Ms", "Sd", "Jd", "Jk")


def aggregate_probabilities(
    observations: tuple[CohortObservation, ...],
    *,
    cohort_type: str,
    cutoff: str,
) -> tuple[ProbabilityRow, ...]:
    groups = defaultdict(list)
    for row in observations:
        if row.cohort_type == cohort_type:
            groups[(row.division, row.age)].append(row)
    return tuple(
        _row(division, age, rows, cutoff)
        for (division, age), rows in sorted(
            groups.items(), key=lambda item: (DIVISION_ORDER.index(item[0][0]), item[0][1])
        )
    )


def _row(division, age, rows, cutoff):
    counts = Counter(row.outcome for row in rows)
    total = len(rows)
    success = counts["success"]
    failure = counts["failure"]
    censored = counts["right_censored"]
    unknown = counts["unknown"]
    resolved = success + failure
    return ProbabilityRow(
        division, age, total, success, failure, censored, unknown, resolved,
        success / resolved if resolved else "",
        success / total,
        (success + censored + unknown) / total,
        cutoff,
    )

from __future__ import annotations

from collections import Counter, defaultdict

from src.analysis.site89.rikishi_bio_data import completed_years
from src.infra.get_bios.api import BioBashoDate, BioStore
from src.sumo_core.History import History

from .cohorts import prospect_division
from .lifecycle import classify_non_success_outcome
from .model import Population, RankStateObservation, RankStateProbabilityRow


def build_rank_state_observations(
    history: History,
    bios: BioStore,
    population: Population,
    coverage,
    first_sanyaku,
    cutoff_statuses,
) -> tuple[RankStateObservation, ...]:
    """Return one observation for every eligible pre-san'yaku banzuke appearance."""
    latest_ids = history[population.cutoff].banzuke.riks
    cutoff_bio = BioBashoDate.from_history_date(population.cutoff)
    rows: list[RankStateObservation] = []

    for index, basho in enumerate(population.dates):
        banzuke = history[basho].banzuke
        start_date = coverage[basho].start_date
        for rikishi_id, chii in banzuke.rikchii.items():
            if rikishi_id not in population.birth_dated_ids:
                continue
            event = first_sanyaku.get(rikishi_id)
            if event is not None and event[0] <= index:
                continue
            division = prospect_division(chii)
            if division is None:
                continue

            if event is not None:
                outcome = "success"
                outcome_evidence = "later_sanyaku"
                follow_up = event[0] - index
                event_basho = str(population.dates[event[0]])
                event_chii = str(event[1])
            else:
                bio = bios[rikishi_id]
                outcome, outcome_evidence = classify_non_success_outcome(
                    rikishi_id,
                    bio=bio,
                    latest_ids=latest_ids,
                    cutoff_bio=cutoff_bio,
                    cutoff_statuses=cutoff_statuses,
                )
                follow_up = len(population.dates) - 1 - index
                event_basho = ""
                event_chii = ""

            bio = bios[rikishi_id]
            rows.append(
                RankStateObservation(
                    rikishi_id=int(rikishi_id),
                    shikona=str(banzuke.rikshik[rikishi_id]),
                    basho=str(basho),
                    start_date=start_date.isoformat(),
                    age=completed_years(bio.birth_date.value, start_date),
                    division=division,
                    rank_number=chii.number,
                    chii=str(chii),
                    first_sanyaku_basho=event_basho,
                    first_sanyaku_chii=event_chii,
                    outcome=outcome,
                    outcome_evidence=outcome_evidence,
                    follow_up_basho=follow_up,
                    intai="" if bio.intai is None else str(bio.intai),
                )
            )
    return tuple(rows)


def aggregate_rank_state_probabilities(
    observations: tuple[RankStateObservation, ...],
    *,
    cutoff: str,
) -> tuple[RankStateProbabilityRow, ...]:
    observation_counts = Counter()
    grouped: dict[tuple[str, int, int], dict[int, str]] = defaultdict(dict)
    for row in observations:
        key = (row.division, row.rank_number, row.age)
        observation_counts[key] += 1
        previous = grouped[key].setdefault(row.rikishi_id, row.outcome)
        if previous != row.outcome:
            raise ValueError("A rikishi has inconsistent outcomes within one rank-state cell")

    rows = []
    for (division, rank_number, age), rikishi_outcomes in sorted(
        grouped.items(), key=lambda item: (_division_order(item[0][0]), item[0][1], item[0][2])
    ):
        counts = Counter(rikishi_outcomes.values())
        success = counts["success"]
        failure = counts["failure"]
        censored = counts["right_censored"]
        unknown = counts["unknown"]
        resolved = success + failure
        total = resolved + censored + unknown
        rows.append(
            RankStateProbabilityRow(
                division=division,
                rank_number=rank_number,
                age=age,
                observations=observation_counts[(division, rank_number, age)],
                unique_rikishi=total,
                success=success,
                failure=failure,
                right_censored=censored,
                unknown=unknown,
                resolved=resolved,
                resolved_probability="" if resolved == 0 else success / resolved,
                lower_bound_probability=success / total,
                upper_bound_probability=(success + censored + unknown) / total,
                cutoff=cutoff,
            )
        )
    return tuple(rows)


def _division_order(division: str) -> int:
    return {"M": 0, "J": 1, "Ms": 2, "Sd": 3, "Jd": 4, "Jk": 5}[division]

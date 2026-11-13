from __future__ import annotations

from src.infra.get_bios.api import BioStore, BioBashoDate
from src.sumo_core.History import History

from .cohorts import PendingObservation
from .model import CohortObservation, Population


def classify_observations(
    pending: tuple[PendingObservation, ...],
    first_sanyaku,
    history: History,
    bios: BioStore,
    population: Population,
    coverage,
) -> tuple[CohortObservation, ...]:
    latest_ids = history[population.cutoff].banzuke.riks
    cutoff_bio = BioBashoDate.from_history_date(population.cutoff)
    rows = []
    for item in pending:
        event = first_sanyaku.get(item.rikishi_id)
        if event is not None and event[0] > item.basho_index:
            outcome = "success"
            follow_up = event[0] - item.basho_index
            event_basho = population.dates[event[0]]
            event_chii = str(event[1])
        else:
            bio = bios[item.rikishi_id]
            if bio.intai is not None and bio.intai <= cutoff_bio:
                outcome = "failure"
            elif item.rikishi_id in latest_ids:
                outcome = "right_censored"
            else:
                outcome = "unknown"
            follow_up = len(population.dates) - 1 - item.basho_index
            event_basho = ""
            event_chii = ""
        bio = bios[item.rikishi_id]
        observation_basho = population.dates[item.basho_index]
        debut_basho = population.dates[item.division_debut_index]
        rows.append(
            CohortObservation(
                cohort_type=item.cohort_type,
                rikishi_id=int(item.rikishi_id),
                shikona=str(bio.latest_shikona()),
                division=item.division,
                age=item.age,
                observation_basho=str(observation_basho),
                observation_start_date=str(coverage[observation_basho].start_date),
                observation_chii=str(item.chii),
                division_debut_basho=str(debut_basho),
                division_debut_age=item.division_debut_age,
                first_sanyaku_basho=str(event_basho),
                first_sanyaku_chii=event_chii,
                outcome=outcome,
                follow_up_basho=follow_up,
                intai="" if bio.intai is None else str(bio.intai),
            )
        )
    return tuple(rows)

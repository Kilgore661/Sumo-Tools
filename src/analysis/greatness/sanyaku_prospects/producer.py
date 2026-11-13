from __future__ import annotations

from pathlib import Path

from src.infra.get_bios.api import BioStore
from src.infra.parser.basho_calendar import basho_date_coverage
from src.sumo_core.History import Date, History

from .cohorts import build_pending_observations
from .model import OutputPaths
from .outcomes import classify_observations
from .outputs import write_bundle
from .population import build_population
from .probabilities import aggregate_probabilities


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/greatness/sanyaku_prospects")


def produce(
    history: History,
    bios: BioStore,
    *,
    epoch: Date | None = None,
    results_root: Path,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    source_manifest: dict[str, str] | None = None,
) -> OutputPaths:
    population = build_population(history, bios, epoch=epoch)
    coverage = {
        basho: basho_date_coverage(basho, results_root=results_root)
        for basho in population.dates
    }
    invalid = [row for row in coverage.values() if row.start_date is None or not row.consistent]
    if invalid:
        labels = ", ".join(str(row.basho) for row in invalid[:10])
        raise ValueError(f"Exact Day 1 coverage is missing or inconsistent: {labels}")
    pending, first_sanyaku = build_pending_observations(history, bios, population, coverage)
    observations = classify_observations(pending, first_sanyaku, history, bios, population, coverage)
    debut = aggregate_probabilities(observations, cohort_type="division_debut", cutoff=str(population.cutoff))
    state = aggregate_probabilities(observations, cohort_type="division_state", cutoff=str(population.cutoff))
    _validate(population, observations, debut, state)
    return write_bundle(
        output_root=output_root,
        population=population,
        coverage=coverage,
        observations=observations,
        debut_probabilities=debut,
        state_probabilities=state,
        source_manifest=source_manifest or {},
    )


def _validate(population, observations, debut, state) -> None:
    if len(population.history_ids) != len(population.boundary_ids) + len(population.complete_ids):
        raise ValueError("Population reconciliation failed")
    for row in (*debut, *state):
        if row.rikishi != row.success + row.failure + row.right_censored + row.unknown:
            raise ValueError("Outcome reconciliation failed")
        if row.resolved != row.success + row.failure:
            raise ValueError("Resolved-outcome reconciliation failed")
    for cohort_type, aggregates in (("division_debut", debut), ("division_state", state)):
        if sum(row.rikishi for row in aggregates) != sum(row.cohort_type == cohort_type for row in observations):
            raise ValueError(f"Atomic-to-aggregate reconciliation failed for {cohort_type}")

from __future__ import annotations

from pathlib import Path

from src.infra.get_bios.api import BioStore
from src.infra.get_bios.career_rows import load_cutoff_career_statuses
from src.infra.parser.basho_calendar import basho_date_coverage
from src.sumo_core.History import Date, History

from .cohorts import build_pending_observations
from .career_charts import build_career_chart_points
from .model import OutputPaths
from .outcomes import classify_observations
from .outputs import write_bundle
from .population import build_population
from .probabilities import aggregate_probabilities
from .rank_states import build_rank_state_observations, aggregate_rank_state_probabilities


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/greatness/sanyaku_prospects")


def produce(
    history: History,
    bios: BioStore,
    *,
    epoch: Date | None = None,
    results_root: Path,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    source_manifest: dict[str, str] | None = None,
    chart_rikishi_ids: tuple[int, ...] = (),
    career_pages_root: Path | None = None,
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
    latest_ids = history[population.cutoff].banzuke.riks
    status_candidates = {
        rikishi_id
        for rikishi_id in population.birth_dated_ids
        if rikishi_id not in latest_ids
        and rikishi_id not in first_sanyaku
        and bios[rikishi_id].intai is None
    }
    cutoff_statuses = (
        load_cutoff_career_statuses(
            career_pages_root,
            status_candidates,
            cutoff=population.cutoff,
        )
        if career_pages_root is not None
        else {}
    )
    observations = classify_observations(
        pending,
        first_sanyaku,
        history,
        bios,
        population,
        coverage,
        cutoff_statuses,
    )
    debut = aggregate_probabilities(observations, cohort_type="division_debut", cutoff=str(population.cutoff))
    state = aggregate_probabilities(observations, cohort_type="division_state", cutoff=str(population.cutoff))
    rank_state_observations = build_rank_state_observations(
        history, bios, population, coverage, first_sanyaku, cutoff_statuses
    )
    rank_state_probabilities = aggregate_rank_state_probabilities(
        rank_state_observations, cutoff=str(population.cutoff)
    )
    career_chart_points = build_career_chart_points(
        chart_rikishi_ids,
        observations=rank_state_observations,
        probabilities=rank_state_probabilities,
        first_sanyaku=first_sanyaku,
        history=history,
        bios=bios,
        population=population,
        coverage=coverage,
    )
    _validate(
        population,
        observations,
        debut,
        state,
        rank_state_observations,
        rank_state_probabilities,
        career_chart_points,
    )
    return write_bundle(
        output_root=output_root,
        population=population,
        coverage=coverage,
        observations=observations,
        debut_probabilities=debut,
        state_probabilities=state,
        rank_state_observations=rank_state_observations,
        rank_state_probabilities=rank_state_probabilities,
        career_chart_points=career_chart_points,
        source_manifest=source_manifest or {},
    )


def _validate(
    population,
    observations,
    debut,
    state,
    rank_state_observations,
    rank_state_probabilities,
    career_chart_points,
) -> None:
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
    if sum(row.observations for row in rank_state_probabilities) != len(rank_state_observations):
        raise ValueError("Rank-state atomic-to-aggregate reconciliation failed")

    probability_lookup = {
        (row.division, row.rank_number, row.age): row.resolved_probability
        for row in rank_state_probabilities
    }
    for point in career_chart_points:
        if point.point_kind == "sanyaku_attainment":
            if point.probability != 1.0:
                raise ValueError("San'yaku attainment point must be 100%")
            continue
        expected = probability_lookup[(point.division, point.rank_number, point.age)]
        if point.probability != expected:
            raise ValueError("Career chart point does not match rank-state probability")

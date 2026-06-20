"""History preprocessing for support-domain fixed-point experiments."""

from __future__ import annotations

from dataclasses import dataclass

from src.analysis.equelo.support_domain.measure import SupportMeasurement, measure_support
from src.analysis.equelo.support_domain.policy import collapse_chii
from src.sumo_core.BasicPrimitives import Riks, Torikumi
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History
from src.sumo_core.Summary import DailyResults, ResultLookup, Summary


@dataclass(frozen=True)
class FilteredHistory:
    """Cleaned and RFSC-filtered history for one support threshold."""

    history: History
    measurement: SupportMeasurement
    supported_chii: frozenset[Chii]
    domain_label: str
    retained_bouts: int
    ignored_bouts: int


def build_threshold_filtered_history(
    history: History,
    *,
    threshold: float,
    baseline_chii: Chii | None = None,
) -> FilteredHistory:
    """Collapse chii with RFSC and remove unsupported chii from the rating economy."""

    if baseline_chii is None:
        baseline_chii = Chii.from_str("M1e")

    measurement = measure_support(history)
    baseline_support = measurement.max_possible_rikishi_bouts[baseline_chii]
    if baseline_support <= 0:
        raise ValueError(f"Baseline chii has no support: {baseline_chii}")

    supported_chii = frozenset(
        chii
        for chii, support in measurement.max_possible_rikishi_bouts.items()
        if support / baseline_support >= threshold
    )
    filtered_history, retained_bouts, ignored_bouts = _filter_history(
        history,
        supported_chii=supported_chii,
    )

    return FilteredHistory(
        history=filtered_history,
        measurement=measurement,
        supported_chii=supported_chii,
        domain_label=f"support_ratio_m1e_gte_{threshold:g}",
        retained_bouts=retained_bouts,
        ignored_bouts=ignored_bouts,
    )


def build_max_chii_filtered_history(
    history: History,
    *,
    max_chii: Chii,
) -> FilteredHistory:
    """Collapse chii with RFSC and keep only chii at or above a fixed cutoff."""

    measurement = measure_support(history)
    supported_chii = frozenset(
        chii
        for chii in measurement.max_possible_rikishi_bouts
        if chii.ordinal() <= max_chii.ordinal()
    )
    filtered_history, retained_bouts, ignored_bouts = _filter_history(
        history,
        supported_chii=supported_chii,
    )

    return FilteredHistory(
        history=filtered_history,
        measurement=measurement,
        supported_chii=supported_chii,
        domain_label=f"max_chii_{max_chii}",
        retained_bouts=retained_bouts,
        ignored_bouts=ignored_bouts,
    )


def build_min_appearances_filtered_history(
    history: History,
    *,
    min_appearances: int,
) -> FilteredHistory:
    """Collapse chii with RFSC and keep chii with enough basho-start observations."""

    if min_appearances < 1:
        raise ValueError(f"min_appearances must be positive: {min_appearances}")

    measurement = measure_support(history)
    supported_chii = frozenset(
        chii
        for chii, appearances in measurement.appearances.items()
        if appearances >= min_appearances
    )
    filtered_history, retained_bouts, ignored_bouts = _filter_history(
        history,
        supported_chii=supported_chii,
    )

    return FilteredHistory(
        history=filtered_history,
        measurement=measurement,
        supported_chii=supported_chii,
        domain_label=f"min_appearances_{min_appearances}",
        retained_bouts=retained_bouts,
        ignored_bouts=ignored_bouts,
    )


def _filter_history(
    history: History,
    *,
    supported_chii: frozenset[Chii],
) -> tuple[History, int, int]:
    filtered = History()
    retained_bouts = 0
    ignored_bouts = 0

    for date in sorted(history.keys()):
        basho = history[date]
        collapsed_by_rikishi = {
            rikid: collapse_chii(chii)
            for rikid, chii in basho.banzuke.rikchii.items()
        }
        rikishi_to_keep = {
            rikid
            for rikid, chii in collapsed_by_rikishi.items()
            if chii in supported_chii
        }
        banzuke = _rebuild_banzuke(basho.banzuke, rikishi_to_keep, collapsed_by_rikishi)
        summary, kept, ignored = _filter_summary(
            basho.summary,
            rikishi_to_keep=rikishi_to_keep,
        )
        retained_bouts += kept
        ignored_bouts += ignored
        filtered[date] = BashoState(banzuke=banzuke, summary=summary)

    return filtered, retained_bouts, ignored_bouts


def _rebuild_banzuke(
    original: Banzuke,
    rikishi_to_keep: set,
    collapsed_by_rikishi: dict,
) -> Banzuke:
    return Banzuke(
        riks=Riks(rikishi_to_keep),
        rikchii=RikChii({
            rikid: collapsed_by_rikishi[rikid]
            for rikid in rikishi_to_keep
        }),
        rikshik=RikShikona({
            rikid: original.rikshik[rikid]
            for rikid in rikishi_to_keep
        }),
    )


def _filter_summary(
    summary: Summary,
    *,
    rikishi_to_keep: set,
) -> tuple[Summary, int, int]:
    filtered_days = {}
    retained_bouts = 0
    ignored_bouts = 0

    for day in sorted(summary.keys()):
        daily_results = summary[day]
        filtered_lookup = ResultLookup()

        for pair, bout in daily_results.results_lookup.items():
            if bout.rikishi1 in rikishi_to_keep and bout.rikishi2 in rikishi_to_keep:
                filtered_lookup[pair] = bout
                retained_bouts += 1
            else:
                ignored_bouts += 1

        filtered_days[day] = DailyResults(
            torikumi=Torikumi(filtered_lookup.keys()),
            results_lookup=filtered_lookup,
        )

    return Summary(filtered_days, performances=summary.performances), retained_bouts, ignored_bouts

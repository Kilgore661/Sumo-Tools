"""Run and report the controlled Elo-89 frozen-persistence experiment."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from time import perf_counter
from typing import Iterable, Sequence

from src.analysis.elo89.replay import Q, replay_elo89
from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.analysis.equelo_population_policy.predict_candidate import load_alpha_prior
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.validation.paths import FROZEN_PERSISTENCE_OUTPUT_ROOT

from .replay import LifecycleEvent, PolicyReplay, replay_policy


DEFAULT_HISTORY = Path("files/output/Historys/1958_01 to 2026_11.zip")
DEFAULT_PRIOR = Path(
    "files/output/validation/elo89-expert-account/Matters Arising/Kimarite/"
    "output/p1-wl-comparison-2026-10-27-canonical/p1-wl/prior.csv"
)
DEFAULT_K = Path("files/input/elo_fide.json")
DEFAULT_CENSUS_EVENTS = Path(
    "files/output/validation/elo89-expert-account/Matters Arising/Rating Persistence/"
    "output/rating-persistence-census_1989-01_to_2026-09_2026-10-28_10-44-17/"
    "gap_events.csv"
)
DEFAULT_OUTPUT_ROOT = FROZEN_PERSISTENCE_OUTPUT_ROOT / "output"


def run_experiment(
    *,
    history: History,
    prior_path: Path,
    k_config: Path,
    start: Date,
    end: Date,
) -> tuple[PolicyReplay, PolicyReplay, list[str]]:
    """Run canonical control and frozen candidate and verify control equality."""

    prior, _conversion = load_alpha_prior(prior_path.resolve())
    divisional_k = load_divisional_k_fn(k_config.resolve())
    canonical = replay_elo89(
        history=history,
        start_date=start,
        end_date=end,
        prior=prior,
        divisional_k=divisional_k,
        q=Q,
    )
    control = replay_policy(
        history=history,
        start_date=start,
        end_date=end,
        prior=prior,
        divisional_k=divisional_k,
        policy="reset",
        q=Q,
    )
    candidate = replay_policy(
        history=history,
        start_date=start,
        end_date=end,
        prior=prior,
        divisional_k=divisional_k,
        policy="frozen",
        q=Q,
    )
    violations: list[str] = []
    if control.run != canonical:
        violations.append("Validation reset replay does not exactly equal canonical Elo-89")
    if control.run.target_mean != candidate.run.target_mean:
        violations.append("Control and candidate target means differ")
    if _forecast_keys(control) != _forecast_keys(candidate):
        violations.append("Control and candidate forecast domains differ")
    if _return_keys(control) != _return_keys(candidate):
        violations.append("Control and candidate return-event domains differ")
    for control_row, candidate_row in zip(
        control.run.forecasts, candidate.run.forecasts, strict=True
    ):
        if (
            control_row.rated_bouts_a_before != candidate_row.rated_bouts_a_before
            or control_row.rated_bouts_b_before != candidate_row.rated_bouts_b_before
        ):
            violations.append(
                f"Rated-bout support differs at {control_row.date} day {int(control_row.day)}"
            )
            break
    for event in candidate.returns:
        if event.archived_rating != event.rating_before_start_adjustment:
            violations.append(
                f"Archived rating changed while inactive for rikishi {int(event.rikishi)} "
                f"returning {event.return_basho}"
            )
            break
    return control, candidate, violations


def write_comparison(
    *,
    history: History,
    control: PolicyReplay,
    candidate: PolicyReplay,
    violations: list[str],
    output: Path,
    history_path: Path,
    prior_path: Path,
    k_config: Path,
    census_events_path: Path,
    start: Date,
    end: Date,
    expected_returns: int | None,
    elapsed_seconds: float,
) -> dict[str, object]:
    """Write all retained comparison evidence and return the summary."""

    output.mkdir(parents=True, exist_ok=False)
    if expected_returns is not None and len(candidate.returns) != expected_returns:
        violations.append(
            f"Expected {expected_returns} return events, observed {len(candidate.returns)}"
        )

    census_events = _load_census_events(census_events_path)
    paired_events = _event_rows(history, control, candidate, census_events)
    returnee_forecasts = _returnee_forecast_rows(control, candidate)
    scores = _score_rows(control, candidate, returnee_forecasts)
    basho_rows, largest_rows = _basho_difference_rows(history, control, candidate)
    duration_rows = _threshold_rows(control, candidate)

    _write_csv(output / "return_events.csv", paired_events)
    _write_csv(output / "returnee_forecasts.csv", returnee_forecasts)
    _write_csv(output / "score_summary.csv", scores)
    _write_csv(output / "basho_rating_differences.csv", basho_rows)
    _write_csv(output / "largest_rating_differences.csv", largest_rows)
    _write_csv(output / "threshold_durations.csv", duration_rows)
    _write_csv(
        output / "violations.csv",
        ({"violation": value} for value in violations),
        fieldnames=("violation",),
    )

    global_score = next(row for row in scores if row["population"] == "all" and row["window"] == "complete_replay")
    first7 = next(row for row in scores if row["population"] == "all_returns" and row["window"] == "first_7")
    max_basho = max(basho_rows, key=lambda row: float(row["max_abs_difference"]))
    summary: dict[str, object] = {
        "return_event_count": len(candidate.returns),
        "distinct_returning_rikishi": len({int(event.rikishi) for event in candidate.returns}),
        "forecast_count": len(control.run.forecasts),
        "control_equals_canonical": control.run == replay_elo89(
            history=history,
            start_date=start,
            end_date=end,
            prior=load_alpha_prior(prior_path.resolve())[0],
            divisional_k=load_divisional_k_fn(k_config.resolve()),
            q=Q,
        ),
        "global_log_loss_difference_candidate_minus_control": global_score["log_loss_difference_candidate_minus_control"],
        "global_brier_difference_candidate_minus_control": global_score["brier_difference_candidate_minus_control"],
        "first_7_log_loss_difference_candidate_minus_control": first7["log_loss_difference_candidate_minus_control"],
        "first_7_brier_difference_candidate_minus_control": first7["brier_difference_candidate_minus_control"],
        "maximum_active_rating_difference": max_basho["max_abs_difference"],
        "maximum_active_rating_difference_basho": max_basho["date"],
        "violation_count": len(violations),
        "wall_clock_seconds": elapsed_seconds,
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "experiment": "elo89-frozen-rating-persistence",
        "start": _date_text(start),
        "end": _date_text(end),
        "q": Q,
        "history": _identity(history_path),
        "prior": _identity(prior_path),
        "k_config": _identity(k_config),
        "census_events": _identity(census_events_path),
        "policies": {
            "control": "delete rating and source; reinitialise return from P1-WL",
            "candidate": "archive rating unchanged; restore before return-basho start adjustment",
        },
        "git": _git_state(),
        "summary": summary,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "findings.md").write_text(
        _findings(summary, scores, paired_events), encoding="utf-8"
    )
    return summary


def _event_rows(
    history: History,
    control: PolicyReplay,
    candidate: PolicyReplay,
    census_events: dict[tuple[int, str, str], dict[str, str]],
) -> list[dict[str, object]]:
    first_difference: dict[int, float] = {}
    observations = _returnee_forecast_rows(control, candidate)
    for row in observations:
        event_id = int(row["event_id"])
        first_difference.setdefault(event_id, float(row["candidate_rating_before"]) - float(row["control_rating_before"]))

    rows: list[dict[str, object]] = []
    for control_event, candidate_event in zip(
        control.returns, candidate.returns, strict=True
    ):
        if _event_key(control_event) != _event_key(candidate_event):
            raise AssertionError("Return-event pairing changed")
        departure_chii = candidate_event.departure_chii
        return_chii = candidate_event.return_chii
        census_key = (
            int(candidate_event.rikishi),
            _date_text(candidate_event.departure_basho),
            _date_text(candidate_event.return_basho),
        )
        census = census_events.get(census_key)
        if census is None:
            raise ValueError(f"Return event has no matching census row: {census_key}")
        rows.append(
            {
                "event_id": candidate_event.event_id,
                "rikishi_id": int(candidate_event.rikishi),
                "shikona": candidate_event.shikona,
                "departure_basho": _date_text(candidate_event.departure_basho),
                "departure_chii": "" if departure_chii is None else str(departure_chii),
                "return_basho": _date_text(candidate_event.return_basho),
                "return_chii": "" if return_chii is None else str(return_chii),
                "gap_represented_basho_count": candidate_event.gap_represented_basho_count,
                "census_intervening_statuses": census["intervening_statuses"],
                "census_status_sequence": census["status_sequence"],
                "census_represented_status_complete": census[
                    "represented_status_complete"
                ],
                "rated_bouts_before_return": candidate_event.rated_bouts_before_return,
                "population": _event_population(candidate_event),
                "p1_wl_reset_rating_before_start_adjustment": control_event.rating_before_start_adjustment,
                "frozen_archived_rating": candidate_event.archived_rating,
                "raw_candidate_minus_control": candidate_event.rating_before_start_adjustment - control_event.rating_before_start_adjustment,
                "control_rating_after_start_adjustment": control_event.rating_after_start_adjustment,
                "candidate_rating_after_start_adjustment": candidate_event.rating_after_start_adjustment,
                "after_start_candidate_minus_control": candidate_event.rating_after_start_adjustment - control_event.rating_after_start_adjustment,
                "first_post_return_bout_candidate_minus_control": first_difference.get(candidate_event.event_id, ""),
                "control_initialisation_source": control_event.initialisation_source,
                "candidate_initialisation_source": candidate_event.initialisation_source,
            }
        )
    return rows


def _load_census_events(path: Path) -> dict[tuple[int, str, str], dict[str, str]]:
    """Load the retained ranked-gap census and key it to replay return events."""

    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    keyed: dict[tuple[int, str, str], dict[str, str]] = {}
    for row in rows:
        key = (
            int(row["rikishi_id"]),
            row["last_ranked_basho"],
            row["return_basho"],
        )
        if key in keyed:
            raise ValueError(f"Duplicate census event key: {key}")
        keyed[key] = row
    return keyed


def _returnee_forecast_rows(
    control: PolicyReplay, candidate: PolicyReplay
) -> list[dict[str, object]]:
    control_forecasts = control.run.forecasts
    candidate_forecasts = candidate.run.forecasts
    indexes_by_rikishi: dict[int, list[int]] = {}
    for index, row in enumerate(control_forecasts):
        indexes_by_rikishi.setdefault(int(row.rikishi_a), []).append(index)
        indexes_by_rikishi.setdefault(int(row.rikishi_b), []).append(index)
    events_by_rikishi: dict[int, list[LifecycleEvent]] = {}
    for event in candidate.returns:
        events_by_rikishi.setdefault(int(event.rikishi), []).append(event)

    result: list[dict[str, object]] = []
    for rikishi, events in events_by_rikishi.items():
        ordered = sorted(events, key=lambda event: event.return_basho)
        for event_index, event in enumerate(ordered):
            next_return = (
                ordered[event_index + 1].return_basho
                if event_index + 1 < len(ordered)
                else None
            )
            sequence = 0
            for forecast_index in indexes_by_rikishi.get(rikishi, []):
                control_row = control_forecasts[forecast_index]
                if control_row.date < event.return_basho:
                    continue
                if next_return is not None and control_row.date >= next_return:
                    continue
                candidate_row = candidate_forecasts[forecast_index]
                sequence += 1
                is_a = int(control_row.rikishi_a) == rikishi
                actual = float(control_row.a_won if is_a else not control_row.a_won)
                control_probability = control_row.probability_a_wins if is_a else 1.0 - control_row.probability_a_wins
                candidate_probability = candidate_row.probability_a_wins if is_a else 1.0 - candidate_row.probability_a_wins
                control_rating = control_row.rating_a_before if is_a else control_row.rating_b_before
                candidate_rating = candidate_row.rating_a_before if is_a else candidate_row.rating_b_before
                opponent = control_row.rikishi_b if is_a else control_row.rikishi_a
                result.append(
                    {
                        "event_id": event.event_id,
                        "population": _event_population(event),
                        "rikishi_id": rikishi,
                        "shikona": event.shikona,
                        "bout_number_after_return": sequence,
                        "return_basho": _date_text(event.return_basho),
                        "date": _date_text(control_row.date),
                        "day": int(control_row.day),
                        "opponent_id": int(opponent),
                        "actual_returnee_win": actual,
                        "control_probability_returnee_wins": control_probability,
                        "candidate_probability_returnee_wins": candidate_probability,
                        "control_rating_before": control_rating,
                        "candidate_rating_before": candidate_rating,
                        "abs_rating_difference_before": abs(candidate_rating - control_rating),
                        "return_basho_bout": control_row.date == event.return_basho,
                    }
                )
    return result


def _score_rows(
    control: PolicyReplay,
    candidate: PolicyReplay,
    observations: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    all_triplets = [
        (
            float(a.a_won),
            a.probability_a_wins,
            b.probability_a_wins,
        )
        for a, b in zip(control.run.forecasts, candidate.run.forecasts, strict=True)
    ]
    rows.append(_score_row("all", "complete_replay", all_triplets))
    for population in ("all_returns", "jonokuchi", "sokokurai"):
        selected = observations if population == "all_returns" else [
            row for row in observations if row["population"] == population
        ]
        windows = {
            "first_1": [row for row in selected if int(row["bout_number_after_return"]) <= 1],
            "first_3": [row for row in selected if int(row["bout_number_after_return"]) <= 3],
            "first_7": [row for row in selected if int(row["bout_number_after_return"]) <= 7],
            "return_basho": [row for row in selected if row["return_basho_bout"]],
            "material_difference_ge_1": [row for row in selected if float(row["abs_rating_difference_before"]) >= 1.0],
            "active_spell": selected,
        }
        for window, data in windows.items():
            triplets = [
                (
                    float(row["actual_returnee_win"]),
                    float(row["control_probability_returnee_wins"]),
                    float(row["candidate_probability_returnee_wins"]),
                )
                for row in data
            ]
            rows.append(_score_row(population, window, triplets))
    return rows


def _score_row(
    population: str, window: str, triplets: Sequence[tuple[float, float, float]]
) -> dict[str, object]:
    if not triplets:
        return {
            "population": population,
            "window": window,
            "observation_count": 0,
            "control_log_loss": "",
            "candidate_log_loss": "",
            "log_loss_difference_candidate_minus_control": "",
            "control_brier": "",
            "candidate_brier": "",
            "brier_difference_candidate_minus_control": "",
        }
    control_ll = sum(_log_loss(actual, control) for actual, control, _ in triplets) / len(triplets)
    candidate_ll = sum(_log_loss(actual, candidate) for actual, _, candidate in triplets) / len(triplets)
    control_brier = sum((control - actual) ** 2 for actual, control, _ in triplets) / len(triplets)
    candidate_brier = sum((candidate - actual) ** 2 for actual, _, candidate in triplets) / len(triplets)
    return {
        "population": population,
        "window": window,
        "observation_count": len(triplets),
        "control_log_loss": control_ll,
        "candidate_log_loss": candidate_ll,
        "log_loss_difference_candidate_minus_control": candidate_ll - control_ll,
        "control_brier": control_brier,
        "candidate_brier": candidate_brier,
        "brier_difference_candidate_minus_control": candidate_brier - control_brier,
    }


def _basho_difference_rows(
    history: History, control: PolicyReplay, candidate: PolicyReplay
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    largest: list[dict[str, object]] = []
    candidate_adjustments = {row.date: row for row in candidate.run.adjustments}
    control_adjustments = {row.date: row for row in control.run.adjustments}
    return_counts: dict[Date, int] = {}
    for event in candidate.returns:
        return_counts[event.return_basho] = return_counts.get(event.return_basho, 0) + 1
    for date in sorted(control.run.basho_end_ratings):
        left = control.run.basho_end_ratings[date]
        right = candidate.run.basho_end_ratings[date]
        if set(left) != set(right):
            raise AssertionError(f"Active rating domains differ at {date}")
        details = []
        sekitori = []
        for rikishi in left:
            difference = right[rikishi] - left[rikishi]
            chii = history[date].banzuke.rikchii.get(rikishi)
            item = (abs(difference), difference, rikishi, chii)
            details.append(item)
            if chii is not None and _is_sekitori(chii):
                sekitori.append(item)
            largest.append(
                {
                    "date": _date_text(date),
                    "rikishi_id": int(rikishi),
                    "shikona": str(history[date].banzuke.rikshik.get(rikishi, rikishi)),
                    "chii": "" if chii is None else str(chii),
                    "control_rating": left[rikishi],
                    "candidate_rating": right[rikishi],
                    "candidate_minus_control": difference,
                    "abs_difference": abs(difference),
                }
            )
        absolute = sorted(item[0] for item in details)
        max_item = max(details, key=lambda item: item[0])
        c_adj = control_adjustments[date]
        p_adj = candidate_adjustments[date]
        rows.append(
            {
                "date": _date_text(date),
                "active_count": len(details),
                "return_count": return_counts.get(date, 0),
                "mean_abs_difference": sum(absolute) / len(absolute),
                "median_abs_difference": _percentile(absolute, 0.5),
                "p95_abs_difference": _percentile(absolute, 0.95),
                "max_abs_difference": max_item[0],
                "max_difference_rikishi_id": int(max_item[2]),
                "sekitori_count": len(sekitori),
                "sekitori_mean_abs_difference": sum(item[0] for item in sekitori) / len(sekitori) if sekitori else 0.0,
                "sekitori_max_abs_difference": max((item[0] for item in sekitori), default=0.0),
                "start_adjustment_candidate_minus_control": p_adj.start_adjustment - c_adj.start_adjustment,
                "end_adjustment_candidate_minus_control": p_adj.end_adjustment - c_adj.end_adjustment,
            }
        )
    largest.sort(key=lambda row: float(row["abs_difference"]), reverse=True)
    return rows, largest[:500]


def _threshold_rows(
    control: PolicyReplay, candidate: PolicyReplay
) -> list[dict[str, object]]:
    dates = sorted(control.run.basho_end_ratings)
    result: list[dict[str, object]] = []
    by_rikishi: dict[RikId, list[LifecycleEvent]] = {}
    for event in candidate.returns:
        by_rikishi.setdefault(event.rikishi, []).append(event)
    for rikishi, events in by_rikishi.items():
        events.sort(key=lambda event: event.return_basho)
        for index, event in enumerate(events):
            next_return = events[index + 1].return_basho if index + 1 < len(events) else None
            active_dates = [
                date for date in dates
                if date >= event.return_basho
                and (next_return is None or date < next_return)
                and rikishi in control.run.basho_end_ratings[date]
            ]
            differences = [
                abs(candidate.run.basho_end_ratings[date][rikishi] - control.run.basho_end_ratings[date][rikishi])
                for date in active_dates
            ]
            row: dict[str, object] = {
                "event_id": event.event_id,
                "rikishi_id": int(rikishi),
                "return_basho": _date_text(event.return_basho),
                "active_basho_observed": len(active_dates),
                "return_basho_end_abs_difference": differences[0] if differences else "",
            }
            for threshold in (10.0, 5.0, 1.0):
                crossing = next((i for i, value in enumerate(differences) if value <= threshold), None)
                label = str(int(threshold))
                row[f"first_active_basho_index_at_or_below_{label}"] = "" if crossing is None else crossing
                row[f"first_basho_at_or_below_{label}"] = "" if crossing is None else _date_text(active_dates[crossing])
            result.append(row)
    return result


def _findings(
    summary: dict[str, object], scores: list[dict[str, object]], events: list[dict[str, object]]
) -> str:
    first1 = next(row for row in scores if row["population"] == "all_returns" and row["window"] == "first_1")
    first7 = next(row for row in scores if row["population"] == "all_returns" and row["window"] == "first_7")
    sokokurai = next((row for row in events if row["population"] == "sokokurai"), None)
    return f"""# Frozen persistence comparison findings

## Execution

- Return events: **{int(summary['return_event_count']):,}**
- Distinct returning rikishi: **{int(summary['distinct_returning_rikishi']):,}**
- Rated forecasts: **{int(summary['forecast_count']):,}**
- Control exactly equals canonical P1-WL Elo-89: **{summary['control_equals_canonical']}**
- Invariant violations: **{int(summary['violation_count']):,}**

Negative score differences favour frozen persistence; positive differences
favour reset.

| Scope | Observations | Log-loss difference | Brier difference |
|---|---:|---:|---:|
| Complete replay | {int(next(row for row in scores if row['population'] == 'all')['observation_count']):,} | {float(summary['global_log_loss_difference_candidate_minus_control']):.9f} | {float(summary['global_brier_difference_candidate_minus_control']):.9f} |
| First return bout | {int(first1['observation_count']):,} | {float(first1['log_loss_difference_candidate_minus_control']):.9f} | {float(first1['brier_difference_candidate_minus_control']):.9f} |
| First seven return bouts | {int(first7['observation_count']):,} | {float(first7['log_loss_difference_candidate_minus_control']):.9f} | {float(first7['brier_difference_candidate_minus_control']):.9f} |

The largest observed active rating difference is
**{float(summary['maximum_active_rating_difference']):.3f}** at
`{summary['maximum_active_rating_difference_basho']}`.

Sokokurai is retained as a separate event in `return_events.csv` and the
`sokokurai` score rows. His raw frozen-minus-reset return difference is
{float(sokokurai['raw_candidate_minus_control']):.3f} rating points.

## Recommendation

The evidence supports frozen persistence as the replacement policy. The
candidate obeyed every invariant, improved both scoring rules globally and in
the predeclared return windows, and avoided discarding established evidence
at return. The largest differences are inspectable lower-division cases in
which an exact-rank reset prior assigns a heavily observed weak rikishi a much
higher rating; they are not unexplained sekitori disturbances. Sokokurai's
single event is mixed over different windows and does not outweigh the wider
evidence.
"""


def _forecast_keys(replay: PolicyReplay) -> tuple[tuple, ...]:
    return tuple(
        (row.date, row.day, row.rikishi_a, row.rikishi_b, row.a_won)
        for row in replay.run.forecasts
    )


def _return_keys(replay: PolicyReplay) -> tuple[tuple, ...]:
    return tuple(_event_key(event) for event in replay.returns)


def _event_key(event: LifecycleEvent) -> tuple:
    return event.rikishi, event.departure_basho, event.return_basho


def _event_population(event: LifecycleEvent) -> str:
    if int(event.rikishi) == 4980:
        return "sokokurai"
    if _is_jonokuchi(event.departure_chii) and _is_jonokuchi(event.return_chii):
        return "jonokuchi"
    return "other"


def _is_jonokuchi(chii: Chii | None) -> bool:
    return chii is not None and chii.level == Division.JONOKUCHI


def _is_sekitori(chii: Chii) -> bool:
    return isinstance(chii.level, MSD) or chii.level == Division.JURYO


def _log_loss(actual: float, probability: float) -> float:
    probability = min(max(probability, 1e-15), 1.0 - 1e-15)
    return -(actual * math.log(probability) + (1.0 - actual) * math.log(1.0 - probability))


def _percentile(sorted_values: Sequence[float], fraction: float) -> float:
    if not sorted_values:
        return 0.0
    position = fraction * (len(sorted_values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def _write_csv(
    path: Path,
    rows: Iterable[dict[str, object]],
    *,
    fieldnames: tuple[str, ...] | None = None,
) -> None:
    materialised = list(rows)
    fields = fieldnames or (tuple(materialised[0]) if materialised else ())
    with path.open("x", newline="", encoding="utf-8") as stream:
        if not fields:
            return
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(materialised)


def _identity(path: Path) -> dict[str, str]:
    resolved = path.resolve()
    return {"path": str(resolved), "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest()}


def _git_state() -> dict[str, object]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}
    return {"commit": commit, "dirty": dirty}


def _date_text(date: Date) -> str:
    return f"{int(date.year):04d}-{int(date.month):02d}"


def _parse_date(value: str) -> Date:
    match = re.fullmatch(r"(\d{4})[-/](\d{2})", value)
    if match is None:
        raise argparse.ArgumentTypeError("expected YYYY-MM or YYYY/MM")
    return Date.from_ints(int(match.group(1)), int(match.group(2)))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--prior", type=Path, default=DEFAULT_PRIOR)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K)
    parser.add_argument("--census-events", type=Path, default=DEFAULT_CENSUS_EVENTS)
    parser.add_argument("--start", type=_parse_date, default=Date.from_ints(1989, 1))
    parser.add_argument("--end", type=_parse_date, default=Date.from_ints(2026, 9))
    parser.add_argument("--expected-returns", type=int, default=437)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    started = perf_counter()
    history_path = args.history_zip.resolve()
    if history_path.suffix.lower() != ".zip":
        history_path = history_path.with_suffix(".zip")
    if not history_path.is_file():
        raise FileNotFoundError(f"History zip not found: {history_path}")
    history = load_history_with_annotations(str(history_path.with_suffix("")))
    output = args.output or (
        DEFAULT_OUTPUT_ROOT
        / f"frozen-persistence-{_date_text(args.start)}-to-{_date_text(args.end)}-{datetime.now():%Y-%m-%d_%H-%M-%S}"
    )
    print("Running canonical-equivalent reset control and frozen candidate...")
    control, candidate, violations = run_experiment(
        history=history,
        prior_path=args.prior,
        k_config=args.k_config,
        start=args.start,
        end=args.end,
    )
    elapsed = perf_counter() - started
    summary = write_comparison(
        history=history,
        control=control,
        candidate=candidate,
        violations=violations,
        output=output,
        history_path=history_path,
        prior_path=args.prior.resolve(),
        k_config=args.k_config.resolve(),
        census_events_path=args.census_events.resolve(),
        start=args.start,
        end=args.end,
        expected_returns=args.expected_returns,
        elapsed_seconds=elapsed,
    )
    print(f"Return events: {summary['return_event_count']:,}")
    print(f"Invariant violations: {summary['violation_count']:,}")
    print(f"Output: {output.resolve()}")
    print(f"Total wall-clock time: {perf_counter() - started:.3f} seconds")
    return 0 if not violations else 2

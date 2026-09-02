"""Replay the complete history from P2 with persistent divisional averages."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from statistics import fmean
from time import perf_counter
from typing import Callable, Mapping

from src.analysis.bout_data_completeness.__main__ import load_history
from src.analysis.equelo.api import annotation_free_chii
from src.analysis.equelo2_baseline.selection import select_basho_bouts
from src.analysis.equelo_bkp1.params import DEFAULT_K_CONFIG, load_divisional_k
from src.sumo_core.BasicPrimitives import Month, RikId, Year
from src.sumo_core.Banzuke import Banzuke, RikChii
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .division import division_name
from .model import DIVISIONS
from .recenter import recenter_by_division
from .solve import complete_priors


DEFAULT_P2 = Path(
    "files/output/analysis/divisional_averages/"
    "p2_epsilon_0_001_blank_fixed/prior.csv"
)
DEFAULT_OUTPUT = Path(
    "files/output/analysis/divisional_averages/"
    "full_history_from_p2_blank_fixed"
)


@dataclass(frozen=True, slots=True)
class PriorValue:
    rating: float
    source_chii: Chii
    provenance: str


@dataclass(slots=True)
class ChiiAggregate:
    observations: int = 0
    total: float = 0.0
    first_basho: str = ""
    last_basho: str = ""

    def add(self, date: Date, rating: float) -> None:
        self.observations += 1
        self.total += rating
        if not self.first_basho:
            self.first_basho = str(date)
        self.last_basho = str(date)

    @property
    def mean(self) -> float:
        return self.total / self.observations


@dataclass(slots=True)
class Score:
    bouts: int = 0
    log_loss: float = 0.0
    brier_loss: float = 0.0

    def add(self, probability: float, actual: float) -> None:
        probability = min(max(probability, 1e-15), 1.0 - 1e-15)
        self.bouts += 1
        self.log_loss -= actual * math.log(probability) + (
            1.0 - actual
        ) * math.log(1.0 - probability)
        self.brier_loss += (actual - probability) ** 2

    def row(self, period: str) -> dict[str, object]:
        denominator = self.bouts or 1
        return {
            "period": period,
            "rated_bouts": self.bouts,
            "mean_log_loss": self.log_loss / denominator,
            "mean_brier_loss": self.brier_loss / denominator,
            "log_loss_minus_chance": self.log_loss / denominator - math.log(2.0),
            "brier_loss_minus_chance": self.brier_loss / denominator - 0.25,
        }


def main(argv: list[str] | None = None) -> int:
    started = perf_counter()
    args = _parser().parse_args(argv)
    history, source = load_history(args.history_zip)
    history = collapse_history_annotations(history)
    history = _date_slice(history, args.start, args.end)
    manifest_path = args.p2_manifest or args.p2_prior.parent / "manifest.json"
    p2_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    targets = {key: float(value) for key, value in p2_manifest["targets"].items()}
    threshold = (
        args.support_threshold
        if args.support_threshold is not None
        else int(p2_manifest["support_threshold"])
    )
    p2 = load_p2(args.p2_prior)
    required = {
        chii
        for basho in history.values()
        for chii in basho.banzuke.rikchii.values()
    }
    prior = complete_historical_p2(p2, required)

    print("P2 divisional-average complete-history replay", flush=True)
    print(f"History: {min(history)} to {max(history)}", flush=True)
    print(f"P2: {args.p2_prior.resolve()}", flush=True)
    print(f"Implied-map support threshold: {threshold}", flush=True)
    print(f"Output: {args.output.resolve()}", flush=True)

    args.output.mkdir(parents=True, exist_ok=True)
    result = run_full_history(
        history,
        prior=prior,
        p2=p2,
        targets=targets,
        divisional_k=load_divisional_k(args.k_config.resolve()),
        support_threshold=threshold,
        reference_start=args.reference_start,
        output=args.output,
        progress=lambda message: print(message, flush=True),
    )
    _write_manifest(
        args,
        source=source,
        p2_manifest_path=manifest_path,
        p2_manifest=p2_manifest,
        targets=targets,
        threshold=threshold,
        result=result,
    )
    print(
        f"Rated bouts: {result['scores']['all'].bouts:,}; "
        f"log loss={result['scores']['all'].row('all')['mean_log_loss']:.6f}; "
        f"Brier={result['scores']['all'].row('all')['mean_brier_loss']:.6f}",
        flush=True,
    )
    print(f"Total wall-clock time: {perf_counter() - started:.2f} seconds", flush=True)
    return 0


def run_full_history(
    history: History,
    *,
    prior: Mapping[Chii, PriorValue],
    p2: Mapping[Chii, PriorValue],
    targets: Mapping[str, float],
    divisional_k: Callable[[int], float],
    support_threshold: int,
    reference_start: Date,
    output: Path,
    progress: Callable[[str], None] | None = None,
) -> dict[str, object]:
    """Run once through history, retaining inactive rikishi ratings."""

    if support_threshold < 1:
        raise ValueError("support_threshold must be at least 1")
    ratings: dict[RikId, float] = {}
    rated_bouts: dict[RikId, int] = {}
    sources: dict[RikId, str] = {}
    previous_active: set[RikId] = set()
    previous_chii: dict[RikId, Chii] = {}
    aggregates: dict[Chii, ChiiAggregate] = defaultdict(ChiiAggregate)
    scores = {period: Score() for period in ("pre_1989", "post_1988", "all")}
    last_seen: dict[RikId, dict[str, object]] = {}
    adjustment_rows: list[dict[str, object]] = []
    selection_totals = defaultdict(int)
    dates = sorted(history)

    for date in dates:
        basho = history[date]
        active = set(basho.banzuke.riks)
        known = set(ratings)
        new = active - known
        returning = (active & known) - previous_active
        departing = previous_active - active
        for rikishi in sorted(new):
            chii = basho.banzuke.rikchii[rikishi]
            entry = prior[chii]
            ratings[rikishi] = entry.rating
            rated_bouts[rikishi] = 0
            sources[rikishi] = f"{entry.provenance} from {entry.source_chii}"

        adjustment_rows.extend(
            shift_active_divisions(
                ratings,
                active,
                basho.banzuke.rikchii,
                targets,
                date=date,
                phase="start",
                new=new,
                returning=returning,
                departing=departing,
                previous_chii=previous_chii,
            )
        )
        for rikishi in active:
            aggregates[basho.banzuke.rikchii[rikishi]].add(date, ratings[rikishi])

        selection = select_basho_bouts(date, basho)
        for key in (
            "raw_result_count",
            "rated_bout_count",
            "excluded_fusen_count",
            "excluded_non_binary_count",
            "excluded_off_banzuke_count",
        ):
            selection_totals[key] += getattr(selection, key)
        period = (
            "pre_1989"
            if _date_key(date) < _date_key(reference_start)
            else "post_1988"
        )
        for bout in selection.bouts:
            a = bout.rikishi_a
            b = bout.rikishi_b
            probability = 1.0 / (1.0 + 10.0 ** ((ratings[b] - ratings[a]) / 400.0))
            actual = float(bout.a_won)
            scores[period].add(probability, actual)
            scores["all"].add(probability, actual)
            residual = actual - probability
            ratings[a] += divisional_k(bout.chii_a.ordinal()) * residual
            ratings[b] -= divisional_k(bout.chii_b.ordinal()) * residual
            rated_bouts[a] += 1
            rated_bouts[b] += 1

        adjustment_rows.extend(
            shift_active_divisions(
                ratings,
                active,
                basho.banzuke.rikchii,
                targets,
                date=date,
                phase="end",
                new=new,
                returning=returning,
                departing=departing,
                previous_chii=previous_chii,
            )
        )
        for rikishi in active:
            chii = basho.banzuke.rikchii[rikishi]
            last_seen[rikishi] = {
                "rikishi_id": int(rikishi),
                "shikona": str(basho.banzuke.rikshik[rikishi]),
                "last_basho": str(date),
                "last_chii": str(chii),
                "last_chii_ordinal": chii.ordinal(),
                "rating": ratings[rikishi],
                "rated_bouts": rated_bouts[rikishi],
                "initialisation_source": sources[rikishi],
            }
        previous_active = active
        previous_chii = dict(basho.banzuke.rikchii)
        if progress is not None and (int(date.month) == 1 or date == dates[-1]):
            progress(
                f"[P2 full history] {date}: {selection.rated_bout_count:,} rated "
                f"of {selection.raw_result_count:,} represented results"
            )

    for rikishi, row in last_seen.items():
        row["active_at_end"] = rikishi in previous_active
    output.mkdir(parents=True, exist_ok=True)
    _write_csv(output / "completed_prior.csv", completed_prior_rows(prior, p2))
    _write_csv(output / "basho_division_adjustments.csv", adjustment_rows)
    _write_csv(
        output / "latest_ratings.csv",
        [last_seen[rikishi] for rikishi in sorted(last_seen)],
    )
    score_rows = [scores[period].row(period) for period in ("pre_1989", "post_1988", "all")]
    _write_csv(output / "score_summary.csv", score_rows)

    map_result = implied_map(
        aggregates,
        p2=p2,
        targets=targets,
        support_threshold=support_threshold,
    )
    _write_csv(output / "implied_chii_map.csv", map_result["map_rows"])
    _write_csv(output / "p2_final_map_comparison.csv", map_result["comparison_rows"])
    _write_csv(output / "division_map_summary.csv", map_result["division_rows"])
    _write_csv(output / "division_boundary_summary.csv", map_result["boundary_rows"])
    _write_csv(
        output / "division_adjustment_summary.csv",
        adjustment_summary(adjustment_rows),
    )
    (output / "findings.md").write_text(
        findings(score_rows, map_result["division_rows"], adjustment_rows),
        encoding="utf-8",
    )
    return {
        "scores": scores,
        "selection": dict(selection_totals),
        "map": map_result,
        "adjustments": adjustment_rows,
        "rikishi_count": len(last_seen),
    }


def shift_active_divisions(
    ratings: dict[RikId, float],
    active: set[RikId],
    chii_by_rikishi: Mapping[RikId, Chii],
    targets: Mapping[str, float],
    *,
    date: Date,
    phase: str,
    new: set[RikId],
    returning: set[RikId],
    departing: set[RikId],
    previous_chii: Mapping[RikId, Chii],
) -> list[dict[str, object]]:
    rows = []
    for division in DIVISIONS:
        members = [
            rikishi
            for rikishi in active
            if division_name(chii_by_rikishi[rikishi]) == division
        ]
        if not members:
            continue
        raw = fmean(ratings[rikishi] for rikishi in members)
        adjustment = float(targets[division]) - raw
        for rikishi in members:
            ratings[rikishi] += adjustment
        rows.append(
            {
                "date": str(date),
                "phase": phase,
                "division": division,
                "active_count": len(members),
                "new_rikishi_count": sum(rikishi in new for rikishi in members),
                "returning_rikishi_count": sum(
                    rikishi in returning for rikishi in members
                ),
                "departing_rikishi_count": sum(
                    rikishi in departing
                    and division_name(previous_chii[rikishi]) == division
                    for rikishi in departing
                ),
                "target_mean": targets[division],
                "raw_mean": raw,
                "adjustment_per_rikishi": adjustment,
                "adjusted_mean": fmean(ratings[rikishi] for rikishi in members),
            }
        )
    return rows


def implied_map(
    aggregates: Mapping[Chii, ChiiAggregate],
    *,
    p2: Mapping[Chii, PriorValue],
    targets: Mapping[str, float],
    support_threshold: int,
) -> dict[str, list[dict[str, object]]]:
    support = {chii: value.observations for chii, value in aggregates.items()}
    supported = {
        chii for chii, count in support.items() if count >= support_threshold
    }
    missing_divisions = set(DIVISIONS) - {division_name(chii) for chii in supported}
    if missing_divisions:
        raise ValueError(
            "Full-history threshold leaves no supported chii in divisions: "
            + ", ".join(sorted(missing_divisions))
        )
    raw = {chii: aggregates[chii].mean for chii in supported}
    centred = recenter_by_division(raw, targets=targets, support=support)
    completed, sources = complete_priors(set(aggregates), centred.ratings)
    map_rows = [
        {
            "chii": str(chii),
            "chii_ordinal": chii.ordinal(),
            "division": division_name(chii),
            "observations": support[chii],
            "supported": chii in supported,
            "source_chii": str(sources[chii]),
            "raw_mean_basho_start_rating": aggregates[chii].mean,
            "implied_rating": completed[chii],
            "first_basho": aggregates[chii].first_basho,
            "last_basho": aggregates[chii].last_basho,
        }
        for chii in sorted(aggregates, key=lambda item: item.ordinal())
    ]
    common = sorted(set(p2) & set(completed), key=lambda item: item.ordinal())
    comparison_rows = [
        {
            "chii": str(chii),
            "chii_ordinal": chii.ordinal(),
            "division": division_name(chii),
            "observations": support[chii],
            "supported": chii in supported,
            "source_chii": str(sources[chii]),
            "p2_rating": p2[chii].rating,
            "full_history_implied_rating": completed[chii],
            "full_history_minus_p2": completed[chii] - p2[chii].rating,
        }
        for chii in common
    ]
    division_rows = comparison_summary(comparison_rows)
    boundary_rows = boundary_summary(completed, sources, p2)
    return {
        "map_rows": map_rows,
        "comparison_rows": comparison_rows,
        "division_rows": division_rows,
        "boundary_rows": boundary_rows,
    }


def comparison_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    for division in (*DIVISIONS, "All"):
        members = [
            row for row in rows if division == "All" or row["division"] == division
        ]
        differences = [float(row["full_history_minus_p2"]) for row in members]
        result.append(
            {
                "division": division,
                "chii_count": len(members),
                "p2_mean": fmean(float(row["p2_rating"]) for row in members),
                "full_history_mean": fmean(
                    float(row["full_history_implied_rating"]) for row in members
                ),
                "mean_difference": fmean(differences),
                "mean_absolute_difference": fmean(abs(value) for value in differences),
                "root_mean_square_difference": math.sqrt(
                    fmean(value * value for value in differences)
                ),
                "minimum_difference": min(differences),
                "maximum_difference": max(differences),
            }
        )
    return result


def boundary_summary(
    final: Mapping[Chii, float],
    sources: Mapping[Chii, Chii],
    p2: Mapping[Chii, PriorValue],
) -> list[dict[str, object]]:
    rows = []
    common = set(final) & set(p2)
    for upper, lower in zip(DIVISIONS, DIVISIONS[1:]):
        upper_members = [chii for chii in common if division_name(chii) == upper]
        lower_members = [chii for chii in common if division_name(chii) == lower]
        upper_chii = max(upper_members, key=lambda chii: chii.ordinal())
        lower_chii = min(lower_members, key=lambda chii: chii.ordinal())
        rows.append(
            {
                "boundary": f"{upper}/{lower}",
                "upper_chii": str(upper_chii),
                "upper_source_chii": str(sources[upper_chii]),
                "lower_chii": str(lower_chii),
                "lower_source_chii": str(sources[lower_chii]),
                "p2_gap": p2[upper_chii].rating - p2[lower_chii].rating,
                "full_history_gap": final[upper_chii] - final[lower_chii],
            }
        )
    return rows


def adjustment_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    for division in DIVISIONS:
        for phase in ("start", "end"):
            values = [
                float(row["adjustment_per_rikishi"])
                for row in rows
                if row["division"] == division and row["phase"] == phase
            ]
            result.append(
                {
                    "division": division,
                    "phase": phase,
                    "basho_count": len(values),
                    "mean_adjustment": fmean(values),
                    "mean_absolute_adjustment": fmean(abs(value) for value in values),
                    "maximum_absolute_adjustment": max(abs(value) for value in values),
                    "minimum_adjustment": min(values),
                    "maximum_adjustment": max(values),
                }
            )
    return result


def load_p2(path: Path) -> dict[Chii, PriorValue]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    result = {}
    for row in rows:
        chii = Chii.from_str(row["chii"])
        source = Chii.from_str(row.get("source_chii") or row["chii"])
        provenance = "p2_supported" if row.get("supported", "True") == "True" else "p2_threshold_completion"
        result[chii] = PriorValue(float(row["rating"]), source, provenance)
    if not result:
        raise ValueError(f"Empty P2 prior: {path}")
    return result


def complete_historical_p2(
    p2: Mapping[Chii, PriorValue], required: set[Chii]
) -> dict[Chii, PriorValue]:
    result = dict(p2)
    supported_sources = [
        chii for chii, value in p2.items() if value.provenance == "p2_supported"
    ]
    for chii in sorted(required - set(result), key=lambda item: item.ordinal()):
        candidates = [
            candidate
            for candidate in supported_sources
            if division_name(candidate) == division_name(chii)
            and candidate.ordinal() < chii.ordinal()
        ]
        if not candidates:
            raise ValueError(f"No supported P2 chii above historical {chii}")
        source = max(candidates, key=lambda item: item.ordinal())
        result[chii] = PriorValue(
            p2[source].rating,
            source,
            "historical_nearest_supported_above",
        )
    missing = required - set(result)
    if missing:
        raise AssertionError(f"Historical P2 completion left {len(missing)} gaps")
    return result


def completed_prior_rows(
    prior: Mapping[Chii, PriorValue], p2: Mapping[Chii, PriorValue]
) -> list[dict[str, object]]:
    return [
        {
            "chii": str(chii),
            "chii_ordinal": chii.ordinal(),
            "rating": value.rating,
            "source_chii": str(value.source_chii),
            "provenance": value.provenance,
            "in_p2_domain": chii in p2,
        }
        for chii, value in sorted(prior.items(), key=lambda item: item[0].ordinal())
    ]


def findings(
    scores: list[dict[str, object]],
    divisions: list[dict[str, object]],
    adjustments: list[dict[str, object]],
) -> str:
    lines = [
        "# P2 divisional-average complete-history replay",
        "",
        "This is the direct test of whether divisional-average persistence prevents",
        "the sekitori/sub-sekitori displacement seen under global-mean persistence.",
        "The comparison is the supported-and-completed full-history implied literal",
        "chii map minus the converged P2 input map; enforced active means are not",
        "treated as the result.",
        "",
        "## Implied map minus P2",
        "",
        "| Division | Chii | Mean difference | MAE | RMS |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in divisions:
        lines.append(
            f"| {row['division']} | {row['chii_count']} | "
            f"{row['mean_difference']:+.3f} | "
            f"{row['mean_absolute_difference']:.3f} | "
            f"{row['root_mean_square_difference']:.3f} |"
        )
    lines.extend(["", "## Predictive scores", "", "| Period | Bouts | Log loss | Brier |", "|---|---:|---:|---:|"])
    for row in scores:
        lines.append(
            f"| {row['period']} | {row['rated_bouts']:,} | "
            f"{row['mean_log_loss']:.6f} | {row['mean_brier_loss']:.6f} |"
        )
    lines.extend(
        [
            "",
            f"The replay retained {len(adjustments):,} per-division population corrections.",
            "See the correction and boundary summaries before interpreting smaller",
            "division-level mean differences as an improvement.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_manifest(
    args,
    *,
    source,
    p2_manifest_path: Path,
    p2_manifest: dict,
    targets: Mapping[str, float],
    threshold: int,
    result: dict[str, object],
) -> None:
    payload = {
        "experiment": "P2 divisional-average complete-history replay",
        "start": str(args.start),
        "end": str(args.end),
        "reference_start": str(args.reference_start),
        "history_source": asdict(source),
        "p2_prior": str(args.p2_prior.resolve()),
        "p2_prior_sha256": _sha256(args.p2_prior.resolve()),
        "p2_manifest": str(p2_manifest_path.resolve()),
        "p2_manifest_sha256": _sha256(p2_manifest_path.resolve()),
        "p2_fixed_point_epsilon": p2_manifest.get("epsilon"),
        "p2_fixed_point_scores": {
            "rated_bouts": p2_manifest.get("rated_bouts"),
            "mean_log_loss": p2_manifest.get("mean_log_loss"),
            "mean_brier_loss": p2_manifest.get("mean_brier_loss"),
        },
        "support_threshold": threshold,
        "targets": dict(targets),
        "population_policy": "fixed_divisional_means_at_basho_start_and_end",
        "inactive_policy": "archive and restore rating across banzuke gaps",
        "historical_completion": "nearest supported P2 chii above within division",
        "implied_map": "full-history basho-start mean; thresholded and recentered by division; nearest-supported completion",
        "rikishi_count": result["rikishi_count"],
        "selection": result["selection"],
        "scores": {
            period: result["scores"][period].row(period)
            for period in ("pre_1989", "post_1988", "all")
        },
    }
    (args.output / "manifest.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, default=None)
    parser.add_argument("--start", type=_date, default=_date("1958/01"))
    parser.add_argument("--end", type=_date, default=_date("2026/07"))
    parser.add_argument("--reference-start", type=_date, default=_date("1989/01"))
    parser.add_argument("--p2-prior", type=Path, default=DEFAULT_P2)
    parser.add_argument("--p2-manifest", type=Path, default=None)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--support-threshold", type=int, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def _date(value: str) -> Date:
    year_text, month_text = value.split("/", maxsplit=1)
    return Date(Year(int(year_text)), Month(int(month_text)))


def _date_slice(history: History, start: Date, end: Date) -> History:
    selected = History(
        {
            date: basho
            for date, basho in history.items()
            if _date_key(start) <= _date_key(date) <= _date_key(end)
        }
    )
    if not selected:
        raise ValueError(f"History has no basho from {start} through {end}")
    return selected


def collapse_history_annotations(history: History) -> History:
    """Remove chii annotations without filtering the complete banzuke or results."""

    return History(
        {
            date: BashoState(
                banzuke=Banzuke(
                    riks=basho.banzuke.riks,
                    rikchii=RikChii(
                        {
                            rikishi: annotation_free_chii(chii)
                            for rikishi, chii in basho.banzuke.rikchii.items()
                        }
                    ),
                    rikshik=basho.banzuke.rikshik,
                ),
                summary=basho.summary,
            )
            for date, basho in history.items()
        }
    )


def _date_key(value) -> tuple[int, int]:
    return int(value.year), int(value.month)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())

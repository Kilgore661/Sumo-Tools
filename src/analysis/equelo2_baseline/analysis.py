"""Run and persist the first Equelo2 full-history baseline experiment."""

from __future__ import annotations

from contextlib import ExitStack
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Callable, Iterable

from src.analysis.elo_model_selection.model import rank_pair
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .model import BashoReplay, ForecastRow
from .prior import CompletedPrior, load_and_complete_prior
from .replay import ReplayEngine
from .selection import select_basho_bouts


CANDIDATE = "equelo2_full_history"
REFERENCE = "elo89_reference"


@dataclass(frozen=True, slots=True)
class ExperimentDefinition:
    start_date: Date
    end_date: Date
    reference_start_date: Date
    boundary_date: Date
    q: float = 400.0


@dataclass(frozen=True, slots=True)
class RunOutputs:
    output_root: Path
    findings: Path
    manifest: Path


@dataclass(slots=True)
class _Score:
    bouts: int = 0
    log_loss: float = 0.0
    brier_loss: float = 0.0

    def add(self, row: ForecastRow) -> None:
        probability = min(max(row.probability_a_wins, 1e-15), 1.0 - 1e-15)
        actual = float(row.a_won)
        self.bouts += 1
        self.log_loss -= actual * math.log(probability) + (1.0 - actual) * math.log(
            1.0 - probability
        )
        self.brier_loss += (actual - probability) ** 2

    def row(self, *, run: str, period: str) -> dict[str, object]:
        denominator = self.bouts or 1
        return {
            "run": run,
            "period": period,
            "rated_bouts": self.bouts,
            "mean_log_loss": self.log_loss / denominator,
            "mean_brier_loss": self.brier_loss / denominator,
        }


@dataclass(slots=True)
class _Difference:
    bouts: int = 0
    log_difference: float = 0.0
    brier_difference: float = 0.0

    def add(self, candidate: ForecastRow, reference: ForecastRow) -> None:
        actual = float(candidate.a_won)
        pc = min(max(candidate.probability_a_wins, 1e-15), 1.0 - 1e-15)
        pr = min(max(reference.probability_a_wins, 1e-15), 1.0 - 1e-15)
        candidate_log = -(actual * math.log(pc) + (1.0 - actual) * math.log(1.0 - pc))
        reference_log = -(actual * math.log(pr) + (1.0 - actual) * math.log(1.0 - pr))
        self.bouts += 1
        self.log_difference += candidate_log - reference_log
        self.brier_difference += (actual - pc) ** 2 - (actual - pr) ** 2

    def row(self) -> dict[str, object]:
        denominator = self.bouts or 1
        return {
            "period": "post_1988",
            "rated_bouts": self.bouts,
            "candidate_minus_reference_mean_log_loss": self.log_difference
            / denominator,
            "candidate_minus_reference_mean_brier_loss": self.brier_difference
            / denominator,
        }


@dataclass(slots=True)
class _RatingAggregate:
    observations: int = 0
    total: float = 0.0
    total_squared: float = 0.0
    minimum: float = math.inf
    maximum: float = -math.inf
    first_basho: str = ""
    last_basho: str = ""

    def add(self, date: Date, rating: float) -> None:
        self.observations += 1
        self.total += rating
        self.total_squared += rating * rating
        self.minimum = min(self.minimum, rating)
        self.maximum = max(self.maximum, rating)
        if not self.first_basho:
            self.first_basho = str(date)
        self.last_basho = str(date)

    def row(self, *, run: str, period: str, pair: str) -> dict[str, object]:
        mean = self.total / self.observations
        variance = max(0.0, self.total_squared / self.observations - mean * mean)
        return {
            "run": run,
            "period": period,
            "rank_pair": pair,
            "observations": self.observations,
            "mean_basho_start_rating": mean,
            "standard_deviation": math.sqrt(variance),
            "minimum": self.minimum,
            "maximum": self.maximum,
            "first_basho": self.first_basho,
            "last_basho": self.last_basho,
        }


def run_experiment(
    history: History,
    definition: ExperimentDefinition,
    *,
    prior_path: Path,
    k_config_path: Path,
    divisional_k: Callable[[int], float],
    output_root: Path,
    history_source: dict[str, object],
    progress: Callable[[str], None] | None = None,
) -> RunOutputs:
    """Run the historical candidate and an exact post-1988 Elo-89 control."""

    dates = sorted(
        date for date in history if definition.start_date <= date <= definition.end_date
    )
    if not dates:
        raise ValueError("The requested Equelo2 baseline interval contains no basho")
    if definition.reference_start_date not in history:
        raise ValueError(
            f"Reference start basho is absent: {definition.reference_start_date}"
        )

    required_chii = tuple(
        chii
        for date in dates
        for chii in history[date].banzuke.rikchii.values()
    )
    required_chii += tuple(
        history[definition.reference_start_date].banzuke.rikchii.values()
    )
    prior = load_and_complete_prior(prior_path, required_chii)
    target_mean = elo89_target_mean(
        history, definition.reference_start_date, prior
    )

    output_root.mkdir(parents=True, exist_ok=True)
    candidate = ReplayEngine(
        name=CANDIDATE,
        prior=prior,
        divisional_k=divisional_k,
        target_mean=target_mean,
        q=definition.q,
    )
    reference = ReplayEngine(
        name=REFERENCE,
        prior=prior,
        divisional_k=divisional_k,
        target_mean=target_mean,
        q=definition.q,
        persist_inactive_ratings=False,
    )
    scores = {
        (CANDIDATE, "pre_1989"): _Score(),
        (CANDIDATE, "post_1988"): _Score(),
        (CANDIDATE, "all"): _Score(),
        (REFERENCE, "post_1988"): _Score(),
    }
    difference = _Difference()
    aggregates: dict[tuple[str, str, str], _RatingAggregate] = {}
    boundary_replay: BashoReplay | None = None
    handover_rows: list[dict[str, object]] = []
    selection_totals = {
        "raw_result_count": 0,
        "rated_bout_count": 0,
        "excluded_fusen_count": 0,
        "excluded_non_binary_count": 0,
        "excluded_off_banzuke_count": 0,
    }

    with _CsvOutputs(output_root) as outputs:
        outputs.write_prior(prior)
        for date in dates:
            basho = history[date]
            selection = select_basho_bouts(date, basho)
            for key in selection_totals:
                selection_totals[key] += getattr(selection, key)
            outputs.write_excluded(selection.excluded)

            candidate_replay = candidate.process_basho(date, basho, selection)
            outputs.write_replay(candidate_replay, basho)
            _aggregate_ratings(
                aggregates,
                CANDIDATE,
                "all",
                date,
                basho.banzuke.rikchii,
                candidate_replay.start_ratings,
            )
            candidate_period = (
                "pre_1989"
                if date < definition.reference_start_date
                else "post_1988"
            )
            _aggregate_ratings(
                aggregates,
                CANDIDATE,
                candidate_period,
                date,
                basho.banzuke.rikchii,
                candidate_replay.start_ratings,
            )
            for row in candidate_replay.forecasts:
                scores[(CANDIDATE, "all")].add(row)
                scores[(CANDIDATE, candidate_period)].add(row)

            if date == definition.boundary_date:
                boundary_replay = candidate_replay
                outputs.write_boundary(candidate_replay, basho)

            if date < definition.reference_start_date:
                _report_progress(progress, date, dates[-1], selection)
                continue

            reference_replay = reference.process_basho(date, basho, selection)
            outputs.write_replay(reference_replay, basho)
            _aggregate_ratings(
                aggregates,
                REFERENCE,
                "post_1988",
                date,
                basho.banzuke.rikchii,
                reference_replay.start_ratings,
            )
            for row in reference_replay.forecasts:
                scores[(REFERENCE, "post_1988")].add(row)
            outputs.write_post_comparison(
                candidate_replay,
                reference_replay,
                basho,
                difference,
            )

            if date == definition.reference_start_date and boundary_replay is not None:
                handover_rows = _handover(
                    boundary_replay,
                    history[definition.boundary_date],
                    candidate_replay,
                    reference_replay,
                    basho,
                )
                outputs.write_handover(handover_rows)

            _report_progress(progress, date, dates[-1], selection)

        score_rows = [
            score.row(run=run, period=period)
            for (run, period), score in scores.items()
            if score.bouts or period == "all"
        ]
        outputs.write_score_summary(score_rows, difference.row())
        outputs.write_chii_summary(aggregates)

    manifest = {
        "experiment": "Equelo2 full-history baseline on frozen Elo-89 priors",
        "status": "retrospective diagnostic; the adopted Elo-89 prior is future-informed",
        "definition": {
            "start_date": str(definition.start_date),
            "end_date": str(definition.end_date),
            "reference_start_date": str(definition.reference_start_date),
            "boundary_date": str(definition.boundary_date),
            "q": definition.q,
            "population_policy": (
                "full represented banzuke; common shift to the fixed Elo-89 "
                "target mean before and after each basho"
            ),
            "rating_persistence": (
                "candidate ratings persist across result gaps and are archived while "
                "off-banzuke; the Elo-89 control discards ratings on departure"
            ),
            "bout_policy": (
                "all represented W/L results irrespective of kimarite; fusen, "
                "non-binary and off-banzuke results excluded"
            ),
        },
        "history": history_source,
        "prior": {
            "path": str(prior_path.resolve()),
            "sha256": _sha256(prior_path.resolve()),
            "elo89_pair_count": sum(
                entry.provenance == "elo89" for entry in prior.entries.values()
            ),
            "historical_completion_count": sum(
                entry.provenance != "elo89" for entry in prior.entries.values()
            ),
            "completion_policy": "nearest represented rank above within division",
        },
        "k_config": {
            "path": str(k_config_path.resolve()),
            "sha256": _sha256(k_config_path.resolve()),
        },
        "elo89_target_mean": target_mean,
        "selection": selection_totals,
        "handover_continuing_rikishi": len(handover_rows),
        "outputs": _output_descriptions(),
    }
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    findings_path = output_root / "findings.md"
    findings_path.write_text(
        _findings(definition, prior, target_mean, selection_totals, scores, difference),
        encoding="utf-8",
    )
    return RunOutputs(output_root, findings_path, manifest_path)


def elo89_target_mean(
    history: History,
    reference_start_date: Date,
    prior: CompletedPrior,
) -> float:
    """Return the frozen scale anchor implied by the first Elo-89 banzuke."""

    banzuke = history[reference_start_date].banzuke
    if not banzuke.riks:
        raise ValueError(f"Reference banzuke is empty: {reference_start_date}")
    ratings = [prior.rating_for(banzuke.rikchii[rikishi])[0] for rikishi in banzuke.riks]
    return sum(ratings) / len(ratings)


def _report_progress(
    progress: Callable[[str], None] | None,
    date: Date,
    last_date: Date,
    selection,
) -> None:
    if progress is not None and (int(date.month) == 1 or date == last_date):
        progress(
            f"[{CANDIDATE}] {date}: {selection.rated_bout_count:,} rated "
            f"of {selection.raw_result_count:,} represented results"
        )


def _aggregate_ratings(
    aggregates: dict[tuple[str, str, str], _RatingAggregate],
    run: str,
    period: str,
    date: Date,
    chii_by_rikishi: dict,
    ratings: dict[RikId, float],
) -> None:
    for rikishi, rating in ratings.items():
        pair = rank_pair(chii_by_rikishi[rikishi])
        aggregates.setdefault((run, period, pair), _RatingAggregate()).add(
            date, rating
        )


def _handover(
    boundary: BashoReplay,
    boundary_basho,
    candidate: BashoReplay,
    reference: BashoReplay,
    reference_basho,
) -> list[dict[str, object]]:
    continuing = set(boundary.end_ratings) & set(candidate.start_ratings)
    return [
        {
            "rikishi_id": int(rikishi),
            "shikona_1988_11": str(boundary_basho.banzuke.rikshik[rikishi]),
            "chii_1988_11": str(boundary_basho.banzuke.rikchii[rikishi]),
            "chii_1989_01": str(reference_basho.banzuke.rikchii[rikishi]),
            "equelo2_1988_11_end_rating": boundary.end_ratings[rikishi],
            "equelo2_1989_01_start_rating": candidate.start_ratings[rikishi],
            "elo89_1989_01_start_rating": reference.start_ratings[rikishi],
            "equelo2_minus_elo89_at_1989_01_start": (
                candidate.start_ratings[rikishi] - reference.start_ratings[rikishi]
            ),
            "pre_1989_rated_bouts": boundary.rated_bouts_after[rikishi],
        }
        for rikishi in sorted(continuing)
    ]


class _CsvOutputs:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.stack = ExitStack()
        self.writers: dict[str, csv.DictWriter] = {}

    def __enter__(self) -> "_CsvOutputs":
        schemas = {
            "completed_prior.csv": (
                "rank_pair", "rating", "source_rank_pair", "provenance"
            ),
            "forecast_ledger.csv": (
                "run", "basho", "day", "rikishi_a", "rikishi_b", "chii_a",
                "chii_b", "rating_a_before", "rating_b_before",
                "rated_bouts_a_before", "rated_bouts_b_before",
                "probability_a_wins", "a_won", "k_a", "k_b", "delta_a",
                "delta_b", "rating_a_after", "rating_b_after",
            ),
            "rating_ledger.csv": (
                "run", "basho", "phase", "rikishi_id", "shikona", "chii",
                "rating", "rated_bouts", "initialisation_source",
            ),
            "basho_adjustments.csv": (
                "run", "date", "active_count", "new_rikishi_count",
                "returning_rikishi_count", "departing_rikishi_count",
                "target_mean", "raw_start_mean", "start_adjustment",
                "adjusted_start_mean", "raw_end_mean", "end_adjustment",
                "adjusted_end_mean",
            ),
            "excluded_bouts.csv": (
                "basho", "day", "rikishi_1", "rikishi_2", "outcome_1",
                "outcome_2", "decision", "reason",
            ),
            "post_1988_forecast_comparison.csv": (
                "basho", "day", "rikishi_a", "rikishi_b", "a_won",
                "equelo2_probability_a_wins", "elo89_probability_a_wins",
                "probability_difference", "equelo2_log_loss", "elo89_log_loss",
                "log_loss_difference", "equelo2_brier_loss", "elo89_brier_loss",
                "brier_loss_difference",
            ),
            "post_1988_rating_comparison.csv": (
                "basho", "phase", "rikishi_id", "shikona", "chii",
                "equelo2_rating", "elo89_rating", "rating_difference",
                "equelo2_rated_bouts", "elo89_rated_bouts",
            ),
            "1988_11_ratings.csv": (
                "rikishi_id", "shikona", "chii", "start_rating", "end_rating",
                "rated_bouts_before", "rated_bouts_after", "initialisation_source",
            ),
            "1989_01_handover.csv": (
                "rikishi_id", "shikona_1988_11", "chii_1988_11", "chii_1989_01",
                "equelo2_1988_11_end_rating", "equelo2_1989_01_start_rating",
                "elo89_1989_01_start_rating", "equelo2_minus_elo89_at_1989_01_start",
                "pre_1989_rated_bouts",
            ),
        }
        for name, fields in schemas.items():
            stream = self.stack.enter_context(
                (self.root / name).open("w", newline="", encoding="utf-8")
            )
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            self.writers[name] = writer
        return self

    def __exit__(self, *args) -> None:
        self.stack.close()

    def write_prior(self, prior: CompletedPrior) -> None:
        writer = self.writers["completed_prior.csv"]
        for entry in sorted(
            prior.entries.values(),
            key=lambda item: Chii.from_str(f"{item.rank_pair}e").ordinal(),
        ):
            writer.writerow(asdict(entry))

    def write_excluded(self, rows: Iterable) -> None:
        writer = self.writers["excluded_bouts.csv"]
        for row in rows:
            writer.writerow({
                "basho": str(row.date),
                "day": row.day,
                "rikishi_1": int(row.rikishi_1),
                "rikishi_2": int(row.rikishi_2),
                "outcome_1": row.outcome_1,
                "outcome_2": row.outcome_2,
                "decision": row.decision,
                "reason": row.reason,
            })

    def write_replay(self, replay: BashoReplay, basho) -> None:
        forecast_writer = self.writers["forecast_ledger.csv"]
        for row in replay.forecasts:
            forecast_writer.writerow({
                "run": row.run,
                "basho": str(row.date),
                "day": row.day,
                "rikishi_a": int(row.rikishi_a),
                "rikishi_b": int(row.rikishi_b),
                "chii_a": str(row.chii_a),
                "chii_b": str(row.chii_b),
                "rating_a_before": row.rating_a_before,
                "rating_b_before": row.rating_b_before,
                "rated_bouts_a_before": row.rated_bouts_a_before,
                "rated_bouts_b_before": row.rated_bouts_b_before,
                "probability_a_wins": row.probability_a_wins,
                "a_won": row.a_won,
                "k_a": row.k_a,
                "k_b": row.k_b,
                "delta_a": row.delta_a,
                "delta_b": row.delta_b,
                "rating_a_after": row.rating_a_after,
                "rating_b_after": row.rating_b_after,
            })
        self.writers["basho_adjustments.csv"].writerow(
            _adjustment_row(replay.adjustment)
        )
        rating_writer = self.writers["rating_ledger.csv"]
        for phase, ratings, counts in (
            ("start", replay.start_ratings, replay.rated_bouts_before),
            ("end", replay.end_ratings, replay.rated_bouts_after),
        ):
            for rikishi in sorted(ratings):
                rating_writer.writerow({
                    "run": replay.adjustment.run,
                    "basho": str(replay.adjustment.date),
                    "phase": phase,
                    "rikishi_id": int(rikishi),
                    "shikona": str(basho.banzuke.rikshik[rikishi]),
                    "chii": str(basho.banzuke.rikchii[rikishi]),
                    "rating": ratings[rikishi],
                    "rated_bouts": counts[rikishi],
                    "initialisation_source": replay.initialisation_sources[rikishi],
                })

    def write_boundary(self, replay: BashoReplay, basho) -> None:
        writer = self.writers["1988_11_ratings.csv"]
        for rikishi in sorted(replay.start_ratings):
            writer.writerow({
                "rikishi_id": int(rikishi),
                "shikona": str(basho.banzuke.rikshik[rikishi]),
                "chii": str(basho.banzuke.rikchii[rikishi]),
                "start_rating": replay.start_ratings[rikishi],
                "end_rating": replay.end_ratings[rikishi],
                "rated_bouts_before": replay.rated_bouts_before[rikishi],
                "rated_bouts_after": replay.rated_bouts_after[rikishi],
                "initialisation_source": replay.initialisation_sources[rikishi],
            })

    def write_handover(self, rows: Iterable[dict[str, object]]) -> None:
        self.writers["1989_01_handover.csv"].writerows(rows)

    def write_post_comparison(
        self,
        candidate: BashoReplay,
        reference: BashoReplay,
        basho,
        difference: _Difference,
    ) -> None:
        if len(candidate.forecasts) != len(reference.forecasts):
            raise AssertionError("Candidate and Elo-89 forecast domains differ")
        writer = self.writers["post_1988_forecast_comparison.csv"]
        for candidate_row, reference_row in zip(
            candidate.forecasts, reference.forecasts, strict=True
        ):
            candidate_key = (
                candidate_row.date, candidate_row.day,
                candidate_row.rikishi_a, candidate_row.rikishi_b,
            )
            reference_key = (
                reference_row.date, reference_row.day,
                reference_row.rikishi_a, reference_row.rikishi_b,
            )
            if candidate_key != reference_key or candidate_row.a_won != reference_row.a_won:
                raise AssertionError("Candidate and Elo-89 forecast rows differ")
            actual = float(candidate_row.a_won)
            pc = min(max(candidate_row.probability_a_wins, 1e-15), 1.0 - 1e-15)
            pr = min(max(reference_row.probability_a_wins, 1e-15), 1.0 - 1e-15)
            lc = -(actual * math.log(pc) + (1.0 - actual) * math.log(1.0 - pc))
            lr = -(actual * math.log(pr) + (1.0 - actual) * math.log(1.0 - pr))
            bc = (actual - pc) ** 2
            br = (actual - pr) ** 2
            writer.writerow({
                "basho": str(candidate_row.date),
                "day": candidate_row.day,
                "rikishi_a": int(candidate_row.rikishi_a),
                "rikishi_b": int(candidate_row.rikishi_b),
                "a_won": candidate_row.a_won,
                "equelo2_probability_a_wins": pc,
                "elo89_probability_a_wins": pr,
                "probability_difference": pc - pr,
                "equelo2_log_loss": lc,
                "elo89_log_loss": lr,
                "log_loss_difference": lc - lr,
                "equelo2_brier_loss": bc,
                "elo89_brier_loss": br,
                "brier_loss_difference": bc - br,
            })
            difference.add(candidate_row, reference_row)

        rating_writer = self.writers["post_1988_rating_comparison.csv"]
        for phase, candidate_ratings, reference_ratings, candidate_counts, reference_counts in (
            (
                "start", candidate.start_ratings, reference.start_ratings,
                candidate.rated_bouts_before, reference.rated_bouts_before,
            ),
            (
                "end", candidate.end_ratings, reference.end_ratings,
                candidate.rated_bouts_after, reference.rated_bouts_after,
            ),
        ):
            if set(candidate_ratings) != set(reference_ratings):
                raise AssertionError("Candidate and Elo-89 active populations differ")
            for rikishi in sorted(candidate_ratings):
                rating_writer.writerow({
                    "basho": str(candidate.adjustment.date),
                    "phase": phase,
                    "rikishi_id": int(rikishi),
                    "shikona": str(basho.banzuke.rikshik[rikishi]),
                    "chii": str(basho.banzuke.rikchii[rikishi]),
                    "equelo2_rating": candidate_ratings[rikishi],
                    "elo89_rating": reference_ratings[rikishi],
                    "rating_difference": (
                        candidate_ratings[rikishi] - reference_ratings[rikishi]
                    ),
                    "equelo2_rated_bouts": candidate_counts[rikishi],
                    "elo89_rated_bouts": reference_counts[rikishi],
                })

    def write_score_summary(
        self,
        scores: list[dict[str, object]],
        difference: dict[str, object],
    ) -> None:
        _write_csv(self.root / "score_summary.csv", scores)
        _write_csv(self.root / "post_1988_score_difference.csv", [difference])

    def write_chii_summary(
        self,
        aggregates: dict[tuple[str, str, str], _RatingAggregate],
    ) -> None:
        rows = [
            aggregate.row(run=run, period=period, pair=pair)
            for (run, period, pair), aggregate in sorted(
                aggregates.items(),
                key=lambda item: (
                    item[0][0], item[0][1],
                    Chii.from_str(f"{item[0][2]}e").ordinal(),
                ),
            )
        ]
        _write_csv(self.root / "chii_rating_summary.csv", rows)


def _adjustment_row(adjustment) -> dict[str, object]:
    row = asdict(adjustment)
    row["date"] = str(adjustment.date)
    return row


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


def _output_descriptions() -> dict[str, str]:
    return {
        "completed_prior.csv": "Frozen Elo-89 pairs plus historical nearest-higher completions.",
        "forecast_ledger.csv": "Every rated forecast for the candidate and post-1988 reference.",
        "rating_ledger.csv": "Basho-start and post-normalisation basho-end process ratings.",
        "basho_adjustments.csv": "Whole-population mean shifts for each rating world.",
        "excluded_bouts.csv": "Every represented result excluded from rating and its reason.",
        "1988_11_ratings.csv": "Candidate ratings at the last pre-Elo-89 basho.",
        "1989_01_handover.csv": "Continuing-rikishi comparison across the boundary.",
        "chii_rating_summary.csv": "Basho-start empirical rating summaries by paired chii.",
        "post_1988_forecast_comparison.csv": "Bout-level candidate/reference prediction differences.",
        "post_1988_rating_comparison.csv": "Basho-boundary candidate/reference rating differences.",
        "score_summary.csv": "Aggregate predictive scores by run and period.",
        "post_1988_score_difference.csv": "Aggregate candidate-minus-reference predictive loss.",
    }


def _findings(
    definition: ExperimentDefinition,
    prior: CompletedPrior,
    target_mean: float,
    selection: dict[str, int],
    scores: dict[tuple[str, str], _Score],
    difference: _Difference,
) -> str:
    completions = [
        entry for entry in prior.entries.values() if entry.provenance != "elo89"
    ]
    lines = [
        "# Equelo2 full-history baseline",
        "",
        f"The candidate replay covers {definition.start_date} to {definition.end_date}.",
        f"Its fixed Elo-89 population-mean anchor is {target_mean:.6f}.",
        f"The historical completion layer adds {len(completions)} paired chii values.",
        "",
        "All represented W/L results are eligible irrespective of kimarite. No",
        "missing result is inferred. Ratings persist across result gaps.",
        "",
        "## Bout domain",
        "",
        f"- Raw represented results: {selection['raw_result_count']:,}",
        f"- Rated W/L results: {selection['rated_bout_count']:,}",
        f"- Excluded fusen: {selection['excluded_fusen_count']:,}",
        f"- Excluded non-binary: {selection['excluded_non_binary_count']:,}",
        f"- Excluded because a participant is off-banzuke: {selection['excluded_off_banzuke_count']:,}",
        "",
        "## Predictive scores",
        "",
        "| Run | Period | Bouts | Log loss | Brier loss |",
        "|---|---|---:|---:|---:|",
    ]
    for (run, period), score in scores.items():
        if not score.bouts:
            continue
        row = score.row(run=run, period=period)
        lines.append(
            f"| {run} | {period} | {score.bouts:,} | "
            f"{row['mean_log_loss']:.6f} | {row['mean_brier_loss']:.6f} |"
        )
    if difference.bouts:
        row = difference.row()
        lines.extend([
            "",
            "Negative differences favour the full-history candidate:",
            "",
            f"- Candidate minus Elo-89 log loss: {row['candidate_minus_reference_mean_log_loss']:+.6f}",
            f"- Candidate minus Elo-89 Brier loss: {row['candidate_minus_reference_mean_brier_loss']:+.6f}",
        ])
    lines.extend([
        "",
        "See `1989_01_handover.csv` for the boundary test and",
        "`chii_rating_summary.csv` for the empirical chii/rating maps.",
        "",
    ])
    return "\n".join(lines)

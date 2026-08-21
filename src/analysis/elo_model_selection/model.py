"""Four controlled post-1988 Elo-family forecast producers."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
import hashlib
import math
from pathlib import Path
from typing import Callable, Literal

from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.analysis.equelo.fixed_supported.policy import collapse_chii
from src.analysis.prediction.bouts import BoutSelection, RatedBout, select_rated_bouts
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


ModelName = Literal["B", "B_k", "B_P", "B_kP"]
DEFAULT_PRIOR_CSV = Path(
    "files/output/Equelo/boundary_reconciliation/"
    "2026-08-19_lower_banzuke_merge/paired_literal_chii_merge_candidate.csv"
)
DEFAULT_K_CONFIG = Path("files/input/elo_fide.json")


@dataclass(frozen=True, slots=True)
class ComparisonDefinition:
    """Parameters held fixed across the controlled comparison."""

    end_date: Date
    start_date: Date
    q: float = 400.0
    constant_k: float = 35.0
    constant_initial_rating: float = 1500.0
    reference_probability: float = 0.5
    bootstrap_seed: int = 20260820
    bootstrap_resamples: int = 2000
    confidence_level: float = 0.95
    noninferiority_fraction: float = 0.05
    calibration_bin_width: float = 0.05
    calibration_min_bin_participants: int = 100

    def __post_init__(self) -> None:
        if not 0.0 < self.calibration_bin_width <= 0.5:
            raise ValueError("calibration_bin_width must be in (0, 0.5]")
        bin_count = round(1.0 / self.calibration_bin_width)
        if not math.isclose(
            bin_count * self.calibration_bin_width,
            1.0,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("calibration_bin_width must divide 1 exactly")
        if self.calibration_min_bin_participants < 1:
            raise ValueError("calibration_min_bin_participants must be positive")


@dataclass(frozen=True, slots=True)
class ModelSpec:
    name: ModelName
    divisional_k: bool
    informed_prior: bool


MODEL_SPECS = (
    ModelSpec("B", divisional_k=False, informed_prior=False),
    ModelSpec("B_k", divisional_k=True, informed_prior=False),
    ModelSpec("B_P", divisional_k=False, informed_prior=True),
    ModelSpec("B_kP", divisional_k=True, informed_prior=True),
)


@dataclass(frozen=True, slots=True)
class AdoptedPrior:
    """The exact paired initial-rating artifact adopted in story document 10."""

    source_path: str
    sha256: str
    rating_by_pair: dict[str, float]
    fallback_rating: float

    def rating_for(self, chii: Chii | None) -> tuple[float, str]:
        if chii is None:
            return self.fallback_rating, "unranked weakest-prior fallback"
        pair = rank_pair(chii)
        try:
            return self.rating_by_pair[pair], f"adopted prior {pair}"
        except KeyError as error:
            raise KeyError(f"Adopted prior has no value for represented chii {chii}") from error


@dataclass(frozen=True, slots=True)
class BoutContext:
    bout: RatedBout
    chii_a: Chii | None
    chii_b: Chii | None


@dataclass(frozen=True, slots=True)
class ForecastRow:
    model: ModelName
    date: Date
    day: int
    rikishi_a: int
    rikishi_b: int
    chii_a: Chii | None
    chii_b: Chii | None
    rating_a_before: float
    rating_b_before: float
    rated_bouts_a_before: int
    rated_bouts_b_before: int
    probability_a_wins: float
    a_won: bool
    k_a: float
    k_b: float
    delta_a: float
    delta_b: float
    rating_a_after: float
    rating_b_after: float
    initialisation_a: str
    initialisation_b: str


@dataclass(frozen=True, slots=True)
class ModelRun:
    spec: ModelSpec
    forecasts: tuple[ForecastRow, ...]


@dataclass(frozen=True, slots=True)
class ComparisonRun:
    definition: ComparisonDefinition
    selection: BoutSelection
    prior: AdoptedPrior
    k_config_path: str
    k_config_sha256: str
    models: tuple[ModelRun, ...]


@dataclass(slots=True)
class _State:
    ratings: dict[RikId, float] = field(default_factory=dict)
    counts: dict[RikId, int] = field(default_factory=dict)
    sources: dict[RikId, str] = field(default_factory=dict)


def load_adopted_prior(path: Path = DEFAULT_PRIOR_CSV) -> AdoptedPrior:
    """Load the retained unsmoothed paired curve without transforming it."""

    resolved = path.resolve()
    with resolved.open(newline="", encoding="utf-8") as stream:
        rows = tuple(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"Adopted prior CSV contains no rows: {resolved}")
    values: dict[str, float] = {}
    for row in rows:
        pair = row["rank_pair"]
        if pair in values:
            raise ValueError(f"Duplicate adopted-prior rank pair: {pair}")
        values[pair] = float(row["pre_smoothing_rating"])
    return AdoptedPrior(
        source_path=str(resolved),
        sha256=_sha256(resolved),
        rating_by_pair=values,
        fallback_rating=min(values.values()),
    )


def run_comparison(
    history: History,
    definition: ComparisonDefinition,
    *,
    prior: AdoptedPrior,
    k_config: Path = DEFAULT_K_CONFIG,
) -> ComparisonRun:
    """Run all four models over one shared canonical bout selection."""

    selection = select_rated_bouts(
        history,
        start_date=definition.start_date,
        end_date=definition.end_date,
    )
    contexts = tuple(_context(history, bout) for bout in selection.bouts)
    resolved_k = k_config.resolve()
    divisional_k = load_divisional_k_fn(resolved_k)
    models = tuple(
        _run_model(contexts, definition, spec, prior, divisional_k)
        for spec in MODEL_SPECS
    )
    expected_ids = tuple(_bout_key(row) for row in models[0].forecasts)
    for model in models[1:]:
        if tuple(_bout_key(row) for row in model.forecasts) != expected_ids:
            raise AssertionError(f"{model.spec.name} forecast domain differs from B")
    return ComparisonRun(
        definition=definition,
        selection=selection,
        prior=prior,
        k_config_path=str(resolved_k),
        k_config_sha256=_sha256(resolved_k),
        models=models,
    )


def rank_pair(chii: Chii) -> str:
    """Return the adopted table's side- and annotation-free pair label."""

    collapsed = collapse_chii(chii)
    return f"{collapsed.level.as_abbreviation()}{collapsed.number}"


def _context(history: History, bout: RatedBout) -> BoutContext:
    banzuke = history[bout.contest.id.date].banzuke
    return BoutContext(
        bout=bout,
        chii_a=banzuke.rikchii[bout.contest.rikishi_a]
        if bout.contest.rikishi_a in banzuke else None,
        chii_b=banzuke.rikchii[bout.contest.rikishi_b]
        if bout.contest.rikishi_b in banzuke else None,
    )


def _run_model(
    contexts: tuple[BoutContext, ...],
    definition: ComparisonDefinition,
    spec: ModelSpec,
    prior: AdoptedPrior,
    divisional_k: Callable[[int], float],
) -> ModelRun:
    state = _State()
    rows: list[ForecastRow] = []
    for context in contexts:
        bout = context.bout
        a = bout.contest.rikishi_a
        b = bout.contest.rikishi_b
        _ensure_rating(state, a, context.chii_a, spec, definition, prior)
        _ensure_rating(state, b, context.chii_b, spec, definition, prior)
        rating_a = state.ratings[a]
        rating_b = state.ratings[b]
        probability = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / definition.q))
        k_a = _k(context.chii_a, spec, definition, divisional_k)
        k_b = _k(context.chii_b, spec, definition, divisional_k)
        residual = float(bout.a_won) - probability
        delta_a = k_a * residual
        delta_b = -k_b * residual
        rows.append(ForecastRow(
            model=spec.name,
            date=bout.contest.id.date,
            day=int(bout.contest.id.day),
            rikishi_a=int(a),
            rikishi_b=int(b),
            chii_a=context.chii_a,
            chii_b=context.chii_b,
            rating_a_before=rating_a,
            rating_b_before=rating_b,
            rated_bouts_a_before=state.counts[a],
            rated_bouts_b_before=state.counts[b],
            probability_a_wins=probability,
            a_won=bout.a_won,
            k_a=k_a,
            k_b=k_b,
            delta_a=delta_a,
            delta_b=delta_b,
            rating_a_after=rating_a + delta_a,
            rating_b_after=rating_b + delta_b,
            initialisation_a=state.sources[a],
            initialisation_b=state.sources[b],
        ))
        state.ratings[a] = rating_a + delta_a
        state.ratings[b] = rating_b + delta_b
        state.counts[a] += 1
        state.counts[b] += 1
    return ModelRun(spec=spec, forecasts=tuple(rows))


def _ensure_rating(
    state: _State,
    rikishi: RikId,
    chii: Chii | None,
    spec: ModelSpec,
    definition: ComparisonDefinition,
    prior: AdoptedPrior,
) -> None:
    if rikishi in state.ratings:
        return
    if spec.informed_prior:
        rating, source = prior.rating_for(chii)
    else:
        rating, source = definition.constant_initial_rating, "constant"
    state.ratings[rikishi] = rating
    state.counts[rikishi] = 0
    state.sources[rikishi] = source


def _k(
    chii: Chii | None,
    spec: ModelSpec,
    definition: ComparisonDefinition,
    divisional_k: Callable[[int], float],
) -> float:
    if not spec.divisional_k or chii is None:
        return definition.constant_k
    return divisional_k(chii.ordinal())


def _bout_key(row: ForecastRow) -> tuple[Date, int, int, int]:
    return row.date, row.day, row.rikishi_a, row.rikishi_b


def score(row: ForecastRow) -> tuple[float, float]:
    """Return log and Brier loss for one immutable forecast."""

    actual = float(row.a_won)
    result_probability = row.probability_a_wins if row.a_won else 1.0 - row.probability_a_wins
    return -math.log(max(result_probability, 1e-15)), (row.probability_a_wins - actual) ** 2


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

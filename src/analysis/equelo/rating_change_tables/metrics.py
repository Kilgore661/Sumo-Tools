"""Per-bout metric collection for production Rating Changes tables."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode, simulate
from src.analysis.equelo.fixed_supported.api import master_chii_initial_rating_map_path
from src.analysis.equelo.fixed_supported.build import make_chii_initialiser, oracle_collapse_mode
from src.analysis.equelo.fixed_supported.master_map import (
    load_master_chii_initial_rating_map,
    ratings_by_chii,
)
from src.analysis.equelo.fixed_supported.model import (
    K_CONFIG,
    K_POLICY,
    OUTPUT_ROOT as FIXED_SUPPORTED_OUTPUT_ROOT,
    Q,
)
from src.sumo_core.Banzuke import Banzuke
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult

from .model import BoutMetrics


class RatingChangeMetricsObserver:
    """Collect rated-bout count and K-normalised movement by rikishi/date."""

    def __init__(self, k_fn):
        self.k_fn = k_fn
        self._chii_by_date_rikishi: dict[Date, dict[RikId, Chii]] = {}
        self._actual_bouts: dict[RikId, dict[Date, int]] = defaultdict(lambda: defaultdict(int))
        self._normalised_delta: dict[RikId, dict[Date, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.metrics_by_rikishi_date: dict[RikId, dict[Date, BoutMetrics]] = defaultdict(dict)

    def on_basho_start(self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke) -> None:
        self._chii_by_date_rikishi[date] = dict(banzuke.rikchii)

    def on_entry(self, date: Date, rikid: RikId, rating: float, ratings: dict[RikId, float]) -> None:
        pass

    def on_retirement(
        self,
        date: Date,
        rikid: RikId,
        rating: float,
        n: int,
        delta: float,
        delta_per_rikishi: float,
        abs_delta_per_rikishi: float,
        closed: bool,
    ) -> None:
        pass

    def on_day_start(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None:
        pass

    def on_bout(
        self,
        date: Date,
        day: Day,
        bout: BoutResult,
        delta1: float,
        delta2: float,
        r1_before: float,
        r2_before: float,
        r1_after: float,
        r2_after: float,
        rating_mass_before: float,
        rating_mass_after: float,
    ) -> None:
        self._record(date=date, rikishi_id=bout.rikishi1, delta=float(delta1))
        self._record(date=date, rikishi_id=bout.rikishi2, delta=float(delta2))

    def on_ignored_bout(self, date: Date, day: Day, bout: BoutResult) -> None:
        pass

    def on_day_end(self, date: Date, day: Day, ratings: dict[RikId, float]) -> None:
        pass

    def on_basho_end(self, date: Date, ratings: dict[RikId, float], banzuke: Banzuke) -> None:
        rikishi_ids = set(self._actual_bouts) | set(self._normalised_delta)
        for rikishi_id in rikishi_ids:
            actual = int(self._actual_bouts[rikishi_id].get(date, 0))
            normalised = float(self._normalised_delta[rikishi_id].get(date, 0.0))
            if actual or normalised:
                self.metrics_by_rikishi_date[rikishi_id][date] = BoutMetrics(
                    actual_bouts=actual,
                    normalised_delta=normalised,
                )

    def _record(self, *, date: Date, rikishi_id: RikId, delta: float) -> None:
        chii = self._chii_by_date_rikishi[date][rikishi_id]
        k = float(self.k_fn(chii.ordinal()))
        self._actual_bouts[rikishi_id][date] += 1
        self._normalised_delta[rikishi_id][date] += delta / k if k else 0.0


def collect_fixed_supported_bout_metrics(
    *,
    raw_history: History,
    master_map_path: Path | None = None,
    fixed_supported_output_root: Path = FIXED_SUPPORTED_OUTPUT_ROOT,
) -> tuple[History, dict[RikId, dict[Date, BoutMetrics]]]:
    """Return fixed-supported oracle history and per-basho bout metrics.

    The site table uses fixed-supported day-end ratings for endpoints. This
    helper replays the same fixed-supported simulation only to observe rated
    bout counts and ``delta / K`` movement, because those values are not present
    in the persisted day-end rating artifact.
    """

    resolved_master_map_path = (
        master_map_path
        if master_map_path is not None
        else master_chii_initial_rating_map_path(fixed_supported_output_root)
    )
    oracle = make_oracle(raw_history, collapse_mode=oracle_collapse_mode())
    params = build_elo_params(k_policy=K_POLICY, q=Q, config_path=K_CONFIG)
    entrant_initial_ratings = ratings_by_chii(
        load_master_chii_initial_rating_map(resolved_master_map_path)
    )
    observer = RatingChangeMetricsObserver(params.k)
    simulate(
        history=oracle.history,
        params=params,
        entrant_initialiser=make_chii_initialiser(entrant_initial_ratings),
        mode=SimulationMode.CLOSED,
        observer=observer,
    )
    return oracle.history, observer.metrics_by_rikishi_date

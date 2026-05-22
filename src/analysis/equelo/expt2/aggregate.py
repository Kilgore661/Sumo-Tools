from __future__ import annotations

from collections import defaultdict

from ....sumo_core.History import History, Date
from ....sumo_core.Chii import Chii
from ....sumo_core.BasicPrimitives import RikId

from ..expt1.simulate import SimulationResult
from .types import AggregateResult


def aggregate(history: History, results: SimulationResult) -> AggregateResult:
    """Aggregate basho-start observations into mean rating by chii.

    The contract is Expt2's contract:
    * use basho-start observations only
    * group by canonical chii on the cleaned banzuke
    * use the arithmetic mean
    """
    totals: dict[Chii, float] = defaultdict(float)
    counts: dict[Chii, int] = defaultdict(int)

    for date in sorted(history.keys()):
        if date not in results.basho_start_ratings:
            continue

        basho_state = history[date]
        start_ratings = results.basho_start_ratings[date]

        for rikid, chii in basho_state.banzuke.rikchii.items():
            rating = start_ratings[rikid]
            totals[chii] += rating
            counts[chii] += 1

    mean_by_chii = {chii: totals[chii] / counts[chii] for chii in counts}
    return AggregateResult(mean_by_chii=mean_by_chii, count_by_chii=dict(counts))

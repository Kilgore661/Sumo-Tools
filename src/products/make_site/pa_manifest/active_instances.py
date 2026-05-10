"""PA manifest constants for the currently active page ids."""

from __future__ import annotations

from .chart_instances import (
    banzuke_division_by_era,
    career_length,
    division_stability,
    finish_by_chii,
    lower_rank_rating_stability,
    makuuchi_rank_by_era,
    rank_at_retirement,
    v5_landmark_policy,
    win_probability_by_standing,
)
from .chart_pa import ChartPA, EssayPA, ExcludedPA, MultiViewPA
from .table_instances import banzuke_changes, standings_by_wins, typical_equelo_values
from .table_pa import TablePA

PA_INSTANCE = ChartPA | EssayPA | ExcludedPA | MultiViewPA | TablePA


ACTIVE_PA_MANIFESTS: dict[str, PA_INSTANCE] = {
    "banzuke_changes": banzuke_changes,
    "standings_by_wins": standings_by_wins,
    "finish_by_chii": finish_by_chii,
    "banzuke_division_by_era": banzuke_division_by_era,
    "makuuchi_rank_by_era": makuuchi_rank_by_era,
    "division_stability": division_stability,
    "win_probability_by_standing": win_probability_by_standing,
    "career_length": career_length,
    "rank_at_retirement": rank_at_retirement,
    "typical_equelo_values": typical_equelo_values,
    "v5_landmark_policy": v5_landmark_policy,
    "lower_rank_rating_stability": lower_rank_rating_stability,
}


def validate_active_pa_manifests() -> None:
    for page_id, pa in ACTIVE_PA_MANIFESTS.items():
        if page_id != pa.id:
            raise ValueError(f"{page_id}: PA id is {pa.id!r}")
        pa.validate()


validate_active_pa_manifests()
